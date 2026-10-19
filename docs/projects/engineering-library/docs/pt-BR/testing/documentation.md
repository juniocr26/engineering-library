# Validação e limites

[Validador de documentação existente](../guides/documentation-validator.md).


Use `python3 -B docs/validation/check_catalog.py` na raiz para conferir o catálogo atual por projeto. Testes de runtime são separados da validação estática.

## Validação da auditoria — 2026-10-19

A suíte Python isolada existente foi executada com 27 testes aprovados. Cobre fixtures do catálogo, caminhos restritos, links/âncoras, symlinks, validação somente leitura e falhas do contrato bilíngue. Na raiz do repositório:

```sh
python3 -B docs/validation/check_catalog.py
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
git diff --check
```

A primeira validação encontrou seis erros preexistentes de alcance: duas páginas de fontes inacessíveis pelos índices central e do projeto e outras duas páginas de verificação sem links. As mudanças acrescentam navegação. Contagens finais pertencem ao [registro da auditoria](../../../../../validation/documentation-audit-2026-10-19.json), separadas dos relatos anteriores.

`node` e `npm` estavam ausentes no host. Não foram executados build/typecheck frontend, paginação no navegador ou suítes Rails/banco. Testes backend definem fronteiras de sync/ordem e favoritos/CSRF; testes frontend definem ordem lógica. Essas asserções lidas não são novos resultados runtime. Validação estrutural não certifica respostas ou tradução equivalente.
