# FAQ técnica — cofre-paciente

2026-11-04. Revisão estática dos contratos atuais; sem chamada ao provedor.

[Index / Índice](../index.md)

<!-- reading-section: q001 -->

## Q001 — Um token válido do Cofre impede replay?

Não. PoliticaRequisicaoCofre vincula método/caminho/corpo e limita duração sem registro de nonce consumido. Isso não fornece mutação exatamente uma vez. Débito também compara sub delegado com o proprietário decifrado; o Use Case base de crédito não possui essa mesma checagem adicional.

<!-- reading-section: q002 -->

## Q002 — Por que preservar um item ilegível?

Envelope armazenado rejeitado difere de ausência. LeitorFinanceiroArmazenado informa identidade do item e resultado incompleto; falhas de repositório/configuração são distintas. Exclusão exige hash observado e comparação do valor exato. Débito possui ramo separado para envelope rejeitado; não presumir exclusão manual idêntica em crédito/débito.

<!-- reading-section: q003 -->

## Q003 — Quais afirmações permanecem sem verificação?

Concorrência Mongo real, índices implantados, ciclo completo de avaliações, recuperação de filas, restauração e autorização ponta a ponta do titular não foram verificados. Exclusão de débito/confirmação do provedor em produção está implementada, mas não foi exercitada. Não houve chamada real a Mongo, broker ou provedor.

## Cartão salvo ou webhook assinado comprova pagamento concluído?

Não. Tokenização, associação do cliente, armazenamento cifrado, aprovação do provedor, efeito financeiro SQL e entrega ao Portal são resultados distintos. A simulação local Pix também é distinta da confirmação do provedor.

[Integration / Integração](../integrations/saved-cards.md) · [Failure scenarios / Cenários de falha](failure-scenarios.md) · [Source / Origem](../../../../../cofre-paciente/docs/pt-br/architecture/current-implementation.md).
