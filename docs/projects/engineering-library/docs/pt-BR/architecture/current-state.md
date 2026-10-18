# Engineering Library: arquitetura atual

> Inspeção histórica do scaffold registrada em 18/10/2026. Para o catálogo atual, leitor Markdown interno, busca e marcações anônimas, consulte [Frontend em formato de livro e catálogo](../guides/book-frontend.md).

## Propósito e limites da evidência

A biblioteca preserva mecanismos, decisões, limites e raciocínio de entrevistas de engenharia em inglês e português brasileiro. Markdown local é a fonte atual do conteúdo. A inspeção estática de 2026-10-18 examinou rotas, classes da aplicação, página e componente de status do frontend, Compose, configuração do banco, dependências, nomes de variáveis do template e definições de testes. Relatos de execução existentes continuam como evidência datada; nenhuma aplicação foi executada nesta catalogação.

## Base implementada

`backend/` contém um scaffold de API Rails 8.1.4 em Ruby 3.4.11, ActiveRecord com adaptador `pg`, Puma e classes-base convencionais de controller/model/job. `config/routes.rb` expõe `/up` pelo health do Rails. Não há endpoint de coleção/capítulo, pipeline de ingestão nem modelo de domínio para registros do catálogo. A configuração PostgreSQL separa bancos de desenvolvimento e teste pelo nome configurado e sufixo `_test`.

`frontend/` é uma aplicação separada Next.js 16.4.2 App Router com React 19.3.1 e TypeScript. A página inicial aponta para a documentação do repositório. Seu componente de servidor consulta `/up` no Rails com timeout de três segundos e apresenta indisponibilidade em caso de falha. Isso indica boot/liveness, não prontidão do banco nem um livro interativo de documentação renderizado.

`compose.yaml` define PostgreSQL, backend e frontend. O tráfego entre contêineres usa nomes de serviço e portas internas; as portas publicadas ficam em loopback. O backend depende de PostgreSQL saudável; o frontend depende de Rails saudável. Código e dependências de desenvolvimento usam bind mounts, incluindo `backend/vendor/bundle` e `node_modules` do frontend. PostgreSQL usa o diretório `.dockerized-postgres` do host, sem volume de dados nomeado do Docker. Sobreviver à recriação é persistência, não backup validado.

## Responsabilidades e trade-offs

As convenções Rails fornecem boot, HTTP, configuração de persistência e estrutura de testes, reduzindo trabalho inicial de infraestrutura. Essa é uma análise de adequação, não evidência de benchmarks entre frameworks pelo autor. Next.js separa apresentação e consultas no servidor da API Rails, ao custo de outra fronteira de build e implantação. O scaffold não faz chamadas de API a partir da origem do navegador e não demonstra necessidade atual de middleware CORS.

Clean Architecture é um princípio para fronteiras futuras: casos de uso devem expressar operações de catálogo sem depender de transporte, adaptadores de arquivos e provedores de inferência quando esses casos existirem. As classes-base Rails não comprovam camadas de domínio/aplicação completas. Abstrações anteriores a um contrato concreto acrescentariam manutenção sem benefício demonstrado.

## Contrato do catálogo

A navegação é Biblioteca → Projeto → Idioma → Índice → Categoria → Documento. `docs/projects/<repository>/` é uma coleção; seu identificador acompanha o diretório do workspace. Caminhos de idiomas e nomes de ADRs permanecem estáveis. Índices de categoria listam páginas como capítulos. Os índices inglês e português oferecem seleção de projetos. Assuntos aparecem nas descrições e capítulos, sem hierarquia separada por tema nem índice de busca.

A entrada Engineering Library explica somente este projeto. Reutiliza os guias canônicos de ambiente e validação, sem conter outra cópia do catálogo do portfólio. As coleções preservam suas referências disponíveis; dossiês removidos dos diretórios de idioma da raiz não foram recriados. Identidade do repositório, revisão, caminhos inspecionados e limites acompanham cada coleção. Cópias são snapshots e não adquirem validação de execução porque seus links passaram numa checagem.

## Segurança e evidência pendente

Somente documentação pública do portfólio pertence aqui. Valores reais de ambiente, chaves, dados do banco e documentação privada de trabalho são excluídos. Links para fontes servem à rastreabilidade, sem autorizar leitura de caminhos restritos. Não existe autenticação nem serviço de isolamento de biblioteca privada no scaffold. A separação pública/privada na ingestão futura requer raízes explícitas, controle de acesso e revisão antes da publicação.

Fontes desta revisão: `backend/config/routes.rb`, `backend/config/database.yml`, `backend/app/`, `backend/test/integration/health_test.rb`, `frontend/app/page.tsx`, `frontend/components/backend-status.tsx`, `frontend/package.json`, `backend/Gemfile`, `compose.yaml` e nomes das variáveis do template. Os links de repositório estão no README do projeto. Este marco não mediu desempenho, prontidão de produção, restauração nem requisitos mínimos de hardware.
