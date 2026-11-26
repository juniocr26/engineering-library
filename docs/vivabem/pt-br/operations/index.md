# Operações e revisão

## Estado de implantação — 16/11/2026

Readiness SQL usa `SELECT 1` autenticado; crypto, storage privado de saúde e verificações HTTP/FPM são separados. O ambiente Compose define `VIVABEM_RUN_MIGRATIONS` como `0` por padrão, embora a execução direta do entrypoint tenha padrão `1`; migrations e instalação de saúde dependem desse seletor existente. A ausência de `--migrate` na linha de comando não basta para inferir ausência de escritas.

**Implementado:** configuração presente no código. **Validado anteriormente:** a tarefa Docker anterior relatou Compose mesclado, contrato de deploy, quatro builds Linux ARM64 no Docker Desktop/macOS e clientes isolados com configuração sintética sem rede. Essas verificações não foram repetidas aqui e não comprovam conectividade externa nem aceite nativo de servidor. **Pendente:** configuração da infraestrutura, conectividade, conferência dos dados migrados, backup/rollback, ativação autorizada e aceite de produção. Os dados existentes permanecem até desativação controlada separadamente. Esta tarefa documental não executou deploy, restart ou migração de produção.

[Index / Índice](../index.md)

- [Revisão das fontes](source-review.md)

- [Backend](backend-testing.md)

- [Cockpit Técnico](technical-cockpit.md)
