# FastAPI: cache de dependências e fronteiras do solver

Candidato de pesquisa isolado. Somente revisão da fonte pelo autor; verificação separada e revisão do proprietário pendentes. Sem aprovação para publicação ou treino.

fastapi/fastapi @ `05e6df7e906c3decba377c37548019973f40bf15`. Este capítulo cobre o contrato selecionado, não o repositório inteiro. Evidência: `source-freeze-v1.json`; critérios: `acceptance-protocol-v1.json`.

## Arquitetura e comportamento

**F01** — Dependant armazena dependências aninhadas e define use_cache como True por padrão; seu scope pode ser function, request ou None. [F01: `fastapi/dependencies/models.py:35-56`]

**F02** — _get_cache_key inclui o callable, escopos OAuth normalizados condicionais e o escopo calculado da dependência; não é apenas uma chave pelo nome da função. [F02: `fastapi/dependencies/models.py:87-101`]

**F03** — solve_dependencies exige objetos AsyncExitStack de request e function em request.scope; quando dependency_cache não é fornecido, cria um dicionário. [F03: `fastapi/dependencies/utils.py:686-703`]

**F04** — O solver pode reconstruir um dependant para um override e passa recursivamente o mesmo dependency_cache para a resolução de dependências. [F04: `fastapi/dependencies/utils.py:708-736`]

**F05** — Após coletar erros de uma dependência, ela é pulada; caso contrário, um valor em cache é reutilizado somente quando use_cache é true e a chave existe. Uma chave ausente é preenchida após o cálculo mesmo quando use_cache é false. [F05: `fastapi/dependencies/utils.py:738-775`]

**F06** — Dependências generator usam uma exit stack, callables de coroutine são aguardados e outros callables passam por run_in_threadpool; os ramos selecionados incluem limites opcionais de concorrência. [F06: `fastapi/dependencies/utils.py:748-771`]

## Exemplo

Fragmento sintético de uso, não executado. Resolva dependências em um ambiente autorizado separadamente antes de executar. Nenhum comando de inicialização ou instalação está autorizado aqui.

```python
from fastapi import Depends, FastAPI
app = FastAPI()
async def counter():
    return 1
@app.get("/sample")
async def sample(value: int = Depends(counter, use_cache=False)):
    return {"value": value}
```

## Evidências de testes e limitações

`tests/test_dependency_cache.py` está preservado como evidência de testes escritos. Nenhuma suíte externa, exemplo, instalação de dependências ou runtime foi executado. Asserções escritas não são resultados aprovados. Nenhum benchmark, garantia de concorrência ou compatibilidade de API entre releases foi estabelecido.

## FAQ

### Q001 — use_cache=False impede toda escrita no cache?

Após coletar erros de uma dependência, ela é pulada; caso contrário, um valor em cache é reutilizado somente quando use_cache é true e a chave existe. Uma chave ausente é preenchida após o cálculo mesmo quando use_cache é false. [F05]

### Q002 — A chave de cache é apenas o nome de uma função?

_get_cache_key inclui o callable, escopos OAuth normalizados condicionais e o escopo calculado da dependência; não é apenas uma chave pelo nome da função. [F02]

### Q003 — A inspeção estática comprova um cache global?

A fonte selecionada não estabelece duração global para o cache. solve_dependencies exige objetos AsyncExitStack de request e function em request.scope; quando dependency_cache não é fornecido, cria um dicionário. [F03]

## Manutenção e direitos

Este clone raso não possui o pai de HEAD localmente. Uma decisão histórica MODIFY é INCONCLUSIVE sem uma fonte anterior verificada e documentação correspondente. Símbolos ausentes neste escopo selecionado não autorizam REMOVE. A documentação existente do projeto permanece sem alterações.

MIT / LICENSE. Os avisos estão preservados com o snapshot de fonte. Este artefato é somente para avaliação, excluído de treino e não aprovado pelo proprietário.
