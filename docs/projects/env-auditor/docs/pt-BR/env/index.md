# ENV — env-auditor

[Project index](../index.md)

Referência verificada em 2026-10-18 a partir dos arquivos locais seguros. Valores reais de `.env` não foram usados nesta referência. Exemplos com segredos usam `<secret>`. Não publique senhas, tokens ou URLs com credenciais; preserve credenciais do cluster existente. Variáveis do shell podem sobrepor o arquivo de ambiente do Compose.

A CLI não consome variáveis de configuração próprias. Ela lê atribuições literais dos arquivos selecionados por argumentos; não expande `${NAME}`, não interpola o ambiente do processo e preserva valores vazios. Uma chave ausente pode ser adicionada do exemplo; uma chave existente vazia é preservada, sem receber o padrão do exemplo. Não existe lista universal de nomes obrigatórios: cada projeto define seu exemplo autoritativo. Backups podem conter segredos e devem ficar privados.

[Implementation](../../../../../../../env-auditor/scripts/audit-envs.py) · [Tests](../../../../../../../env-auditor/tests/test_audit_envs.py)
