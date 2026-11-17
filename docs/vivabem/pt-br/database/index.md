# Estruturas declaradas e limites de verificação

2026-11-04. Inventário do código atual, sem conexão com banco. Migrations descrevem a estrutura pretendida, não comprovam o schema instalado. Nenhuma migration, consulta, limpeza ou alteração estrutural foi executada.

## Models atuais

| Model | Conexão / mapeamento declarado |
| --- | --- |
| `app/Models/Atendimento.php` | table=atendimentos |
| `app/Models/Paciente.php` | table=pacientes |
| `app/Models/Psicologo.php` | table=psicologos |
| `app/Models/RegistroFcm.php` | table=registros_fcm |
| `app/Models/SolicitacaoExclusaoConta.php` | table=solicitacoes_exclusao_conta |
| `app/Models/TempoAtendimento.php` | table=tempo_atendimentos |
| `app/Models/Usuario.php` | table=usuarios |

## Migrations presentes

| Arquivo | Tabelas em create/table |
| --- | --- |
| `database/migrations/0001_01_01_000000_create_usuario_table.php` | `usuarios` |
| `database/migrations/0001_01_01_000001_create_cache_table.php` | `cache` |
| `database/migrations/0001_01_01_000002_create_jobs_table.php` | `jobs` |
| `database/migrations/0001_01_01_000010_create_password_reset_tokens_table.php` | `password_reset_tokens` |
| `database/migrations/0001_01_01_000011_create_sessions_table.php` | `sessions` |
| `database/migrations/0001_01_01_000012_create_cache_locks_table.php` | `cache_locks` |
| `database/migrations/0001_01_01_000013_create_job_batches_table.php` | `job_batches` |
| `database/migrations/0001_01_01_000014_create_failed_jobs_table.php` | `failed_jobs` |
| `database/migrations/2025_10_03_063440_create_personal_access_tokens_table.php` | `personal_access_tokens` |
| `database/migrations/2025_10_03_215955_psicologos.php` | `psicologos` |
| `database/migrations/2025_10_05_154602_pacientes.php` | `pacientes` |
| `database/migrations/2026_05_19_000000_create_atendimentos.php` | `atendimentos` |
| `database/migrations/2026_05_19_000001_create_tempo_atendimentos_table.php` | `tempo_atendimentos` |
| `database/migrations/2026_07_22_000003_create_solicitacoes_exclusao_conta_table.php` | `solicitacoes_exclusao_conta` |
| `database/migrations/2026_07_22_000004_criar_registros_fcm.php` | `registros_fcm` |

[Implementation / Implementação](../architecture/overview.md). Resultados históricos permanecem nos relatórios datados de operações; referências textuais a colunas removidas não são prova de uso atual.

<!-- reading-section: current-storage -->
## Contrato atual de armazenamento — 2026-11-10

Público: mantenedores backend/banco. A: inspeção de `Atendimento`, `Usuario`, `TempoAtendimento` e migrations create de atendimento/participação em `d412cc7`; sem consulta a banco em execução. Inventário acima preservado; texto explica restrições conferidas.

`atendimentos` usa UUID textual primário e valores decimal(10,2). Referência profissional é anulável com null-on-delete, comprador referencia usuarios com cascade e atendimento interrompido usa null-on-delete. Índices cobrem usuário/status/início, profissional/status/início e status/fim. Declarações apoiam o modelo de leitura/estado sem medir melhoria de consulta. Referência de transação Portal não possui FK para banco da Carteira.

`tempo_atendimentos` usa identidade primária do atendimento, participantes, contadores unsigned inteiros e duração. FKs de atendimento/participantes têm cascade. Casts mantêm inteiros e valores do atendimento usam decimal:2; `Atendimento::toDTO` ainda converte valor em float. Não descrever aritmética fixa uniforme no Portal apenas porque armazenamento é decimal ou uma compra usa centavos.

Hooks registram efeitos de cache/notificação e algumas operações após commit SQL. Commit não garante invalidação Redis, entrega Hub, referência remota ou conclusão financeira. `salvarRecuperacaoFinanceira` distingue salvamento interno de recuperação quando invalidação falha; não é transação entre serviços ou comando público de retry. Usuario oculta credenciais/chave Pix na serialização, sem eliminar sensibilidade de armazenamento/acesso.

Migrations create definem schema novo; presença não autoriza reset/reexecução sobre instalação existente. Preservar SQL, uploads, custódia criptográfica e auditoria/controle do operador conforme responsabilidades separadas. Backup/restore e cascades não foram exercitados. Rever idiomas/coleção após mudança de schema/model/hooks. [Arquitetura atual](../architecture/overview.md) e [testes atuais](../operations/backend-testing.md) delimitam implementação e verificação real.

- [Query Plan e diagnóstico seguro](query-plan.md)
