# Operações e revisão

## Estado de implantação — 16/11/2026

A extensão PHP MongoDB e a biblioteca da aplicação continuam necessárias em runtime. A prontidão usa a conexão MongoDB existente e o comando `ping`; crypto, storage de controle, heartbeat de workers e HTTP têm verificações distintas. O overlay de servidor não depende da saúde de MongoDB local; indisponibilidade externa não equivale a readiness bem-sucedido.

**Implementado:** configuração presente no código. **Validado anteriormente:** a tarefa Docker anterior relatou Compose mesclado, contrato de deploy, quatro builds Linux ARM64 no Docker Desktop/macOS e clientes isolados com configuração sintética sem rede. Essas verificações não foram repetidas aqui e não comprovam conectividade externa nem aceite nativo de servidor. **Pendente:** configuração da infraestrutura, conectividade, conferência dos dados migrados, backup/rollback, ativação autorizada e aceite de produção. Os dados existentes permanecem até desativação controlada separadamente. Esta tarefa documental não executou deploy, restart ou migração de produção.

[Index / Índice](../index.md)

- [Revisão das fontes](source-review.md)

- [Backend](backend-testing.md)
