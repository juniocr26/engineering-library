# payment-reconciliation-lab — FAQ técnica

[Índice do projeto](../index.md) · [English](../../en/faq/index.md)

Perguntas técnicas, respostas detalhadas e aprofundamentos estão diretamente nesta página. Afirmações históricas conservam suas datas; as correções atuais abaixo prevalecem. Exemplos em primeira pessoa descrevem artefatos do portfólio, sem atribuir experiência profissional. O [roteiro de estudo](study-guide.md) preserva URLs e âncoras existentes por compatibilidade.

## Revisão do código atual — 2026-10-19

As respostas abaixo foram verificadas em código atual e definições de testes selecionados. Nenhum teste de aplicação ou serviço dos repositórios irmãos foi executado. Veja o [registro de escopo e evidências](../operations/documentation-audit-2026-10-19.md).

## Payment Reconciliation Lab — Guia de Estudo para Entrevista Técnica


[English](../../en/faq/index.md) | [Português brasileiro](index.md)

Consulte [arquitetura atual](../architecture/overview.md), [decisões](../adr/architecture-decisions.md) e [testes](../testing/strategy.md). É laboratório de portfólio em transição de comércio para reconciliação, não plataforma de pagamentos implementada. Respostas seguem o código; justificativas são interpretações e alternativas são estudo, não avaliações históricas. Nenhum comando runtime foi executado nesta auditoria.

## 1. Introdução

#### Pergunta: Qual problema o projeto resolve hoje?

**Resposta modelo:** “O novo problema pretendido é reconciliação de pagamentos, mas a interface ainda é catálogo legado somente leitura. Infraestrutura usa Payment Reconciliation Lab; Spring Boot, Angular, PostgreSQL e migrações existentes permanecem. Matching, reconciliação e Stripe são planejados. Demonstro camadas, preservação de dados e fronteiras HTTP sem afirmar fluxos financeiros concluídos.”

Política de compra, vocabulário CUSTOMER/ADMIN e seed foram removidos. Roadmap da padaria e testes anteriores são históricos. Configuração Stripe reservada no exemplo não cria integração.

## 2. Arquitetura e fluxo

Angular lazy `/products` → `/api/v1/products` relativo → proxy dev → `ProductController` → `CatalogService` transacional de leitura → JPA `ProductRepository` → PostgreSQL → array DTO → UI loading/erro/vazio/ready.

#### Pergunta: É Clean Architecture?

**Resposta modelo:** “Há API, aplicação, domínio e persistência, mas aplicação importa repositório concreto e Product usa JPA. É separação pragmática com framework. DTO protege contrato público; inversão estrita precisaria de outra porta/adaptador.”

AVAILABLE/TEMPORARILY_UNAVAILABLE ficam públicos, ordenados por destaque/nome; descontinuados/arquivados ficam ocultos e preservados. `purchasable` é metadado sem endpoint de compra. Lista inteira sem paginação/cache. HTML no servidor reduziria frontend; JDBC daria SQL explícito. Nenhuma alternativa é apresentada como protótipo histórico.

## 3. Schema e dados preservados

#### Pergunta: Por que manter migrações/tabelas legadas?

**Resposta modelo:** “V1/V2 preservam instalações Flyway. V2 renomeia stores para legacy_stores e cria products sem descartar linhas históricas. Hibernate valida schema. Renomear infraestrutura não renomeia banco/roles inicializados nem migra domínio.”

A [transição com volume externo](../docker/runtime.md) reutiliza volume inspecionado e recusa criar substituto ausente. Nome novo não move dados automaticamente. São instruções, não ações desta revisão. Custo: nomes/tabelas/UI legados até mudança separada. Banco novo simplificaria nomes com necessidade de migração/recuperação explícita.

## 4. Segurança e falhas de startup

#### Pergunta: Como proteger escritas sem login?

**Resposta modelo:** “Libera GETs explícitos e OpenAPI dev, nega demais rotas. Não há login/admin autenticado. CORS define origens/GET; falhas devolvem Problem Details genérico. Logs do servidor ainda contêm diagnóstico de exceção.”

