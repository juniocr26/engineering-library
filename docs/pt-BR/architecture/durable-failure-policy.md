[Other language](../../en/architecture/durable-failure-policy.md)

# Classificação de falhas, retries duráveis e identidade de replay

## Princípios gerais de engenharia

Categoria de erro descreve evidência técnica na fronteira, não regra universal de retry. Serialização pode depender do conteúdo ou implementação; unroutable pode indicar topologia corrigível; outage não prova invalidade permanente. Política combina fase, efeitos conhecidos/incertos, autoridade, orçamento e evidência independente de permanência. Preservar falha primária e cleanup secundário separadamente.

Retry durável grava due time atomicamente com diagnóstico e liberação da autoridade válida. Espera em memória desaparece no restart. Escolher relógio autoritativo, precisão, jitter limitado e aritmética verificada. Separar infraestrutura de agenda por evento e evitar retry oculto no adapter. Aceite/COMMIT desconhecido não prova ausência/rollback: observar estado exato quando possível ou recuperar por predicados duráveis admitindo duplicação. Nomear reconciliação não implementa capacidade de reconciliar.

Orçamentos contam fatos diferentes: aquisição confirmada é observável duravelmente mas cobra crash antes do envio; publicação/aceite externo não é medido atomicamente com storage local sem protocolo adicional; ciclo de recuperação renova intenção preservando histórico. Esgotamento é decisão operacional, não prova poison nem entrega bem-sucedida. Limite da aplicação e capacidade numérica são separados; nunca wrap ou saturação silenciosa do histórico.

Isolamento exige evidência/evento preservado. Estado terminal existente evita movimentação de lifecycle; quarentena separada favorece controle de acesso mas exige atomicidade/consistência de replay. Mecanismo baseado em envelope válido possuído não trata toda linha inválida: precisa manutenção protegida da linha bruta. Evitar obstrução repetida de trabalho válido, preservar dono ativo, sanitizar diagnóstico e restringir evidência bruta. DLQ do broker não trata linha que nunca chegou ao broker.

Replay é intenção explícita auditável com estado/revisão esperados, identidade original estável, contador vitalício preservado e orçamento de ciclo definido. Concorrência/repetição/perda de reconhecimento de COMMIT exigem identidade durável de request e consulta. Mesmo ID pode intencionalmente não gerar efeito adicional em consumidor que já confirmou dedup e efeito atomicamente. Renovar entrega não garante renovar efeito de negócio.

## Desenho Rust escolhido — 2026-10-12

[ADR 008](../../../../rust-event-relay/docs/pt-BR/adr/008-durable-failure-policy.md) e [matriz/roadmap completos](../../../../rust-event-relay/docs/pt-BR/architecture/milestone-3-1.md): 10 aquisições confirmadas por ciclo, baseline inicial zero, attempt_count vitalício preservado e novo ciclo auditado no replay. Agenda implementada em 3.2 usa UTC PostgreSQL pós-lock, microssegundos inteiros, base 1 s/teto 300 s e equal jitter de metade do ceiling arredondada para cima até ceiling. Sem retry hints. Publicação incerta retém lease; conclusão falha/incerta não autoriza release compensatório/envio cego. Escolhas do projeto, não padrões universais.

Marco 3.2 implementa metadados aditivos de ciclo/baseline/orçamento/revisão, agenda protegida, preservação dead_letter e porta de manutenção exata de esgotados. Scanner geral de poison permanece 3.4; integração da política é 3.3, replay autenticado/auditado 3.5 e fechamento integrado 3.6. Não alegar pipeline implantado, scanner, replay ou consumidor implementados. Vue permanece ilustrativo/inalterado; evidência histórica do Marco 2 mantém seu escopo.

## Mecânica das transições duráveis

Persistir orçamento do ciclo com contador vitalício, sem reset de histórico nem dependência de configuração volátil. Backfill com baseline zero inclui aquisições históricas; contador >= 10 exige manutenção sem nova aquisição. A última aquisição pode concluir com lease válido. Agenda não contorna orçamento nem capacidade numérica.

Transação curta bloqueia linha exata, depois amostra tempo do banco em statement separado e valida status, identidade, token ativo, ciclo e revisão esperados. Delay selecionado, diagnóstico, limpeza da autoridade e avanço da revisão são atômicos. Aquisição, conclusão, release e transições novas incrementam revisão; escritores externos seguem o mesmo protocolo. Constraints validam formato, não autorização de operador nem toda a sequência histórica.

Manutenção mínima usa um ID/ciclo/revisão observado independentemente com SKIP LOCKED, revalida pending vencido sem lease ativo e distingue acquisition_budget_exhausted de storage_counter_exhausted. Não constrói envelope válido nem faz scanner/reparo poison. Terminal preserva identidade/envelope/contadores, não tem dono/processed_at e registra motivo/horário/evidência. Dead_letter legado recebe motivo legado e horário de observação pela migration; horário histórico da falha é desconhecido. Sem reativação nem exclusão automática por retenção.

Evidência aceita versões fixas de policy/validator, fase tipada e referência UUID opcional, limitada a 2 KiB JSON UTF-8 serializado. Diagnóstico legado é dado restrito; não copiar cadeia livre de driver, credenciais ou payload para evidência pública. CHECK SQL precisa recusar JSON null explicitamente porque resultado NULL pode passar.

Repetição após sucesso conflita; ausência de match não implica sucesso. Reconhecimento de COMMIT perdido permanece CommitUncertain; cancelamento pode suprimir resultado durável. Observar estado exato antes de agir, sem recomputar agenda ou republicar cegamente. Experimentos PostgreSQL isolados cobrem locks, orçamento, concorrência de manutenção, rejeição do servidor, reconhecimento perdido e cancelamento após COMMIT; testes puros não comprovam essas propriedades.

[Implementação Rust e contrato de rollout](../../../../rust-event-relay/docs/pt-BR/architecture/milestone-3-2.md) separam decisões do projeto de princípios gerais. Rollout compartilhado, acesso/retenção de evidência e ativação produtiva dependem de autorização separada. Down perde metadados/auditoria e só é testado em fixtures descartáveis, nunca como recuperação produtiva. A biblioteca altera somente documentação; aplicação/dependências/runtime permanecem inalterados.
