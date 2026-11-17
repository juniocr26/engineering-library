#!/usr/bin/env python3
"""Read-only bilingual catalog, file, anchor, image and provenance checks."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


def project_directories(docs):
    """Shared assets and command recovery state are not catalog projects."""
    return {p.name for p in docs.iterdir()
            if p.name not in {'img', '.docs-state', '.evaluations'} and not p.is_symlink() and p.is_dir()}


def main():
    library = Path(__file__).absolute().parents[1]
    docs = library / 'docs'
    workspace = library.parents[1]
    spec = importlib.util.spec_from_file_location('documentation_parser', library / 'tools/check_docs.py')
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    config_path = library / 'tools/docs_manifest.json'
    project_paths, discovery_findings = parser.discover_projects(library, json.loads(config_path.read_text())) if config_path.exists() else ({}, [])
    errors, warnings = [[f['code'], f['path'], f['detail']] for f in discovery_findings], []
    pages = {p: p.read_text() for p in docs.rglob('*.md') if not parser.classify(workspace, p)}
    for name in ['README.md', 'README.pt-BR.md', 'backend/README.md', 'frontend/README.md']:
        p = library / name
        if p.is_file(): pages[p] = p.read_text()
    graph = {p: set() for p in pages}
    links = 0
    for p, body in pages.items():
        for target in parser.links(body):
            url = urlsplit(target)
            if url.scheme or url.netloc: continue
            public = unquote(url.path)
            raw = docs / public.removeprefix('/api/shared-assets/') if public.startswith('/api/shared-assets/') else library / 'frontend/public' / public.removeprefix('/') if public.startswith('/assets/') else p.parent / public if public else p
            if parser.classify(workspace, raw):
                # Fixture source links are metadata-only; no restricted target is opened.
                warnings.append(['restricted-reference', str(p.relative_to(library)), target]); continue
            destination = Path(os.path.normpath(raw))
            links += 1
            if not destination.exists(): errors.append(['missing-target', str(p.relative_to(library)), target])
            elif destination in pages:
                graph[p].add(destination)
                if url.fragment and unquote(url.fragment) not in parser.anchors(pages[destination]):
                    errors.append(['missing-anchor', str(p.relative_to(library)), target])
    def reachable(start):
        seen, pending = set(), [start]
        while pending:
            p = pending.pop()
            if p not in seen:
                seen.add(p); pending.extend(graph.get(p, set()) - seen)
        return seen
    manifest_path = docs / 'engineering-library/en/operations/catalog-provenance.json'
    manifest = json.loads(manifest_path.read_text())
    policy_path = docs / '.catalog-policy.json'
    temporary = set()
    if policy_path.is_symlink():
        raise ValueError('Symlink catalog lifecycle policy rejected')
    if policy_path.exists():
        policy = json.loads(policy_path.read_text())
        names = policy.get('temporary_projects') if policy.get('schema') == 1 else None
        if not isinstance(names, list) or any(not isinstance(s, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', s) for s in names) or len(set(names)) != len(names):
            raise ValueError('Invalid catalog lifecycle policy')
        temporary = set(names)
    # Historical provenance remains intact; it is not the permanent catalog.
    projects = {slug: record for slug, record in manifest['projects'].items() if slug not in temporary}
    actual = project_directories(docs)
    if actual != set(projects): errors.append(['project-collection-inventory-mismatch', sorted(actual)])
    private = {'vivabem', 'carteira-digital', 'cofre-paciente', 'hub-vivabem'}
    imported = 0
    for slug, metadata in projects.items():
        bios = []
        for folder in ('en', 'pt-br'):
            bio = docs / slug / folder / 'bio.md'
            body = bio.read_text() if bio.is_file() else ''
            frontmatter = re.match(r'\A---\n(.*?)\n---\n(.+)', body, re.S)
            if not frontmatter:
                errors.append(['invalid-bio', slug, folder])
            else:
                fields = dict(re.findall(r'^(id|name):\s*(.+)$', frontmatter[1], re.M))
                if set(fields) != {'id', 'name'}: errors.append(['invalid-bio-metadata', slug, folder])
                bios.append(fields)
        if len(bios) == 2 and bios[0] != bios[1]: errors.append(['bio-language-parity', slug])
        path_sets = []
        for folder in ('en', 'pt-br'):
            base = docs / slug
            lang_root = base / folder
            subset = {p for p in pages if p.is_relative_to(lang_root) and p.name != 'bio.md'}
            path_sets.append({p.relative_to(lang_root) for p in subset})
            readme = lang_root / 'README.md'
            if readme not in pages: errors.append(['missing-readme', slug, folder])
            seen = reachable(lang_root / 'index.md')
            for p in subset - seen: errors.append(['unreachable-from-project', str(p.relative_to(docs))])
            env = lang_root / 'env/index.md'
            if env not in pages or len(pages[env].splitlines()) < 5: errors.append(['missing-env-reference', slug, folder])
            if slug in private and (lang_root / 'testing').exists(): errors.append(['removed-testing-present', slug, folder])
        exceptions = {Path(x).relative_to(Path(x).parts[0]) for x in metadata.get('monolingual_history', [])}
        mismatch = (path_sets[0] ^ path_sets[1]) - exceptions
        if mismatch: errors.append(['language-path-parity', slug, sorted(map(str, mismatch))])
        for rel in path_sets[0] & path_sets[1]:
            en = pages[docs / slug / 'en' / rel]
            pt = pages[docs / slug / 'pt-br' / rel]
            if parser.question_ids(en) != parser.question_ids(pt): errors.append(['question-id-parity', slug, str(rel)])
            if rel == Path('env/index.md'):
                variables = lambda body: set(re.findall(r'\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b', body))
                if variables(en) != variables(pt): errors.append(['env-variable-parity', slug])
        for item in metadata.get('relocated_interviews', []):
            body = pages.get(library / item['destination'], '')
            headings = [line for line in body.splitlines() if line.startswith('#')]
            if headings != item['preserved_headings']:
                errors.append(['retained-interview-headings', slug, item['destination']])
        for item in metadata.get('imports', []):
            imported += 1
            source = project_paths.get(slug, library.parent / slug) / item['source']
            if parser.classify(workspace, source): errors.append(['unsafe-import-source', slug])
            elif not source.is_file(): errors.append(['missing-import-source', slug, item['source']])
            elif hashlib.sha256(source.read_bytes()).hexdigest() != item['sha256']: warnings.append(['source-changed-since-import', slug, item['source']])
            if library / item['destination'] not in pages: errors.append(['missing-import', slug, item['destination']])
    print(json.dumps({'projects': len(projects), 'markdown_files': len(pages), 'imported_files': imported, 'local_links_checked': links, 'errors': errors, 'warnings': warnings, 'limits': ['Static Markdown parser subset; no external URL, browser, database or runtime verification.', 'Semantic translation parity requires human review.']}, ensure_ascii=False, indent=2))
    return bool(errors)

if __name__ == '__main__':
    raise SystemExit(main())
