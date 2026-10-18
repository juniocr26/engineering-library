# Documentation validation

Run from the repository root:

```sh
python3 -B docs/validation/check_catalog.py
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
```

The catalog validator follows Library → Project → Language → Index → Category → Document. It checks local links and Markdown anchors, reachability from central and project indexes, bilingual path and question-ID parity, FAQ indexes, ENV references and recorded import headings. Root language collections are forbidden. Imported source hashes identify changes since the historical snapshot; they are not current-file hashes. Both public root READMEs and component READMEs participate in link validation.

`tools/check_docs.py` remains the legacy sibling-repository checker and Markdown/security helper used by this validator. Its old workspace manifest includes historical root-language paths and is not the completion command for the project catalog. The [isolated helper tests](../../../../../../tools/test_check_docs.py) exercise restricted targets, symlinks, read-only behavior, anchors and malformed inputs.

The tools never read real environment files, keys or database files. Application/source links receive metadata checks only. No external URLs are fetched. Markdown parsing covers a subset; semantic correctness, translation quality and third-party availability require review. Runtime verification is separate: see [development](application-development.md) and [database migration](../operations/database-migration.md).
