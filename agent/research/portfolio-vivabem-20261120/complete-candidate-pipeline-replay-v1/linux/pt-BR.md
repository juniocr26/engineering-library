# Fluxo de dados do cache de dependências do FastAPI

Candidato isolado de pesquisa com verificação de fonte; revisão do proprietário e aprovações de publicação e treino estão pendentes.

## Escopo e arquitetura

Fonte fixada: fastapi/fastapi @ 05e6df7e906c3decba377c37548019973f40bf15. Este capítulo acompanha seis grupos de regras: um grupo de declarações selecionadas de Dependant e cinco grupos de fluxo de cache/asserções em solve_dependencies. Ele conecta a declaração do modelo, o laço do solver, a passagem recursiva, a condição de reutilização e a condição posterior de escrita. Ele não documenta toda a arquitetura do FastAPI, uma release instalada ou comportamento observado de serviço.

## Declarações, fluxo e limites de erro

### PF01

A classe escrita Dependant declara use_cache: bool = True e um campo scope cujo valor declarado é None. Isso registra as instruções da classe selecionada; não é observação de um objeto de dependência em execução.

Evidência: `fastapi/dependencies/models.py:53-53`, `fastapi/dependencies/models.py:55-55`.

### PF02

No ramo de inicialização, dependency_cache is None condiciona a atribuição de um dicionário vazio a dependency_cache. A função selecionada não possui outra atribuição direta a esse nome local. Isso não estabelece duração do cache no processo inteiro ou entre requisições.

Evidência: `fastapi/dependencies/utils.py:700-701`.

### PF03

Dentro do laço selecionado sobre dependant.dependencies, a chamada escrita e aguardada de solve_dependencies passa dependency_cache=dependency_cache. Isso conecta a variável local de cache à resolução de subdependências no fluxo de dados escrito; vínculos dinâmicos e conclusão efetiva permanecem não verificados.

Evidência: `fastapi/dependencies/utils.py:726-737`.

### PF04

O ramo selecionado de reutilização exige sub_dependant.use_cache and sub_dependant_cache_key in dependency_cache. Seu corpo atribui solved = dependency_cache[sub_dependant_cache_key]. A conjunção é uma condição de leitura/reutilização; não é garantia de que cada dependência execute exatamente uma vez.

Evidência: `fastapi/dependencies/utils.py:746-746`, `fastapi/dependencies/utils.py:747-747`.

### PF05

Quando o controle alcança a condição posterior de escrita e a chave está ausente, o corpo escrito atribui dependency_cache[sub_dependant_cache_key] = solved. Essa condição não menciona use_cache. Portanto, a fonte selecionada não implementa use_cache=False como proibição geral de escritas no cache. Erros, exceções ou fluxo de controle anteriores podem impedir que essa condição seja alcançada.

Evidência: `fastapi/dependencies/utils.py:774-775`.

### PF06

A função selecionada contém duas asserções escritas que usam isinstance com AsyncExitStack: uma para request_astack e outra para function_astack. Essas instruções não comprovam que as asserções estejam habilitadas no interpretador implantado, que a composição da requisição as satisfaça ou que callbacks de dependências não possam lançar outras exceções.

Evidência: `fastapi/dependencies/utils.py:687-689`, `fastapi/dependencies/utils.py:691-693`.

## Exemplo e testes escritos

Fragmento sintético de declaração de dependência, não um serviço em execução. Ele segue o padrão escrito de chamada com use_cache=False em tests/test_dependency_cache.py:30-35. Sua sintaxe Python foi analisada; imports, resolução de dependências, compatibilidade de tipos e execução não foram testados. Nenhuma rota está registrada aqui.

```python
from fastapi import Depends

async def synthetic_value():
    return 1

async def synthetic_endpoint(value: int = Depends(synthetic_value, use_cache=False)):
    return {"value": value}
```

O arquivo fixado tests/test_dependency_cache.py contém asserções escritas sobre requisições repetidas, dependências aninhadas e reutilização desabilitada. Esses testes do projeto externo não foram executados. Asserções em um arquivo não são resultados aprovados nem aceite de produção. Nenhum comando de instalação, inicialização ou teste é certificado por este capítulo.

## FAQ

### Q001 — use_cache=False proíbe toda escrita no cache?

A condição selecionada de leitura usa use_cache, mas a condição posterior de escrita não. Se a execução alcançar essa condição com uma chave ausente, a atribuição escrita armazena solved. Essa é uma distinção da fonte, não observação de que toda invocação tenha sucesso. [PF04, PF05]

### Q002 — Uma duração global do cache foi estabelecida?

Nenhuma duração global foi estabelecida por este perfil. Ele observa a inicialização quando o valor local é None e a passagem do mesmo nome local à chamada recursiva escrita. Composição do chamador, aliases externos e reutilização efetiva entre requisições exigem evidências separadas. [PF02, PF03]

### Q003 — Isso comprova execução exatamente uma vez das dependências?

Não. As regras descrevem fluxo de dados e condições selecionados do cache. Elas não estabelecem conclusão de callbacks, contagens de invocações concorrentes, equivalência efetiva de chaves de cache ou comportamento real de overrides. Asserções de testes escritos são diferentes de resultados executados. [PF03, PF04, PF05]

### Q004 — As asserções de stack estabelecem tratamento completo de erros?

Não. Elas são duas asserções escritas específicas. Este perfil não estabelece as configurações de asserções do interpretador, correção do chamador, tradução de exceções de callbacks, conclusão de cleanup ou todos os caminhos possíveis de erro. [PF06]

## Contexto não resolvido e preservação

Este perfil fechado não reconstrói a construção de chaves de cache, a resolução de overrides, os escopos efetivos de generators, os limites de concorrência ou o comportamento completo de cleanup. Em particular, ele não afirma que as chaves sejam apenas nomes de funções. Esses contratos precisam de evidências próprias. Sintaxe de fonte, texto fixo e citações exatas não comprovam a verdade de prosa arbitrária ou integração em runtime.

O inventário congelado registrou um clone raso sem revisão pai local. Nenhuma decisão histórica MODIFY é inferida desta única revisão. Símbolos ausentes em fonte parcial nunca autorizam REMOVE. A documentação existente do projeto permanece sem alterações. Os avisos da licença MIT estão preservados na evidência fixada de fonte. Este candidato e sua família de fonte permanecem fora de treino; verificação de fonte não é gold aprovado pelo proprietário.
