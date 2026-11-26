# Ambiente de desenvolvimento e comandos operacionais

[Índice de guias](index.md) · [Operação e recuperação](../operations/runtime-and-recovery.md)

<!-- reading-section: application-development-1 -->
## Pré-requisitos e startup

Use o stack Docker/Compose existente e Python 3.10+ em host POSIX. Node.js/npm, Ruby/Bundler/Rails e clientes PostgreSQL executam nos containers. Python no host é necessário ao adapter gerenciado de filesystem, não apenas um gerador opcional de credenciais. No Windows, utilize ambiente POSIX WSL2 integrado ao Docker; PowerShell nativo não suporta este adapter. Preserve scripts em LF conforme `.gitattributes`. Não se afirma homologação no host Windows.

Execute os exemplos na raiz do checkout. Garanta Docker disponível, compartilhamento do checkout no Docker Desktop quando necessário e portas loopback padrão 3099, 3098 e 5499 livres. Preserve `.env` existente; o launcher cria credenciais aleatórias privadas somente quando o arquivo está ausente, sem exibi-las. No Linux, gera UID/GID a partir do usuário atual; `.env` existente ainda exige revisão deliberada de permissões. Nunca atribua recursivamente o armazenamento PostgreSQL ao usuário da aplicação.

```sh
python3 -B tools/init_dev_env.py up -d --build --wait --wait-timeout 600
# Abra http://127.0.0.1:3099 e http://127.0.0.1:3098/up
python3 -B tools/init_dev_env.py status
docker compose ps
# Pare e reinicie preservando os dados:
python3 -B tools/init_dev_env.py stop
python3 -B tools/init_dev_env.py up -d
# Remova containers/rede dos serviços preservando arquivos persistentes:
python3 -B tools/init_dev_env.py down
```

Startup não é somente leitura. O backend verifica dependências, aguarda o adapter obrigatório, executa `db:prepare catalog:sync` e inicia Rails. O frontend aguarda health do backend. Revise migrations antes de upgrades. Compose sem supervisor gerenciado é incompleto para operações com projetos no host.

<!-- reading-section: application-development-2 -->
## Serviços, rede e armazenamento

| Componente | Endereço no Compose | Acesso padrão pelo host | Armazenamento / limite |
| --- | --- | --- | --- |
| Frontend Next.js | `frontend:3000` | `127.0.0.1:3099` | Bind de código/dependências; `.next` tmpfs; biblioteca `/docs` gravável |
| Backend Rails | `backend:3000` | `127.0.0.1:3098` | Bind de código/dependências; tmp/log tmpfs; biblioteca `/docs` gravável |
| PostgreSQL 18 | `postgres:5432` | `127.0.0.1:5499` | `.dockerized-postgres/18/docker` |
| Ollama | `ollama:11434` | Sem porta publicada por padrão | `ollama/` persistente, inferência local, nuvem desabilitada |
| Adapter no host | Troca privada por arquivos | Sem porta HTTP | Processo supervisionado do usuário comum e snapshots privados |

`docker/Dockerfile` fornece targets separados de dependências/desenvolvimento. O backend também lê `/agent` e mounts de código existentes; mapeamentos restritos de auto-documentação/compatibilidade vêm da configuração gerada de mounts. Origens externas comuns usam o adapter, sem novos mounts arbitrários. Não edite metadados gerados de mounts como substituto de diagnóstico.

Backend e frontend são processos independentes que conversam por HTTP, não servidor único. O navegador acessa rotas de mesma origem do Next; o servidor usa `BACKEND_URL=http://backend:3000`. Alterar portas do host não muda portas internas. Bindings loopback e gerenciamento restrito a desenvolvimento não constituem arquitetura de autenticação de produção.

<!-- reading-section: application-development-3 -->
## Fontes locais de dependências (desenvolvimento Docker)

