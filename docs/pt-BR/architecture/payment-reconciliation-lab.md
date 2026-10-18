# payment-reconciliation-lab: dossiê de implementação

[English](../../en/architecture/payment-reconciliation-lab.md) | [Português brasileiro](payment-reconciliation-lab.md)

Revisão estática: 2026-10-10. Este projeto independente não tem chamadas runtime verificadas a outro repositório do portfólio. Links de evidência sustentam as explicações completas abaixo.

## API e UI de catálogo implementadas

O nome do projeto expressa a direção de conciliação; a interface de negócio atual é o catálogo legado somente leitura. Angular carrega `/products` sob demanda e chama `GET /api/v1/products` relativo. O proxy de desenvolvimento encaminha ao Spring Boot. `ProductController` delega a `CatalogService.list`, que usa transação somente leitura e repositório Spring Data JPA, mapeando entidades para records `ProductSummary` antes de retornar array JSON. Não há endpoint de conciliação, checkout, pedido ou upload.

O resultado inclui AVAILABLE e TEMPORARILY_UNAVAILABLE, ordenado por featured decrescente e nome crescente. DISCONTINUED e ARCHIVED continuam armazenados, mas ocultos. O DTO inclui UUID, slug, nome, descrição, preço BigDecimal, categoria, imagePath opcional, featured, availability e purchasable. Purchasable é true apenas para AVAILABLE, mas não autoriza nem executa compra. A interface Angular usa number para preço e não inclui todos os campos do servidor; o tipo de compilação não valida JSON HTTP arbitrário. Estados loading/error/empty/ready e retry manual tornam resultados visíveis.

Não há paginação, cache ou contrato de contagem total. O repositório materializa todas as entidades correspondentes e depois DTOs; o frontend recebe a lista completa. É simples para catálogo pequeno legado, mas memória/rede/consulta crescem com dados. Paginação exigiria desempate estável, semântica de cursor/página e estado da UI; é hipotética. Exceções inesperadas retornam 500 Problem Details genérico; logs retêm a exceção. Não exponha logs nem derive taxonomia de falhas de pagamento de um erro genérico de catálogo.

## Schema de catálogo e transição de domínio

Flyway V1 cria stores. V2 renomeia para `legacy_stores`, preservando linhas, e cria `products`. IDs são chaves primárias UUID; slug é único com CHECK de formato; nomes/categorias precisam de conteúdo não vazio; preço é NUMERIC(12,2) positivo; availability aceita quatro valores explícitos; timestamps têm default de horário atual. Não há chave estrangeira ligando produtos às lojas retidas nem tabelas de ledger, evento de provedor ou matching. `updated_at` tem default de criação, não trigger que comprove atualização em toda mudança.

JPA usa BigDecimal para preço e Hibernate valida schema em vez de gerá-lo. `open-in-view=false` exige concluir o mapeamento dentro da transação do serviço, sem depender de persistência durante serialização. `readOnly=true` expressa intenção/hint transacional; não substitui privilégios do banco ou autorização. O serviço importa o repositório JPA concreto, portanto há camadas úteis, mas não inversão estrita de dependências.

Índices de slug único e chave primária atendem identidade; migrações não declaram índice específico de filtro/ordenação do catálogo. Não alegue plano otimizado sem EXPLAIN e dados representativos. Escala monetária evita arredondamento binário no catálogo persistido, mas conciliação real também exigiria moeda explícita, regras de arredondamento, fontes financeiras imutáveis, ajustes e identidades de matching. São requisitos futuros não selecionados. Preserve histórico/checksums de migração; renomear serviços Compose ou volume não transforma identidade inicializada de usuário/banco nem dados do domínio.

## Segurança da API de leitura e futuras fronteiras de pagamento

Spring Security permite GETs específicos de produtos/health e OpenAPI no perfil dev; depois nega todas as outras rotas. Não há login persistido, modelo de roles ou administrador autenticado. CORS permite origens configuradas, GET, Accept/Content-Type e nenhuma credencial; clientes fora do navegador não aplicam CORS. Sessões stateless e CSRF desabilitado correspondem à superfície atual somente leitura, mas não garantem futuro projeto seguro de escrita autenticada por cookie. Rotas bloqueadas produzem 403 Problem Details genérico.

