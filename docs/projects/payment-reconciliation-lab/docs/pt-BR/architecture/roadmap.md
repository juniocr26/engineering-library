# Escopo e estado da implementação

[English](../../en/architecture/roadmap.md) | [Português](roadmap.md)

## Base atual

Identidade de infraestrutura Payment Reconciliation Lab configurada. Spring Boot, Angular, PostgreSQL, migrações Flyway preservadas, segurança que nega por padrão e catálogo legado somente leitura permanecem. Política de compra/consentimento e seed foram removidos; resultados antigos pertencem ao [relatório histórico](../operations/historical-refactor-report.md). Testes presentes estão em [testes](../testing/strategy.md).

## Direção futura

Reconciliação de pagamentos e integração Stripe de teste não estão implementadas. Não há schema de reconciliação, matching, adaptador de importação/provedor, webhook, ciclo de divergências ou UI de revisão. O roadmap anterior de identidade/checkout/fidelidade da padaria é histórico, sem estabelecer requisitos da nova direção.

Ordem sugerida de pré-requisitos para projeto/estudo, não marcos de release aprovados nem trabalho concluído:

1. Definir registros de origem, precisão monetária/moeda, correspondência e divergências.
2. Definir acesso, persistência e histórico imutável antes de expor escritas.
3. Implementar fixtures determinísticas isoladas e testes antes do provedor.
4. Definir adaptador Stripe de teste, assinaturas, idempotência e replay/recuperação.
5. Introduzir UI de revisão e verificações de falhas após os contratos de backend.

São questões razoáveis para projeto, não evidência de alternativas avaliadas/selecionadas no desenvolvimento. Nenhum tópico é marcado estudado ou concluído. Preserve dados ao substituir superfícies legadas em mudanças separadas.

## Infraestrutura adiada

Não há necessidade atual de broker, cache, worker distribuído ou object storage em fluxo implementado de reconciliação. Introduza-os para requisitos explícitos de entrega, latência, retenção ou implantação. Desenvolvimento não equivale a produção.
