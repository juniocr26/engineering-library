# rust-event-relay: avaliação documental local

Registro de verificação redigido pelo revisor, 2026-11-16. É separado do rascunho do modelo local e não certifica segurança, desempenho ou plataformas integralmente.

## Baseline real

O crate da biblioteca compilou offline no Docker: 25 testes unitários passaram e dois dependentes de RabbitMQ foram ignorados, sem iniciar supervisor, workers, PostgreSQL ou RabbitMQ. Teste adicional em cópia isolada exercitou o domínio original: máximo inicial 10, orçamento esgotado, rejeição de timestamp submicrossegundo e campos JSON condicionais.

## Cenários reversíveis e recuperação

Máximo 10→7 e remoção do guard de precisão alteraram o domínio compilado real. Fontes e verificações originais foram restauradas. Uma resposta do modelo excedeu tempo; outra atribuiu aplicação de regra incorretamente e citou imports. São resultados documentais rejeitados, não falha de restauração. Não há certificação de entrega/reconciliação via broker de ponta a ponta.

Fontes da aplicação foram restauradas; entregas aceitas de implementação/documentação permanecem. Os dois destinos gerados usam um resultado lógico bilíngue. Validação mecânica e citações não comprovam redação correta. A execução usou containers Linux em host macOS; Windows/WSL2 e host Linux independente continuam sem validação. Não houve treinamento de pesos.

[Sumário](../index.md)
