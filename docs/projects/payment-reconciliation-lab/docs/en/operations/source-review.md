# Provenance and limits

- Repository: `payment-reconciliation-lab`
- Workspace: `payment-reconciliation-lab/`
- Git revision: `c27a55959101e6c29d0fb201c6d6b0d322fd40d1`
- Remote (observed, not fetched): `git@github.com:juniocr26/aurora-bakery.git`
- Review: 2026-10-18, static/selective.

READMEs and maintained documentation in `docs/en/` and `docs/pt-BR/` were read and imported preserving filenames and ADRs. Existing Library interviews were relocated with compatibility entries at old paths. Relative links were adapted to cataloged copies or local workspace sources; explanations are local, but code links require sibling repositories. Restricted links are rendered as non-navigation text. No remote URL was checked.

## Inspected implementation sources

- [backend/src/main/java/com/aurorabakery/catalog/api/ProductController.java](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/catalog/api/ProductController.java)
- [backend/src/main/java/com/aurorabakery/catalog/application/CatalogService.java](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/catalog/application/CatalogService.java)
- [backend/src/main/java/com/aurorabakery/configuration/SecurityConfiguration.java](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/configuration/SecurityConfiguration.java)

## Limits

Selective static inspection, not a complete code audit or application/test execution. Earlier results belong to their source revision/date, not this import. Path parity does not prove translation quality. Undocumented motivations and production readiness were not inferred. The observed remote is still named aurora-bakery; no new URL was inferred or configured. Reconciliation and Stripe integration are not implemented.

[Import mapping and hashes](../../../../../catalog-provenance.json).
