# Validação documental, testes da aplicação e evidências

[Sumário](../index.md) | [English](../../en/testing/documentation.md)

Revisado/executado em 2026-11-10. Público: mantenedores e revisores. Sucesso estrutural não comprova completude técnica, produção ou aprovação semântica da tradução.

<!-- reading-section: static -->
## Suíte estática existente de fixtures

Na raiz:

```sh
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
```

Saída real 0: **28 testes aprovados**. tools/test_catalog.py e tools/test_check_docs.py usam árvores temporárias próprias e fixtures sintéticas para catálogo, variáveis/perguntas bilíngues, arquivos/âncoras, caminhos inseguros, symlinks, encoding, CLI e comportamento somente leitura. Testa validador, sem comprovar corpus real. Não altera banco da aplicação nem sincroniza catálogo.

<!-- reading-section: application -->
## Suítes da aplicação inspecionadas, sem execução

Backend inclui test/integration de catálogo, bookmarks, highlights, notes e annotations, testes de migração e Ruby offline. offline/catalog_files_offline.rb inspecionado cobre contenção, bios, traversal/symlinks, ausência/binário; offline/note_identity_offline.rb verifica identidade lógica independente do contexto. Definições não constituem aprovação Ruby nova.

package.json frontend define Node --experimental-strip-types --test tests/*.test.ts, typecheck/lint/build e scripts browser separados. Comandos de browser/demos podem criar dados ou exigir serviços; não tratar todo script como estático inofensivo. Node ausente; suítes Rails, frontend, browser e banco não foram executadas nesta continuação. Nenhuma dependência/runtime foi instalado.

<!-- reading-section: corpus -->
## Validação do corpus e histórico

check_docs.py verifica fontes configuradas; check_catalog.py confere coleções e inventário/procedência históricos. Execuções integrais podem ler vizinhos e reprovar divergência de manifesto. Diferem da suíte de fixtures e de verificações delimitadas em memória. Nenhuma procedência/snapshot foi regenerada e não se afirma aprovação integral do corpus.

Relato de 27 testes e seis erros iniciais em 2026-10-19 permanece histórico no registro datado; execução atual observou 28. Separar datas/escopos. Rever idiomas após mudanças de validador, parser, comandos ou runtimes. Revisar precisão, segurança e tradução além da estrutura automática.

## Execução no corpus durante a reconciliação do ecossistema

Executado na raiz do workspace do ecossistema em 2026-11-10:

```sh
python3 -B engineering-library/tools/check_docs.py --workspace "$PWD"
python3 -B engineering-library/tools/check_catalog.py
```

O primeiro retornou saída 1: 580 documentos, cinco erros e quatro avisos. Os achados compreendem quatro locais inseguros de repositórios fora do workspace selecionado, um achado README/índice causado pela comparação lexical pt-br/pt-BR, referências restritas a vendor e uma âncora não verificada. O verificador de coleções retornou saída 1: 778 arquivos Markdown, 4806 links relativos, uma divergência histórica de inventário de projetos e 26 avisos. São gates completos reprovados, não validação aprovada. Nenhum manifesto, proveniência ou snapshot foi alterado.

Uma comparação em memória usando versões HEAD dos documentos modificados e excluindo páginas recém-criadas encontrou 80 erros/quatro avisos antes destas mudanças, sem nenhum achado introduzido. A comparação normaliza caixa na substituição pelo HEAD e exclui arquivos novos da travessia. O erro da coleção era idêntico ao HEAD e nenhum aviso novo foi introduzido. Verificações direcionadas validam separadamente páginas alteradas, identidades de seções bilíngues, links/âncoras relativos e alcance pelo índice; não certificam semântica de legado não revisado ou disponibilidade de URLs externas. Os links do índice português do Portal agora são relativos à pasta daquele idioma, eliminando seus 55 achados de alcance. O README já aponta para `docs/pt-BR/index.md`, rastreado pelo Git; o achado restante do validador não deve ser “corrigido” introduzindo caminho minúsculo inexistente em sistemas sensíveis à caixa. A capitalização dos repositórios permanece como rastreada, sem renomeação apenas de caixa.
