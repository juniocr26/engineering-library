# Entrevista da Engineering Library

Comparações conceituais não implicam integração runtime. Fatos implementados, teoria e alternativas hipotéticas são separados explicitamente.

### Q001 — Introdutória: Qual a responsabilidade da Engineering Library?

**Resposta:** Implementado: repositório é coleção Markdown bilíngue e ferramentas documentais somente leitura. Leitor deve compreender mecanismos e ensaiar respostas substanciais sem abrir fontes; links permitem verificar/aprofundar. Não tem API runtime, banco, pagamentos ou serviço implantado. Arquitetura é navegação: READMEs levam a catálogos por idioma, categorias contêm dossiês/entrevistas/fluxos e validador examina documentação/metadados permitidos.

Aprofundamento: Por que reter respostas antigas em vez de substituí-las por dossiês? Respostas ensinam raciocínio/falhas, dossiês explicam mecanismos; ambos são requisitos. IDs Q adicionais conservam numeração e alinhamento. Aprofundamento: Qual custo da autossuficiência? Fatos repetem entre projetos/biblioteca; revisão e lacunas explícitas precisam manter consistência. Links sozinhos reduziriam duplicação, mas descumpririam entrevistas. Precisão semântica continua revisão humana; links corretos não provam respostas verdadeiras.

### Q002 — Desafiadora: Como o validador impede que links virem leituras inseguras?

**Resposta:** Implementado: check_docs.py percorre READMEs e docs/en/docs/pt-BR, além de JSON explícito seguro em tools. Classifica componentes lexicais antes de normalizar, rejeita fora do workspace/caminhos restritos e usa lstat para rejeitar links simbólicos. Links de código recebem existência, não leitura de conteúdo; anchors Markdown são verificados apenas em documentos mantidos carregados. Ambiente, chaves, storage, dependências e Git não são lidos. Links bloqueados viram warnings; externos não são buscados. Nenhuma aplicação executa.

Aprofundamento: É sandbox livre de corrida? Não. lstat seguido de leitura tem janela TOCTOU em filesystem maliciosamente alterado; assume workspace cooperativo. Percurso por descritores no-follow fortaleceria com custo de portabilidade. Aprofundamento: Parser equivale ao GitHub completo? Não. Trata subconjunto documentado de links/referências, headings, fences e IDs. Sintaxe aninhada complexa exige revisão. Erros retornam não zero, JSON registra findings e fixtures isoladas exercitam falhas. Validador expõe lacunas, não decide verdade técnica ou qualidade de tradução.

### Q003 — Intermediária: Como a coleção representa e valida navegação sem implantar aplicação?

**Resposta:** Implementado: caminhos Markdown são contrato público de navegação; validador carrega páginas permitidas em dicionário, extrai anchors/destinos e constrói conjuntos de adjacência. Busca em largura a partir de cada índice verifica alcance dentro do próprio repositório/idioma; link externo não substitui catálogo próprio. JSON separa erros, warnings e limites informativos. Ferramenta Python padrão não tem lifecycle de serviço/banco; distribuição é arquivos/Python, publicação fora do escopo. Parser regex é mantível, mas incompleto para Markdown complexo.

Aprofundamento: Qual custo? Leitura/parser crescem com bytes; percurso com vértices/arestas, mais metadados filesystem; sem medições. Aprofundamento: Estrutura detecta fatos conflitantes/traduções ruins? Não. Detecta IDs/contrapartes/respostas ausentes, mas revisão do código julga significado. Testes isolados comprovam contratos selecionados, não operação livre de corrida sob mutação hostil ou alcance externo.
