# Arquitetura e limites de integração

## Arquitetura de servidor — 16/11/2026

A implantação de servidor combina Compose base e overlay de servidor, usando MongoDB gerenciado externamente. O overlay remove o serviço local `mongo` e seu mount exclusivo; dependências das aplicações e endpoints dos gerenciadores são ajustados. A aplicação usa `docker/Dockerfile.server`, preservando clientes de runtime e entrypoints. Desenvolvimento mantém banco e persistência locais originais. Remover mount da configuração não migra nem exclui fisicamente dados existentes.

[Estado operacional e limites](../operations/index.md) · [Interface de conexão](../env/index.md)

[Sumário](../index.md)

## Estado verificado e limites públicos — 11/11/2026

Serviço Laravel com MongoDB e integração criptográfica. O escopo verificado mantém referências cifradas e coleções específicas, não um prontuário clínico geral. Autenticação, autorização e proteção de dados são responsabilidades distintas. Falha de decifragem, leitura incompleta, remoção confirmada e resultado incerto precisam permanecer distinguíveis. TracePaw recebe eventos minimizados; dados clínicos e referências de pagamento não devem virar contexto de log.

Os três consumidores declaram e fixam `parceiro-vivabem/tracepaw-lib 0.2.0`; metadados locais também registram essa versão. Canal `tracepaw`, namespace `TracePaw` e arquivos `tracepaw-YYYY-MM-DD.log` são os contratos atuais. Monolog controla formato/rotação/retenção; o gravador JSONL interno é outro adaptador. Logs históricos permanecem intactos.

Inspeção de fonte e metadados locais não confirma imagem Docker, implantação, montagens ou homologação externa. Esta síntese pública omite endpoints internos, topologia, identificadores e regras privadas; contratos operacionais completos permanecem nos repositórios de origem. Não houve sincronização do catálogo no banco.
