# Registro de evidência: maintenance-spec-boundary-evaluation.json

Este é um artefato bruto de pesquisa de um recorte datado. Resultados e saídas rejeitadas do modelo mantêm o status registrado. Ler o registro não aprova publicação nem treinamento.

SHA-256: `2e14da9b56adc60c64a2246ef9b4c86e8b2ebc215f299cd6cf9ecc09499d98d6`. Bytes originais: `3177`.

Caminho original: `agent/research/documentation-intelligence-20261119/maintenance-spec-boundary-evaluation.json`.

<!-- reading-section:reference:2e14da9b56adc60c64a2:consumers -->
## Referenciado por

- [Agente de documentação: contratos de fonte, identidade e propriedade](../chapters/documentation-agent-contracts.md)

<!-- reading-section:reference:2e14da9b56adc60c64a2:artifact -->
## Artefato original

O bloco reproduz o artefato UTF-8 exato; acrescenta-se uma quebra final apenas para exibição se ela não existir no original.

<!-- artifact-body:2e14da9b56adc60c64a2246ef9b4c86e8b2ebc215f299cd6cf9ecc09499d98d6:start -->
````json
{
  "at": "2026-11-20T07:04:42.996018+00:00",
  "status": "MAINTENANCE_CLI_FIFO_HANG_REPRODUCED_AND_FIXED_WITH_BOUNDED_DESCRIPTOR_ADMISSION",
  "before_version": "0.1.1",
  "current_version": "0.1.2",
  "protocol": {
    "path": ".local-backups/documentation-intelligence-20261119/maintenance-spec-boundary-v1/protocol.json",
    "sha256": "1112fe7bb9f15aaee2b04371db63dd25d973d650f5719d7135cd6a34011f5bdd"
  },
  "before_fifo": {
    "completed": false,
    "bounded_probe_timeout_seconds": 2,
    "process_killed_and_reaped_by_subprocess_run": true,
    "stdout": "",
    "stderr": "",
    "failure": "FIFO_SPECIFICATION_BLOCKS_UNBOUNDED_CLI_BEFORE_VALIDATION",
    "started": "2026-11-20T07:03:10.031043+00:00"
  },
  "before_source": {
    "path": ".local-backups/documentation-intelligence-20261119/maintenance-spec-boundary-v1/documentation_maintenance.py",
    "sha256": "35cd85cdd7b9861a585c8ec46c4f5aa7624cd1cc795022f7db60cc09fb5664e6"
  },
  "current_source": {
    "path": "agent/tools/documentation_maintenance.py",
    "sha256": "fd72ef8717a394856c00f77e1d132626b3b2dd183af64b0b3e7139ec528eadfe"
  },
  "after_fifo": {
    "exit_code": 2,
    "result": {
      "status": "REFUSED_PRESERVE_ORIGINALS",
      "error_type": "WorkspaceRefused",
      "reason": "specification must be a bounded regular file",
      "publication_authorized": false,
      "owner_approved": false,
      "partial_candidate_policy": "Any owned partial new root remains preserved; no overwrite or automatic cleanup."
    },
    "stdout": {
      "path": ".local-backups/documentation-intelligence-20261119/maintenance-spec-boundary-v1/after-fix-fifo.stdout",
      "sha256": "304fd248d255c4745731dcd6913669487d4f8f4a208604631aa556cd1078be38"
    }
  },
  "new_boundary_tests": 6,
  "all_python_tests": 244,
  "all_python_seconds": 6.919,
  "all_test_log": {
    "path": ".local-backups/documentation-intelligence-20261119/documentation-tests-v17.stderr",
    "sha256": "72359ae39731d816c2ca020cf1132fe76f732da2b71a7b048d8bc53358e3303e"
  },
  "controls": [
    "Valid regular specification still yields dry-run without writes.",
    "FIFO refuses without waiting for writer; directory/final symlink/ancestor symlink refuse.",
    "Duplicate keys, nonfinite tokens and exponent overflow, unpaired Unicode surrogates, depth/node overflow refuse.",
    "Named file growth and replacement during reading refuse.",
    "Existing exact2MiB file bound remains accepted; one extra byte refuses."
  ],
  "source_lifecycle_decisions_changed": false,
  "original_documents_written": 0,
  "model_calls": 0,
  "new_containers": 0,
  "owner_approved": false,
  "training_gold": false,
  "limits": [
    "Specific local CLI admission boundary, not arbitrary Python sandbox or global deadline.",
    "Path traversal uses descriptor-safe parents and refuses symlink ancestors; some OS convenience aliases such as /tmp must be passed using their real path.",
    "The typed build API remains a trusted caller API; raw lexical JSON guarantees apply only before typed decoding.",
    "Current244-test independent Linux restore still pending; prior238-testV4 capsule remains a valid dated recovery cut."
  ]
}
````
<!-- artifact-body:2e14da9b56adc60c64a2246ef9b4c86e8b2ebc215f299cd6cf9ecc09499d98d6:end -->
