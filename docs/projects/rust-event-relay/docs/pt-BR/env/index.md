# ENV — rust-event-relay

[Project index](../index.md)

Referência verificada em 2026-10-18 a partir dos arquivos locais seguros. Valores reais de `.env` não foram usados nesta referência. Exemplos com segredos usam `<secret>`. Não publique senhas, tokens ou URLs com credenciais; preserve credenciais do cluster existente. Variáveis do shell podem sobrepor o arquivo de ambiente do Compose.

## Entradas do Docker Compose

Cada linha descreve o comportamento **na interpolação Compose**, antes da aplicação. `:-` aplica o padrão tanto na ausência como no vazio; `:?` rejeita ambos. Um padrão vazio é intencionalmente permitido nessa camada. A aceitação final pelo consumidor é detalhada abaixo.

[Configuração fonte](../../../../../../../rust-event-relay/compose.yaml)

| Variável | Responsabilidade / consumidor | Obrigatória | Ausente | Vazia | Exemplo seguro / padrão | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| `LOCAL_UID` | Permissões de arquivos / build ou usuário do container | não | padrão | padrão | `1000` | L7 |
| `LOCAL_GID` | Permissões de arquivos / build ou usuário do container | não | padrão | padrão | `1000` | L8 |
| `HOST_FRONTEND_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `5173` | L21 |
| `POSTGRES_HOST_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `5433` | L22 |
| `RABBITMQ_MANAGEMENT_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `15672` | L23 |
| `HTTP_METRICS_ADDR` | http metrics addr | não | padrão | padrão | `127.0.0.1:9100` | L24 |
| `RELAY_METRICS_ADDR` | Limite, tempo ou topologia relay metrics addr / worker Rust | não | padrão | padrão | `127.0.0.1:9101` | L25 |
| `CONSUMER_METRICS_ADDR` | Limite, tempo ou topologia consumer metrics addr / worker Rust | não | padrão | padrão | `127.0.0.1:9102` | L26 |
| `CONSUMER_NAME` | Limite, tempo ou topologia consumer name / worker Rust | não | padrão | padrão | `inventory.stock.v1` | L27 |
| `CONSUMER_PREFETCH` | Limite, tempo ou topologia consumer prefetch / worker Rust | não | padrão | padrão | `1` | L28 |
| `CONSUMER_SOURCE_EXCHANGE` | Limite, tempo ou topologia consumer source exchange / worker Rust | não | padrão | padrão | `relay.events` | L29 |
| `CONSUMER_SOURCE_QUEUE` | Limite, tempo ou topologia consumer source queue / worker Rust | não | padrão | padrão | `relay.local` | L30 |
| `CONSUMER_SOURCE_ROUTING_KEY` | Limite, tempo ou topologia consumer source routing key / worker Rust | não | padrão | padrão | `event` | L31 |
| `CONSUMER_QUARANTINE_EXCHANGE` | Limite, tempo ou topologia consumer quarantine exchange / worker Rust | não | padrão | padrão | `relay.quarantine` | L32 |
| `CONSUMER_QUARANTINE_QUEUE` | Limite, tempo ou topologia consumer quarantine queue / worker Rust | não | padrão | padrão | `relay.quarantine.inventory` | L33 |
| `CONSUMER_QUARANTINE_ROUTING_KEY` | Limite, tempo ou topologia consumer quarantine routing key / worker Rust | não | padrão | padrão | `inventory` | L34 |
| `CONSUMER_OPERATION_MS` | Limite, tempo ou topologia consumer operation ms / worker Rust | não | padrão | padrão | `10000` | L35 |
| `CONSUMER_RECONNECT_MS` | Limite, tempo ou topologia consumer reconnect ms / worker Rust | não | padrão | padrão | `5000` | L36 |
| `CONSUMER_DRAIN_MS` | Limite, tempo ou topologia consumer drain ms / worker Rust | não | padrão | padrão | `15000` | L37 |
| `CONSUMER_SHUTDOWN_MS` | Limite, tempo ou topologia consumer shutdown ms / worker Rust | não | padrão | padrão | `25000` | L38 |
| `CONSUMER_POOL_MAX` | Limite, tempo ou topologia consumer pool max / worker Rust | não | padrão | padrão | `2` | L39 |
| `CONSUMER_POOL_ACQUIRE_MS` | Limite, tempo ou topologia consumer pool acquire ms / worker Rust | não | padrão | padrão | `5000` | L40 |
| `CONSUMER_STATEMENT_MS` | Limite, tempo ou topologia consumer statement ms / worker Rust | não | padrão | padrão | `5000` | L41 |
| `CONSUMER_LOCK_MS` | Limite, tempo ou topologia consumer lock ms / worker Rust | não | padrão | padrão | `3000` | L42 |
| `REPLAY_OPERATORS` | replay operators | não | padrão | padrão | `""` | L43 |
| `RELAY_MAINTENANCE_CANDIDATES` | Limite, tempo ou topologia relay maintenance candidates / worker Rust | não | padrão | padrão | `""` | L44 |
| `RELAY_LEASE_MS` | Limite, tempo ou topologia relay lease ms / worker Rust | não | padrão | padrão | `60000` | L45 |
| `RELAY_IDLE_MS` | Limite, tempo ou topologia relay idle ms / worker Rust | não | padrão | padrão | `1000` | L46 |
| `RELAY_FAILURE_MS` | Limite, tempo ou topologia relay failure ms / worker Rust | não | padrão | padrão | `1000` | L47 |
| `RELAY_RECONNECT_MS` | Limite, tempo ou topologia relay reconnect ms / worker Rust | não | padrão | padrão | `5000` | L48 |
| `RELAY_POOL_MAX` | Limite, tempo ou topologia relay pool max / worker Rust | não | padrão | padrão | `2` | L49 |
| `RELAY_POOL_ACQUIRE_MS` | Limite, tempo ou topologia relay pool acquire ms / worker Rust | não | padrão | padrão | `5000` | L50 |
| `RELAY_STATEMENT_MS` | Limite, tempo ou topologia relay statement ms / worker Rust | não | padrão | padrão | `5000` | L51 |
| `RELAY_LOCK_MS` | Limite, tempo ou topologia relay lock ms / worker Rust | não | padrão | padrão | `3000` | L52 |
| `RELAY_DRAIN_MS` | Limite, tempo ou topologia relay drain ms / worker Rust | não | padrão | padrão | `15000` | L53 |
| `RELAY_SHUTDOWN_MS` | Limite, tempo ou topologia relay shutdown ms / worker Rust | não | padrão | padrão | `25000` | L54 |
| `RABBITMQ_CONNECT_TIMEOUT_MS` | rabbitmq connect timeout ms / broker, Rust AMQP | não | padrão | padrão | `10000` | L55 |
| `RABBITMQ_PUBLISH_TIMEOUT_MS` | rabbitmq publish timeout ms / broker, Rust AMQP | não | padrão | padrão | `10000` | L56 |
| `RABBITMQ_EXCHANGE` | rabbitmq exchange / broker, Rust AMQP | não | padrão | padrão | `relay.events` | L57 |
| `RABBITMQ_QUEUE` | rabbitmq queue / broker, Rust AMQP | não | padrão | padrão | `relay.local` | L58 |
| `RABBITMQ_ROUTING_KEY` | rabbitmq routing key / broker, Rust AMQP | não | padrão | padrão | `event` | L59 |
| `RABBITMQ_DEFAULT_USER` | rabbitmq default user / broker, Rust AMQP | sim | erro Compose | erro Compose | `Set RABBITMQ_DEFAULT_USER in .env` | L62 |
| `RABBITMQ_DEFAULT_PASS` | rabbitmq default pass / broker, Rust AMQP | sim | erro Compose | erro Compose | `<secret>` | L63 |
| `RABBITMQ_DEFAULT_VHOST` | rabbitmq default vhost / broker, Rust AMQP | não | padrão | padrão | `relay` | L64 |
| `POSTGRES_USER` | Conexão e inicialização PostgreSQL / banco e backend | não | padrão | padrão | `change_me` | L67 |
| `POSTGRES_PASSWORD` | Conexão e inicialização PostgreSQL / banco e backend | não | padrão | padrão | `<secret>` | L68 |
| `POSTGRES_DB` | Conexão e inicialização PostgreSQL / banco e backend | não | padrão | padrão | `reliable_event_relay` | L69 |
| `POSTGRES_HOST` | Conexão e inicialização PostgreSQL / banco e backend | não | padrão | padrão | `postgres` | L70 |
| `POSTGRES_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `5432` | L71 |
| `HOST_HTTP_PORT` | Porta de rede / Compose e serviço correspondente | não | padrão | padrão | `8080` | L80 |

