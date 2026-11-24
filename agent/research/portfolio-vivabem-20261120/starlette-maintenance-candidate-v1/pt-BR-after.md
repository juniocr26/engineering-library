# Diagnóstico de conversão de Config — depois da revisão

Em `271c277da0ff64e2048a4d46ecc812b9d61db5f6`, o tratador selecionado de `Config._perform_cast` continua capturando `TypeError` e `ValueError` provenientes de `cast(value)`. Agora atribui `cast_name = getattr(cast, "__name__", type(cast).__name__)` e usa `cast_name` na mensagem de erro.

Evidência: `starlette/config.py:139–143`. A expressão padrão identifica o tipo do callable quando a consulta ordinária ao atributo não encontra `__name__`. Isso não estabelece que toda consulta personalizada a atributos ou construção do diagnóstico tenha sucesso. O AST anterior do método selecionado, a expressão da chamada e os tipos de exceção capturados permanecem iguais. Não houve execução em runtime.
