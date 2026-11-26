#!/usr/bin/env python3
"""Prepare authorized source/docs mounts and recover existing backend configuration.

Legacy preparation can create missing docs/ directories. Host-only access flags
persist local configuration; --apply explicitly recreates only the backend after
preflight checks. The application receives no Docker socket or host executor.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import posixpath
import subprocess
import tempfile
import sys
import unicodedata
from pathlib import PureWindowsPath


def valid_project_directory(value):
    return (isinstance(value, str) and 1 <= len(value.encode('utf-8')) <= 255
            and not re.search(r'[\x00-\x1f\x7f\\/:*?"<>|]', value)
            and not value.endswith(('.', ' '))
            and not re.match(r'^(?:CON|PRN|AUX|NUL|(?:COM|LPT)[1-9])(?:[ .]|$)', value, re.I))


def host_path(value):
    return PureWindowsPath(value) if PureWindowsPath(value).drive else Path(value)


def host_library(library):
    if not Path('/.dockerenv').exists():
        return library
    matches = []
    for line in Path('/proc/self/mountinfo').read_text().splitlines():
        fields = line.split(); separator = fields.index('-')
        decode = lambda text: re.sub(r'\\([0-7]{3})', lambda m: chr(int(m[1], 8)), text)
        target, origin, device = map(decode, (fields[4], fields[3], fields[separator + 2]))
        if device.startswith('/run/host_mark/'):
            origin = posixpath.join(device.removeprefix('/run/host_mark'), origin.lstrip('/'))
        relative = library.relative_to(target) if library.is_relative_to(target) else None
        if relative is not None:
            matches.append((len(target), Path(origin) / relative))
    if not matches:
        raise ValueError('Host library mount cannot be established')
    return max(matches, key=lambda item: item[0])[1]


def source_child(parent, name):
    requested = parent / name
    if requested.is_symlink():
        raise ValueError('Linked source rejected')
    if not requested.exists():
        return requested
    children = list(parent.iterdir())
    exact = next((child for child in children if child.name == name), None)
    if exact is not None:
        return exact
    matches = [child for child in children if not child.is_symlink() and child.samefile(requested)]
    if len(matches) != 1:
        raise ValueError('Ambiguous source spelling')
    return matches[0]


def project_catalog(library, bindings=None):
    path = library / 'docs/.catalog.json'
    if path.is_symlink():
        raise ValueError('Symlink project catalog rejected')
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('version') != 1 or not isinstance(data.get('projects'), list):
        raise ValueError('Invalid project catalog')
    result = {}
    for entry in data['projects']:
        slug, source = entry.get('slug'), entry.get('sourcePath')
        if not valid_project_directory(slug) or not isinstance(source, str):
            raise ValueError('Invalid project catalog entry')
        if bindings:
            native_library = host_library(library)
            absolute = host_path(source)
            if not absolute.is_absolute():
                absolute = host_path(os.path.normpath(str(native_library / source)))
            matches = []
            for available, host in bindings.items():
                base = host_path(host)
                if not base.is_absolute():
                    base = host_path(os.path.normpath(str(native_library / host)))
                candidates = [base]
                for record in data.get('sourceRoots', []):
                    if record.get('containerPath') != available.as_posix():
                        continue
                    aliases = [host_path(value) for value in record.get('hostAliases', [])]
                    if base in aliases:
                        canonical = unicodedata.normalize('NFC', base.as_posix()).casefold()
                        candidates += [alias for alias in aliases if unicodedata.normalize('NFC', alias.as_posix()).casefold() == canonical]
                for candidate in candidates:
                    if absolute.is_relative_to(candidate):
                        relative = absolute.relative_to(candidate)
                        if '..' in relative.parts:
                            raise ValueError('Source path traversal rejected')
                        location = available
                        for name in relative.parts:
                            location = source_child(location, name)
                        matches.append((len(candidate.parts), location))
            if not matches:
                raise ValueError('Registered source is outside configured roots')
            location = max(matches, key=lambda item: item[0])[1]
        else:
            location = Path(os.path.normpath(str(library / source)))
        if not bindings and location.is_dir():
            location = checked_directory(location)
        if location in result or slug in result.values():
            raise ValueError('Duplicate project catalog entry')
        result[location] = slug
    return result


def project_roots(library, collections, explicit_roots=None):
    catalog = project_catalog(library, explicit_roots if isinstance(explicit_roots, dict) else None)
    roots = list(explicit_roots) if explicit_roots else [library.parent]
    if collections or (catalog is not None and not explicit_roots):
        if catalog is not None:
            metadata = json.loads((library / 'docs/.catalog.json').read_text())
            roots = [(library / source['path']).resolve() for source in metadata['sourceRoots']]
        else:
            manifest = json.loads((library / 'tools/docs_manifest.json').read_text())
            roots = [(library / value).resolve() for value in manifest['project_roots']]
    result = []
    for root in dict.fromkeys(roots):
        if root.is_symlink() or not root.is_dir():
            raise FileNotFoundError('Source root unavailable')
        candidates = sorted(catalog) if catalog is not None else sorted(root.iterdir())
        for path in candidates:
            if not path.is_relative_to(root) or (path == root and not (root / '.git').exists()):
                continue
            if (path == library and catalog is None) or path.name == 'skills' or path.is_symlink():
                continue
            if (path / 'docs').exists() and (library / 'docs').exists() and (path / 'docs').samefile(library / 'docs'):
                continue
            if path.is_dir() and (path / '.git').exists():
                checked_directory(path)
                if catalog is None and not valid_project_directory(path.name):
                    raise ValueError('Unsupported project directory')
                if path not in result:
                    result.append(path)
    if len({catalog[p] if catalog is not None else p.name for p in result}) != len(result):
        raise ValueError('Duplicate project slugs across source collections')
    return roots, result


def prepare(library, output, collections=False, bindings=None):
    library = library.resolve()
    output = output.resolve()
    if bindings:
        if any(root.is_symlink() for root in bindings):
            raise ValueError('Linked source collection rejected')
        normalized = {root.resolve(): host for root, host in bindings.items()}
        if len(normalized) != len(bindings):
            raise ValueError('Duplicate source collection aliases')
        bindings = normalized
    if collections and bindings:
        raise ValueError('Use --collections or explicit --bind-root values, not both')
    roots, projects = project_roots(library, collections, explicit_roots=bindings)
    output.mkdir(parents=True, exist_ok=True)
    volumes = [
        {'type': 'bind', 'source': './docs' if bindings else str(library / 'docs'), 'target': '/docs', 'read_only': False,
         'bind': {'create_host_path': False}},
        {'type': 'bind', 'source': './agent' if bindings else str(library / 'agent'), 'target': '/agent', 'read_only': True,
         'bind': {'create_host_path': False}},
    ]
    source_mounts = {}
    catalog = project_catalog(library, bindings)
    for index, root in enumerate(roots):
        target = '/sources' if index == 0 else f'/extra-sources-{index}'
        metadata_path = library / 'docs/.catalog.json'
        if metadata_path.exists():
            for record in json.loads(metadata_path.read_text())['sourceRoots']:
                configured = Path(record['containerPath']) if bindings else library / record['path']
                if configured.resolve() == root.resolve():
                    target = record['containerPath']
        source_mounts[root] = target
        volumes.append({'type': 'bind', 'source': bindings[root] if bindings else str(root), 'target': target, 'read_only': True,
                        'bind': {'create_host_path': False}})
    configuration = []
    for project in projects:
        slug = catalog[project] if catalog is not None else project.name
        docs = project / 'docs'
        if docs.is_symlink():
            raise ValueError(f'Symlink documentation destination rejected: {docs}')
        # This is the only creation outside the generated runtime configuration.
        # Existing documentation is never moved, removed or rewritten here.
        existed = docs.exists()
        if not existed:
            docs.mkdir()
        if not existed and hasattr(os, 'geteuid') and os.geteuid() == 0:
            owner = project.stat()
            os.chown(docs, owner.st_uid, owner.st_gid)
        target = '/project-docs/' + slug
        parent = max((root for root in roots if project.is_relative_to(root)), key=lambda root: len(root.parts))
        relative = project.relative_to(parent)
        host_docs = str(host_path(bindings[parent]).joinpath(*relative.parts, 'docs')).replace('\\', '/') if bindings else str(docs)
        volumes.append({'type': 'bind', 'source': host_docs, 'target': target, 'read_only': False,
                        'bind': {'create_host_path': False}})
        configuration.append({'slug': slug,
                              'source': source_mounts[parent] if relative == Path('.') else source_mounts[parent] + '/' + relative.as_posix(),
                              'destination': target})
    # Registered paths use their authorized roots; uncataloged legacy discovery stays sibling-only.
    overlay = {'services': {'backend': {'volumes': volumes}}}
    atomic_json(output / 'mounts.json', overlay)
    atomic_json(output / 'projects.json', {'projects': configuration})
    return {'projects': len(projects), 'source_roots': len(roots),
            'overlay': str(output / 'mounts.json'), 'selection': str(output / 'projects.json'),
            'restart_performed': False}


def atomic_json(path, data):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('Linked configuration rejected')
    for parent in path.parents:
        if parent.is_symlink():
            raise ValueError('Linked configuration directory rejected')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def checked_directory(path):
    if not Path(path).is_absolute() or '..' in Path(path).parts:
        raise ValueError('An absolute directory without traversal is required')
    path = Path(os.path.abspath(path))
    if any(part.is_symlink() for part in (path, *path.parents)) or not path.is_dir() or not os.access(path, os.R_OK | os.X_OK):
        raise ValueError('Directory unavailable or linked')
    if sys.platform == 'darwin':
        import fcntl
        descriptor = os.open(path, os.O_RDONLY)
        try:
            # Darwin F_GETPATH returns the stored spelling without enumerating siblings.
            path = Path(os.fsdecode(fcntl.fcntl(descriptor, 50, bytes(1024)).split(b'\0', 1)[0]))
        finally:
            os.close(descriptor)
    else:
        path = path.resolve(strict=True)
    return path


def authorized_aliases(path):
    spelling = str(path)
    candidates = {unicodedata.normalize(form, value) for form in ('NFC', 'NFD')
                  for value in (spelling, spelling.lower(), spelling.upper(), spelling.swapcase())}
    aliases = []
    for value in candidates:
        candidate = Path(value)
        if any(part.is_symlink() for part in (candidate, *candidate.parents)):
            continue
        try:
            if candidate.is_dir() and candidate.samefile(path):
                aliases.append(candidate.as_posix())
        except OSError:
            continue
    return sorted(set(aliases))


def compose(library, *args):
    return subprocess.check_output(['docker', 'compose', '--project-directory', str(library), *args], text=True)


def running_mounts(library):
    identifiers = subprocess.check_output(['docker', 'ps', '-q', '--filter', 'label=com.docker.compose.service=backend'], text=True).split()
    if not identifiers:
        raise ValueError('Existing backend is required for initial access recovery')
    candidates = json.loads(subprocess.check_output(['docker', 'inspect', *identifiers], text=True))
    matches = []
    for candidate in candidates:
        for mount in candidate['Mounts']:
            if mount['Type'] == 'bind' and mount['Destination'] == '/docs':
                source = Path(mount['Source'])
                if source.is_dir() and source.samefile(library / 'docs'):
                    matches.append(candidate)
    if len(matches) != 1:
        raise ValueError('Backend mount identity is unavailable or ambiguous')
    info = matches[0]
    volumes = []
    for mount in info['Mounts']:
        if mount['Type'] != 'bind':
            continue
        checked_directory(mount['Source'])
        volumes.append({'type': 'bind', 'source': mount['Source'], 'target': mount['Destination'],
                        'read_only': not mount['RW'], 'bind': {'create_host_path': False}})
    return volumes


def restore_access(library, output, config):
    if config.get('schema') != 1 or not isinstance(config.get('volumes'), list):
        raise ValueError('Invalid local filesystem configuration')
    targets = set()
    identities = config.get('hostRootIdentities', {})
    for volume in config['volumes']:
        checked_directory(volume['source'])
        target = volume['target']
        if target in identities:
            current = Path(volume['source']).stat()
            if identities[target] != [current.st_dev, current.st_ino]:
                raise ValueError('Authorized source root identity changed; preserve configuration and inspect storage')
        if target in targets or volume.get('type') != 'bind' or volume.get('bind') != {'create_host_path': False}:
            raise ValueError('Invalid or duplicate mount')
        targets.add(target)
    overlay = {'services': {'backend': {'volumes': config['volumes']}}}
    override = library / 'compose.override.yaml'
    if override.exists():
        if override.is_symlink() or json.loads(override.read_text()) != config.get('installedOverlay', overlay):
            raise ValueError('Existing Compose override belongs to another configuration')
    atomic_json(output / 'mounts.json', overlay)
    atomic_json(override, overlay)
    config['installedOverlay'] = overlay
    atomic_json(output / 'access.json', config)
    return overlay


def authorize_root(library, config, location, create_docs=False):
    root = checked_directory(location)
    if root == Path(root.anchor) or root == Path.home() or (Path.home().is_dir() and root.samefile(Path.home())):
        raise ValueError('Select a bounded project collection, not a filesystem root or entire home')
    if any(volume['source'] == str(root) for volume in config['volumes']):
        raise ValueError('Filesystem location is already configured')
    slots = [int(match[1]) for volume in config['volumes'] if (match := re.match(r'^/extra-sources-([1-9][0-9]*)(?:/|$)', volume['target']))]
    base = '/extra-sources-' + str(max(slots, default=0) + 1)
    project_root = (root / '.git').exists()
    target = base + '/' + root.name if project_root else base
    try:
        reference = os.path.relpath(root, library).replace('\\', '/')
    except ValueError as error:
        raise ValueError('Source has no relative path from the library; cross-drive authorization rejected') from error
    record = {'path': reference, 'containerPath': target}
    aliases = authorized_aliases(root)
    if len(aliases) > 1:
        record['hostAliases'] = aliases
    if project_root:
        record['projectRoot'] = True
    config['applied'] = False
    identity = root.stat()
    config.setdefault('hostRootIdentities', {})[target] = [identity.st_dev, identity.st_ino]
    config['sourceRoots'].append(record)
    config['volumes'].append({'type': 'bind', 'source': str(root), 'target': target, 'read_only': True,
                              'bind': {'create_host_path': False}})
    candidates = []
    if project_root:
        candidates = [root]
    else:
        excluded = {'.git', 'node_modules', 'vendor', 'docs', 'agent', '.local-backups', 'storage', 'ollama'}
        for folder, directories, _ in os.walk(root, followlinks=False):
            path = Path(folder)
            directories[:] = [name for name in directories if name not in excluded and not name.startswith('.') and not (path / name).is_symlink()]
            if (path / '.git').exists():
                candidates.append(path); directories[:] = []
    existing = {volume['target'] for volume in config['volumes']}
    for project in candidates:
        checked_directory(project)
        if not valid_project_directory(project.name):
            raise ValueError('Unsupported project directory')
        destination = '/project-docs/' + project.name
        if destination in existing:
            raise ValueError('Conflicting project documentation directory')
        docs = project / 'docs'
        if not docs.exists():
            if not create_docs:
                raise ValueError('Documentation directory missing; authorized host setup requires --create-docs')
            docs.mkdir()
        checked_directory(docs)
        config['volumes'].append({'type': 'bind', 'source': str(docs), 'target': destination, 'read_only': False,
                                  'bind': {'create_host_path': False}})
        existing.add(destination)
    return record


def git_identity(path):
    path = checked_directory(path)
    result = subprocess.run(['git', '-c', f'safe.directory={path}', '-C', str(path),
                             'rev-list', '--max-parents=0', 'HEAD'], capture_output=True, text=True)
    roots = result.stdout.split()
    if result.returncode or not roots or any(not re.fullmatch(r'[0-9a-f]{40,64}', value) for value in roots):
        raise ValueError('Source Git identity unavailable')
    return hashlib.sha256('\n'.join(sorted(roots)).encode()).hexdigest()


def plan_relocation(library, config, project_id, reference):
    """Return a reviewable proposal only; never install mounts or alter a catalog."""
    library = checked_directory(library)
    if not isinstance(reference, str) or not reference or re.search(r'[\x00-\x1f\x7f]', reference):
        raise ValueError('Invalid relative source reference')
    reference = reference.replace('\\', '/')
    if reference.startswith('/') or re.match(r'^[A-Za-z]:', reference):
        raise ValueError('Expected relative source reference')
    catalog_path = library / 'docs/.catalog.json'
    if catalog_path.is_symlink():
        raise ValueError('Linked project catalog rejected')
    catalog = json.loads(catalog_path.read_text())
    if config.get('schema') != 1 or config.get('sourceRoots') != catalog['sourceRoots']:
        raise ValueError('Local access configuration and catalog mappings differ')
    entries = [entry for entry in catalog['projects'] if entry['id'] == project_id]
    if len(entries) != 1:
        raise ValueError('Unknown or ambiguous project identity')
    entry = entries[0]
    source = checked_directory(Path(os.path.abspath(library / reference)))
    reference = os.path.relpath(source, library).replace('\\', '/')
    if source.name != entry['slug'] or source.name != entry.get('sourceDirectory', source.name):
        raise ValueError('Relocation must preserve the physical project directory and slug')
    if git_identity(source) != entry.get('sourceIdentity'):
        raise ValueError('Source identity changed')
    docs = checked_directory(source / 'docs')
    previous = Path(os.path.abspath(library / entry['sourcePath']))
    if previous.exists() or previous.is_symlink():
        raise ValueError('Previous source remains accessible; relocation is ambiguous')
    parent = previous.parent
    while not parent.exists():
        parent = parent.parent
    checked_directory(parent)
    roots = [volume for volume in config['volumes']
             if volume['target'] in {root['containerPath'] for root in config['sourceRoots']}]
    matches, seen, pending = [], set(), [source]
    pending += [Path(volume['source']) for volume in roots if Path(volume['source']).is_dir()]
    while pending:
        candidate = pending.pop()
        if candidate.is_symlink():
            continue
        checked_directory(candidate)
        stat = candidate.stat()
        key = (stat.st_dev, stat.st_ino)
        if key in seen:
            continue
        seen.add(key)
        if len(seen) > 10000:
            raise ValueError('Source search incomplete; relocation is ambiguous')
        if (candidate / '.git').exists():
            if git_identity(candidate) == entry['sourceIdentity']:
                matches.append(candidate)
        else:
            pending += [child for child in candidate.iterdir() if child.is_dir() and not child.is_symlink()]
    if len(matches) != 1 or not matches[0].samefile(source):
        raise ValueError('Multiple accessible source copies; relocation is ambiguous')
    proposed = copy.deepcopy(config)
    old_roots = [root for root in proposed['sourceRoots']
                 if root.get('projectRoot') and root['path'] == entry['sourcePath']]
    available = [volume for volume in roots if Path(volume['source']).is_dir()
                 and source.is_relative_to(Path(volume['source']))]
    changes = []
    if old_roots:
        root = old_roots[0]
        target = root['containerPath']
        root['path'] = reference
        root.pop('mountIdentity', None)
        root.pop('hostAliases', None)
        volume = next(volume for volume in proposed['volumes'] if volume['target'] == target)
        if volume.get('read_only') is not True or volume.get('bind') != {'create_host_path': False}:
            raise ValueError('Existing source mapping must remain read-only and bounded')
        changes.append({'target': target, 'before': volume['source'], 'after': str(source)})
        volume['source'] = str(source)
        stat = source.stat()
        proposed.setdefault('hostRootIdentities', {})[target] = [stat.st_dev, stat.st_ino]
    elif not available:
        slots = [int(match[1]) for volume in proposed['volumes']
                 if (match := re.match(r'^/extra-sources-([1-9][0-9]*)(?:/|$)', volume['target']))]
        target = f'/extra-sources-{max(slots, default=0) + 1}/{source.name}'
        proposed['sourceRoots'].append({'path': reference, 'containerPath': target, 'projectRoot': True})
        proposed['volumes'].append({'type': 'bind', 'source': str(source), 'target': target,
                                   'read_only': True, 'bind': {'create_host_path': False}})
        stat = source.stat()
        proposed.setdefault('hostRootIdentities', {})[target] = [stat.st_dev, stat.st_ino]
        changes.append({'target': target, 'before': None, 'after': str(source)})
    destination = '/project-docs/' + entry['slug']
    volumes = [volume for volume in proposed['volumes'] if volume['target'] == destination]
    if len(volumes) != 1 or volumes[0].get('read_only') is not False:
        raise ValueError('Existing writable documentation mapping is unavailable')
    changes.append({'target': destination, 'before': volumes[0]['source'], 'after': str(docs)})
    volumes[0]['source'] = str(docs)
    proposed['applied'] = False
    proposed['installedOverlay'] = {'services': {'backend': {'volumes': copy.deepcopy(proposed['volumes'])}}}
    entry['sourcePath'] = reference
    catalog['sourceRoots'] = copy.deepcopy(proposed['sourceRoots'])
    return {'projectId': project_id, 'sourcePath': reference, 'mountChanges': changes,
            'documentationHostWritable': os.access(docs, os.W_OK),
            'catalog': catalog, 'access': proposed, 'applied': False}


def apply_access(library, output, config):
    state = library / 'backend/storage/makedocs/state'
    if any(state.glob('*.pending.json')):
        raise ValueError('MakeDocs recovery must finish before container recreation')
    for path in state.joinpath('management').glob('*.json'):
        if re.fullmatch(r'[0-9a-f]{32}\.json', path.name) and json.loads(path.read_text()).get('state') not in ('completed', 'error', 'interrupted'):
            raise ValueError('Catalog operation is still running')
    # The existing entrypoint runs db:prepare and catalog:sync. Refuse pending migrations.
    compose(library, 'exec', '-T', 'backend', 'bundle', 'exec', 'rails', 'db:abort_if_pending_migrations')
    compose(library, 'config', '--quiet')
    previous = {'services': {'backend': {'volumes': running_mounts(library)}}}
    atomic_json(output / 'previous-mounts.json', previous)
    try:
        compose(library, 'up', '-d', '--no-deps', '--force-recreate', '--wait', '--wait-timeout', '180', 'backend')
        actual = {volume['target']: volume for volume in running_mounts(library)}
        for desired in config['volumes']:
            if actual.get(desired['target']) != desired:
                raise ValueError('Runtime mount verification failed; catalog mapping preserved')
    except (ValueError, subprocess.CalledProcessError):
        atomic_json(output / 'mounts.json', previous)
        atomic_json(library / 'compose.override.yaml', previous)
        config['installedOverlay'] = previous
        config['applied'] = False
        atomic_json(output / 'access.json', config)
        compose(library, 'up', '-d', '--no-deps', '--force-recreate', '--wait', '--wait-timeout', '180', 'backend')
        raise
    root_stats = json.loads(compose(library, 'exec', '-T', 'backend', 'ruby', '-rjson', '-e',
                                  'puts JSON.generate(ARGV.to_h { |path| stat=File.stat(path); [path,[stat.dev,stat.ino]] })',
                                  *[root['containerPath'] for root in config['sourceRoots']]))
    for root in config['sourceRoots']:
        root['mountIdentity'] = root_stats[root['containerPath']]
    catalog_path = library / 'docs/.catalog.json'
    if catalog_path.is_symlink():
        raise ValueError('Linked project catalog rejected')
    # Use the same catalog lock and atomic writer as registration; preserve concurrent entries.
    compose(library, 'exec', '-T', 'backend', 'ruby', '-r./lib/documentation/catalog', '-rjson', '-e',
            'Documentation::Catalog.new(ENV.fetch("CATALOG_ROOT", "/docs")).change { |data| data["sourceRoots"] = JSON.parse(ARGV.fetch(0)) }',
            json.dumps(config['sourceRoots'], ensure_ascii=False))
    config['applied'] = True
    atomic_json(output / 'access.json', config)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serve', action='store_true', help='Host-only: serve bounded project filesystem operations without Docker daemon access')
    parser.add_argument('--collections', action='store_true')
    parser.add_argument('--output', type=Path, help='Defaults to ignored persistent local storage')
    parser.add_argument('--bind-root', action='append', default=[], metavar='CONTAINER_PATH=COMPOSE_SOURCE')
    parser.add_argument('--recover-running', action='store_true', help='Host-only: preserve the actual running backend bind mounts')
    parser.add_argument('--restore', action='store_true', help='Host-only: regenerate the persistent overlay from saved access configuration')
    parser.add_argument('--authorize-root', type=Path, action='append', default=[], help='Host-only initial authorization of a bounded collection or project directory')
    parser.add_argument('--create-docs', action='store_true', help='Explicitly allow host setup to create missing docs directories')
    parser.add_argument('--apply', action='store_true', help='Host-only: verify migrations, recreate only backend, verify mounts, then persist source mappings')
    parser.add_argument('--plan-relocation', metavar='PROJECT_ID=RELATIVE_PATH', help='Host-only: print a relocation proposal without changing files or containers')
    args = parser.parse_args()
    library = Path(__file__).resolve().parent.parent
    output = args.output or library / 'backend/storage/makedocs/filesystem'
    if args.serve:
        if any((args.collections, args.bind_root, args.recover_running, args.restore, args.authorize_root, args.create_docs, args.apply, args.plan_relocation)):
            parser.error('--serve cannot be combined with mount preparation or mutation flags')
        if Path('/.dockerenv').exists():
            parser.error('The filesystem adapter must run on the host')
        from host_filesystem import HostFilesystem
        HostFilesystem(library, output / 'host').serve()
        raise SystemExit(0)
    if args.plan_relocation:
        if Path('/.dockerenv').exists() or args.apply or args.restore or args.authorize_root or args.recover_running or args.bind_root or args.collections or args.create_docs:
            parser.error('Relocation planning is read-only and host-only; do not combine with mutation flags')
        project_id, separator, reference = args.plan_relocation.partition('=')
        if not separator:
            parser.error('--plan-relocation expects PROJECT_ID=RELATIVE_PATH')
        access = output / 'access.json'
        if access.is_symlink():
            parser.error('Linked local access configuration rejected')
        print(json.dumps(plan_relocation(library, json.loads(access.read_text()), project_id, reference), ensure_ascii=False, indent=2))
        raise SystemExit(0)
    if args.recover_running or args.restore or args.authorize_root or args.apply:
        if Path('/.dockerenv').exists():
            parser.error('Filesystem authorization and Docker execution must run on the host')
        if args.bind_root or args.collections:
            parser.error('Do not mix local access configuration with legacy binding flags')
        access = output / 'access.json'
        if args.recover_running:
            if access.exists():
                parser.error('Existing access configuration must be restored, not overwritten')
            config = {'schema': 1, 'sourceRoots': json.loads((library / 'docs/.catalog.json').read_text())['sourceRoots'],
                      'volumes': running_mounts(library)}
            config['hostRootIdentities'] = {}
            for root in config['sourceRoots']:
                mount = next(volume for volume in config['volumes'] if volume['target'] == root['containerPath'])
                info = Path(mount['source']).stat()
                config['hostRootIdentities'][root['containerPath']] = [info.st_dev, info.st_ino]
        else:
            if access.is_symlink():
                parser.error('Linked local access configuration rejected')
            config = json.loads(access.read_text())
        for location in args.authorize_root:
            authorize_root(library, config, location, args.create_docs)
        restore_access(library, output, config)
        if args.apply:
            apply_access(library, output, config)
        print(json.dumps({'overlay': str(library / 'compose.override.yaml'), 'source_roots': len(config['sourceRoots']),
                          'backend_recreated': bool(args.apply), 'host_execution_required': True}))
    else:
        if args.collections and args.bind_root:
            parser.error('Use --collections or --bind-root, not both')
        bindings = {}
        for value in args.bind_root:
            mounted, separator, host = value.partition('=')
            if not separator or not mounted or not host:
                parser.error('--bind-root expects CONTAINER_PATH=COMPOSE_SOURCE')
            root = checked_directory(mounted)
            if root in bindings:
                parser.error('Duplicate source root')
            bindings[root] = host
        print(json.dumps(prepare(library, output, args.collections, bindings or None)))
