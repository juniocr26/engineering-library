# Payment Reconciliation Lab — Guia de Estudo para Entrevista Técnica

[English](../en/payment-reconciliation-lab.md) | [Português brasileiro](payment-reconciliation-lab.md)

Consulte [arquitetura atual](../../../payment-reconciliation-lab/docs/pt-BR/architecture.md), [decisões](../../../payment-reconciliation-lab/docs/pt-BR/architecture-decisions.md) e [testes](../../../payment-reconciliation-lab/docs/pt-BR/testing.md). É laboratório de portfólio em transição de comércio para reconciliação, não plataforma de pagamentos implementada. Respostas seguem o código; justificativas são interpretações e alternativas são estudo, não avaliações históricas. Nenhum comando runtime foi executado nesta auditoria.

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

A [transição com volume externo](../../../payment-reconciliation-lab/docs/pt-BR/docker.md) reutiliza volume inspecionado e recusa criar substituto ausente. Nome novo não move dados automaticamente. São instruções, não ações desta revisão. Custo: nomes/tabelas/UI legados até mudança separada. Banco novo simplificaria nomes com necessidade de migração/recuperação explícita.

## 4. Segurança e falhas de startup

#### Pergunta: Como proteger escritas sem login?

**Resposta modelo:** “Libera GETs explícitos e OpenAPI dev, nega demais rotas. Não há login/admin autenticado. CORS define origens/GET; falhas devolvem Problem Details genérico. Logs do servidor ainda contêm diagnóstico de exceção.”

CORS não autentica. Stateless/CSRF desabilitado atende leitura atual; cookies/tokens futuros exigem decisão. Runtime base aplica Flyway; override dev o desabilita e exige schema existente. `DEV_SEED_ENABLED=true` registra runner que falha o startup em vez de inserir fixtures. False evita essa falha, sem implementar fixtures de reconciliação.

Retry Angular faz nova requisição, sem offline/retry automático. Erro de banco vira 500 genérico. Readiness inclui conectividade do banco, não saúde de reconciliação/provedor. Stripe não tem SDK, binding ou webhook; Compose não injeta a chave reservada.

## 5. Testes e evidências

Inventário: 5 métodos ProductApiTest, 2 de seed guard, 5 PostgreSQL opt-in e 4 Angular. MockMvc substitui CatalogService; Angular substitui HTTP. Integração possui banco Testcontainers e verifica migrações, constraints, visibilidade e health/docs. Fakes não provam banco; testes reais exigem Docker e não rodaram aqui. Não há testes atuais de pricing, seed repetível, reconciliação ou Stripe. [Verificação](../../../payment-reconciliation-lab/docs/pt-BR/verification.md) separa resultados anteriores desta revisão estática.

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

Não marca estudo/conclusão. Consulte [roadmap atual](../../../payment-reconciliation-lab/docs/pt-BR/roadmap.md); compromissos da padaria não são herdados automaticamente.
