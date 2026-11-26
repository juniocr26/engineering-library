# Arquitetura e limites de integração

## Arquitetura de servidor — 16/11/2026

A implantação de servidor combina Compose base e overlay de servidor, usando Redis gerenciado externamente. O overlay remove o serviço local `redis` e seu mount exclusivo; dependências das aplicações e endpoints dos gerenciadores são ajustados. A aplicação usa `docker/Dockerfile.server`, preservando clientes de runtime e entrypoints. Desenvolvimento mantém banco e persistência locais originais. Remover mount da configuração não migra nem exclui fisicamente dados existentes.

[Estado operacional e limites](../operations/index.md) · [Interface de conexão](../env/index.md)

[Sumário](../index.md)

## Estado verificado e limites públicos — 11/11/2026

Serviço Node.js ES modules, Socket.IO, Redis e jose. Conexões de publicação/assinatura Redis e prontidão são independentes da autorização de publicadores e destinatários. RabbitMQ atende consumidores das aplicações, sem instalar biblioteca PHP no Hub. Redis Pub/Sub e saída ao vivo não fornecem replay durável. Logs Node, mensagens RabbitMQ, eventos entregues e eventos TracePaw gerados pelos consumidores Laravel são evidências distintas.

Inspeção de fonte e metadados locais não confirma imagem Docker, implantação, montagens ou homologação externa. Esta síntese pública omite endpoints internos, topologia, identificadores e regras privadas; contratos operacionais completos permanecem nos repositórios de origem. Não houve sincronização do catálogo no banco.