CORS não autentica. Stateless/CSRF desabilitado atende leitura atual; cookies/tokens futuros exigem decisão. Runtime base aplica Flyway; override dev o desabilita e exige schema existente. `DEV_SEED_ENABLED=true` registra runner que falha o startup em vez de inserir fixtures. False evita essa falha, sem implementar fixtures de reconciliação.

Retry Angular faz nova requisição, sem offline/retry automático. Erro de banco vira 500 genérico. Readiness inclui conectividade do banco, não saúde de reconciliação/provedor. Stripe não tem SDK, binding ou webhook; Compose não injeta a chave reservada.

## 5. Testes e evidências

Inventário: 5 métodos ProductApiTest, 2 de seed guard, 5 PostgreSQL opt-in e 4 Angular. MockMvc substitui CatalogService; Angular substitui HTTP. Integração possui banco Testcontainers e verifica migrações, constraints, visibilidade e health/docs. Fakes não provam banco; testes reais exigem Docker e não rodaram aqui. Não há testes atuais de pricing, seed repetível, reconciliação ou Stripe. [Verificação](../testing/verification.md) separa resultados anteriores desta revisão estática.

**Aprofundamento:** Contagem prova cobertura ou aprovação? Não: inventário não é execução, porcentagem nem prova de fluxos ausentes.

## 6. Decisões e aprofundamento

| Decisão | Benefício | Custo / alternativa de estudo |
| --- | --- | --- |
| Catálogo mantido na transição | Base de código preservada | Domínio/UI novos ausentes; substituição exige contratos |
| JPA/Flyway/DTO | Constraints, schema versionado, API explícita | Framework; JDBC/portas ampliariam explicitude |
| Negar escritas/demais rotas | Restringe superfície atual | Sem identidade/escrita autorizada |
| Rejeitar seed removido | Configuração obsoleta falha visivelmente | Corrigir flag; fixtures ausentes |
| Preservar volume/migrações | Evita renomeação destrutiva automática | Nomes/tabelas legados |

Pratique: onde termina a transação? Por que open-in-view=false? O que readiness prova? Por que variável reservada não é feature? Como reconciliação difere de formatar preço de catálogo? Quais registros/moedas/matching definir antes do schema? Como testar assinaturas, idempotência e replay em fixtures isoladas?

## 7. Roteiro ordenado

1. Explicar escopo atual/novo/histórico antes da arquitetura.
2. Seguir controller/service/repository/DTO e estados Angular.
3. Ler V1/V2 e transição do volume; separar identidade do schema e Compose.
4. Ler segurança/seed guard e testes; separar inventário de execução anterior.
5. Estudar entradas, valores/moeda, matching e divergências como requisitos futuros não selecionados.
6. Discutir provedor, assinaturas, idempotência/replay e acesso após definir domínio.

Não marca estudo/conclusão. Consulte [roadmap atual](../architecture/roadmap.md); compromissos da padaria não são herdados automaticamente.

## Aprofundamentos adicionais de entrevista fundamentados no código

Perguntas e respostas originais acima foram preservadas. IDs abaixo identificam a sequência adicional; não renumeram material retido. Níveis orientam estudo, não status implementado. Aprofundamentos incluem respostas para manter a sequência autossuficiente.

### Q001 — Introdutória: Como defender o projeto sem apresentar pagamentos planejados como implementados?

**Resposta:** Implementado: catálogo de produtos somente leitura Spring Boot/Angular/PostgreSQL permanece enquanto infraestrutura passa a Payment Reconciliation Lab. A API lê estados visíveis, ordena e mapeia entidades para DTOs; UI apresenta loading/error/empty/ready. Não há entidades de conciliação, matching, chamadas de provedor, webhooks assinados ou ledger. Stripe reservado não é consumido nem passado pelo Compose. Linguagem de padaria retida é UI legada, não evidência de compromissos antigos de checkout.

