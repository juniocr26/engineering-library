# Provenance and limits

- Repository: `url-shortener`
- Workspace: `url-shortener/`
- Git revision: `ed43c65c2893172f94c231ee608ecf2753b8f92f`
- Remote (observed, not fetched): `git@github.com:juniocr26/url-shortener.git`
- Review: 2026-10-18, static/selective.

READMEs and maintained documentation in `docs/en/` and `docs/pt-BR/` were read and imported preserving filenames and ADRs. Existing Library interviews were relocated with compatibility entries at old paths. Relative links were adapted to cataloged copies or local workspace sources; explanations are local, but code links require sibling repositories. Restricted links are rendered as non-navigation text. No remote URL was checked.

## Inspected implementation sources

- [app/services/url_service.py](../../../../../../../url-shortener/app/services/url_service.py)
- [app/infrastructure/redis_id_generator.py](../../../../../../../url-shortener/app/infrastructure/redis_id_generator.py)

## Limits

Selective static inspection, not a complete code audit or application/test execution. Earlier results belong to their source revision/date, not this import. Path parity does not prove translation quality. Undocumented motivations and production readiness were not inferred.

[Import mapping and hashes](../../../../../catalog-provenance.json).
