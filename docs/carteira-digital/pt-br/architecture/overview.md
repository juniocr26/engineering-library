# Arquitetura e limites de integração

## Arquitetura de servidor — 16/11/2026

A implantação de servidor combina Compose base e overlay de servidor, usando MySQL gerenciado externamente. O overlay remove o serviço local `db` e seu mount exclusivo; dependências das aplicações e endpoints dos gerenciadores são ajustados. A aplicação usa `docker/Dockerfile.server`, preservando clientes de runtime e entrypoints. Desenvolvimento mantém banco e persistência locais originais. Remover mount da configuração não migra nem exclui fisicamente dados existentes.

[Estado operacional e limites](../operations/index.md) · [Interface de conexão](../env/index.md)

[Sumário](../index.md)

## Estado verificado e limites públicos — 11/11/2026

Serviço Laravel de operações financeiras com persistência relacional, autenticação de serviço e validação de autorização de domínio. Resultado financeiro, confirmação de provedor, mensageria e entrega de notificações são estados distintos. Idempotência e recuperação pertencem à aplicação; logging TracePaw não constitui liquidação nem comprovante de entrega. Contratos financeiros detalhados permanecem no repositório privado.

Os três consumidores declaram e fixam `parceiro-vivabem/tracepaw-lib 0.2.0`; metadados locais também registram essa versão. Canal `tracepaw`, namespace `TracePaw` e arquivos `tracepaw-YYYY-MM-DD.log` são os contratos atuais. Monolog controla formato/rotação/retenção; o gravador JSONL interno é outro adaptador. Logs históricos permanecem intactos.

Inspeção de fonte e metadados locais não confirma imagem Docker, implantação, montagens ou homologação externa. Esta síntese pública omite endpoints internos, topologia, identificadores e regras privadas; contratos operacionais completos permanecem nos repositórios de origem. Não houve sincronização do catálogo no banco.
