# Relatório da reestruturação Aurora Bakery

> Escopo histórico de comércio. Payment Reconciliation Lab remove a política de compra e o seed de catálogo. Reconciliação e Stripe seguem planejados; infraestrutura atual e transição em [Docker](../docker/runtime.md).


[English](../../en/operations/historical-refactor-report.md) | [Português](historical-refactor-report.md)

Este relatório descreve a reestruturação anterior. Seus resultados de runtime são históricos e não representam novas execuções da revisão documental.

## Alterações entregues

- Substituído diretório de múltiplas lojas, API e página Angular por catálogo de uma padaria. Namespace Java `com.aurorabakery`, classe/nome da aplicação e identidades Angular/package foram renomeados.
- Disponibilidade explícita, ordenação de destaques, preços BRL, descrições, categorias, metadados opcionais de imagem e timestamps. Indisponibilidade temporária permanece visível; descontinuados/arquivados permanecem armazenados e ocultos.
- Preservados deny-by-default, CORS, erros sanitizados, camadas Spring, DTOs, Flyway, readiness do banco, estados Angular e ferramentas/imagens fixadas.
- Política de compra server-side com desconto ADMIN padrão 15%, sem acúmulo de benefícios CUSTOMER e exclusão ADMIN de fidelidade/marketing. Preparação de domínio, não checkout.
- Documentação de escopo, domínio, setup, direção de pagamento/autenticação, decisões e verificação atualizada. ADRs de rede anteriores substituídos. Guias inglês/português mantidos em paralelo; README português aponta para os guias correspondentes.

## Escopo removido

Entidades/repositórios/serviços/controller/fixtures de múltiplas lojas e rota `/stores`; textos de franquia/rede; roadmap de estoque/autorização por loja; sugestões especulativas de broker/cache. Não existiam brokers, SSO, folha, contabilidade, ERP ou aplicações adicionais para desinstalar.

## Banco e autenticação

V1 inalterada; V2 renomeia `stores` para `legacy_stores`, preservando linhas, e cria products com constraints. Produtos novos não têm dono legado. Tabela histórica não exposta; remoção futura exige decisão de retenção separada. Flyway altera schema, Hibernate valida e fixtures idempotentes dev inserem três produtos fictícios fora das migrações. A verificação anterior inicializou volume nomeado novo.

Não havia autenticação no baseline. Mutações/rotas não previstas continuam bloqueadas. Vocabulário CUSTOMER/ADMIN e política estão preparados; identidade persistida, hash, cadastro/login, provisionamento interno ADMIN e escritas por papel estão pendentes. Sem cadastro público ADMIN ou seed administrativo. Comando interno de hashing é estratégia futura junto da identidade; sem segredo ADMIN versionado.

## Frontend e pagamentos

Uma aplicação Angular, rota lazy `/products`, preços e indisponibilidade. Sem aplicação admin adicional. Gestão de produtos, uploads, conta, carrinho e checkout pendentes. Stripe estava ausente e continua não implementado: sem dinheiro real, fake success, segredo ou SDK. Porta de pagamento de teste e webhooks assinados autoritativos são incremento futuro.

## Testes

A verificação anterior registrou 19 testes aprovados: 9 unidade/API backend, 6 integração PostgreSQL e 4 Angular. Cobrem DTOs, vazio/erro, CORS/rotas negadas, migrações, constraints, visibilidade/comprabilidade, preservação de ocultos, fixtures repetíveis, saúde/docs dev, política ADMIN, não acúmulo, consentimento, desconto configurável/arredondamento e estados frontend. Build produção Angular aprovado. Autenticação, fidelidade por pagamento e Stripe ainda não têm fluxos para testar.

## Entrega Docker

Alterados `docker-compose.yml`, Dockerfiles backend/frontend, `.env.example`, `.env` local ignorado, configuração backend e README/docs Docker. Docker ignores revisados/preservados, já excluindo segredos/builds. Não existiam overrides Compose, proxy reverso, Makefile, CI versionado ou scripts Docker.

Retidos `db` (antes `postgres`), `backend`, `frontend`; removidas redes `commerce`, `web`, `db_access`, declaração não usada `postgres_data` e seletor de bind mount legado. Sem nomes explícitos de container. Projeto `aurora-bakery` gera containers `aurora-bakery-db-1`, `aurora-bakery-backend-1`, `aurora-bakery-frontend-1`, rede `aurora-bakery_default`, volume `aurora-bakery_db_data` e imagens `aurora-bakery-backend`/`aurora-bakery-frontend`. PostgreSQL oficial fixado. Hostnames: `db`, `backend`, `frontend`.

Comandos da verificação anterior:

```sh
docker compose config --quiet
docker compose build
docker compose up --build -d --wait --wait-timeout 180
docker compose ps
docker compose logs --tail=60
docker build --target build -t aurora-bakery-backend-tests ./backend
docker compose run --rm --no-deps frontend npm run build
docker compose run --rm --no-deps frontend npm test
```

Backend executou `./mvnw -B -ntp verify -Pintegration` na imagem build-stage, com socket, override host e fonte final somente leitura. SQL e Node fetch conferiram migrações, fixtures, readiness, frontend e igualdade API/proxy. Veja [verificação](../testing/verification.md) e [testes](../testing/strategy.md).

**Registro histórico:** a stack completa iniciou com sucesso naquela verificação. Não é declaração do estado atual dos containers. Três serviços passaram saúde; logs sem erro de aplicação. Avisos normais Angular/toolchain e restart de inicialização PostgreSQL permaneceram. Nenhuma configuração ativa usa identidade antiga; V1 preserva schema histórico. Logs de modernização/artefatos ignorados não são configuração ativa.

## Dívida restante e limites

A base era diretório de leitura, não e-commerce existente. Reestruturação entregue, especificação completa pendente: contas, autenticação, CPF, perfil/telefone/preferências opcionais, ADMIN interno, gestão admin de produtos/imagens/promoções/pedidos, storage, carrinho, lifecycle/snapshots, promoções/fidelidade persistidas, progressão por pagamento, Stripe/webhooks, notificações e UI conta/admin. Política isolada não impõe regras em compras inexistentes.

Construtor Product usa defaults básicos; criação admin futura exige inputs validados e controle de lifecycle/timestamps. BRL é convenção. Tabela histórica permanece. Sem QA visual no navegador, servidor Angular de produção, deploy, volume de imagens ou validação de segurança de upload. Segurança stateless sem CSRF precisa ser revista com autenticação antes de escritas.

Adiados: SSO, WhatsApp, object storage, arquivamento automático configurável e entrega durável em background. Sem necessidade atual de infraestrutura adicional. Multi-tenancy, folha, ERP e contabilidade estão fora do escopo.

**Próximo incremento recomendado:** identidade persistida, cadastro CUSTOMER, hash de senha, comando interno ADMIN e autorização backend; depois mutações administrativas na mesma aplicação Angular.

## Fronteira atual — 2026-10-09

Contagens, regras de comércio, inserção de fixtures e próximo incremento acima descrevem a reestruturação anterior. Código atual removeu pacotes de identidade/preços, testes da política e SQL de seed; habilitar a flag removida falha o startup. Reconciliação/Stripe seguem planejados. Consulte [arquitetura atual](../architecture/overview.md), [roadmap](../architecture/roadmap.md) e [inventário de testes](../testing/strategy.md). Resultados históricos não foram reexecutados nesta auditoria.
