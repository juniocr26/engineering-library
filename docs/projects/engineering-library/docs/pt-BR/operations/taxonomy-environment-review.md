# Relatório de implementação — 2026-10-18

## Arquivos e taxonomia

- Renomeados 26 arquivos de `technical-interview/` para `faq/`, nas 12 coleções de idioma dos seis projetos. Comparação com HEAD confirmou conteúdo e títulos Q preservados, descontando somente o nome da categoria e destinos de links corrigidos.
- Criadas 12 referências `env/index.md` (EN e pt-BR em cada projeto), quatro guias recuperados do commit `bed78d2` dentro da coleção Engineering Library, dois procedimentos de migração e este relatório bilíngue.
- Criados `LICENSE` na raiz e `tools/test_catalog.py` com cinco testes de regressão do contrato do catálogo.
- Modificados `.env.example`, quatro atribuições não secretas do `.env` local, `compose.yaml` e `.gitignore` (backups privados).
- Atualizados READMEs da raiz, dos componentes e dos projetos; `docs/index.md`, destinos em `catalog-provenance.json`, links em `catalog-review.md`, índices de idioma/categoria, referências de arquitetura/testes e os verificadores `docs/validation/check_catalog.py` e `tools/check_docs.py`.
- Não foram criados `docs/en/` ou `docs/pt-BR/`. A hierarquia permanece Biblioteca → Projeto → Idioma → Índice → Categoria → Documento. Evidências históricas e hashes de importação foram mantidos como registros históricos; destinos foram atualizados.

## Cobertura ENV por projeto

| Projeto | Cobertura e limites |
| --- | --- |
| engineering-library | Compose, PostgreSQL, Rails/Puma, backend URL Next, configuração fixa de containers e variáveis de teste/boot. Ausência versus vazio e validações obrigatórias documentadas. |
| env-auditor | A CLI não tem esquema próprio de variáveis de runtime; referência explica atribuições literais, vazio preservado, chave ausente e backups privados. |
| go-image-optimizer | Portas Compose/Go/Next, URL backend, perfis de runtime e entradas opcionais de fixtures. |
| payment-reconciliation-lab | Compose, placeholders Spring, JDBC, credenciais, origens CORS, seed desabilitado, volume e chave Stripe reservada sem consumidor. |
| rust-event-relay | Compose, workers, tempos/limites, PostgreSQL, AMQP, topologias, métricas, replay e demo; distinção entre padrões Compose e execução direta. |
| url-shortener | Compose, settings Python, Redis/Cassandra, autenticação, URL pública, IDs, Base62 e ofuscação opcional. |

Todas as fontes locais dos seis projetos estavam disponíveis. Foram usados templates e código, sem copiar valores reais de segredos. Comportamentos não demonstrados pelo código inspecionado (por exemplo, conversões específicas Spring e resolução de URL de produção Rails) estão explicitamente limitados nas referências.

## Infraestrutura, banco e segurança

| Serviço | Publicação local | Porta interna |
| --- | --- | --- |
| Next.js | 127.0.0.1:3099 | 3000 |
| Rails | 127.0.0.1:3098 | 3000 |
| PostgreSQL | 127.0.0.1:5499 | 5432 |

As três portas estavam livres antes da mudança. Após autorização explícita, foram feitos backups custom dos bancos antigo de desenvolvimento e teste e backup dos papéis, com permissões privadas e exclusão do Git. Ambos os dumps passaram por `pg_restore --list`. Os aplicativos foram parados temporariamente e ambos os bancos renomeados via SQL para `engineering_library` e `engineering_library_test`. Nomes novos foram consultados e confirmados; o desenvolvimento manteve sua linha de metadados. Não foram encontradas tabelas de domínio, slots ou transações preparadas. A consulta posterior também não encontrou assinaturas de replicação no desenvolvimento.

O cluster PostgreSQL 18 existente e seu bind mount foram preservados; nenhuma limpeza de volume, exclusão ou reinicialização ocorreu. Credenciais não foram regeneradas. Rails continua em `postgres:5432` e Next continua com fetch no servidor para `http://backend:3000`, sem necessidade de alterar CORS. `database.yml` já usa `POSTGRES_DB`; não foi necessário duplicar o nome nele. Backups privados estão em `.local-backups/2026-10-18-database-rename/`. [Procedimento e recuperação](database-migration.md).

## Licença

MIT padrão com copyright 2026 Júnio César Rosa, confirmado pelo histórico Git e licenças MIT dos cinco projetos de origem. Não havia licença raiz conflitante; materiais importados vieram desses projetos e conservam a mesma atribuição. Dependências de terceiros mantêm suas licenças. Software reutilizável não autoriza publicar documentação privada: mantenha separação de repositórios, controle de acesso e gestão de segredos. Arquivos reais de ambiente, backups e dados continuam ignorados e fora do stage.

## Verificações executadas

- `python3 -B docs/validation/check_catalog.py`: links, âncoras, navegação, paridade bilíngue, FAQ e ENV, sem erros ou avisos.
- `python3 -B -m unittest discover -s tools -p 'test_*.py' -v`: 27 testes passaram (22 existentes e cinco novos).
- `docker compose config --quiet`: configuração válida.
- `docker compose up -d` e `docker compose ps`: três serviços saudáveis nas portas novas.
- `docker compose exec -T backend bin/rails test`: dois testes, quatro asserções, zero falhas, erros ou skips.
- `curl --fail` para Rails `/up` na porta 3098 e frontend na porta 3099: HTTP 200 em ambos.
- Conexão TCP com negociação de protocolo PostgreSQL em `127.0.0.1:5499`: resposta válida, sem usar credenciais.
- SQL de catálogo, tabelas, conexões, ACLs, slots, transações preparadas, nomes finais e metadados; arquivo `PG_VERSION` confirmou 18.
- Comparação dos 26 arquivos FAQ com HEAD: conteúdo preservado, descontando alterações autorizadas de categoria e links.
- `git diff --check`: sem erros; revisão do diff e conferência de `.env`, backups e dados ignorados e não rastreados. Nenhum arquivo foi adicionado ao stage; nenhum commit ou push foi criado.

## Limitações

Não foi usado o cliente DBeaver. A porta publicada respondeu ao PostgreSQL, mas isso não representa uma conexão autenticada pelo DBeaver. A leitura de catálogo dos dumps não equivale a uma restauração completa; não foi realizado ensaio de recuperação. URLs externas não foram consultadas. Validação estrutural não certifica tradução nem todo comportamento de bibliotecas ou imagens externas. O verificador legado e seu manifesto continuam disponíveis como evidência/tooling anterior; a verificação do catálogo atual usa `docs/validation/check_catalog.py`.

Mensagem Conventional Commit sugerida:

```text
feat(docs): standardize FAQ and env catalogs and update development infrastructure
```
