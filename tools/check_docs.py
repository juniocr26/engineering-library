#!/usr/bin/env python3
"""Read-only bilingual documentation validator; no network or application reads."""
from __future__ import annotations

import argparse
from collections import Counter, deque
import json
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import unquote, urlsplit

LANGS = ('en', 'pt-BR')
CATEGORIES = {'architecture', 'adr', 'guides', 'testing', 'benchmarks', 'docker',
              'database', 'api', 'integrations', 'deployment', 'operations',
              'security', 'observability', 'payments', 'interviews', 'faq', 'env'}
DENIED = {'.git', '.hg', '.svn', '.aws', '.codex', '.agents', 'node_modules',
          'vendor', 'target', '.cargo-cache', 'storage', 'data', 'backups',
          'backup', '.local-backups', '.env-audit-backups', '.venv', 'venv', '__pycache__',
          'dist', 'build', '.next', '.cache', 'coverage'}
OBSOLETE = re.compile(r'(?<![\w-])(?:tecnical-interview|technical-interview)(?=/|\b)', re.I)
PRIVATE_KEY = re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----')
INLINE = re.compile(r'!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+["\'][^\n]*?["\'])?\s*\)')
DEFINITION = re.compile(r'^\s{0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)', re.M)
REFERENCE = re.compile(r'!?\[([^\]\n]+)\](?:\[([^\]\n]*)\])')


def blocked_part(part: str) -> bool:
    low = part.lower()
    return (low in DENIED or low.startswith(('.env', '.dockerized-'))
            or low.endswith(('.pem', '.key', '.p12', '.pfx', '.sqlite', '.db'))
            or low in {'credentials', 'id_rsa', 'id_ed25519'})


def classify(root: Path, path: Path) -> str | None:
    """Inspect lexical path and lstat components, never follow a linked target."""
    # Inspect the original path BEFORE normalization: denied/../safe is still denied.
    try:
        raw = path.relative_to(root)
    except ValueError:
        return 'outside-workspace'
    try:
        if stat.S_ISLNK(root.lstat().st_mode):
            return 'symlink-workspace'
    except OSError:
        return 'unreadable-workspace'
    if any(blocked_part(part) for part in raw.parts):
        return 'restricted-target'
    current = root
    for part in raw.parts:
        if part == '..':
            current = current.parent
            if not current.is_relative_to(root):
                return 'outside-workspace'
        elif part != '.':
            current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            # Continue lexical checks even when an earlier component is absent.
            continue
        except OSError:
            return 'unreadable-target'
        if stat.S_ISLNK(mode):
            return 'symlink-target'
    return None


def prose(text: str) -> str:
    """Remove fenced blocks; keep heading text for slug generation."""
    result = []
    fence = None
    for line in text.splitlines():
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            result.append('')
        elif fence is None:
            result.append(line)
        else:
            result.append('')
    return '\n'.join(result)


def anchors(text: str) -> set[str]:
    result = set()
    counts: Counter[str] = Counter()
    lines = prose(text).splitlines()
    for i, line in enumerate(lines):
        match = re.match(r'^\s{0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$', line)
        heading = match.group(1) if match else None
        if not heading and i + 1 < len(lines) and re.match(r'^\s{0,3}(?:=+|-+)\s*$', lines[i+1]) and line.strip():
            heading = line.strip()
        if heading:
            heading = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', heading)
            heading = re.sub(r'<[^>]*>', '', heading)
            slug = re.sub(r'[^\w\- ]', '', heading.lower(), flags=re.UNICODE).replace(' ', '-')
            number = counts[slug]
            counts[slug] += 1
            result.add(slug + (f'-{number}' if number else ''))
    result.update(re.findall(r'<(?:a|[a-z]+)\b[^>]*\b(?:id|name)=["\']([^"\']+)["\']', prose(text), re.I))
    return result


def links(text: str):
    body = prose(text)
    # Inline code snippets can describe example link syntax without being links.
    body = re.sub(r'(`+).*?\1', '', body)
    definitions = {key.casefold(): value.strip('<>') for key, value in DEFINITION.findall(body)}
    for match in INLINE.finditer(body):
        yield match.group(1).strip('<>')
    for label, ref in REFERENCE.findall(body):
        key = (ref or label).casefold()
        yield definitions.get(key, 'unresolved-reference:' + key)
    # Referenced targets are checked even for shortcut reference forms.
    for value in definitions.values():
        yield value


