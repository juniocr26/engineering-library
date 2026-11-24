# Registro de evidência: candidate-output-closure-evaluation-v1.json

Este é um artefato bruto de pesquisa de um recorte datado. Resultados e saídas rejeitadas do modelo mantêm o status registrado. Ler o registro não aprova publicação nem treinamento.

SHA-256: `f97e4e4179eb79aeb9a994b13d7fe3200b5b03d52809ff94d5ef8b14421940cf`. Bytes originais: `28232`.

Caminho original: `agent/research/documentation-intelligence-20261119/candidate-output-closure-evaluation-v1.json`.

<!-- reading-section:reference:f97e4e4179eb79aeb9a9:consumers -->
## Referenciado por

- [Agente de documentação: contratos de fonte, identidade e propriedade](../chapters/documentation-agent-contracts.md)

<!-- reading-section:reference:f97e4e4179eb79aeb9a9:artifact -->
## Artefato original

O bloco reproduz o artefato UTF-8 exato; acrescenta-se uma quebra final apenas para exibição se ela não existir no original.

<!-- artifact-body:f97e4e4179eb79aeb9a994b13d7fe3200b5b03d52809ff94d5ef8b14421940cf:start -->
````json
{
  "at": "2026-11-20T08:38:13.459114+00:00",
  "status": "CANDIDATE_OUTPUT_IDENTITY_CONTENT_HISTORY_AND_RESULT_READBACK_VERIFIED",
  "maintenance_version": "0.1.4",
  "before_false_successes": 5,
  "fresh_equivalent_mutation_cases_now_refused": 5,
  "valid_candidate_control_prepared": true,
  "results": [
    {
      "case": "candidate-root-relocated-and-replaced",
      "status": "REFUSED",
      "reason": "candidate root or parent identity changed",
      "report": null,
      "triggered": [
        "history-index.json"
      ],
      "normalized_specification_identical_to_before": true,
      "original_bytes_and_mtimes_unchanged": true,
      "preserved_output_files": [
        {
          "path": "specification.json",
          "sha256": "86c9563c59db6f7c2d19927e4a7fb75b495d02c09966a3b2307d1e9ed61c1f4e",
          "bytes": 2892
        },
        {
          "path": "candidate/human.txt",
          "sha256": "ba83fa0bd79bcbfc27d5d6c5b22d6551823adc1a8e13e10fa7132ce96ac4503a",
          "bytes": 32
        },
        {
          "path": "preserved-relocated-candidate/history-index.json",
          "sha256": "3a7a9c09b575ea9a339ce4ca1cbe635a6771e49d5069b46fd9cb0dc6b1d2a2ad",
          "bytes": 1064
        },
        {
          "path": "preserved-relocated-candidate/preconditions.json",
          "sha256": "7324be7d5781e2afcef5fbe71dce27101d427ab31f574ee101d022640a4572fa",
          "bytes": 5611
        },
        {
          "path": "current/api.py",
          "sha256": "d3fe37235936f63ebabd6ba2bb8d3cf67404555d856dc63b0611fe9b6231ec13",
          "bytes": 26
        },
        {
          "path": "before/api.py",
          "sha256": "5d080563b57287276f589c2b2714ef499269efe7405a288b3c1474f5a92bf271",
          "bytes": 26
        },
        {
          "path": "documents/pt-br/guide.md",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "documents/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "documents/en/guide.md",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "documents/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "preserved-relocated-candidate/history/3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73.bin",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "preserved-relocated-candidate/history/365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee.bin",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "preserved-relocated-candidate/history/4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1.bin",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "preserved-relocated-candidate/active/pt-br/guide.md",
          "sha256": "700cb0661770a358dd74925181e848304a9ddb98d052f029f7d5fc0491847d70",
          "bytes": 189
        },
        {
          "path": "preserved-relocated-candidate/active/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "preserved-relocated-candidate/active/en/guide.md",
          "sha256": "f082ff51b807df5fc6a19b339cda252154974902981c6128d6c00ac9cdced5f3",
          "bytes": 189
        },
        {
          "path": "preserved-relocated-candidate/active/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        }
      ]
    },
    {
      "case": "active-file-corrupted",
      "status": "REFUSED",
      "reason": "workspace checksum changed: en/guide.md",
      "report": null,
      "triggered": [
        "history-index.json"
      ],
      "normalized_specification_identical_to_before": true,
      "original_bytes_and_mtimes_unchanged": true,
      "preserved_output_files": [
        {
          "path": "specification.json",
          "sha256": "bd7b238e8c8805508630eb0f74a27f68f600977b2468056287d8ede081f3712f",
          "bytes": 2828
        },
        {
          "path": "candidate/history-index.json",
          "sha256": "d244d1173af80d5afbb6b90241a6ab4030fd12825a88b292522f6b54b2008a73",
          "bytes": 1064
        },
        {
          "path": "candidate/preconditions.json",
          "sha256": "4877094d9f186c84b99c134052900f9b5805969f20ed62343b54b0b636178eb0",
          "bytes": 5547
        },
        {
          "path": "current/api.py",
          "sha256": "d3fe37235936f63ebabd6ba2bb8d3cf67404555d856dc63b0611fe9b6231ec13",
          "bytes": 26
        },
        {
          "path": "before/api.py",
          "sha256": "5d080563b57287276f589c2b2714ef499269efe7405a288b3c1474f5a92bf271",
          "bytes": 26
        },
        {
          "path": "documents/pt-br/guide.md",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "documents/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "documents/en/guide.md",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "documents/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/history/3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73.bin",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "candidate/history/365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee.bin",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/history/4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1.bin",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "candidate/active/pt-br/guide.md",
          "sha256": "700cb0661770a358dd74925181e848304a9ddb98d052f029f7d5fc0491847d70",
          "bytes": 189
        },
        {
          "path": "candidate/active/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/active/en/guide.md",
          "sha256": "4ca265835d7f548231eb58cc59751b3fbfea93473fb5a97f859bd687aaab798d",
          "bytes": 18
        },
        {
          "path": "candidate/active/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        }
      ]
    },
    {
      "case": "history-blob-corrupted",
      "status": "REFUSED",
      "reason": "workspace checksum changed: 3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73.bin",
      "report": null,
      "triggered": [
        "history-index.json"
      ],
      "normalized_specification_identical_to_before": true,
      "original_bytes_and_mtimes_unchanged": true,
      "preserved_output_files": [
        {
          "path": "specification.json",
          "sha256": "bc6e1372c747d360795e892de0c5498a7b37ce31ecd56210f00d5b7aa48c4e26",
          "bytes": 2832
        },
        {
          "path": "candidate/history-index.json",
          "sha256": "9cd39f5ee90cf43b419edce43554dee606cca14d1e2f77ab4835addc66c7a66f",
          "bytes": 1064
        },
        {
          "path": "candidate/preconditions.json",
          "sha256": "db5d0d4087c3723dda842e9f8079542dd3f36f032f8a15e075a71bd12928b95e",
          "bytes": 5551
        },
        {
          "path": "current/api.py",
          "sha256": "d3fe37235936f63ebabd6ba2bb8d3cf67404555d856dc63b0611fe9b6231ec13",
          "bytes": 26
        },
        {
          "path": "before/api.py",
          "sha256": "5d080563b57287276f589c2b2714ef499269efe7405a288b3c1474f5a92bf271",
          "bytes": 26
        },
        {
          "path": "documents/pt-br/guide.md",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "documents/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "documents/en/guide.md",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "documents/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/history/3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73.bin",
          "sha256": "e783b12c373972f85ea9144319b597e4bbfececdca495edb52e1a753be8516a4",
          "bytes": 25
        },
        {
          "path": "candidate/history/365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee.bin",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/history/4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1.bin",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "candidate/active/pt-br/guide.md",
          "sha256": "700cb0661770a358dd74925181e848304a9ddb98d052f029f7d5fc0491847d70",
          "bytes": 189
        },
        {
          "path": "candidate/active/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/active/en/guide.md",
          "sha256": "f082ff51b807df5fc6a19b339cda252154974902981c6128d6c00ac9cdced5f3",
          "bytes": 189
        },
        {
          "path": "candidate/active/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        }
      ]
    },
    {
      "case": "unexpected-root-file",
      "status": "REFUSED",
      "reason": "candidate output inventory changed",
      "report": null,
      "triggered": [
        "history-index.json"
      ],
      "normalized_specification_identical_to_before": true,
      "original_bytes_and_mtimes_unchanged": true,
      "preserved_output_files": [
        {
          "path": "specification.json",
          "sha256": "a2a0b5d7136e1dba39f8ae55003dd431417745cff391d262081b09fc3c2eff0b",
          "bytes": 2824
        },
        {
          "path": "candidate/history-index.json",
          "sha256": "07fbd69553e260c68310c3af1213b58777982f12268f86f2a5a66d80d94b0763",
          "bytes": 1064
        },
        {
          "path": "candidate/human.txt",
          "sha256": "752367ef45937123f2c3c208d1401acb8bddd467b1b867b48bc3dfc06ed00fba",
          "bytes": 25
        },
        {
          "path": "candidate/preconditions.json",
          "sha256": "72b5466a5d01a5cad34c163a934bd9c6f15d332f3c05e49165dd1bd6247c2c44",
          "bytes": 5543
        },
        {
          "path": "current/api.py",
          "sha256": "d3fe37235936f63ebabd6ba2bb8d3cf67404555d856dc63b0611fe9b6231ec13",
          "bytes": 26
        },
        {
          "path": "before/api.py",
          "sha256": "5d080563b57287276f589c2b2714ef499269efe7405a288b3c1474f5a92bf271",
          "bytes": 26
        },
        {
          "path": "documents/pt-br/guide.md",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "documents/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "documents/en/guide.md",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "documents/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/history/3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73.bin",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "candidate/history/365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee.bin",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/history/4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1.bin",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "candidate/active/pt-br/guide.md",
          "sha256": "700cb0661770a358dd74925181e848304a9ddb98d052f029f7d5fc0491847d70",
          "bytes": 189
        },
        {
          "path": "candidate/active/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/active/en/guide.md",
          "sha256": "f082ff51b807df5fc6a19b339cda252154974902981c6128d6c00ac9cdced5f3",
          "bytes": 189
        },
        {
          "path": "candidate/active/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        }
      ]
    },
    {
      "case": "durable-result-corrupted",
      "status": "REFUSED",
      "reason": "candidate metadata readback differs: result.json",
      "report": null,
      "triggered": [
        "result.json"
      ],
      "normalized_specification_identical_to_before": true,
      "original_bytes_and_mtimes_unchanged": true,
      "preserved_output_files": [
        {
          "path": "specification.json",
          "sha256": "6832bbd9d0d8dacd027b834c544f242029b95c5e1553383120f52aa6afe0729c",
          "bytes": 2840
        },
        {
          "path": "candidate/result.json",
          "sha256": "14469a6749940905faa663cc02fe93e83ccc263be89d477b80d3bced0bc16a77",
          "bytes": 18
        },
        {
          "path": "candidate/history-index.json",
          "sha256": "12de467c3dfe937eee9e734678c88ac972786de0ba4be1681b0ae4d3318c2bf2",
          "bytes": 1064
        },
        {
          "path": "candidate/preconditions.json",
          "sha256": "e162d525a78c357a3b213d85d5042d6da58f7cf6f798c4938add974f67689e55",
          "bytes": 5559
        },
        {
          "path": "current/api.py",
          "sha256": "d3fe37235936f63ebabd6ba2bb8d3cf67404555d856dc63b0611fe9b6231ec13",
          "bytes": 26
        },
        {
          "path": "before/api.py",
          "sha256": "5d080563b57287276f589c2b2714ef499269efe7405a288b3c1474f5a92bf271",
          "bytes": 26
        },
        {
          "path": "documents/pt-br/guide.md",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "documents/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "documents/en/guide.md",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "documents/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/history/3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73.bin",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "candidate/history/365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee.bin",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/history/4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1.bin",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "candidate/active/pt-br/guide.md",
          "sha256": "700cb0661770a358dd74925181e848304a9ddb98d052f029f7d5fc0491847d70",
          "bytes": 189
        },
        {
          "path": "candidate/active/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/active/en/guide.md",
          "sha256": "f082ff51b807df5fc6a19b339cda252154974902981c6128d6c00ac9cdced5f3",
          "bytes": 189
        },
        {
          "path": "candidate/active/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        }
      ]
    },
    {
      "case": "valid-candidate-control",
      "status": "VALID_CANDIDATE_PREPARED",
      "reason": null,
      "report": {
        "status": "ISOLATED_CANDIDATE_PREPARED_PENDING_REVIEW",
        "version": "0.1.4",
        "repository": "owned-maintenance-lab",
        "scope_kind": "owned-synthetic-project",
        "operations": [
          {
            "claim_id": "sample.value",
            "action": "MODIFY",
            "source_file": "api.py",
            "source_sha256": "d3fe37235936f63ebabd6ba2bb8d3cf67404555d856dc63b0611fe9b6231ec13",
            "previous_file": "api.py",
            "previous_source_sha256": "5d080563b57287276f589c2b2714ef499269efe7405a288b3c1474f5a92bf271"
          }
        ],
        "changed_documents": [
          "pt-br/guide.md",
          "en/guide.md"
        ],
        "candidate_created": true,
        "inconclusive_claims": [],
        "original_files_written": 0,
        "model_calls": 0,
        "owner_approved": false,
        "publication_authorized": false,
        "training_gold": false,
        "previous_revision": {
          "kind": "sha256-source-inventory",
          "digest": "7de0f8324f465a12dce2cf4cf77597cf2b677dab305835572386dad6e3c75c98"
        },
        "current_revision": {
          "kind": "sha256-source-inventory",
          "digest": "ef5208ac90f591d7244a9d599855bfd88ffb9b874c6a10cb84da2397f15d13ab"
        },
        "documentation_inventory_sha256": "796046f549f3f4e7be5bebf41301a4b2de01217ef438c49e3291991789b14109",
        "document_evidence": {
          "en/guide.md": {
            "version": "0.1.2",
            "before_sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
            "candidate_sha256": "f082ff51b807df5fc6a19b339cda252154974902981c6128d6c00ac9cdced5f3",
            "changed": true,
            "human_outside_managed_ranges_sha256": "a928c371fed40279cccae3197b648157d1af53042cd035761f6605b5bbc94483",
            "history_required": true,
            "operations": [
              {
                "claim_id": "sample.value",
                "action": "MODIFY",
                "changed": true,
                "technical_recommendation": "MODIFY"
              }
            ],
            "original_files_written": 0,
            "owner_approved": false,
            "training_gold": false,
            "limitations": [
              "In-memory candidate construction only; no active documentation is changed.",
              "Caller must bind current source/document bytes to an approved frozen registry.",
              "Link/navigation and live-source rechecks are separate preconditions before filesystem publication."
            ]
          },
          "pt-br/guide.md": {
            "version": "0.1.2",
            "before_sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
            "candidate_sha256": "700cb0661770a358dd74925181e848304a9ddb98d052f029f7d5fc0491847d70",
            "changed": true,
            "human_outside_managed_ranges_sha256": "a928c371fed40279cccae3197b648157d1af53042cd035761f6605b5bbc94483",
            "history_required": true,
            "operations": [
              {
                "claim_id": "sample.value",
                "action": "MODIFY",
                "changed": true,
                "technical_recommendation": "MODIFY"
              }
            ],
            "original_files_written": 0,
            "owner_approved": false,
            "training_gold": false,
            "limitations": [
              "In-memory candidate construction only; no active documentation is changed.",
              "Caller must bind current source/document bytes to an approved frozen registry.",
              "Link/navigation and live-source rechecks are separate preconditions before filesystem publication."
            ]
          }
        },
        "existing_broken_local_links": [],
        "new_broken_local_links": [],
        "fragment_links_not_semantically_verified": [],
        "limitations": [
          "Closed owned synthetic roots only; no general Git/module/build or semantic completeness claim.",
          "Original Markdown is preserved; publication and training approval remain separate.",
          "Current registered files are rehashed before and after construction; not an atomic filesystem snapshot.",
          "Heading/fragment semantics are not certified by this Markdown-path check."
        ],
        "candidate_output_readback_verified": true,
        "candidate_root_identity_rechecked": true,
        "candidate_files_sha256": {
          "pt-br/guide.md": "700cb0661770a358dd74925181e848304a9ddb98d052f029f7d5fc0491847d70",
          "pt-br/notes.md": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "en/guide.md": "f082ff51b807df5fc6a19b339cda252154974902981c6128d6c00ac9cdced5f3",
          "en/notes.md": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee"
        },
        "observed_seconds": 0.005520124999748077
      },
      "triggered": [],
      "normalized_specification_identical_to_before": false,
      "original_bytes_and_mtimes_unchanged": true,
      "preserved_output_files": [
        {
          "path": "specification.json",
          "sha256": "fa1b7fe4563987b43236a6e8c312680c3b95f2d8d10829b9cc32006d9233b3e4",
          "bytes": 2836
        },
        {
          "path": "candidate/result.json",
          "sha256": "c2e72934a327b46018d5945f01245555deab62712a2c5916b61f5b74ece2cb1c",
          "bytes": 3581
        },
        {
          "path": "candidate/history-index.json",
          "sha256": "107f1de72a09fc9db4ad539ca05fd34676f0ded200dfba126608517ebb2f8b57",
          "bytes": 1064
        },
        {
          "path": "candidate/preconditions.json",
          "sha256": "0967fc37f89bed74056a2e7b083abc1200ec5db87814eefa1dd31dc7ecd033fb",
          "bytes": 5555
        },
        {
          "path": "current/api.py",
          "sha256": "d3fe37235936f63ebabd6ba2bb8d3cf67404555d856dc63b0611fe9b6231ec13",
          "bytes": 26
        },
        {
          "path": "before/api.py",
          "sha256": "5d080563b57287276f589c2b2714ef499269efe7405a288b3c1474f5a92bf271",
          "bytes": 26
        },
        {
          "path": "documents/pt-br/guide.md",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "documents/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "documents/en/guide.md",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "documents/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/history/3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73.bin",
          "sha256": "3b74bb1d36476429405e7bb247b7a6421f910c0a41f0b443483dcc371fa3aa73",
          "bytes": 189
        },
        {
          "path": "candidate/history/365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee.bin",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/history/4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1.bin",
          "sha256": "4e9cb65a7773230e28cbf31651e667d9f8e1241fc676fa20ab6118a5bc6b0ae1",
          "bytes": 189
        },
        {
          "path": "candidate/active/pt-br/guide.md",
          "sha256": "700cb0661770a358dd74925181e848304a9ddb98d052f029f7d5fc0491847d70",
          "bytes": 189
        },
        {
          "path": "candidate/active/pt-br/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        },
        {
          "path": "candidate/active/en/guide.md",
          "sha256": "f082ff51b807df5fc6a19b339cda252154974902981c6128d6c00ac9cdced5f3",
          "bytes": 189
        },
        {
          "path": "candidate/active/en/notes.md",
          "sha256": "365d0b84ae63c2afc293dedd2b00bdf0dc8d6ef70c9297d90f9e5682ab0d72ee",
          "bytes": 8
        }
      ]
    }
  ],
  "protocol_ref": {
    "path": ".local-backups/documentation-intelligence-20261119/candidate-output-closure-v1/protocol.json",
    "sha256": "f4e6e421fe134194d377d7bc815911a51da1c78f5c26c3c5ff828ed0e4e416e1"
  },
  "before_results_ref": {
    "path": ".local-backups/documentation-intelligence-20261119/candidate-output-closure-v1/before-results.json",
    "sha256": "f0ad9d8a4073dbec3ce07776a09b72182d4f9f1289ee6e245022d5803cc24a2d"
  },
  "working_suite_tests": 278,
  "working_suite_seconds": 8.09,
  "new_test_methods": 7,
  "additional_directory_symlink_and_preserved_mtime_controls": true,
  "final_maintenance_targeted_suite": "PASS after moving the controlled renamed active directory outside candidate to exercise no-follow instead of the top-level inventory check.",
  "all_original_source_and_document_bytes_and_mtimes_unchanged": true,
  "partial_outputs_and_replacement_human_files_preserved": true,
  "candidate_writebacks_to_repair_corruption": 0,
  "model_calls": 0,
  "source_programs_executed": false,
  "training_runs": 0,
  "owner_approved": false,
  "publication_authorized": false,
  "training_gold": false,
  "limits": [
    "Freshcase roots differ from beforecases, but allnon-root specificationfields, source/doc hashes and frozenmutation rules are exactlyequal; no misleading samebyteinput claim.",
    "Readback and identity checks are sequential, not an atomic transaction against a writer after the final check.",
    "Any refused partial directory and even a result written before a final refusal remain evidence. File existence alone is not completion, approval or publication permission.",
    "Runtime/code recoveryV6 predates outputreadback fix; current278test cut still requires independent restored Mac/Linux execution."
  ]
}
````
<!-- artifact-body:f97e4e4179eb79aeb9a994b13d7fe3200b5b03d52809ff94d5ef8b14421940cf:end -->
