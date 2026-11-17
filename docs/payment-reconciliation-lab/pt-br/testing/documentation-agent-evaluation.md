# payment-reconciliation-lab: avaliação documental local

Registro de verificação redigido pelo revisor, 2026-11-16. É separado do rascunho do modelo local e não certifica segurança, desempenho ou plataformas integralmente.

## Baseline real

O pacote completo Maven compilou com JDK 25; fontes de testes compilaram, mas package -DskipTests não os executou. A API HTTP real usou PostgreSQL 17 novo sintético: um produto, preço decimal, availability string, purchasable booleano e imagem nula foram conferidos; escrita retornou 403. pg_dump foi restaurado em banco isolado e o JSON das linhas coincidiu exatamente.

## Cenários reversíveis e recuperação

Renomear name do DTO para displayName alterou a resposta real. Remover imagePath exigiu adaptar o construtor de produção e um fixture de teste obsoleto; a primeira falha de compilação foi preservada. Build/API corrigidos conferiram ausência de imagePath. Fontes/fixture experimentais e runtime original foram restaurados.

Fontes da aplicação foram restauradas; entregas aceitas de implementação/documentação permanecem. Os dois destinos gerados usam um resultado lógico bilíngue. Validação mecânica e citações não comprovam redação correta. A execução usou containers Linux em host macOS; Windows/WSL2 e host Linux independente continuam sem validação. Não houve treinamento de pesos.

[Sumário](../index.md)
