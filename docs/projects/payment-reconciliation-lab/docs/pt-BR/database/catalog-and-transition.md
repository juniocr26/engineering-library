# Schema de catálogo e transição de domínio

[English](../../en/database/catalog-and-transition.md) | [Português brasileiro](catalog-and-transition.md)

Revisão estática do código: 2026-10-10. Fatos implementados, teoria geral e mudanças hipotéticas são separados abaixo. Comandos runtime não foram executados.

Flyway V1 cria stores. V2 renomeia para `legacy_stores`, preservando linhas, e cria `products`. IDs são chaves primárias UUID; slug é único com CHECK de formato; nomes/categorias precisam de conteúdo não vazio; preço é NUMERIC(12,2) positivo; availability aceita quatro valores explícitos; timestamps têm default de horário atual. Não há chave estrangeira ligando produtos às lojas retidas nem tabelas de ledger, evento de provedor ou matching. `updated_at` tem default de criação, não trigger que comprove atualização em toda mudança.

JPA usa BigDecimal para preço e Hibernate valida schema em vez de gerá-lo. `open-in-view=false` exige concluir o mapeamento dentro da transação do serviço, sem depender de persistência durante serialização. `readOnly=true` expressa intenção/hint transacional; não substitui privilégios do banco ou autorização. O serviço importa o repositório JPA concreto, portanto há camadas úteis, mas não inversão estrita de dependências.

Índices de slug único e chave primária atendem identidade; migrações não declaram índice específico de filtro/ordenação do catálogo. Não alegue plano otimizado sem EXPLAIN e dados representativos. Escala monetária evita arredondamento binário no catálogo persistido, mas conciliação real também exigiria moeda explícita, regras de arredondamento, fontes financeiras imutáveis, ajustes e identidades de matching. São requisitos futuros não selecionados. Preserve histórico/checksums de migração; renomear serviços Compose ou volume não transforma identidade inicializada de usuário/banco nem dados do domínio.
