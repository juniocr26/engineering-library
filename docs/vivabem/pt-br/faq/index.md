# FAQ técnica — vivabem

2026-11-04. Revisão estática dos contratos atuais; sem chamada ao provedor.

[Index / Índice](../index.md)

<!-- reading-section: q001 -->

## Q001 — Como compras e consultas de saldo são separadas?

LeitorSaldo assina leitura vinculada a titular/corpo/caminho para /api/get_saldo da Carteira e valida a resposta cifrada com saldo decimal string. Controllers de compra delegam pelo adaptador/cliente financeiro e Use Cases atuais. O shell genérico indisponível aposentado não é o contrato atual de compra. Consulta de saldo bem-sucedida não aprova compra.

<!-- reading-section: q002 -->

## Q002 — Qualquer heartbeat do aplicativo renova a autorização de 60 dias?

SessaoAutenticacaoRedis separa atividade qualificadora de presença passiva e heartbeats de Hub/vídeo. Autorização, elegibilidade persistente, duração do cookie e transporte alcançável de notificações são ciclos separados. Marcador Android isolado não é autenticação.

<!-- reading-section: q003 -->

## Q003 — Quais afirmações permanecem sem verificação?

Transições completas de atendimentos, videoconferência/FCM reais, recuperação de filas, acessibilidade, concorrência de banco e inicialização/restauração em produção não foram executadas. Callbacks estão implementados com validação JWT de escopo própria; existência de rota não comprova entrega.

## Cartão salvo ou webhook assinado comprova pagamento concluído?

Não. Tokenização, associação do cliente, armazenamento cifrado, aprovação do provedor, efeito financeiro SQL e entrega ao Portal são resultados distintos. A simulação local Pix também é distinta da confirmação do provedor.

[Integration / Integração](../integrations/mercado-pago.md) · [Failure scenarios / Cenários de falha](failure-scenarios.md) · [Source / Origem](../../../../../vivabem/docs/pt-br/architecture/current-implementation.md).