Aprofundamento: O que permanece tecnicamente valioso? Fronteiras de camadas, DTO dentro da transação, preservação de migrações, constraints SQL, negação padrão HTTP e testes isolados são mecanismos concretos. Aprofundamento: O que decidir antes de conciliar? Registros fonte de verdade, identidade de matching, moedas/valores, estados de divergência, replay e revisão autorizada. São requisitos hipotéticos não selecionados. Defesa honesta conecta mecanismos a necessidades possíveis sem inventar entrega, produção ou motivações históricas. Nome, chave de ambiente ou roadmap são evidências mais fracas que caminho chamável implementado.

### Q002 — Intermediária: Por que mapear DTOs na transação do serviço com open-in-view desabilitado?

**Resposta:** Implementado: `CatalogService.list` tem transação read-only, chama repositório JPA concreto e constrói ProductSummary antes de retornar. Com open-in-view=false, serialização HTTP não deve depender de acesso posterior à persistência. DTO seleciona representação pública e purchasable derivado em vez de expor toda a entidade/ciclo de vida. Isso facilita evolução da API, mas exige manter mapeamento. Aplicação ainda importa infraestrutura e entidades usam JPA; são camadas pragmáticas, não inversão estrita.

Aprofundamento: readOnly proíbe toda escrita? É hint/intenção do framework, não autorização ou proibição SQL universal. Restrinja privilégios e operações da API separadamente. Aprofundamento: Onde surgiria N+1? Em futuras relações lazy acessadas por entidade durante mapeamento; o catálogo atual não demonstra tal relação/consulta. JDBC tornaria SQL explícito; port de repositório desacoplaria aplicação com custo de tipos/mapeamento. Nada disso foi entregue nesta revisão. Mock do serviço no HTTP não verifica transação ou SQL gerado.

### Q003 — Intermediária: Quais invariantes são SQL e quais são política de resposta?

**Resposta:** Implementado: SQL impõe UUID, slug único formatado, nome/categoria não vazios, preço positivo NUMERIC(12,2) e conjunto availability. Repositório escolhe estados visíveis e ordenação; Product deriva purchasable somente para AVAILABLE. Validade no banco não implica visibilidade pública ou autorização real de compra. V2 conserva stores como legacy_stores sem FK de produto. Defaults inicializam timestamps; migração não tem trigger que garanta updated_at em cada alteração.

Aprofundamento: BigDecimal completa modelo financeiro? Não. Evita representação binária no preço Java, mas conciliação exige moeda, arredondamento, ajustes e semântica de fontes. Angular tipa preço como number; conveniência visual não é aritmética financeira exata no cliente. Aprofundamento: Índice sempre acelera consulta? Não. Não há índice dedicado a filtro/ordenação declarado; seletividade, ordenação e volume determinam benefício e manutenção. EXPLAIN e medições seriam trabalho runtime separado. A documentação não pode alegar planos otimizados ou escala medida.

### Q004 — Desafiadora: Por que CORS e stateless são insuficientes para operações futuras de pagamento?

**Resposta:** Implementado: SecurityConfiguration permite GETs explícitos de produto/health e OpenAPI dev, nega demais requisições e retorna 403 genérico. CORS lista origens, GET e cabeçalhos com credenciais desabilitadas. Isso limita navegador/rotas; não há login, administrador ou identidade de provedor. Configuração stateless define gerenciamento de sessões, não quem faz a requisição. CSRF desabilitado corresponde à leitura atual, não autorização geral de escrita futura autenticada por cookie.

Aprofundamento: Cliente fora do navegador pode ignorar CORS? Não aplica CORS de navegador; autorização no servidor continua necessária. Aprofundamento: Como webhook assinado entraria? Hipoteticamente verificar contrato exato de assinatura contra corpo bruto exigido, limitar replay, guardar identidade do evento e coordenar deduplicação com efeitos financeiros. TLS protege trânsito; assinatura autentica origem; identidade autoriza operações de usuário. São distintos. Não há SDK/webhook Stripe para defender, nem política de timeout/assinatura que possa ser inventada a partir de chave reservada.

### Q005 — Desafiadora: Como renomeação de infraestrutura e rollback preservam dados?

**Resposta:** Implementado: Flyway V1/V2 permanecem e conservam linhas legadas. Hibernate valida; startup base aplica Flyway e override dev desabilita. Projeto Compose renomeado pode escolher outro volume, mas não renomeia roles/bancos PostgreSQL no volume inicializado. Override existing-db aponta volume externo para falhar se ausente em vez de criar armazenamento vazio silencioso. Preserve credenciais e confirme localização dos dados antes de mudanças runtime. Esses procedimentos não foram executados nesta revisão.

