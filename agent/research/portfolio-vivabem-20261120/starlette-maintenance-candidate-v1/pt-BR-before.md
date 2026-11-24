# Diagnóstico de conversão de Config — antes da revisão

Em `9b403a0c33f0e2eebba099e9e6aa1c1e9535daec`, o tratador selecionado de `Config._perform_cast` captura `TypeError` e `ValueError` provenientes de `cast(value)`. Sua mensagem de erro lê diretamente `cast.__name__`.

Evidência: `starlette/config.py:139–142`. Esta é uma descrição estática do ramo selecionado, sem execução em runtime.
