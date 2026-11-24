# Diagnóstico de conversão de Config — revisão anterior

Em `9b403a0c33f0e2eebba099e9e6aa1c1e9535daec`, o tratador selecionado de `Config._perform_cast` captura `TypeError` e `ValueError` provenientes de `cast(value)` e constrói seu diagnóstico usando diretamente `cast.__name__`. Evidência: `starlette/config.py:139–142`.

Uma observação limitada posterior da campanha executou somente uma cópia do corpo desse método, com anotações removidas e vínculos conhecidos de builtins. Uma instância própria de `OwnedInvalidCallable` lançou `ValueError` em sua chamada e não possuía `__name__`; o corpo anterior copiado então levantou `AttributeError` ao construir seu diagnóstico. Esse é um resultado observado para esse caso próprio, não uma afirmação de que toda conversão com falha levanta essa exceção.

Não foi realizada importação do módulo Starlette, construção de `Config`, acesso a ambiente/arquivos ou suíte de testes upstream. Essa observação do código/corpo não é integração completa da aplicação, aprovação do proprietário ou gold de treinamento.
