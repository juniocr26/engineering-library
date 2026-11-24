# VivaBem documentation modernization — 2026-11-04

## Scope and evidence

All nine immediate workspace repositories were inspected and updated: `vivabem`, `carteira-digital`, `cofre-paciente`, `hub-vivabem`, `vivabem-android`, `engineering-library`, `acesso-servidor`, `criptografia-lib`, `script-auditoria-envs`. Root tooling metadata was classified without treating it as another application. Dependencies, signing, secret directories and generated runtime data were excluded. No dotenv/credential/runtime-store contents were read.

Four external portfolio roots were resolved by the existing manifest. Their repositories were not edited; only their catalog references in this private installation were repaired.

## Resulting documentation

Every project has a source-grounded current-implementation chapter and a configuration contract, linked from its existing navigation/README. Portal registration/profile/appointment workflows, Wallet factories/enum/Orders/reconciliation, Cofre collections/deletion/cleanup, Hub authentication/routing/readiness, Android TWA/build/signing, crypto envelopes, deployment safeguards and environment synchronization have explicit boundaries and limitations.

The old boleto/12-case enum table was replaced with the actual 11-case mapping. Current purchase/webhook processing replaces the obsolete shell description. The local Pix simulator is explicitly distinct from provider approval. Debit Elo history is not live homologation or permanent ineligibility. Historical ADRs/reviews were retained and superseded claims labeled; removed production classes are historical paths, not broken live links. No pre-existing documentation file was deleted.

The central catalog keeps its real `docs/<slug>/{en,pt-br}` layout, private/public separation, bios, canonical project IDs and shared assets. Source operational detail and central conceptual summaries are linked rather than blindly mirrored. The private projects retain backend-test references in Operations, respecting existing catalog validation policy; source test chapters use their conventional Testing category.

## Cards, languages and diagrams

The four supplied test-card rows match the official Orders card guide checked on 2026-11-04. They are labeled TEST DATA ONLY — NEVER USE IN PRODUCTION. Official cardholder scenarios are documented separately from Pix. Four new screenshots were not attached: no visual comparison or new screenshot asset is claimed. Existing redacted webhook images are reused.

New/current chapters have English/Brazilian Portuguese counterparts; the missing English dashboard-history counterpart was added and linked. Canonical paths/technical identifiers are preserved. This is authored technical parity, not independent translation certification. Two localized Mermaid blocks describe the same implemented financial recovery flow; no new raster image or application UI asset was created.

## Verification

Executed on 2026-11-04 without application startup:

| Check / Verificação | Result / Resultado |
| --- | --- |
| Portal PHPUnit | 23 cases / casos, 77 assertions / asserções: PASS |
| Wallet PHPUnit | 55 cases / casos, 157 assertions / asserções: PASS |
| Cofre PHPUnit | 21 cases / casos, 52 assertions / asserções: PASS |
| Crypto standalone | 292 security assertions / asserções de segurança: PASS |
| Documentation-tool unittest | 28 tests / testes: PASS |
| Hub Node suite | Not executed / Não executada: host Node unavailable / ausente |

The Portal reused the existing Wallet PHPUnit runner because its local runner is absent. No test code/dependencies were changed. No coverage percentage was measured; Xdebug/PCOV is unavailable. Mocked boundaries establish selected business contracts, not provider or production acceptance.

Existing static catalog validation passes with zero errors, including local links/images, anchors, reachability and language-path parity. 711 central source references were repaired after the workspace split. Source-document validation has zero errors in the nine workspace repositories; 37 pre-existing broken references remain in external portfolio repositories (11 go-image-optimizer, 17 payment-reconciliation-lab, 9 url-shortener). Those are outside writable/task scope and were not hidden by changing validator rules. Restricted-path warnings are metadata-only checks; external URLs were not crawled exhaustively.

```sh
python3 -B tools/check_docs.py --discover-only
python3 -B tools/check_docs.py
python3 -B tools/check_catalog.py
python3 -B -m unittest discover -s tools -p 'test_*.py'
```

Run from Engineering Library. `check_docs.py` exits nonzero while external source errors remain; `check_catalog.py` is the clean central result. Neither mutates source or requires Docker.


Final static counts: 730 catalog Markdown files, 4533 local links, zero errors and 26 restricted-reference warnings; source validator: 798 documents across 13 mappings, zero errors in the nine workspace repositories, 37 external errors and 28 restricted-path warnings. `git diff --check` passed in all nine repositories. Added-content scans found no private-key/provider-token/AWS-key patterns; pattern checks are not a universal secrecy proof. Complete inventory: 60 created, 340 modified, zero removed; no non-documentation changes.

## Remaining limitations

No full provider homologation, real debit acceptance, live queues/databases/notifications, full HTTP integration, Android device/build/signing, Rails/Next runtime or deployment was validated. The known Portal JWT temporal-claim omission remains a production defect outside this documentation-only scope. Historical claims were not promoted into current test results. No application/schema/configuration/test/infrastructure behavior, secret, Git history, staging, commit or publication was changed.

## Complete file inventory

[Created, modified and removed files by repository / Arquivos criados, alterados e removidos por repositório](documentation-modernization-2026-11-04.json).
