# ENV — env-auditor

[Project index](../index.md)

Revisão do código: 2026-10-19. A CLI não tem configuração própria por variáveis nem contrato de interpolação Compose. Foram inspecionados código e definições de testes, sem ler valores reais de ambiente.

A CLI não consome variáveis de configuração próprias. Ela lê atribuições literais dos arquivos selecionados por argumentos; não expande `${NAME}`, não interpola o ambiente do processo e preserva valores vazios. Uma chave ausente pode ser adicionada do exemplo; uma chave existente vazia é preservada, sem receber o padrão do exemplo. Não existe lista universal de nomes obrigatórios: cada projeto define seu exemplo autoritativo. Backups podem conter segredos e devem ficar privados.

[Implementation](../../../../../../../env-auditor/scripts/audit-envs.py) · [Tests](../../../../../../../env-auditor/tests/test_audit_envs.py)
