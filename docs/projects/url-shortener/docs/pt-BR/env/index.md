# ENV — url-shortener

[Project index](../index.md)

Referência verificada em 2026-10-18 a partir dos arquivos locais seguros. Valores reais de `.env` não foram usados nesta referência. Exemplos com segredos usam `<secret>`. Não publique senhas, tokens ou URLs com credenciais; preserve credenciais do cluster existente. Variáveis do shell podem sobrepor o arquivo de ambiente do Compose.

## Entradas do Docker Compose

Cada linha descreve o comportamento **na interpolação Compose**, antes da aplicação. `:-` aplica o padrão tanto na ausência como no vazio; `:?` rejeita ambos. Um padrão vazio é intencionalmente permitido nessa camada. A aceitação final pelo consumidor é detalhada abaixo.

[Configuração fonte](../../../../../../../url-shortener/compose.yaml)

| Variável | Responsabilidade / consumidor | Obrigatória | Ausente | Vazia | Exemplo seguro / padrão | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| `CASSANDRA_CLUSTER_NAME` | cassandra cluster name / Cassandra, FastAPI | não | padrão | padrão | `url_shortener_cluster` | L15 |
| `CASSANDRA_DATACENTER` | cassandra datacenter / Cassandra, FastAPI | não | padrão | padrão | `datacenter1` | L16 |
| `CASSANDRA_RACK` | cassandra rack / Cassandra, FastAPI | não | padrão | padrão | `rack1` | L17 |
| `CASSANDRA_ENDPOINT_SNITCH` | cassandra endpoint snitch / Cassandra, FastAPI | não | padrão | padrão | `GossipingPropertyFileSnitch` | L18 |
| `CASSANDRA_SEEDS` | cassandra seeds / Cassandra, FastAPI | não | padrão | padrão | `cassandra-1` | L19 |
| `CASSANDRA_USERNAME` | cassandra username / Cassandra, FastAPI | sim | erro Compose | erro Compose | `Set CASSANDRA_USERNAME in .env` | L20 |
| `CASSANDRA_PASSWORD` | cassandra password / Cassandra, FastAPI | sim | erro Compose | erro Compose | `<secret>` | L21 |
| `CASSANDRA_MAX_HEAP_SIZE` | cassandra max heap size / Cassandra, FastAPI | não | padrão | padrão | `512M` | L22 |
| `CASSANDRA_HEAP_NEWSIZE` | cassandra heap newsize / Cassandra, FastAPI | não | padrão | padrão | `128M` | L23 |
| `PYTHON_VERSION` | python version | não | padrão | padrão | `3.14` | L40 |
| `UV_VERSION` | uv version | não | padrão | padrão | `0.8.17` | L41 |
| `APP_UID` | Permissões de arquivos / build ou usuário do container | não | padrão | padrão | `1000` | L42 |
| `APP_GID` | Permissões de arquivos / build ou usuário do container | não | padrão | padrão | `1000` | L43 |
| `APP_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `8000` | L58 |
| `APP_ENV` | app env | não | padrão | padrão | `development` | L63 |
| `APP_HOST` | app host | não | padrão | padrão | `0.0.0.0` | L64 |
| `REDIS_HOST` | redis host / Redis, FastAPI | não | padrão | padrão | `redis` | L66 |
| `REDIS_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `6379` | L67 |
| `REDIS_DB` | redis db / Redis, FastAPI | não | padrão | padrão | `0` | L68 |
| `REDIS_PASSWORD` | redis password / Redis, FastAPI | não | padrão | padrão | `""` | L69 |
| `CASSANDRA_CONTACT_POINTS` | cassandra contact points / Cassandra, FastAPI | não | padrão | padrão | `cassandra-1,cassandra-2,cassandra-3` | L70 |
| `CASSANDRA_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `9042` | L71 |
| `CASSANDRA_KEYSPACE` | cassandra keyspace / Cassandra, FastAPI | não | padrão | padrão | `url_shortener` | L72 |
| `SHORT_URL_BASE` | short url base | não | padrão | padrão | `http://localhost:8000` | L76 |
| `URL_ID_START` | url id start | não | padrão | padrão | `14776336` | L77 |
| `BASE62_ALPHABET` | base62 alphabet | não | padrão | padrão | `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz` | L78 |
| `OBFUSCATING_KEY` | obfuscating key | não | padrão | padrão | `""` | L79 |
| `BASIC_AUTH_USERNAME` | basic auth username | não | padrão | padrão | `""` | L80 |
| `BASIC_AUTH_PASSWORD` | basic auth password | não | padrão | padrão | `""` | L81 |

## Configuração Python em execução direta

As entradas são opcionais no Python, com padrões abaixo; Compose exige credenciais Cassandra não vazias para o bootstrap.

| Variável | Ausente / padrão | Vazia |
| --- | --- | --- |
| `APP_ENV` | `"development"` | preservado, sem fallback; validade depende do consumidor |
| `APP_HOST` | `"0.0.0.0"` | preservado, sem fallback; validade depende do consumidor |
| `APP_PORT` | `8000` | ValueError: inicialização falha |
| `BASIC_AUTH_USERNAME` | `None` | None: desativa opção; intencional |
| `BASIC_AUTH_PASSWORD` | `None` | None: desativa opção; intencional |
| `REDIS_HOST` | `"redis"` | preservado, sem fallback; validade depende do consumidor |
| `REDIS_PORT` | `6379` | ValueError: inicialização falha |
| `REDIS_DB` | `0` | ValueError: inicialização falha |
| `REDIS_PASSWORD` | `None` | None: desativa opção; intencional |
| `CASSANDRA_CONTACT_POINTS` | `"cassandra-1,cassandra-2,cassandra-3"` | ValueError: exige ao menos um item |
| `CASSANDRA_PORT` | `9042` | ValueError: inicialização falha |
| `CASSANDRA_KEYSPACE` | `"url_shortener"` | preservado, sem fallback; validade depende do consumidor |
| `CASSANDRA_USERNAME` | `None` | None: desativa opção; intencional |
| `CASSANDRA_PASSWORD` | `None` | None: desativa opção; intencional |
| `CASSANDRA_DATACENTER` | `"datacenter1"` | preservado, sem fallback; validade depende do consumidor |
| `SHORT_URL_BASE` | `"http://localhost:8000"` | preservado, sem fallback; validade depende do consumidor |
| `URL_ID_START` | `62**4` | ValueError: inicialização falha |
| `BASE62_ALPHABET` | `"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"` | preservado, sem fallback; validade depende do consumidor |
| `OBFUSCATING_KEY` | `None` | None: desativa opção; intencional |

`BASIC_AUTH_USERNAME` e `BASIC_AUTH_PASSWORD` só habilitam autenticação se ambos forem não vazios. Cassandra também requer o par completo para autenticação. `REDIS_PASSWORD` vazio/ausente desativa a senha; Compose configura Redis de forma correspondente. `OBFUSCATING_KEY` vazio/ausente desativa ofuscação, não é criptografia. `SHORT_URL_BASE` precisa corresponder à URL pública; `BASE62_ALPHABET` e `URL_ID_START` precisam preservar compatibilidade dos IDs existentes. Credenciais e tokens nunca devem ser publicados. Variáveis de heap, snitch, rack e seeds configuram a imagem Cassandra: padrões Compose verificados, tratamento interno adicional da imagem não foi auditado.

[Python settings](../../../../../../../url-shortener/app/core/config.py)
