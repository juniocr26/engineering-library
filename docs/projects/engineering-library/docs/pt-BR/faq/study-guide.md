# Entrevista da Engineering Library

> A [FAQ técnica completa](index.md) é a entrada principal para perguntas e respostas. Este roteiro mantém títulos e links históricos por compatibilidade.

> Revisão do código — 2026-10-19: a árvore atual implementa API de catálogo Rails, registros de catálogo e favoritos anônimos no PostgreSQL, além do leitor Markdown interno em Next.js. A descrição anterior de coleção sem aplicação/scaffold foi superada. Não há agente de IA implementado. Consulte a [arquitetura atual](../architecture/current-state.md).

Comparações conceituais não implicam integração runtime. Fatos implementados, teoria e alternativas hipotéticas são separados explicitamente.

### Q001 — Introdutória: Qual a responsabilidade da Engineering Library?

**Resposta:** Implementado: o repositório mantém documentação bilíngue e a apresenta em um leitor Next.js apoiado por uma API de catálogo Rails. PostgreSQL persiste identidade/visibilidade dos projetos indexados e localizações de favoritos anônimos; Markdown continua como fonte dos documentos e bios localizadas. `Catalog::Sync` valida as duas bios antes de serializar escritas em transação com advisory lock PostgreSQL. A API pagina projetos ativos; Next lê Markdown delimitado da coleção no servidor. Existe aplicação local implementada, sem alegação de implantação em produção, pagamentos ou ingestão por IA.

Aprofundamento: Por que reter respostas antigas em vez de substituí-las por dossiês? Respostas ensinam raciocínio/falhas, dossiês explicam mecanismos; ambos são requisitos. IDs Q adicionais conservam numeração e alinhamento. Aprofundamento: Qual custo da autossuficiência? Fatos repetem entre projetos/biblioteca; revisão e lacunas explícitas precisam manter consistência. Links sozinhos reduziriam duplicação, mas descumpririam entrevistas. Precisão semântica continua revisão humana; links corretos não provam respostas verdadeiras.

### Q002 — Desafiadora: Como o validador impede que links virem leituras inseguras?

**Resposta:** Implementado: `docs/validation/check_catalog.py` valida a árvore atual organizada por projeto e reutiliza parser e verificações de caminhos de `tools/check_docs.py`. O validador antigo também suporta o layout anterior de idiomas na raiz; não é o comando principal do catálogo. A classificação rejeita componentes restritos, externos ao workspace e links simbólicos antes da leitura documental. Links de código recebem verificações de existência/metadados, sem execução. O catálogo acrescenta paridade de caminhos/IDs Q, títulos históricos, proveniência e alcance a partir dos índices da biblioteca e dos projetos. Links inseguros são erros no wrapper atual; URLs externas não são buscadas.

Aprofundamento: É sandbox livre de corrida? Não. lstat seguido de leitura tem janela TOCTOU em filesystem maliciosamente alterado; assume workspace cooperativo. Percurso por descritores no-follow fortaleceria com custo de portabilidade. Aprofundamento: Parser equivale ao GitHub completo? Não. Trata subconjunto documentado de links/referências, headings, fences e IDs. Sintaxe aninhada complexa exige revisão. Erros retornam não zero, JSON registra findings e fixtures isoladas exercitam falhas. Validador expõe lacunas, não decide verdade técnica ou qualidade de tradução.

### Q003 — Intermediária: Como a coleção representa e valida navegação sem implantar aplicação?

**Resposta:** Implementado: caminhos Markdown estáveis formam o contrato de navegação. O validador atual carrega Markdown permitido, extrai âncoras/destinos e percorre o grafo desde a biblioteca e cada índice de projeto/idioma. Essas verificações Python dispensam Rails, PostgreSQL e Next. O leitor em execução tem comportamento separado: `documentationEntries` unifica IDs relativos entre idiomas, omite índices apenas navegacionais, mantém índices substanciais e constrói entradas por categoria/documento. Assim, índices FAQ com respostas tornam-se capítulos automaticamente. Validação estrutural não demonstra paginação no navegador nem disponibilidade da API.

Aprofundamento: Qual custo? Leitura/parser crescem com bytes; percurso com vértices/arestas, mais metadados filesystem; sem medições. Aprofundamento: Estrutura detecta fatos conflitantes/traduções ruins? Não. Detecta IDs/contrapartes/respostas ausentes, mas revisão do código julga significado. Testes isolados comprovam contratos selecionados, não operação livre de corrida sob mutação hostil ou alcance externo.
