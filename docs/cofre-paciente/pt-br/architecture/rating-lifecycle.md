# Contabilização e retenção de avaliações

[Index / Índice](../index.md) · [Evidence / Evidências](../operations/source-review.md)

<!-- reading-section: account -->

## Ordem do resumo e marcador

ServicoCicloVidaAvaliacao::daily obtém lock cooperativo de cache compartilhado com retenção, percorre contribuições contabilizado=false, exige nota inteira de 1 a 5 e identidades válidas de consulta/profissional e reconfere o detalhe observado antes do resumo. Escreve primeiro resumo e depois marcador exato do detalhe. Falha após escrever resumo pode duplicar contribuição na repetição; exceções/logs preservam a incerteza. O desenho Mongo standalone não garante contabilização exatamente uma vez entre documentos.

<!-- reading-section: retention -->

## Retenção e transição

A retenção seleciona entradas contabilizadas estritamente anteriores a 1º de janeiro do ano atual em America/Sao_Paulo, aceitando BSON UTCDateTime ou strings de data validadas com offset. $pull condicional mira a entrada observada; falhas tentam marcar exclusao_pendente e informam limpeza incompleta. Transição explícita por profissional exige fonte congelada, valida contribuições únicas por consulta, escreve resumo-base e depois marcadores; não é reparo automaticamente seguro de totais históricos incertos.

<!-- reading-section: index -->

## Contrato do índice e verificação

ManutencaoIndiceAvaliacao inspeciona metadados de coleção/índice e compara chaves ordenadas exatas avaliacoes.psicologo e avaliacoes.estrelas.oid_atendimento, nome esperado e collation. Unique/sparse/hidden/prepareUnique e opções partial/TTL/wildcard são incompatíveis. Provisionamento é separado da inspeção e pode criar índice/coleção conforme a flag. Nenhum índice foi inspecionado/criado em banco real; código não comprova latência nem schema aplicado.

## Fontes inspecionadas

- `cofre-paciente/app/Services/Avaliacoes/ServicoCicloVidaAvaliacao.php`
- `cofre-paciente/app/Services/Avaliacoes/ManutencaoIndiceAvaliacao.php`
