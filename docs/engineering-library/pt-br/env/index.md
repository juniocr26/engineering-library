# Ambiente e configuração

[Índice do projeto](../index.md) · [Contrato de configuração](configuration-contract.md)

Revisado em declarações públicas em 26/11/2026. `.env` local, chaves de gerenciamento e ambientes efetivos dos containers não são entradas documentais. Os exemplos não contêm credenciais. Variáveis do shell podem prevalecer na interpolação Compose; nunca publique configuração efetiva com segredos em uma issue.

<!-- reading-section: index-1 -->
## Entradas do Compose e da aplicação

| Variável | Consumidor e default | Comportamento importante |
| --- | --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Inicialização PostgreSQL e conexão Rails | Compose recusa ausência/vazio; inicialização não troca credenciais de cluster existente. |
| `SECRET_KEY_BASE` | Rails | Compose recusa ausência/vazio; mantenha privado. |
| `POSTGRES_PORT`, `BACKEND_PORT`, `FRONTEND_PORT` | Portas loopback do host: `5499`, `3098`, `3099` | Ausência/vazio usam defaults; portas internas continuam 5432/3000/3000. |
| `LOCAL_UID`, `LOCAL_GID` | Usuário backend/frontend: `1000:1000` | Geração de ambiente Linux usa UID/GID atual; ambiente existente é preservado. |
| `WATCHPACK_POLLING` | Watcher de desenvolvimento: `1000` | Compose aplica default em ausência/vazio. |
| `CATALOG_ROOT`, `DOCUMENTATION_ROOT` | Catálogo Rails e leitor Next: `/docs` no Compose | Raiz das coleções, não pasta de um idioma/projeto. |
| `BACKEND_URL` | Servidor Next: `http://backend:3000` | Endereço interno; vazio explícito em execução direta não é fallback utilizável. |
| `POSTGRES_HOST` | Rails: `postgres` | Configuração fixa porta interna 5432; não usa a porta publicada do host. |
| `RAILS_MAX_THREADS` | Pool Rails/Puma | Default do pool é 5; do Puma é 3. Revise ambos antes de ajustar. |
| `DOCS_HOST_REQUIRED` | Backend: `1` no Compose | Exige adapter no startup e em `/up`; não é controle de autenticação de produção. |
| `OLLAMA_NO_CLOUD` | Ollama: `1` no Compose | Política local; não há porta Ollama publicada por padrão. |

Execução direta difere da interpolação Compose. Consultas Ruby/JavaScript frequentemente preservam vazio explícito, enquanto `${NAME:-default}` aplica default em ausência ou vazio. `DATABASE_URL` de produção existe na configuração Rails, mas o stack fornecido executa desenvolvimento; sua presença não estabelece procedimento de produção.

<!-- reading-section: index-2 -->
## Chamador padrão de documentação

Estas entradas pertencem a `Documentation::Command`. Exportar no shell do host não as transfere automaticamente a um container ativo; overrides apenas na CLI não alteram jobs do frontend. São controles existentes, não recomendação para modificar modelo ou configuração aprovada do agente.

| Variável | Default | Faixa ou comportamento |
| --- | --- | --- |
| `DOCS_MODEL` | `llama3.2:3b` | Deve corresponder à identidade aprovada e ao digest Ollama. |
| `DOCS_OLLAMA` | `http://ollama:11434` | Endpoint local existente. |
| `DOCS_CONTEXT` | `skills` | `skills` ou `baseline` explícito; fluxo normal carrega três skills aprovadas. |
| `DOCS_TRANSPORT` | `chat` | `chat` ou `generate`. |
| `DOCS_EVIDENCE_MODE` | `declarations` | `raw`, `declarations` ou `structural`; validação varia por modo. |
| `DOCS_CONTEXT_TOKENS` | `16384` | Inteiro 4096–16384. |
| `DOCS_MODEL_THREADS` | Não definida | Inteiro opcional 1–16. |
| `DOCS_REQUEST_TIMEOUT` | `1800` segundos | Inteiro 60–1800; requisições automáticas por declaração dividem o prazo total. |
| `DOCS_FACT_LIMIT` | `4` | Inteiro 1–5; resumo limitado, não número de capítulos nem cobertura completa. |
| `DOCS_RESEARCH` | `offline` | Pesquisa opcional separada; não implica internet/RAG automático. |
| `DOCS_LIBRARY`, `DOCS_AGENT`, `DOCS_SOURCES`, `DOCS_DESTINATIONS` | `/docs`, `/agent`, `/sources`, `/project-docs` | Defaults do container; seleção também respeita catálogo/configuração e snapshots. |
| `DOCS_HOST_EXCHANGE` | Troca privada `filesystem/host` da instalação principal | Diretório interno compartilhado; não substitua por caminhos públicos arbitrários. |
| `DOCS_HOST_DEFER_DELIVERY` | Não definida | Coordenador define `1` no filho e realiza a entrega ao host. |

O worker tem entradas próprias de aquisição: `DOCS_HOST_FILE_BYTES` (32 MiB, máximo 128 MiB), `DOCS_HOST_SOURCE_BYTES` (512 MiB, máximo 8 GiB), `DOCS_HOST_DOCS_BYTES` (128 MiB, máximo 1 GiB), `DOCS_HOST_ENTRIES` (200.000, máximo 2.000.000) e `DOCS_HOST_FILES` (100.000, máximo 200.000). Todas devem ser positivas. São lidas pelo worker no host, não pelo modelo/navegador. Alterar variável no container não configura esse processo do host.

<!-- reading-section: index-3 -->
## Exemplo seguro de instalação

```sh
# Helper existente cria .env privado somente se ausente e inicia o runtime gerenciado.
python3 -B tools/init_dev_env.py up -d --build --wait --wait-timeout 600
```

O launcher não é ferramenta de rotação de segredos. Não sobrescreva ambiente existente, exclua banco ou substitua modelo/skills para passar no startup. Veja [desenvolvimento](../guides/application-development.md), [MakeDocs](../training/local-documentation-command.md) e [recuperação](../operations/runtime-and-recovery.md).

Fontes: `.env.example`, `compose.yaml`, `backend/config/database.yml`, `backend/config/puma.rb`, `backend/lib/documentation/command.rb`, `backend/lib/documentation/host_filesystem.rb`, `frontend/lib/catalog.ts`, `tools/init_dev_env.py` e `tools/host_filesystem.py`.
