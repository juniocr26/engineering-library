# Proveniência e limites

- Repository: `rust-event-relay`
- Workspace: `rust-event-relay/`
- Git revision: `a1e0fa1513a8cbdf362f06f5cf1bdd906eb2430c`
- Remote (observed, not fetched): `git@github.com:juniocr26/rust-event-relay.git`
- Review: 2026-10-18, static/selective.

READMEs e documentação mantida em `docs/en/` e `docs/pt-BR/` foram lidos e importados preservando nomes e ADRs. Entrevistas preexistentes da Library foram realocadas com atalhos nos caminhos antigos. Links relativos foram adaptados para cópias catalogadas ou fontes locais do workspace; a coleção de explicações é local, mas links de código exigem os repositórios irmãos. Links restritos são texto sem navegação. Nenhuma URL remota foi verificada.

## Fontes de implementação inspecionadas

- [backend/src/application.rs](../../../../../../../rust-event-relay/backend/src/application.rs)
- [backend/src/persistence/mod.rs](../../../../../../../rust-event-relay/backend/src/persistence/mod.rs)
- [backend/src/infrastructure/postgres/mod.rs](../../../../../../../rust-event-relay/backend/src/infrastructure/postgres/mod.rs)
- [backend/src/bin/relay.rs](../../../../../../../rust-event-relay/backend/src/bin/relay.rs)
- [backend/src/bin/consumer.rs](../../../../../../../rust-event-relay/backend/src/bin/consumer.rs)
- [backend/src/bin/demo.rs](../../../../../../../rust-event-relay/backend/src/bin/demo.rs)

## Limites

Inspeção estática seletiva, sem auditoria completa do código nem execução de testes/aplicações. Resultados antigos pertencem à revisão/data de origem, não a esta importação. A equivalência de caminhos não prova qualidade de tradução. Motivações não documentadas e prontidão de produção não foram inferidas. Os marcos descrevem estados diferentes e por vezes contraditórios: começar por application-scenarios e milestone-6-3 e ler os anteriores como história. Não houve confirmação de serviços, métricas ou rollout nesta tarefa.

[Mapa de importação e hashes](../../../../../catalog-provenance.json).
