# Referências de código integradas

O leitor compartilhado descobre links de código pela árvore sintática Markdown de todos os projetos documentados. Há suporte a links diretos, links por definição e intervalos de linhas. Cada referência é resolvida no próprio projeto, sem busca por nome de arquivo ou escolha do primeiro resultado. Documentos Markdown abrem dentro do leitor, âncoras preservam a navegação por seção e recursos externos mantêm seu comportamento.

## Identidade e catálogo

O `links/catalog.json` de cada projeto contém um registro autoritativo por caminho completo relativo ao repositório, com projeto, aprovação, SHA-256 e localização do snapshot. A chave canônica serializa `[projeto, caminhoCompleto, revisãoOpcional]`. Intervalos identificam posições dentro desse arquivo e nunca selecionam outro arquivo. Os snapshots por hash ficam em `links/snapshots/`, separados dos documentos bilíngues.

Cada disclosure possui um ID próprio derivado de projeto, documento independente de idioma, identidade canônica, intervalo opcional e ordinal de repetição. Links repetidos, inclusive dentro do mesmo parágrafo, têm expansão independente. Referências correspondentes em inglês e português, na mesma ordem de ocorrência, compartilham IDs estáveis; texto traduzido e número de página não participam da identidade.

Âncoras de código incluem ocorrência, hash do snapshot e linha original. Uma alteração de conteúdo invalida a marcação antiga em vez de abrir silenciosamente outra linha. Reordenar referências repetidas indistinguíveis muda sua associação ordinal; não se infere identidade semântica entre essas edições.

## Aprovação e implantação

Em 18/10/2026, o usuário autorizou snapshots do código referenciado dos seis projetos existentes, excluindo material sensível. Configurações, arquivos de ambiente, dependências, binários, arquivos acima de 512 KB, symlinks que escapam da raiz e padrões detectados de segredos são excluídos. A triagem complementa a autorização; não prova que qualquer conteúdo seja seguro para publicação. Os catálogos exibem apenas caminhos relativos aos repositórios.

A geração é explícita, a partir do diretório frontend:

```sh
SOURCE_WORKSPACE=/caminho/do/portfolio \
APPROVE_REFERENCED_SOURCE=yes \
node --experimental-strip-types tools/build-source-catalog.ts
```

`DOCUMENTATION_ROOT` permite selecionar a coleção. `APPROVED_SOURCE_PROJECTS` delimita os projetos autorizados, separados por vírgula; o padrão são os seis autorizados nessa data. Novos projetos precisam de aprovação antes de incluir código. O gerador descobre documentos automaticamente, valida caminhos reais, lê código como texto, remove snapshots gerados obsoletos e nunca executa arquivos referenciados. Revise o diff antes de publicar.

O leitor usa snapshots aprovados e confere hashes, sem ler repositórios irmãos nem buscar código no GitHub durante a navegação. A montagem existente da documentação no Docker inclui os catálogos e snapshots; Rails e deploy não precisam de montagens dos repositórios ou API genérica de arquivos. Revisões GitHub são aceitas somente quando correspondem à revisão ou fingerprint aprovado. Uma revisão indisponível gera estado explícito, sem substituir pelo código atual.

## Expansão, paginação e navegação

Referências são botões acessíveis por teclado. A expansão insere código após a unidade Markdown que contém o link; itens de listas de fontes são unidades individuais. Links múltiplos em um parágrafo mantêm seus controles inline, seguidos dos blocos expandidos na ordem dos links. Recolher remove todos os segmentos daquela ocorrência e repagina perto do controle original.

Linhas de código estendem o fluxo medido já usado pelas tabelas. O navegador mede cabeçalhos, linhas completas, espaçamentos e capacidades alternadas das páginas. O espaço restante é preenchido antes das continuações. Cada continuação preserva cores de editor, indentação e numeração original, com caminho e intervalo identificados, sem novo disclosure. Linhas longas têm rolagem horizontal; uma linha indivisível maior que a área disponível recebe alternativa acessível com rolagem. Viradas, pergaminho e mecanismo responsivo continuam compartilhados.

Highlight.js fornece gramáticas de leitura para Rust, Go, Python, Ruby, JavaScript, TypeScript, Java, C#, PHP, shell e SQL. Spans multilinha são reabertos nos limites das linhas sem alterar o texto. Gramáticas indisponíveis usam texto escapado.

A busca existente do projeto inclui snapshots aprovados mesmo com disclosures recolhidos. Resultados preservam projeto, caminho completo, documento, ocorrência, revisão/hash, linha e trecho. Selecionar um resultado expande a ocorrência correta, repagina, navega até a linha e aplica o destaque vermelho. Código não aprovado fica fora da busca. Permanece o limite de 80 resultados, sem novo banco ou serviço externo.

As marcações compartilhadas PostgreSQL mantêm a arquitetura existente. Marcar uma continuação salva a primeira linha lógica daquela página. Restaurar a âncora expande a ocorrência correta após a repaginação. Código ausente ou alterado gera aviso de posição indisponível. A expansão permanece durante viradas, redimensionamento e remedição de fontes. O session storage preserva ocorrências independentes ao navegar entre documentos, trocar idiomas e recarregar na mesma aba, quando disponível. Recolher remove explicitamente aquela ocorrência do estado salvo.

## Verificação

O relatório gerado `docs/source-reference-report.json` e os catálogos enumeram ocorrências candidatas, integradas, excluídas e ausentes por projeto. Contagens incluem links repetidos e ambos os idiomas, não apenas arquivos únicos. Documentos sem referências continuam no fluxo comum.

Testes focados cobrem colisões de nomes, isolamento, identidade bilíngue, repetições, intervalos, busca e marcações exatas, revisões, snapshots corrompidos, traversal, symlinks e cores. Testes de navegador exercitam 200 linhas sintéticas em celular, tablet e desktop e referências aprovadas de cada projeto. Execute `npm test`, `npm run typecheck`, `npm run lint`, `npm run build` e `node tests/source-reader.browser.mjs`, configurando os caminhos Playwright do ambiente. As marcações no teste de navegador usam transporte simulado; os testes Rails existentes verificam a persistência separadamente.