As dependências físicas ficam em `frontend/node_modules` e `backend/vendor/bundle`. Isso permite runtime e inspeção, mas módulos nativos pertencem à plataforma do container. Evite substituí-los por instalações do host. O startup calcula impressão de runtime, manifestos, entrypoint e lock npm instalado, verifica integridade/bindings nativos e reutiliza pacotes correspondentes; caso contrário executa `npm ci --include=dev`. O backend usa bundle travado e verificações no startup. Caches e lockfiles não substituem backups.

O editor pode indexar fontes Linux sem executar seus binários no macOS/Windows. Execute ferramentas dentro do container existente; não instale outro runtime no host para apenas satisfazer diagnósticos do editor. O build isolado evita escrever no cache `.next` do servidor de desenvolvimento em uso.

```sh
# Comandos existentes de leitura/análise; exec exige serviços ativos.
docker compose exec -T frontend npm run typecheck
docker compose exec -T frontend npm run lint
# O build escreve apenas em seu workspace isolado dentro do container.
docker compose exec -T frontend npm run build:check
# Logs são privados; remova dados sensíveis antes de compartilhar.
docker compose logs --tail=100 backend frontend postgres ollama
```

São comandos disponíveis, não afirmação de execução nesta atualização documental. Testes com banco e utilitários de demonstração podem alterar dados; consulte o escopo antes de executar. Ferramentas existentes de navegador estão na imagem de desenvolvimento; verificações comuns não exigem serviço ou dependências adicionais.

<!-- reading-section: application-development-4 -->
## Acesso e preservação do PostgreSQL

Um cliente desktop usa host PostgreSQL `127.0.0.1`, porta publicada `5499` ou override, e usuário/banco do `.env` local. Leia credenciais de forma privada; nunca cole em documentação ou histórico de comandos. Rails conecta internamente a `postgres:5432`. O stack local não configura SSL.

Variáveis de inicialização valem na criação do cluster. Alterar `.env` não troca senha de role existente. Diagnostique divergências e coordene alteração autorizada; nunca exclua `.dockerized-postgres/` para resolver autenticação. Bind mount persistente não é backup nem comprova restauração. Mantenha dumps privados e valide restaurações em banco isolado explicitamente autorizado. O [guia de migração](../operations/database-migration.md) preserva o procedimento separado de mudança de versão principal.

<!-- reading-section: application-development-5 -->
## Operações de catálogo e documentação

Use as ações explícitas de cadastro, MakeDocs/atualização e remoção no frontend. Caminhos como `../example-project` são relativos ao checkout da biblioteca, não ao terminal. Cadastro é idempotente e não chama o modelo. Remoção preserva código/docs originais; recadastro pode restaurar conteúdo elegível arquivado. Não execute geração geral para checar health nem crie diretórios manualmente antes da primeira geração.

Para um projeto cadastrado especificamente autorizado, a CLI padrão é `docker compose exec -T backend make docs DOCS_ARGS='--project example-project'`. Escreve documentação e usa o mesmo comando do frontend. Consulte [MakeDocs](../training/local-documentation-command.md) e [recuperação](../operations/runtime-and-recovery.md) antes do uso. Publicação aceita ainda gera rascunho sujeito a revisão factual e bilíngue.

<!-- reading-section: application-development-6 -->
## Limites de manutenção

Não use `down -v`, prune Docker, resets de banco, exclusão de modelos ou limpeza de estado como desligamento normal. Preserve skills, prompts, evidências de aprendizado e recuperação. Infraestrutura opcional de pesquisa não faz parte do startup e não deve ser ativada em diagnóstico rotineiro. Instruções atuais derivadas do código substituem exemplos antigos; relatórios datados preservam evidência de seus escopos originais.

Fontes: `compose.yaml`, `docker/Dockerfile`, `docker/backend-entrypoint.sh`, `docker/frontend-entrypoint.sh`, `.env.example`, `tools/init_dev_env.py`, `tools/library_runtime.py` e `frontend/package.json`.
