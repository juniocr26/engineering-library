# Arquitetura e limites de integração

## Arquitetura de servidor — 16/11/2026

A implantação de servidor combina Compose base e overlay de servidor, usando MySQL gerenciado externamente. O overlay remove o serviço local `mysql` e seu mount exclusivo; dependências das aplicações e endpoints dos gerenciadores são ajustados. A aplicação usa `docker/Dockerfile.server`, preservando clientes de runtime e entrypoints. Desenvolvimento mantém banco e persistência locais originais. Remover mount da configuração não migra nem exclui fisicamente dados existentes.

[Estado operacional e limites](../operations/index.md) · [Interface de conexão](../env/index.md)

[Sumário](../index.md)

## Estado verificado e limites públicos — 11/11/2026

Portal Laravel com Cockpit técnico separado do painel de auditoria. A navegação atual tem Visão Geral, Infraestrutura, RabbitMQ, Bancos de dados, Reconciliações e TracePaw; não há destinos separados de Execuções e Integrações. Observabilidade consulta arquivos retidos sob demanda, com autorização por projeto, filtros, paginação limitada e indicadores de consulta incompleta. O gerador SQL MySQL oferece INSERT/UPDATE/SELECT/DELETE de linhas selecionadas, incluindo chaves compostas verificadas; produz texto para revisão/cópia, sem execução automática.

Os três consumidores declaram e fixam `parceiro-vivabem/tracepaw-lib 0.2.0`; metadados locais também registram essa versão. Canal `tracepaw`, namespace `TracePaw` e arquivos `tracepaw-YYYY-MM-DD.log` são os contratos atuais. Monolog controla formato/rotação/retenção; o gravador JSONL interno é outro adaptador. Logs históricos permanecem intactos.

Inspeção de fonte e metadados locais não confirma imagem Docker, implantação, montagens ou homologação externa. Esta síntese pública omite endpoints internos, topologia, identificadores e regras privadas; contratos operacionais completos permanecem nos repositórios de origem. Não houve sincronização do catálogo no banco.
