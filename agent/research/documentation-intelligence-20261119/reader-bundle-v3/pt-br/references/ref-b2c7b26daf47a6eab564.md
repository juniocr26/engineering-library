# Registro de evidência: python-registry-binding-evaluation.json

Este é um artefato bruto de pesquisa de um recorte datado. Resultados e saídas rejeitadas do modelo mantêm o status registrado. Ler o registro não aprova publicação nem treinamento.

SHA-256: `b2c7b26daf47a6eab56419d4e8fc4a384adc6df03080a530ad6c63d79e0172ee`. Bytes originais: `2008`.

Caminho original: `agent/research/documentation-intelligence-20261119/python-registry-binding-evaluation.json`.

<!-- reading-section:reference:b2c7b26daf47a6eab564:consumers -->
## Referenciado por

- [Agente de documentação: contratos de fonte, identidade e propriedade](../chapters/documentation-agent-contracts.md)

<!-- reading-section:reference:b2c7b26daf47a6eab564:artifact -->
## Artefato original

O bloco reproduz o artefato UTF-8 exato; acrescenta-se uma quebra final apenas para exibição se ela não existir no original.

<!-- artifact-body:b2c7b26daf47a6eab56419d4e8fc4a384adc6df03080a530ad6c63d79e0172ee:start -->
````json
{
  "at": "2026-11-20T02:01:44.024292+00:00",
  "issue": "A literal registry and a same-named function were stored in separate observer maps even though both own one Python module binding.",
  "severity": "CRITICAL_FALSE_REMOVAL_IN_OPTIONAL_RESEARCH_PROTO",
  "before": {
    "version": "0.3.2",
    "action": "REMOVE",
    "packet": {
      "id": "retirement-registry-shadow",
      "family": "python-binding-diagnostic",
      "language": "python",
      "previous_source": "def value():\n    return 1\n",
      "current_source": "RETIRED_CONTRACTS = {\"sample.value\": \"retired\"}\ndef RETIRED_CONTRACTS():\n    return 9\n",
      "documentation": {
        "en": "value returns1.",
        "pt-br": "value retorna1."
      },
      "complete_scope": true,
      "source_available": true,
      "positive_retirement_evidence": {
        "contract_id": "sample.value",
        "source": "current module RETIRED_CONTRACTS",
        "reason": "retired",
        "aliases_checked": true,
        "relocations_checked": true
      },
      "logical_contract_id": "sample.value",
      "metadata": {}
    }
  },
  "after": {
    "version": "0.3.3",
    "action": "INCONCLUSIVE",
    "reason": "duplicate function ownership"
  },
  "fixes": [
    "Shared module-binding uniqueness enforced across functions and all three admitted literal registries, in both declaration orders.",
    "Duplicate positional/keyword/vararg parameter ownership refused before facts are admitted."
  ],
  "regression_tests_added": 3,
  "full_documentation_python_tests": 122,
  "source_executed": false,
  "model_calls": 0,
  "original_documentation_changed": false,
  "false_recommendation_applied": false,
  "production_ruby_routing_changed": false,
  "owner_approved": false,
  "training_gold": false,
  "limits": [
    "This proves bounded source-observer refusal, not general Python namespace/type/conditional/runtime analysis.",
    "Only optional research protocols were changed; publication remains owner-controlled."
  ]
}
````
<!-- artifact-body:b2c7b26daf47a6eab56419d4e8fc4a384adc6df03080a530ad6c63d79e0172ee:end -->