A configuração base oculta mensagens/stack traces/erros de binding nas respostas. `ApiExceptionHandler` registra exceções inesperadas e retorna 500 genérico. Logs detalhados exigem acesso restrito/redação: sanitizar o cliente não sanitiza diagnóstico do servidor. Credenciais de banco por ambiente são configuração, não documentação pública incorporada; esta revisão não leu arquivos reais de ambiente. Portas locais do banco têm bind em loopback; é isolamento de desenvolvimento, não perímetro produtivo auditado.

Stripe não está implementado: não há consumidor SDK, binding, verificação de webhook, chamada de provedor ou chave Stripe injetada no Compose. Entrada reservada em template não muda isso. Conciliação futura exigiria revisão autorizada, autenticação de eventos do provedor, política de duplicata/replay e auditoria. Payload assinado, TLS, identidade de aplicação e idempotência protegem fronteiras distintas; nenhuma pode ser atribuída à política atual de CORS/catálogo. São requisitos hipotéticos, não controles entregues.

## Startup, implantação e fronteiras dos testes

O runtime base aplica Flyway e valida schema. O override de desenvolvimento configura `SPRING_FLYWAY_ENABLED=false`, exigindo schema já inicializado; desabilitar migrações não cria tabelas ausentes. `DEV_SEED_ENABLED=true` ativa runner que falha deliberadamente no startup porque fixtures de conciliação não existem. Mantenha false; não há job de seed para repetir. Compose espera health do banco na base; o override desativa health do backend e muda a dependência do frontend para service_started.

Liveness Spring inclui estado da aplicação; readiness inclui estado e conectividade do banco. Nenhum testa matching, credenciais do provedor ou processamento de webhook. Retry Angular repete GET, não operação financeira. MockMvc substitui serviço de catálogo, Angular substitui HTTP e integração PostgreSQL opt-in usa Testcontainers para migrações/constraints/visibilidade. O inventário atual contém 7 métodos backend unit/API, 5 PostgreSQL e 4 casos Angular; não é percentual de cobertura ou resultado aprovado novo. Nenhum teste de aplicação foi executado aqui.

Preserve credenciais inicializadas e volume real durante a renomeação de infraestrutura. O override existing-db reutiliza volume externo explicitamente em vez de criar substituto silencioso. Antes de atualizar de verdade, revise compatibilidade, produza backup recuperável independentemente, prepare verificação de migração e defina rollback do código com schema compatível. Nenhum desses procedimentos runtime foi executado aqui. Reverter imagem ou arquivo Flyway não restaura dados perdidos. Lacunas incluem rollout/TLS produtivo, restore de backup, planos de consulta de catálogo grande e todo o ciclo de conciliação. Categorias de pagamento devem indicar não implementação, não contratos fictícios de webhook ou ledger.

## Evidência de apoio

- [api/catalog-contract](../../../../payment-reconciliation-lab/docs/pt-BR/api/catalog-contract.md)
- [database/catalog-and-transition](../../../../payment-reconciliation-lab/docs/pt-BR/database/catalog-and-transition.md)
- [security/read-api-boundaries](../../../../payment-reconciliation-lab/docs/pt-BR/security/read-api-boundaries.md)
- [operations/deployment-and-evidence](../../../../payment-reconciliation-lab/docs/pt-BR/operations/deployment-and-evidence.md)
- [Interview / Entrevista](../interviews/payment-reconciliation-lab.md)

## Conciliação com o código — 2026-10-18

`71b8b8f22d38f08e8ab40cb519f8b1a0985b74c6`. Código, entradas API/CLI, limites de persistência/recursos e definições de testes foram revisados estaticamente. Explicações e respostas existentes continuam aplicáveis nos limites registrados. Não foram produzidos resultados de runtime. Consulte o [roteiro autossuficiente de implementação e entrevista](../../../../payment-reconciliation-lab/docs/pt-BR/guides/implementation-study.md).
