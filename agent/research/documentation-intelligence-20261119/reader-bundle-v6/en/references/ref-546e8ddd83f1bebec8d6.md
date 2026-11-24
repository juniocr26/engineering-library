# Evidence record: helper-cache-integrity-evaluation.json

This is a dated raw research artifact. Findings and rejected model outputs retain their recorded status. Reading the record does not approve publication or training.

SHA-256: `546e8ddd83f1bebec8d68b31b13891a6ec8482372b927cde95c7c186f2a8706f`. Original bytes: `3429`.

Original path: `agent/research/documentation-intelligence-20261119/helper-cache-integrity-evaluation.json`.

<!-- reading-section:reference:546e8ddd83f1bebec8d6:consumers -->
## Referenced by

- [Documentation agent: source, identity and ownership contracts](../chapters/documentation-agent-contracts.md)

<!-- reading-section:reference:546e8ddd83f1bebec8d6:artifact -->
## Original artifact

The fenced contents reproduce the exact UTF-8 artifact; a display-only terminal newline is added if the original lacks one.

<!-- artifact-body:546e8ddd83f1bebec8d68b31b13891a6ec8482372b927cde95c7c186f2a8706f:start -->
````json
{
  "at": "2026-11-20T02:13:28.489488+00:00",
  "experiment": "HELPER_CACHE_INTEGRITY_REGRESSION_V1",
  "protocol": {
    "frozen_at": "2026-11-20T02:13:28.344811+00:00",
    "purpose": "Compare result-only tampering under old and fixed cache validation, then test source validation even when both checksum artifacts are rewritten.",
    "old_version": "0.1.1",
    "old_sha256": "b3886500ecfbd87d422d94896fb558383a72d7bb32bd7652e7ac59961c6de049",
    "current_version": "0.1.2",
    "current_sha256": "e6fd18dea79eb8320c566c816b7aa7bf34d60cbe06b825a67e2dc9ef89aa326e",
    "source_sha256": "b6631639de17fb869c43278f858c465cc5b71c8ec51c8c25d803905361f8a544",
    "cases": [
      "legacy-result-only-tamper",
      "current-result-only-tamper",
      "current-result-and-receipt-tamper"
    ],
    "source_executed": false,
    "model_calls": 0
  },
  "outcomes": [
    {
      "case": "legacy-result-only-tamper",
      "first_status": "FOUND",
      "after_tamper": {
        "version": "0.1.1",
        "status": "DUPLICATE",
        "source_executed": false,
        "runtime_bindings_verified": false,
        "owner_approved": false,
        "original_status": "FOUND",
        "result_sha256": "7ed7bbfab4b242e3c964c12d7b0d2498957c6052988541ac4bea000407c04206",
        "result_reference": "r1.result.json",
        "reason": "Duplicate suppressed; do not inject the same quote again."
      },
      "tampered_result_preserved": true,
      "false_quote_delivered_to_model": false,
      "interpretation": "Earlier duplicate suppresses extraction but does not detect changed recorded quote."
    },
    {
      "case": "current-result-only-tamper",
      "first_status": "FOUND",
      "after_tamper": {
        "version": "0.1.2",
        "status": "REFUSED",
        "source_executed": false,
        "runtime_bindings_verified": false,
        "owner_approved": false,
        "reason": "completed result receipt checksum or identity differs"
      },
      "tampered_result_preserved": true,
      "false_quote_delivered_to_model": false,
      "interpretation": "Changed record refused without repeat extraction or quote delivery."
    },
    {
      "case": "current-result-and-receipt-tamper",
      "first_status": "FOUND",
      "after_tamper": {
        "version": "0.1.2",
        "status": "REFUSED",
        "source_executed": false,
        "runtime_bindings_verified": false,
        "owner_approved": false,
        "reason": "Python evidence differs from exact physical source"
      },
      "tampered_result_preserved": true,
      "false_quote_delivered_to_model": false,
      "interpretation": "Changed record refused without repeat extraction or quote delivery."
    }
  ],
  "regression_test_methods": 37,
  "source_bytes_and_mtime_unchanged": true,
  "model_calls": 0,
  "source_program_executed": false,
  "originals_and_tampered_candidates_preserved": true,
  "owner_approved": false,
  "training_gold": false,
  "production_ruby_routing_changed": false,
  "limits": [
    "Checksum receipts detect integrity drift but are not signatures or an authenticated journal.",
    "Matching rewritten receipts are additionally checked against physical source, not trusted as semantic authority.",
    "This uses owned synthetic cache artifacts, not an attack on an external repository or service.",
    "Legacy journals are retained for explicit review and never automatically migrated/retried."
  ]
}
````
<!-- artifact-body:546e8ddd83f1bebec8d68b31b13891a6ec8482372b927cde95c7c186f2a8706f:end -->
