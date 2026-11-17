# Operações e revisão

## Estado de implantação — 16/11/2026

Node `/health` mede liveness; `/ready` exige ambos os clientes Redis, confirmações das assinaturas obrigatórias e ausência de shutdown. Reconexão e publicação offline mantêm o comportamento existente. Publicador e assinante têm credenciais e responsabilidades distintas; Pub/Sub não oferece replay durável. RabbitMQ é broker separado preservado: serviço, imagem, usuários/vhosts, identidade do nó e configuração de persistência não foram alterados. A migração anterior do RabbitMQ para diretório de host permanece pendência separada; não ativar substituição vazia nem inferir sua conclusão a partir desta mudança Redis.

**Implementado:** configuração presente no código. **Validado anteriormente:** a tarefa Docker anterior relatou Compose mesclado, contrato de deploy, quatro builds Linux ARM64 no Docker Desktop/macOS e clientes isolados com configuração sintética sem rede. Essas verificações não foram repetidas aqui e não comprovam conectividade externa nem aceite nativo de servidor. **Pendente:** configuração da infraestrutura, conectividade, conferência dos dados migrados, backup/rollback, ativação autorizada e aceite de produção. Os dados existentes permanecem até desativação controlada separadamente. Esta tarefa documental não executou deploy, restart ou migração de produção.

[Index / Índice](../index.md)

- [Revisão das fontes](source-review.md)

- [Backend](backend-testing.md)