Aprofundamento: Podemos editar V1 para o novo nome? Checksums/histórico aplicado precisam permanecer; evolua com novas migrações. Aprofundamento: Rollback da imagem restaura dados? Não. Compatibilidade de schema e backups recuperáveis importam; down/reset pode perder dados. Rollout futuro seguro exige caminho testado e estratégia rollback/correção adiante. A flag de seed aposentada falha startup se habilitada; corrigir configuração é solução, não repetir seed inexistente. Recuperação produtiva e restore permanecem lacunas.

### Q006 — Intermediária: Quais testes e limites de desempenho podem ser defendidos agora?

**Resposta:** Evidência implementada: 5 métodos ProductApiTest substituem CatalogService; 2 cobrem rejeição/default de seed; 5 PostgreSQL opt-in usam Testcontainers isolados; 4 Angular substituem HTTP. Camadas provam coisas diferentes: fakes API cobrem resposta/segurança/erro; PostgreSQL real exercita migrações/constraints/visibilidade; Angular exercita estados UI. Contagens são inventário, não aprovação atual ou percentual. Nenhum teste de aplicação foi executado aqui e não existem testes de conciliação/provedor.

Aprofundamento: Todos os fakes podem passar e startup falhar? Sim: schema ausente com migração desabilitada, credenciais erradas ou seed aposentado habilitado. Aprofundamento: Qual limite real de escala do catálogo? Consulta retorna todas as entidades visíveis e DTOs sem paginação/cache. Memória, ordenação e resposta crescem com dados; não há limiar medido. Paginação hipotética exige desempate estável e UI; cache exige invalidação/frescor. Readiness verifica conectividade do banco, não esses limites ou pagamentos. Teste requisitos na fronteira da qual dependem.

### Q007 — readOnly=true ou purchasable=true implementam autorização de pagamento?

**Resposta:** Não. `CatalogService.list` usa transação somente leitura para consultar AVAILABLE e TEMPORARILY_UNAVAILABLE e mapear DTOs explícitos antes do retorno. `purchasable` deriva de AVAILABLE: é política de apresentação, sem reserva de estoque, aceite de pedido ou permissão de cobrança. Security permite explicitamente GET do catálogo e health, OpenAPI apenas em desenvolvimento e nega o restante. CORS permite origens configuradas/GET sem credenciais, uma política do navegador, sem autorização financeira. Checkout, conciliação, webhooks Stripe, assinaturas do provedor e idempotência durável de pagamentos não estão implementados. Uma mutação futura precisa definir transação, identidade e retries próprios, sem confiar em uma flag da leitura.

### Q008 — O que sobrevive à transição do schema legado e o que os testes cobrem?

**Resposta:** Flyway mantém V1; V2 renomeia stores para `legacy_stores` antes de criar products. Isso preserva linhas históricas sem expor vínculo de loja no DTO. SQL impõe preço positivo, restrições de slug/nome/categoria e valores de disponibilidade; filtragem da resposta pertence à consulta do serviço/repositório. `ProductApiTest` simula o serviço para verificar DTO, segurança e erros HTTP. `ProductPostgresIT` usa Testcontainers para migrações, restrições SQL, visibilidade, ordenação e health em PostgreSQL isolado. Ler os testes não gera nova execução aprovada; um banco Testcontainers novo não demonstra restauração ou migração do volume local existente. Ativar `DEV_SEED_ENABLED` interrompe a partida porque fixtures de conciliação estão ausentes.


## Conciliação com o código — 2026-10-18

`71b8b8f22d38f08e8ab40cb519f8b1a0985b74c6`. Código, entradas API/CLI, limites de persistência/recursos e definições de testes foram revisados estaticamente. Explicações e respostas existentes continuam aplicáveis nos limites registrados. Não foram produzidos resultados de runtime. Consulte o [roteiro autossuficiente de implementação e entrevista](../guides/implementation-study.md).
