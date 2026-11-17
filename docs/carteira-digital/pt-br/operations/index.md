# Operações e revisão

## Estado de implantação — 16/11/2026

O responsável pelo bootstrap aguarda SQL autenticado e executa automaticamente `php artisan migrate --force --no-interaction`. O comportamento foi preservado, sem execução na alteração Docker ou nesta tarefa documental. Revisar compatibilidade do schema e autorização de manutenção antes de iniciar contra MySQL externo. Processamento financeiro, consumidores e conciliação não foram alterados.

**Implementado:** configuração presente no código. **Validado anteriormente:** a tarefa Docker anterior relatou Compose mesclado, contrato de deploy, quatro builds Linux ARM64 no Docker Desktop/macOS e clientes isolados com configuração sintética sem rede. Essas verificações não foram repetidas aqui e não comprovam conectividade externa nem aceite nativo de servidor. **Pendente:** configuração da infraestrutura, conectividade, conferência dos dados migrados, backup/rollback, ativação autorizada e aceite de produção. Os dados existentes permanecem até desativação controlada separadamente. Esta tarefa documental não executou deploy, restart ou migração de produção.

[Index / Índice](../index.md)

- [Revisão das fontes](source-review.md)

- [Backend](backend-testing.md)
