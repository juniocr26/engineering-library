# Diagnóstico de conversão de Config — versão revisada

Em `271c277da0ff64e2048a4d46ecc812b9d61db5f6`, o tratador selecionado de `Config._perform_cast` continua capturando `TypeError` e `ValueError` provenientes de `cast(value)`. Atribui `cast_name = getattr(cast, "__name__", type(cast).__name__)` e usa `cast_name` no diagnóstico. O AST anterior do método selecionado, a chamada de conversão e a tupla de exceções capturadas permanecem iguais. Evidência: `starlette/config.py:139–143` e o diff real fixado da revisão.

A expressão padrão identifica o tipo do callable quando a consulta ordinária ao atributo não encontra `__name__`. Isso não torna segura toda consulta personalizada a atributos, e Python avalia a expressão do argumento padrão antes de chamar `getattr`.

No caso próprio limitado, uma instância de `OwnedInvalidCallable` lançou `ValueError` em sua chamada e não possuía `__name__`. O corpo revisado copiado levantou `ValueError` com um diagnóstico que nomeia `OwnedInvalidCallable`; a cópia anterior levantou `AttributeError`. A consulta a `__name__` de outro objeto próprio lançou `RuntimeError`, observado nas duas cópias. Assim, a melhoria observada é específica; uma garantia universal de diagnóstico bem-sucedido permanece sem suporte.

Todos os 12 casos próprios foram avaliados nas duas cópias dos corpos sob vínculos conhecidos: 24 observações por contexto. Valores tipados/mensagens de exceção coincidiram entre Darwin ARM64 Python 3.14.7 e o contêiner Linux ARM64 existente com Python 3.11.2. São observações repetidas e correlacionadas dos corpos, não 48 testes independentes do projeto. Não foi realizada importação do módulo original, construção de `Config`, acesso a arquivos de configuração/ambiente pelo método inspecionado ou suíte de testes upstream. Os vínculos completos do módulo, Windows e a integração da aplicação permanecem não verificados.

Evidência: `starlette-cast-bounded-runtime-protocol-v1.json`, `starlette-cast-bounded-runtime-observation-v1.json` e `starlette-cast-cross-context-review-v1.json`. Este candidato isolado de manutenção está pronto apenas para revisão do proprietário; não é aprovado pelo proprietário, gold de treinamento ou atualização do catálogo ativo.

O observador próprio necessariamente lê as evidências retidas de código e escreve recibos de pesquisa. O limite de acesso a arquivos acima se refere ao acesso a configuração/dados da aplicação pelo método selecionado, não à E/S de evidências do observador.
