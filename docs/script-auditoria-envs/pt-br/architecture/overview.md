# Utilitário de ambiente: sincronização e aplicação explícita de propostas

Inspeção do código: 04/11/2026. Comportamento implementado é distinto de verificação executada e homologação no provedor.

CLI Python 3 com biblioteca padrão. `audit-envs.py` delega a `env_sync.py`; `env_apply.py` controla aplicação explícita de propostas. A descoberta parte do pai do repositório do utilitário, salvo raiz explícita; não sobe arbitrariamente pelos ancestrais.

## Fronteiras e implementação detalhada

O capítulo privado de origem mantém fluxos, persistência, autorização, falhas e limitações atuais. A centralização separa este resumo conceitual dos detalhes operacionais.

- [Utilitário de ambiente: sincronização e aplicação explícita de propostas](../../../../../script-auditoria-envs/docs/pt-br/architecture/current-implementation.md)
- [Contratos implementados](contracts.md)
