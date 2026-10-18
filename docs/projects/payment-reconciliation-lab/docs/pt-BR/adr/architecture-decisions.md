# Decisões de Arquitetura e Trade-offs

[English](../../en/adr/architecture-decisions.md) | [Português](architecture-decisions.md)

Este documento explica o catálogo legado atual e a transição para reconciliação de pagamentos. Afirmações sobre implementação vêm do código, migrações, configuração e testes. Quando não há intenção registrada, o raciocínio avalia a arquitetura atual, sem presumir motivação histórica. Alternativas são opções de revisão, não prova de uma avaliação anterior.

## Estado da implementação

- **Implementado:** catálogo Spring Boot, schema PostgreSQL, storefront Angular, segurança HTTP que nega por padrão, Docker de desenvolvimento e testes de catálogo/segurança e rejeição do seed removido.
- **Removido:** vocabulário CUSTOMER/ADMIN, política de compra e seed do catálogo. Decisões anteriores de comércio ficam no relatório histórico.
- **Planejado / trabalho futuro:** reconciliação e Stripe de teste; regras de domínio e acesso ainda precisam ser definidas. Veja o [roadmap](../architecture/roadmap.md).

## Decisão: Manter monólito modular durante a transição de domínio

**Contexto.** O código mantém uma vitrine legada durante a transição; nenhum fluxo de reconciliação está implementado.

**Decisão e justificativa.** Uma aplicação Spring Boot mantém catálogo e configuração. Produtos não têm propriedade por tenant. Consultas atuais ficam na mesma fronteira de aplicação/banco; microsserviços adicionariam falhas de rede e coordenação antes de haver fluxos independentes para implantar.

**Alternativas.** SaaS multi-tenant exigiria chaves, autorização e testes de isolamento por tenant. Serviços independentes de catálogo/pedidos exigiriam contratos e consistência entre serviços.

**Trade-offs e consequências.** Deploy/debug ficam mais simples, mas fronteiras de pacotes são convenções, não serviços isolados. Catálogo separa controller, aplicação, entidade e repositório JPA; o serviço importa diretamente o repositório de infraestrutura, sem inversão de dependência estrita. Folha, ERP e contabilidade estão excluídos. Não há broker ou processamento em background.

**Reavaliar quando.** Módulos com responsáveis independentes precisarem de releases separados ou carga medida justificar escala independente. Multi-loja exige mudança explícita de escopo e isolamento de dados.

**Evidências:** [CatalogService](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/catalog/application/CatalogService.java), [schema V2](../../../../../../../payment-reconciliation-lab/backend/src/main/resources/db/migration/V2__single_bakery_catalog.sql), [visão de domínio](../architecture/overview.md).

## Decisão: Java e Spring Boot para fronteiras tipadas

**Contexto.** Dados do catálogo e regras monetárias futuras precisam de contratos explícitos e comportamento testável no servidor.

**Decisão e justificativa.** Records Java expressam DTOs, enums restringem disponibilidade e `BigDecimal` representa preços decimais do catálogo. MVC, injeção de dependências, Security, JPA, Flyway e Actuator integram HTTP, persistência e operação. O benefício atual aparece no controller fino e serviço transacional, sem alegação de desempenho medido ou motivação original da linguagem.

**Alternativas.** Python/FastAPI ou Go poderiam atender o catálogo com outra integração de persistência/segurança. Spring JDBC tornaria SQL mais explícito que JPA.

**Trade-offs e consequências.** Configuração de framework e Java 25 são necessários mesmo para uma API pequena. Anotações ORM acoplam Product à persistência. Fronteiras lógicas existem, mas não são independentes do framework. DTOs explícitos evitam expor entidades e permitem evoluir o contrato público separadamente.

**Reavaliar quando.** Custo do framework dificultar implantação ou consultas justificarem SQL explícito. Primeiro medir a carga real.

**Evidências:** [pom.xml](../../../../../../../payment-reconciliation-lab/backend/pom.xml), [ProductSummary](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/catalog/application/ProductSummary.java).

## Decisão: PostgreSQL com evolução versionada de schema

**Contexto.** O catálogo precisa de slugs únicos, estados válidos e preços decimais positivos. Clientes/pedidos futuros são relacionais, mas suas tabelas ainda não existem.

**Decisão e justificativa.** PostgreSQL impõe checks/unicidade; Flyway controla evolução e Hibernate valida em vez de gerar tabelas. `open-in-view=false` e mapeamento dentro da transação de leitura mantêm persistência fora da serialização HTTP.

