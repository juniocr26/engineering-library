#!/usr/bin/env python3
"""Prepare narrow documentation mounts for the existing backend service.

The generated Compose overlay is installation-specific runtime configuration,
not a second stack. This helper does not invoke Docker or restart containers.
"""
import argparse
import json
import os
from pathlib import Path
import re


def project_catalog(library):
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
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or not isinstance(source, str) or Path(source).is_absolute():
            raise ValueError('Invalid project catalog entry')
        location = (library / source).absolute()
        location = Path(os.path.normpath(location))
        if location in result or slug in result.values():
            raise ValueError('Duplicate project catalog entry')
        result[location] = slug
    return result


def project_roots(library, collections, explicit_roots=None):
    catalog = project_catalog(library)
    roots = list(explicit_roots) if explicit_roots else [library.parent]
    if collections:
        if catalog is not None:
            metadata = json.loads((library / 'docs/.catalog.json').read_text())
            roots = [(library / source['path']).resolve() for source in metadata['sourceRoots']]
        else:
            manifest = json.loads((library / 'tools/docs_manifest.json').read_text())
            roots = [(library / value).resolve() for value in manifest['project_roots']]
    result = []
    for root in dict.fromkeys(roots):
        for path in sorted(root.iterdir()):
            if (path == library and catalog is None) or path.name == 'skills' or path.is_symlink():
                continue
            if catalog is not None and path not in catalog:
                continue
            if (path / 'docs').exists() and (library / 'docs').exists() and (path / 'docs').samefile(library / 'docs'):
                continue  # Same library mounted through another container path.
            if path.is_dir() and (path / '.git').exists():
                if catalog is None and not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', path.name):
                    raise ValueError(f'Unsupported project slug: {path.name}')
                result.append(path)
    if len({catalog[p] if catalog is not None else p.name for p in result}) != len(result):
        raise ValueError('Duplicate project slugs across source collections')
    return roots, result


def prepare(library, output, collections=False, bindings=None):
    library = library.resolve()
    output = output.resolve()
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
    catalog = project_catalog(library)
    for index, root in enumerate(roots):
        target = '/sources' if index == 0 else f'/extra-sources-{index}'
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
        docs.mkdir(exist_ok=True)
        if not existed and hasattr(os, 'geteuid') and os.geteuid() == 0:
            owner = project.stat()
            os.chown(docs, owner.st_uid, owner.st_gid)
        target = '/project-docs/' + slug
        host_docs = str(Path(bindings[project.parent]) / project.name / 'docs') if bindings else str(docs)
        volumes.append({'type': 'bind', 'source': host_docs, 'target': target, 'read_only': False,
                        'bind': {'create_host_path': False}})
        configuration.append({'slug': slug,
                              'source': source_mounts[project.parent] + '/' + project.name,
                              'destination': target})
    # Source-root sets are explicit and default discovery remains sibling-only.
    overlay = {'services': {'backend': {'volumes': volumes}}}
    (output / 'mounts.json').write_text(json.dumps(overlay, indent=2) + '\n')
    (output / 'projects.json').write_text(json.dumps({'projects': configuration}, indent=2) + '\n')
    return {'projects': len(projects), 'source_roots': len(roots),
            'overlay': str(output / 'mounts.json'), 'selection': str(output / 'projects.json'),
            'restart_performed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collections', action='store_true', help='Explicitly use the existing private collection roots')
    parser.add_argument('--output', type=Path, required=True, help='Transient directory for installation-specific JSON files')
    parser.add_argument('--bind-root', action='append', default=[], metavar='CONTAINER_PATH=COMPOSE_SOURCE',
                        help='Docker-only setup: mounted collection root and its host path relative to the base Compose file; repeat for explicit collections')
    args = parser.parse_args()
    bindings = {}
    for value in args.bind_root:
        mounted, separator, host = value.partition('=')
        if not separator or not mounted or not host:
            parser.error('--bind-root expects CONTAINER_PATH=COMPOSE_SOURCE')
        root = Path(mounted).resolve()
        if root in bindings:
            parser.error('Duplicate --bind-root collection')
        bindings[root] = host
    print(json.dumps(prepare(Path(__file__).resolve().parent.parent, args.output, args.collections, bindings or None)))