## Validação no Rust e relações

Fora do Compose, ausência aplica os padrões definidos no código; vazio não é ausência. `APP_ENV` ausente usa development, vazio falha. `HTTP_ADDR` ausente usa 0.0.0.0:8080, vazio falha como socket. `RUST_LOG` ausente usa info; vazio é preservado para o filtro de tracing (resultado final não verificado). `RELAY_*` e `CONSUMER_*` numéricos usam os padrões da tabela quando ausentes; vazios falham no parse. Todos os limites precisam ser positivos; prefetch ≤32, pool ≤16; drain < shutdown. `RELAY_LEASE_MS` ≤3600000; timings têm limites específicos no código. Nomes de consumidor e topologia são validados; vazio não é uma configuração intencional válida. Source e quarantine exigem exchanges e filas distintas.

`RABBITMQ_DEFAULT_USER` e `RABBITMQ_DEFAULT_PASS` são obrigatórios e não vazios; host ausente usa rabbitmq, porta ausente usa 5672, vhost ausente usa relay. Porta vazia/não numérica/zero falha. Vhost vazio é preservado como segmento de URI, mas acesso depende do broker. Nomes exchange/queue/routing usam os padrões da tabela quando ausentes e passam pela validação de Topology. Timeouts AMQP ausentes usam 10000 ms; vazios falham no parse.

`POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB` são obrigatórios para workers, demo e replay; vazios falham na validação. Host/porta têm padrões postgres/5432 nos workers; demo exige ambos explicitamente. `REPLAY_OPERATORS` vazio/ausente desativa as rotas privilegiadas intencionalmente; preenchido exige credenciais válidas e acesso ao banco. `RELAY_MAINTENANCE_CANDIDATES` vazio/ausente desativa manutenção dirigida; preenchido aceita até 32 entradas únicas UUID:cycle:revision (máximo 4096 bytes). Não publique credenciais de operadores.

`HTTP_METRICS_ADDR`, `RELAY_METRICS_ADDR` e `CONSUMER_METRICS_ADDR` ausentes usam respectivamente 127.0.0.1:9100, 127.0.0.1:9101 e 127.0.0.1:9102 na execução direta; Compose fornece os endereços da tabela. Vazio ou endereço não loopback falha; endereços devem ser distintos entre si e do HTTP. `DEMO_ENABLED` habilita demo somente com a string exata true; vazio/ausente desativa na execução direta, enquanto Compose fixa true. `DEMO_TOKEN` e `DEMO_ORIGIN` são obrigatórios não vazios quando demo está ativa; token é segredo de runtime. O script start-local gera token quando necessário, sem transformá-lo em variável frontend pública. `DEMO_DB_PORT` e `DEMO_MANAGEMENT_PORT` são opcionais para exibição de conexões: ausentes usam 5433/15672; vazios são exibidos sem fallback. Não controlam portas de conexão Rust.

- [backend/src/config.rs](../../../../../../../rust-event-relay/backend/src/config.rs)
- [backend/src/main.rs](../../../../../../../rust-event-relay/backend/src/main.rs)
- [backend/src/infrastructure/rabbitmq.rs](../../../../../../../rust-event-relay/backend/src/infrastructure/rabbitmq.rs)
- [backend/src/infrastructure/rabbitmq/consumer.rs](../../../../../../../rust-event-relay/backend/src/infrastructure/rabbitmq/consumer.rs)
- [backend/src/telemetry/metrics.rs](../../../../../../../rust-event-relay/backend/src/telemetry/metrics.rs)
- [backend/src/infrastructure/demo_http.rs](../../../../../../../rust-event-relay/backend/src/infrastructure/demo_http.rs)
- [scripts/start-local.py](../../../../../../../rust-event-relay/scripts/start-local.py)