**Alternativas.** Banco embarcado reduz infraestrutura mas não exercita constraints PostgreSQL. Document storage transfere mais validação à aplicação. Atualização automática ORM obscurece histórico de migrações.

**Trade-offs e consequências.** Mudanças exigem migrações explícitas. V1 é imutável; V2 renomeia `stores` para `legacy_stores`, sem excluir dados antigos. Bancos novos também mantêm essa tabela não usada. O catálogo carrega todos os produtos visíveis numa lista, sem paginação/cache; resposta e trabalho crescem com o catálogo.

**Reavaliar quando.** Tamanho justificar paginação/análise de índices ou política de retenção aprovada permitir remover legado. Pedidos precisam de regras de transação/snapshot antes da implementação.

**Evidências:** [migrações](../../../../../../../payment-reconciliation-lab/backend/src/main/resources/db/migration), [application.yml](../../../../../../../payment-reconciliation-lab/backend/src/main/resources/application.yml), [testes PostgreSQL](../../../../../../../payment-reconciliation-lab/backend/src/test/java/com/aurorabakery/catalog/ProductPostgresIT.java).

## Decisão: Disponibilidade e histórico em vez de inventário

**Contexto.** O domínio documentado modela produção sob demanda, não contabilidade de ingredientes/estoque.

**Decisão e justificativa.** AVAILABLE e TEMPORARILY_UNAVAILABLE ficam públicos; apenas AVAILABLE é marcado comprável. DISCONTINUED e ARCHIVED são excluídos da consulta pública. Disponibilidade diz se o produto pode ser oferecido sem fingir medir estoque físico. Destaque independe de desconto.

**Alternativas.** Reserva de quantidade exige concorrência, liberação/expiração e regras contra overselling. Exclusão física simplifica armazenamento mas perde registros úteis ao histórico futuro.

**Trade-offs e consequências.** Indisponibilidade temporária permanece compreensível ao cliente. Linhas são preservadas, mas ainda não há API de mutação, agendador de arquivamento ou referências de pedidos. `purchasable` é informação do catálogo, não enforcement de checkout. A UI não oferece compras.

**Reavaliar quando.** Lotes finitos exigirem reservas ou retenção/lifecycle administrativo estiverem definidos.

**Evidências:** [Product](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/catalog/domain/Product.java), [CatalogService](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/catalog/application/CatalogService.java), [ProductPostgresIT](../../../../../../../payment-reconciliation-lab/backend/src/test/java/com/aurorabakery/catalog/ProductPostgresIT.java).

## Decisão: Uma aplicação Angular com estados explícitos

**Contexto.** O cliente precisa distinguir lentidão, catálogo vazio e falha backend.

**Decisão e justificativa.** Catálogo lazy em uma aplicação Angular; `ProductApi` cuida de HTTP e um estado discriminado em signal dirige loading/error/ready. Formatação BRL, roles status/alert, skip link e botão de tentativa transformam estado em feedback. `/api` relativo usa o proxy dev sem expor hostnames Docker ao navegador.

**Alternativas.** HTML no servidor reduz ferramentas cliente num catálogo de leitura. Admin separado permite releases independentes mas duplica ferramentas/contratos.

**Trade-offs e consequências.** Angular fornece componentes tipados/testes ao custo de toolchain. Retry faz nova requisição HTTP; não há cache offline ou retry automático. API retorna metadados de imagem, mas frontend não renderiza imagens. Não há rotas/guards admin nem telas de reconciliação; os planos anteriores de storefront/admin são históricos.

**Reavaliar quando.** Indexação/renderização no servidor for necessária ou admin exigir fronteira independente de release/segurança.

**Evidências:** [UI/testes](../../../../../../../payment-reconciliation-lab/frontend/src/app/catalog), [rotas](../../../../../../../payment-reconciliation-lab/frontend/src/main.ts), [proxy](../../../../../../../payment-reconciliation-lab/frontend/proxy.conf.cjs).

## Decisão: Negar escritas até implementar identidade

**Contexto.** Não há implementação atual de identidade; o antigo vocabulário de papéis foi removido.

**Decisão e justificativa.** Segurança permite GET de catálogo, saúde não sensível e OpenAPI dev; nega o restante. Origens CORS explícitas e Problem Details genéricos limitam exposição acidental enquanto identidade está incompleta.

**Alternativas.** Escritas públicas temporárias expõem privilégios. Provedor de identidade fornece federação mas adiciona infraestrutura antes de existir login.

