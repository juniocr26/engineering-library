#!/usr/bin/env python3
"""Read-only project catalog checks. Run with python3 -B; no network/runtime calls."""
import collections
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


def main():
    docs_root = Path(__file__).absolute().parents[1]
    workspace = docs_root.parent.parent
    spec = importlib.util.spec_from_file_location(
        "legacy_docs_validator", docs_root.parent / "tools/check_docs.py"
    )
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    errors, warnings = [], []
    pages = {}
    for root, directories, files in os.walk(docs_root, followlinks=False):
        directories[:] = [
            name for name in directories
            if not validator.classify(workspace, Path(root) / name)
        ]
        for name in files:
            path = Path(root) / name
            if path.suffix == ".md":
                if validator.classify(workspace, path):
                    errors.append(["unsafe-document", os.path.relpath(path, docs_root)])
                else:
                    pages[path] = path.read_text(encoding="utf-8")
    for relative in ('README.md', 'README.pt-BR.md', 'backend/README.md', 'frontend/README.md'):
        path = docs_root.parent / relative
        if not validator.classify(workspace, path) and path.is_file():
            pages[path] = path.read_text(encoding='utf-8')
    for language in ('en', 'pt-BR'):
        if (docs_root / language).exists():
            errors.append(['forbidden-root-language-directory', language])
    graph = {path: set() for path in pages}
    checked_links = 0
    for path, body in pages.items():
        for target in validator.links(body):
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            raw = path.parent / unquote(url.path) if url.path else path
            reason = validator.classify(workspace, raw)
            if reason:
                errors.append(["unsafe-link", os.path.relpath(path, docs_root), reason])
                continue
            destination = Path(os.path.normpath(raw))
            checked_links += 1
            if not destination.exists():
                errors.append(["missing-target", os.path.relpath(path, docs_root), target])
            elif destination in pages:
                graph[path].add(destination)
                if url.fragment and unquote(url.fragment) not in validator.anchors(pages[destination]):
                    errors.append(["missing-anchor", os.path.relpath(path, docs_root), target])

    def reachable(start):
        seen, pending = set(), [start]
        while pending:
            path = pending.pop()
            if path not in seen:
                seen.add(path)
                pending.extend(graph.get(path, set()) - seen)
        return seen

    central = reachable(docs_root / "index.md")
    for path in pages.keys() - central:
        if path.is_relative_to(docs_root):
            errors.append(["unreachable-from-library", os.path.relpath(path, docs_root)])
    manifest = json.loads((docs_root / "catalog-provenance.json").read_text())
    actual = {
        path.name for path in workspace.iterdir()
        if not path.is_symlink() and path.is_dir()
        and not (path / ".git").is_symlink() and (path / ".git").exists()
    }
    if actual != set(manifest["projects"]):
        errors.append(["workspace-inventory-mismatch", sorted(actual)])
    collections_present = {
        path.name for path in (docs_root / "projects").iterdir()
        if path.is_dir() and not path.is_symlink()
    }
    if collections_present != actual:
        errors.append(["project-collection-inventory-mismatch"])
    imported = 0
    for name, metadata in manifest["projects"].items():
        base = docs_root / "projects" / name
        for filename in ("README.md", "README.pt-BR.md"):
            if base / filename not in pages:
                errors.append(["missing-readme", name, filename])
        paths = []
        for language in ("en", "pt-BR"):
            language_root = base / "docs" / language
            subset = {p for p in pages if p.is_relative_to(language_root)}
            paths.append({p.relative_to(language_root) for p in subset})
            seen = reachable(language_root / "index.md")
            for path in subset - seen:
                errors.append(["unreachable-from-project", os.path.relpath(path, docs_root)])
            interview = language_root / "faq/index.md"
            if interview not in pages:
                errors.append(["missing-faq-index", name, language])
            elif not re.search(r'\*\*(?:Answer|Resposta|Model answer|Resposta modelo):\*\*', pages[interview]):
                errors.append(["faq-without-answers", name, language])
            if {p for p in subset if p.is_relative_to(language_root / 'faq')} != {interview}:
                errors.append(["duplicate-or-nested-faq", name, language])
            if (language_root / 'technical-interview').exists():
                errors.append(['obsolete-faq-category', name, language])
            env = language_root / 'env/index.md'
            if env not in pages or len(pages[env].splitlines()) < 5:
                errors.append(['missing-env-reference', name, language])
            for category in language_root.iterdir():
                if category.is_dir() and not category.is_symlink():
                    substantive = [p for p in subset if p.parent == category and p.name != "index.md"]
                    if (not substantive and category.name not in {"env", "faq"}) or category / "index.md" not in pages:
                        errors.append(["empty-or-unindexed-category", name, language, category.name])
        if paths[0] != paths[1]:
            errors.append(["language-path-parity", name])
        for relative in paths[0] & paths[1]:
            en = pages[base / "docs/en" / relative]
            pt = pages[base / "docs/pt-BR" / relative]
            if validator.question_ids(en) != validator.question_ids(pt):
                errors.append(["question-id-parity", name, str(relative)])
            if relative == Path('env/index.md'):
                variables = lambda body: set(re.findall(r'\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b', body))
                if variables(en) != variables(pt):
                    errors.append(['env-variable-parity', name])
        for item in metadata["imports"]:
            imported += 1
            source = workspace / name / item["source"]
            if validator.classify(workspace, source):
                errors.append(["unsafe-import-source", name])
            elif hashlib.sha256(source.read_bytes()).hexdigest() != item["sha256"]:
                warnings.append(["source-changed-since-import", name, item["source"]])
            if base / item["destination"] not in pages:
                errors.append(["missing-import", name, item["destination"]])
        for item in metadata["relocated_interviews"]:
            body = pages.get(docs_root / item["destination"], "")
            # Consolidation changes heading depth, while retaining the original questions.
            headings = {line.lstrip('#').strip() for line in body.splitlines() if line.startswith('#')}
            if not all(heading.lstrip('#').strip() in headings for heading in item["preserved_headings"]):
                errors.append(["retained-interview-headings", name, item["destination"]])
    hashes = collections.defaultdict(list)
    for path, body in pages.items():
        if path.is_relative_to(docs_root / "projects"):
            hashes[hashlib.sha256(body.encode()).hexdigest()].append(os.path.relpath(path, docs_root))
    for group in hashes.values():
        if len(group) > 1:
            warnings.append(["identical-project-documents", group])
    print(json.dumps({
        "projects": len(manifest["projects"]), "markdown_files": len(pages),
        "imported_files": imported, "local_links_checked": checked_links,
        "errors": errors, "warnings": warnings,
        "limits": ["Shared legacy Markdown parser subset; no full renderer equivalence.",
                   "No external URLs fetched; no runtime or semantic/translation certification.",
                   "Source links checked by metadata only; import sources restricted to recorded Markdown."]
    }, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
