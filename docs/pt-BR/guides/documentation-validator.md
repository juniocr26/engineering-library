# Validador documental somente leitura

Execute do workspace pai (Python 3.10+; apenas biblioteca padrão):

```sh
python3 -B engineering-library/tools/check_docs.py --workspace .
python3 -B -m unittest discover -s engineering-library/tools -p 'test_check_docs.py' -v
```

Na biblioteca, workspace padrão é o pai derivado do script; use `python3 -B tools/check_docs.py`. Saída JSON estruturada em stdout contém inventário, findings com severity/code/path/detail e limites. Exit 1 indica erros; 0 indica ausência deles; warnings/info continuam visíveis. Chamador pode redirecionar stdout ao relatório. O validador não grava, acessa rede, executa aplicação ou lê credenciais/dados. Testes isolados criam árvores documentais sintéticas temporárias e executam apenas o validador.

`--config PATH` seleciona metadados seguros `tools/*.json` no workspace; padrão `tools/docs_manifest.json`. Manifest define `repositories`, `required_documents`, `exceptions` opcionais por caminho relativo/repositório com `exception_reasons` e `additional_categories` justificadas. Nomes de repositório são diretórios imediatos seguros. Descoberta usa diretórios imediatos com marcador Git; repositório inesperado gera erro para impedir omissão silenciosa. `inventory_before` guarda lista original informativa, não exige caminhos obsoletos. Python não fixa nomes de workspace privado; manifest atual configura explicitamente este portfólio.

A varredura lê apenas READMEs e `.md` sob docs/en/docs/pt-BR. Verifica categorias (inclusive diretórios desconhecidos/vazios), índices/checklists, contrapartes, destinos/anchors locais, alcance, seções numeradas antigas de entrevista, sequências adicionais Q001, respostas/aprofundamentos explícitos, nomes locais obsoletos e marcadores de chave privada. Paridade de perguntas compara IDs, não tradução. Respostas anteriores foram preservadas/revisadas separadamente; estrutura não avalia profundidade ou verdade técnica.

Antes de normalizar link, componentes lexicais são verificados contra diretórios/arquivos restritos. Links para ambientes reais, chaves, dados, dependências, Git ou fora do workspace são classificados sem ler destino. lstat rejeita componentes simbólicos e diretórios simbólicos não são percorridos. Links seguros não documentais recebem apenas existência/tipo, não leitura. Anchors são comparados apenas com Markdown mantido já carregado. Arquivos ilegíveis/UTF-8 inválido viram findings. Relatório não reproduz corpo de chave detectada. Há janela TOCTOU entre lstat/leitura em filesystem malicioso; é verificador local cooperativo, não sandbox livre de corrida.

Parser cobre subconjunto: headings ATX/Setext, slugs Unicode comuns/sufixos duplicados, links/imagens inline simples, referências completas/colapsadas, destinos de atalhos definidos, URLs locais percent-decoded, anchors HTML id/name e exclusão de código em fences/inline. Não garante brackets/parênteses complexos, destinos multilinha, HTML/MDX completo, todas as regras de escape/entidades ou equivalência total ao GitHub. Atalho de referência indefinido pode não ser reconhecido. Revise sintaxe complexa manualmente. Links externos não são buscados nem declarados verificados. JSON conserva esses limites.

[Relatório de conclusão](../operations/workspace-completion.md) registra resultado final real. [Testes isolados](../../../tools/test_check_docs.py) cobrem fixtures válidas/somente leitura, repositório/contraparte ausente, links/anchors/referências, Unicode/encoding, alcance/categorias, percurso restrito, symlinks, metadados de código, entradas ilegíveis, entrevistas, exceções, chave/nome, fences, categorias vazias/desconhecidas, lacunas na numeração antiga, workspace simbólico e exit/JSON da CLI.

## Atualização da ferramenta em 2026-10-18

`summary` no JSON contém contagens e códigos dos achados. `external_links` declara ocorrências como `not checked`; nenhuma URL é buscada. `scope_exclusions` associa padrões fora do escopo a razões não vazias; nunca suprime Git inesperado. Marcadores Git simbólicos não são seguidos. Links `.local-backups` são bloqueados antes da leitura. Config deve ser tools/*.json seguro e regular; FIFO é rejeitado sem abrir. Quatro testes novos cobrem esses casos, incluindo guarda de leitura, repositório inesperado e timeout de entrada não regular. Permanecem os limites de parsing/revisão semântica anteriores.