**Trade-offs e consequências.** Login e acesso ADMIN reais não existem. Stateless e CSRF desabilitado descrevem a API de leitura, não uma estratégia futura definida. Cookies exigem rever CSRF; bearer exige validação/ciclo de tokens. Exceções são ocultadas do cliente mas registradas no servidor.

**Revisão futura.** Defina identidade/autorização para operações de reconciliação antes de habilitar escritas. Provisionamento CUSTOMER/ADMIN anterior é histórico, não contrato atual selecionado.

**Reavaliar quando.** Introduzir qualquer endpoint autenticado/de mutação; escolher sessão/tokens antes de ampliar allowlist.

**Evidências:** [SecurityConfiguration](../../../../../../../payment-reconciliation-lab/backend/src/main/java/com/aurorabakery/configuration/SecurityConfiguration.java), [testes API](../../../../../../../payment-reconciliation-lab/backend/src/test/java/com/aurorabakery/catalog/ProductApiTest.java), [roadmap](../architecture/roadmap.md).

## Decisão histórica: Política de compra removida

Política anterior de descontos/fidelidade e testes removidos em 2026-10-09. Não são preparação funcional atual; seu escopo fica no [relatório histórico](../operations/historical-refactor-report.md). Reconciliação exige regras próprias de moeda/valores/matching; `BigDecimal` no catálogo não implementa reconciliação financeira.

## Decisão: Manter reconciliação e Stripe planejados até definir contratos

**Contexto e fronteira atual.** O catálogo guarda metadado de imagem, sem upload/checkout. Não há schema de reconciliação, adaptador, webhook ou SDK Stripe. `STRIPE_SECRET_KEY` é configuração reservada no exemplo, sem binding ou passagem ao backend pelo Compose.

**Alternativas de estudo.** Integração direta poderia receber eventos, mas matching/idempotência e registros autoritativos ainda precisariam de definição. Uma porta isolaria detalhes do provedor; não está implementada nem selecionada como contrato concluído. Outbox pode servir a entrega confiável futura.

**Trade-offs e consequências.** Adiar evita fluxo fake enganoso, mas deixa o produto novo incompleto. Defina entradas, valores/moeda, autorização, eventos assinados e replay antes de alegar funcionalidade. Uploads/fidelidade de comércio são históricos, não compromissos deste escopo.

**Evidência:** [escopo](../architecture/overview.md), [roadmap](../architecture/roadmap.md), [manifesto](../../../../../../../payment-reconciliation-lab/backend/pom.xml), [Compose](../../../../../../../payment-reconciliation-lab/docker-compose.yml).

## Decisão: Docker para reprodutibilidade e verificação em camadas

**Contexto.** Versões Java/Node/PostgreSQL precisam ser reproduzíveis sem toolchains do host.

**Decisão e justificativa.** Compose separa db/backend/frontend numa bridge, usa loopback, volume PostgreSQL nomeado e startup por saúde. Digests e lockfile reduzem drift. Backend e frontend usam usuários não-root. Frontend é servidor dev, não hosting de produção.

**Alternativas.** Setup no host dispensa containers mas exige ferramentas compatíveis; orquestração/proxy de produção resolve outras necessidades.

**Trade-offs e consequências.** Startup executa migrações automaticamente; a flag do seed removido falha o startup quando habilitada. Iniciar sobre dados existentes ainda pode escrever schema/metadados Flyway; o override dev desabilita migrações e exige banco inicializado. Readiness inclui banco, sem observabilidade completa. Volume persiste após desligamento comum.

**Escolha de testes.** MockMvc com serviço fake valida HTTP/segurança; testes de seed validam rejeição da flag removida; Testcontainers PostgreSQL opt-in valida migrações, constraints, consultas e preservação de linhas ocultas. Fakes HTTP Angular validam estados UI. Fakes não provam banco; integração real custa startup/recursos Docker. Não há testes de checkout/pagamento.

**Reavaliar quando.** Hosting de produção, automação de deploy ou recuperação forem necessários. Manter banco de testes isolado de dados dev.

**Evidências:** [Compose](../../../../../../../payment-reconciliation-lab/docker-compose.yml), [Docker](../docker/runtime.md), [testes backend](../../../../../../../payment-reconciliation-lab/backend/src/test/java/com/aurorabakery), [testes frontend](../../../../../../../payment-reconciliation-lab/frontend/src/app/catalog/product-list.spec.ts).