def question_ids(text: str):
    return re.findall(r'^### Q(\d{3})\b', prose(text), re.M)


def legacy_numbers(text: str):
    return re.findall(r'^#{2,3}\s+(\d+)\b', prose(text), re.M)


def validate(workspace: Path, config: dict) -> dict:
    root = Path(os.path.abspath(workspace))
    findings = []
    docs: dict[Path, str] = {}
    graph: dict[Path, set[Path]] = {}
    inventories = {}
    external_links = 0

    def finding(code, path, detail, severity='error'):
        try:
            name = str(path.relative_to(root))
        except ValueError:
            name = '<outside-workspace>'
        findings.append(dict(severity=severity, code=code, path=name, detail=detail))

    if classify(root, root):
        return {'errors': 1, 'warnings': 0, 'findings': [{'severity': 'error', 'code': 'workspace-unsafe', 'detail': 'Workspace root is unreadable or symbolic'}]}
    try:
        actual = sorted(p.name for p in root.iterdir() if not p.is_symlink()
                        and p.is_dir() and not (p / '.git').is_symlink()
                        and (p / '.git').exists())
    except OSError:
        finding('workspace-unreadable', root, 'Cannot enumerate workspace')
        actual = []
    exclusions = config.get('scope_exclusions', {})
    if not isinstance(exclusions, dict) or any(
            not isinstance(k, str) or not isinstance(v, str) or not v.strip()
            for k, v in exclusions.items()):
        finding('exclusion-unjustified', root, 'Scope exclusions require nonempty textual reasons')
        exclusions = {}
    # Exclusions document non-project/generated scope; they never suppress discovered repos.
    expected = config.get('repositories', actual)
    if not isinstance(expected, list) or any(not isinstance(n, str) or '/' in n or n in {'.', '..'} or blocked_part(n) for n in expected):
        finding('invalid-config', root, 'Repository names must be safe immediate directory names')
        expected = []
    for name in sorted(set(expected) - set(actual)):
        finding('repository-missing', root / name, 'Expected repository not discovered')
    for name in sorted(set(actual) - set(expected)):
        finding('repository-unexpected', root / name, 'Repository is absent from configured completion inventory')
    repos = sorted(set(actual) | set(expected))
    exceptions = config.get('exceptions', {})
    reasons = config.get('exception_reasons', {})
    allowed_categories = CATEGORIES | set(config.get('additional_categories', {}))
    for category, reason in config.get('additional_categories', {}).items():
        if not reason:
            finding('category-unjustified', root, f'Additional category {category} requires a reason')
    for repo in repos:
        base = root / repo
        if classify(root, base):
            finding('repository-unsafe', base, 'Unsafe repository path')
            continue
        paths = [base / n for n in ('README.md', 'README.pt-BR.md')]
        for lang in LANGS:
            folder = base / 'docs' / lang
            if classify(root, folder):
                finding('docs-unsafe', folder, 'Documentation root is blocked')
                continue
            if not folder.is_dir():
                finding('docs-missing', folder, 'Language documentation directory missing')
                continue
            def walk_error(error):
                finding('walk-unreadable', Path(error.filename or folder), 'Cannot enumerate documentation')
            for directory, folders, files in os.walk(folder, followlinks=False, onerror=walk_error):
                permitted = []
                for child in folders:
                    child_path = Path(directory) / child
                    if classify(root, child_path):
                        finding('directory-excluded', child_path, 'Restricted or symbolic directory not traversed', 'warning')
                    else:
                        if Path(directory) == folder:
                            if child not in allowed_categories:
                                finding('category-invalid', child_path, 'Unknown category directory')
                            try:
                                if not any(child_path.iterdir()):
                                    finding('category-empty', child_path, 'Empty documentation category')
                            except OSError:
                                finding('category-unreadable', child_path, 'Cannot inspect category')
                        permitted.append(child)
                folders[:] = sorted(permitted)
                for filename in sorted(files):
                    if filename.lower().endswith('.md'):
                        paths.append(Path(directory) / filename)
        inventories[repo] = []
        for path in paths:
            if classify(root, path):
                finding('document-unsafe', path, 'Document not read: restricted/symbolic path')
                continue
            try:
                if not stat.S_ISREG(path.lstat().st_mode):
                    finding('document-nonregular', path, 'Document must be regular')
                    continue
                text = path.read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                finding('document-unreadable', path, 'Cannot read permitted UTF-8 documentation')
                continue
            docs[path] = text
            graph[path] = set()
            inventories[repo].append(str(path.relative_to(base)))
            if PRIVATE_KEY.search(text):
                finding('private-key-marker', path, 'Private-key marker detected; content is not emitted')
            if OBSOLETE.search(text):
                finding('obsolete-library-name', path, 'Obsolete local library naming detected')
            if path.is_relative_to(base / 'docs'):
                rel = path.relative_to(base / 'docs')
                if rel.name != 'index.md' and (len(rel.parts) < 3 or rel.parts[1] not in allowed_categories):
                    finding('category-invalid', path, 'Maintained document must be under a justified category')
                peer = base / 'docs' / ('pt-BR' if rel.parts[0] == 'en' else 'en') / Path(*rel.parts[1:])
                if classify(root, peer) or not peer.exists():
                    exception = str(path.relative_to(base))
                    if exception in exceptions.get(repo, []) and reasons.get(repo + '/' + exception):
                        finding('counterpart-exception', path, reasons[repo + '/' + exception], 'info')
                    else:
                        finding('counterpart-missing', path, 'Missing matching language relative path')
        for required in ('README.md', 'README.pt-BR.md', 'docs/en/index.md', 'docs/pt-BR/index.md',
                         'docs/en/operations/completion-checklist.md', 'docs/pt-BR/operations/completion-checklist.md'):
            if base / required not in docs:
                finding('expected-document-missing', base / required, 'Required introduction/index/checklist missing or unreadable')
        for required in config.get('required_documents', {}).get(repo, []):
            target = base / required
            if classify(root, target) or target not in docs:
                finding('expected-document-missing', target, 'Configured maintained document missing or unsafe')
    anchor_cache = {path: anchors(text) for path, text in docs.items()}
    for path, text in docs.items():
        for url in links(text):
            try:
                parts = urlsplit(url)
            except ValueError:
                finding('link-malformed', path, 'Cannot parse Markdown target')
                continue
            if parts.scheme == 'unresolved-reference':
                finding('reference-missing', path, 'Undefined reference-style link')
                continue
            if parts.scheme or parts.netloc:
                external_links += 1
                if parts.scheme.lower() == 'file':
                    finding('link-blocked', path, 'Machine-specific file URI not inspected', 'warning')
                # No network access or external-link success claims.
                continue
            raw = unquote(parts.path)
            if raw.startswith('/'):
                finding('link-absolute', path, 'Local documentation link must be workspace-relative')
                continue
            raw_target = path.parent / raw if raw else path
            reason = classify(root, raw_target)
            if reason:
                finding('link-blocked', path, reason + ': ' + raw + '; target was not read', 'warning')
                continue
            target = Path(os.path.normpath(raw_target))
            try:
                mode = target.lstat().st_mode
            except FileNotFoundError:
                finding('link-missing', path, f'Missing local target: {raw}')
                continue
            except OSError:
                finding('link-unreadable', path, 'Cannot inspect local target')
                continue
            if target in docs:
                graph[path].add(target)
                if parts.fragment and unquote(parts.fragment) not in anchor_cache[target]:
                    finding('anchor-missing', path, f'Missing anchor: {raw}#{parts.fragment}')
            elif parts.fragment:
                finding('anchor-unchecked', path, 'Anchor on a non-maintained document was not read', 'info')
            if not stat.S_ISREG(mode) and not stat.S_ISDIR(mode):
                finding('link-nonregular', path, 'Target is not regular file/directory')
        if 'interviews' in path.parts or 'faq' in path.parts:
            ids = question_ids(text)
            for level in ('##', '###'):
                retained = re.findall(r'^' + level + r'\s+(\d+)\b', prose(text), re.M)
                if retained and retained != [str(i) for i in range(1, len(retained) + 1)]:
                    finding('legacy-numbering-invalid', path, 'Retained numbered sections at one heading level must be sequential from 1')
            if ids and ids != [f'{i:03d}' for i in range(1, len(ids) + 1)]:
                finding('question-numbering', path, 'New Q IDs must be sequential and unique from Q001')
            for block in re.split(r'^### Q\d{3}\b[^\n]*\n', text, flags=re.M)[1:]:
                if not re.search(r'\*\*(?:Answer|Resposta):\*\*', block):
                    finding('question-answer-missing', path, 'Q block has no explicit answer')
                if not re.search(r'(?:Follow-up|Aprofundamento):', block):
                    finding('question-followup-missing', path, 'Q block has no follow-up')
            if '/en/' in str(path):
                peer = Path(str(path).replace('/docs/en/', '/docs/pt-BR/'))
                if peer in docs:
                    if ids != question_ids(docs[peer]):
                        finding('question-language-mismatch', path, 'Bilingual new question IDs differ')
                    if legacy_numbers(text) != legacy_numbers(docs[peer]):
                        finding('legacy-numbering-mismatch', path, 'Retained numbered interview sections differ by language')
    for repo in repos:
        base = root / repo
        for lang in LANGS:
            start = base / 'docs' / lang / 'index.md'
            seen = {start}
            queue = deque([start])
            while queue:
                current = queue.popleft()
                for target in graph.get(current, ()):
                    # Each repo/language must be understandable without another index.
                    if target.is_relative_to(base / 'docs' / lang) and target not in seen:
                        seen.add(target)
                        queue.append(target)
            for path in docs:
                if path.is_relative_to(base / 'docs' / lang) and path not in seen:
                    finding('index-unreachable', path, 'Document not reachable from its language index')
            readme = base / ('README.md' if lang == 'en' else 'README.pt-BR.md')
            if readme in docs and start not in graph.get(readme, ()):
                finding('readme-index-missing', readme, 'README must link its language catalog')
    errors = sum(f['severity'] == 'error' for f in findings)
    warnings = sum(f['severity'] == 'warning' for f in findings)
    return {'schema_version': 1, 'scope': 'read-only static documentation',
            'repositories': repos, 'documents': len(docs), 'inventory': inventories,
            'scope_exclusions': exclusions,
            'external_links': {'status': 'not checked', 'occurrences': external_links},
            'summary': {'repositories': len(repos), 'documents': len(docs),
                        'errors': errors, 'warnings': warnings,
                        'finding_codes': dict(Counter(f['code'] for f in findings))},
            'errors': errors, 'warnings': warnings, 'findings': findings,
            'limits': ['No network or runtime checks', 'Markdown syntax subset',
                       'Bilingual semantic equivalence and answer accuracy require review',
                       'lstat checks are not a race-free adversarial filesystem sandbox']}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path(__file__).absolute().parents[2])
    parser.add_argument('--config', type=Path, help='Safe tools/*.json metadata within workspace')
    args = parser.parse_args(argv)
    root = Path(os.path.abspath(args.workspace))
    config_path = args.config or Path(__file__).absolute().with_name('docs_manifest.json')
    config_path = Path(os.path.abspath(config_path))
    # Configurable metadata is deliberately narrower than arbitrary JSON/app data.
    if classify(root, config_path) or config_path.parent.name != 'tools' or config_path.suffix != '.json' or (config_path.exists() and not stat.S_ISREG(config_path.lstat().st_mode)):
        report = {'errors': 1, 'warnings': 0, 'findings': [{'severity': 'error', 'code': 'config-unsafe', 'detail': 'Only safe workspace tools/*.json metadata is permitted'}]}
    else:
        try:
            config = json.loads(config_path.read_text(encoding='utf-8'))
            if not isinstance(config, dict):
                raise ValueError('object required')
            report = validate(root, config)
        except (OSError, UnicodeError, ValueError, TypeError, AttributeError):
            report = {'errors': 1, 'warnings': 0, 'findings': [{'severity': 'error', 'code': 'config-unreadable', 'detail': 'Invalid/unreadable safe metadata configuration'}]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
