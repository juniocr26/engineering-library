# Validação da documentação

Execute a partir da raiz do repositório:

```sh
python3 -B docs/validation/check_catalog.py
python3 -B -m unittest discover -s tools -p 'test_*.py' -v
```

O verificador segue Biblioteca → Projeto → Idioma → Índice → Categoria → Documento. Confere links locais, âncoras Markdown, alcance pelos índices central e de projeto, paridade de caminhos e IDs de perguntas, índices FAQ, referências ENV e títulos das importações registradas. Coleções de idioma na raiz são proibidas. Hashes das fontes importadas identificam mudanças desde o snapshot histórico, não representam hashes atuais. Os READMEs públicos da raiz e dos componentes participam da validação de links.

`tools/check_docs.py` permanece como verificador legado dos repositórios irmãos e fornece os auxiliares de Markdown e segurança usados pelo catálogo. Seu manifesto antigo contém caminhos históricos de idioma na raiz e não é o comando de conclusão do catálogo atual. Os [testes isolados](../../../../../../tools/test_check_docs.py) exercitam caminhos restritos, symlinks, comportamento somente leitura, âncoras e entradas inválidas.

As ferramentas não leem arquivos reais de ambiente, chaves ou bancos. Links de código recebem apenas conferência de metadados. URLs externas não são consultadas. O parser cobre um subconjunto Markdown; correção semântica, qualidade da tradução e disponibilidade de terceiros exigem revisão. A verificação de runtime é separada: veja [desenvolvimento](application-development.md) e [migração](../operations/database-migration.md).
