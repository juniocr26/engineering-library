[Other language](../../en/architecture/durable-failure-policy.md)

# Classificação de falhas, retries duráveis e identidade de replay

## Princípios gerais de engenharia

Categoria de erro descreve evidência técnica na fronteira, não regra universal de retry. Serialização pode depender do conteúdo ou implementação; unroutable pode indicar topologia corrigível; outage não prova invalidade permanente. Política combina fase, efeitos conhecidos/incertos, autoridade, orçamento e evidência independente de permanência. Preservar falha primária e cleanup secundário separadamente.

Retry durável grava due time atomicamente com diagnóstico e liberação da autoridade válida. Espera em memória desaparece no restart. Escolher relógio autoritativo, precisão, jitter limitado e aritmética verificada. Separar infraestrutura de agenda por evento e evitar retry oculto no adapter. Aceite/COMMIT desconhecido não prova ausência/rollback: observar estado exato quando possível ou recuperar por predicados duráveis admitindo duplicação. Nomear reconciliação não implementa capacidade de reconciliar.

Orçamentos contam fatos diferentes: aquisição confirmada é observável duravelmente mas cobra crash antes do envio; publicação/aceite externo não é medido atomicamente com storage local sem protocolo adicional; ciclo de recuperação renova intenção preservando histórico. Esgotamento é decisão operacional, não prova poison nem entrega bem-sucedida. Limite da aplicação e capacidade numérica são separados; nunca wrap ou saturação silenciosa do histórico.

Isolamento exige evidência/evento preservado. Estado terminal existente evita movimentação de lifecycle; quarentena separada favorece controle de acesso mas exige atomicidade/consistência de replay. Mecanismo baseado em envelope válido possuído não trata toda linha inválida: precisa manutenção protegida da linha bruta. Evitar obstrução repetida de trabalho válido, preservar dono ativo, sanitizar diagnóstico e restringir evidência bruta. DLQ do broker não trata linha que nunca chegou ao broker.

Replay é intenção explícita auditável com estado/revisão esperados, identidade original estável, contador vitalício preservado e orçamento de ciclo definido. Concorrência/repetição/perda de reconhecimento de COMMIT exigem identidade durável de request e consulta. Mesmo ID pode intencionalmente não gerar efeito adicional em consumidor que já confirmou dedup e efeito atomicamente. Renovar entrega não garante renovar efeito de negócio.

## Desenho Rust escolhido — 2026-10-12

[ADR 008](../../../../rust-event-relay/docs/pt-BR/adr/008-durable-failure-policy.md) e [matriz/roadmap completos](../../../../rust-event-relay/docs/pt-BR/architecture/milestone-3-1.md): 10 aquisições confirmadas por ciclo, baseline inicial zero, attempt_count vitalício preservado e novo ciclo auditado no replay. Agenda planejada usa UTC PostgreSQL pós-lock, microssegundos inteiros, base 1 s/teto 300 s e equal jitter de metade do ceiling arredondada para cima até ceiling. Sem retry hints. Publicação incerta retém lease; conclusão falha/incerta não autoriza release compensatório/envio cego. Escolhas do projeto, não padrões universais.

Isolamento planejado usa dead_letter/evidência/auditoria e manutenção bruta com revisão/lease. Replay aceita envelope terminal válido preservando ID/conteúdo e recusa capacidade i32 esgotada. 3.2 adiciona schema/transições; 3.3 integra política; 3.4 isola poison; 3.5 replay explícito; 3.6 evidência/fechamento. 3.1 tem somente cálculos puros/testes de orçamento/backoff. Não alegar agenda durável, scanner, API replay ou consumidor implementados. Vue permanece ilustrativo; evidência histórica do Marco 2 continua válida no seu escopo.

A biblioteca muda somente documentação, preservando aplicação/dependências/runtime. Testes puros não provam durabilidade SQL ou recuperação concorrente. Acesso/retenção de produção e rollout de migration compartilhada são pré-requisitos separados.
