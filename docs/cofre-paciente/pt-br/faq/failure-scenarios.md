# Raciocínio sobre falhas — Cofre Paciente

[English](../../en/faq/failure-scenarios.md) | [Português brasileiro](failure-scenarios.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `85edbcb16fd029235dc74eba12c7b14b164d3d62`.

<!-- reading-section: q004 -->

## Q004 — Onde termina a consistência?

RepositorioCartoes armazena mapas por usuário, valida identificadores dinâmicos e usa atualizações pontuais Mongo. deleteObserved compara string/tipo exatos observados com collation simple antes de $unset e informa se um item mudou. LeitorFinanceiroArmazenado lê envelopes autenticados atuais e valida JSON do cartão, mantendo entradas ilegíveis como null e retornando complete=false. Falhas de repositório/configuração propagam, sem virar lista vazia completa. Atualizações de documento único Mongo não criam transação com SQL do Portal ou serviços remotos.

<!-- reading-section: q005 -->

## Q005 — Como conduzir a investigação?

Estude ExternalPosterCofrePaciente do Portal e os dois arquivos PoliticaRequisicaoCofre em conjunto. Em fixture isolada autorizada separadamente, teste requisição sintética válida, substituição de corpo/caminho, token expirado, replay exato e item armazenado ilegível. Na exclusão, retenha o valor observado e detecte alteração concorrente, sem substituir o mapa inteiro. Limpeza remota de conferência e remoção de referência local têm resultados diferentes; leia o runbook existente antes de qualquer replay.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
