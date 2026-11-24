# MLX-LM: contratos do código na fronteira do treinamento

**SOURCE-REVIEWED CANDIDATE — NOT OWNER GOLD — NOT PUBLISHED**

Revision: `2d4df8d94a80c0f9f8794e54fafee08728b04fc6`. Group: `mlx-framework-readiness-development-exposed`.

## Propósito e dependências

O ponto de entrada selecionado `mlx_lm.lora` coordena argumentos, carregamento de modelo e dados, seleção de adapters, treinamento e avaliação opcional. Seu módulo importa `mlx.core`, `mlx.nn`, `mlx.optimizers`, `numpy` e `yaml`; este capítulo inspeciona o código sem importar esse módulo. Observações isoladas anteriores executaram somente o construtor puro de argumentos e os adapters de dados admitidos, com métodos próprios que registram chamadas. Nenhum tokenizer real, modelo, tensor, trainer ou otimizador foi executado.

Sources: [entry:preamble](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L1-L85), [entry:run](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L344-L376), [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319).

## Arquitetura e ordem de carregamento

`main` combina a configuração e chama `run`. Em `run`, a preparação de relatórios, `load` e `load_dataset` precedem a decisão entre avaliação, treinamento e erro de modo ausente. Portanto, omitir `--train` não transforma o ponto de entrada real em uma simulação segura sem carregamento. Essas funções do código não foram chamadas; nenhum download ou carregamento de modelo foi observado.

Sources: [entry:main](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L379-L398), [entry:run](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L344-L376).

## Precedência de configuração

A combinação preenche um argumento pela configuração somente quando `args.get(k, None) is None`, e depois preenche os valores ainda ausentes com os padrões. Assim, padrões não nulos do parser impedem os valores correspondentes da configuração: as observações com o construtor próprio mantiveram `trust_remote_code=False` e `clear_cache_threshold=0` apesar de configuração conflitante. Valores da configuração também não passam pela análise de tipos e opções do argparse. Esta é uma análise de admissão pelo código, não uma alegação de que todo valor posterior executará com sucesso.

Sources: [entry:build_parser](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L86-L223), [entry:main](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L379-L398), [entry:preamble](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L1-L85).

## Entradas de dados e admissão

`create_dataset` examina `data[0]`: chaves de prompt/completion têm precedência, seguidas pela chave de chat e pela chave de texto. Ele não inspeciona os campos de aprovação do proprietário ou de exclusão de avaliação da Engineering Library. Linhas próprias nos formatos nativos de chat, completion e texto foram processadas apesar dos indicadores falsos de aprovação; essas linhas não são o esquema dos305 registros congelados. Entrada externa vazia provocou erro de índice, e formatos mistos falharam ao acessar a linha posterior incompatível. Aceitação de formato não é autorização para treinamento.

Sources: [datasets:create_dataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L178-L205).

## Limites dos dados locais e remotos

`load_local_dataset` usa os nomes `train.jsonl`, `valid.jsonl` e `test.jsonl`; um subconjunto ausente retorna uma lista vazia. Um arquivo presente e vazio chega à seleção de formato pela primeira linha. Em `load_dataset`, um caminho local de dados inexistente segue para o ramo de dataset remoto. Treinamento com conjunto de validação vazio produz um aviso, e não uma garantia de avaliação independente. Nenhum carregador de arquivos ou de dataset remoto foi executado no estudo com adapters próprios.

Sources: [datasets:load_local_dataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L208-L222), [datasets:load_dataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L312-L335), [datasets:create_dataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L178-L205).

## Interfaces de tokens e prompt

`ChatDataset.process` retorna os tokens completos do template e, quando a máscara está habilitada, um deslocamento calculado por outra chamada ao template com todas as mensagens exceto a última. Ele compara o último papel com `assistant` para selecionar o indicador de prompt de geração, mas não valida prefixos de tokens correspondentes, limites do deslocamento ou conteúdo não vazio do assistente. Quatro controles com retornos de métodos próprios expõem essas premissas não verificadas. Seus intervalos brutos de alvo não são contagens de supervisão após o deslocamento do trainer nem evidência de defeito em um tokenizer real.

Sources: [datasets:ChatDataset.process](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L59-L79), [datasets:CompletionsDataset.process](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L109-L129), [trainer:default_loss](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L88-L101).

## Escopo de lotes e perda

`iterate_batches` preenche com zeros, trunca os comprimentos retidos e fornece pares de deslocamento/comprimento. `default_loss` desloca os alvos em uma posição e escreve uma comparação inclusiva do limite superior do comprimento. Casos anteriores de inteiros derivados do código mostraram posições de preenchimento ou nenhuma posição elegível para entradas específicas. Esses resultados condicionais de aritmética não executam MLX nem medem perda de treinamento real. Uma verificação futura deve inspecionar em conjunto a identidade real dos tokens, o alinhamento de prefixos e o domínio efetivo dos alvos deslocados.

Sources: [trainer:iterate_batches](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L104-L175), [trainer:default_loss](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L88-L101).

## Cache e aproximações de comprimento

`CacheDataset` memoriza linhas processadas enquanto `itemlen` retorna o comprimento do item bruto subjacente. `iterate_batches` usa esse método quando seu dataset é um wrapper de cache. No exemplo com dicionários próprios, comprimentos brutos1e4 divergiram dos comprimentos de tokens processados11e3 e inverteram a ordenação correspondente. Isso estabelece uma diferença de aproximação na composição mostrada, não um resultado de vazão, memória ou qualidade de treinamento.

Sources: [datasets:CacheDataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L161-L175), [trainer:iterate_batches](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L104-L175), [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319).

## Concatenação e identidade de linhas

`ConcatenatedDataset.__getitem__` escreve `_dataset` na linha original retornada e depois usa esse campo para direcionar o processamento. Acessos próprios a uma linha compartilhada mudaram os metadados de direcionamento da linha retida. Com duas e três linhas em datasets separados, acessar o índice do comprimento declarado retornou uma linha, enquanto a iteração implícita do Python produziu oito linhas em vez de cinco. Essas observações limitadas não estabelecem que o caminho nativo de lotes por índice realiza a mesma iteração implícita.

Sources: [datasets:ConcatenatedDataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L138-L158), [trainer:iterate_batches](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L104-L175).

## Seleção de adapters

Quando `keys` está ausente, `linear_to_lora_layers` descobre caminhos de módulos suportados, em vez de limitar a seleção às projeções de query/value. Seu recorte de camadas usa `-max(num_layers, 0)`, de modo que valores zero e negativos selecionam a lista inteira de camadas pelo recorte do Python. Uma passagem separada pelo modelo completo pode selecionar módulos nomeados explicitamente fora do recorte das últimas camadas. Uma lista explícita vazia de chaves não seleciona módulos na aritmética limitada de seleção. Esses são fatos condicionais de seleção pelo código, não um inventário inspecionado de um modelo treinável.

Sources: [selection:linear_to_lora_layers](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/utils.py#L46-L126), [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319).

## Formatos de baixo rank e escala

O construtor `LoRALinear` mostrado declara os formatos dos adapters `(input_dims, r)` e `(r, output_dims)`. Ele armazena a escala fornecida em `self.scale` antes de reutilizar a variável local na inicialização; a expressão de propagação multiplica a atualização por `self.scale` sem dividir pelo rank. Hooks personalizados de conversão de módulos podem seguir outro caminho. Nenhum objeto de adapter, tensor ou propagação foi criado ou executado aqui.

Sources: [adapter:LoRALinear.__init__](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/lora.py#L67-L93), [adapter:LoRALinear.__call__](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/lora.py#L95-L98), [selection:linear_to_lora_layers](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/utils.py#L46-L126).

## Exemplo condicional de tamanho

Para os metadados fixados do modelo comunitário3B, o modelo declarado com as últimas duas camadas e rank quatro resulta em434176elementos de adapter quando as sete projeções suportadas são selecionadas, contra81920para projeções explícitas de query/value. A contagem pressupõe os formatos e o caminho de conversão revisados. Ilustrações de bytes por elemento são hipotéticas; omitem dtype real, estado do otimizador, ativações, alocações transitórias e comportamento do Metal. Elas não demonstram viabilidade no host de16GiB.

Sources: [selection:linear_to_lora_layers](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/utils.py#L46-L126), [adapter:LoRALinear.from_base](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/lora.py#L12-L32).

## Persistência e retomada

`train_model` carrega pesos opcionais de adapter antes de construir um novo otimizador. O código selecionado de `train` salva parâmetros treináveis achatados em arquivos de adapter periodicamente e na conclusão; a carga salva mostrada não inclui otimizador, estado aleatório ou posição nos dados. Assim, o caminho inspecionado baseado apenas em pesos não é uma continuação verificada de estado exato. Persistência atômica, gravações interrompidas e recuperação real de treinamento permanecem não executadas.

Sources: [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319), [trainer:train](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L221-L380).

## Limites e revisão

A licença do pacote de código está preservada, enquanto direitos de treinamento, alvos aprovados pelo proprietário e independência de avaliação permanecem sem aprovação. Nenhum comando de início de treinamento ou configuração executável do trainer é fornecido. O exemplo abaixo é um registro próprio de revisão, não uma entrada nativa de treinamento. Admissão pelo parser, metadados pequenos, recuperação de compiladores e contextos repetidos de Python não satisfazem os nove requisitos de prontidão; a decisão atual permanece NO-GO.

Sources: [entry:run](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L344-L376), [entry:main](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L379-L398).

## Review record / Registro de revisão

```json
{
  "kind": "owned-review-record-not-trainer-input",
  "source_revision": "2d4df8d94a80c0f9f8794e54fafee08728b04fc6",
  "owner_approved": false,
  "training_use_approved": false,
  "evaluation_excluded_from_training": true,
  "launch_allowed": false,
  "decision": "NO-GO"
}
```

## FAQ

### Omitir o indicador de treinamento impede o carregamento do modelo?

`main` combina a configuração e chama `run`. Em `run`, a preparação de relatórios, `load` e `load_dataset` precedem a decisão entre avaliação, treinamento e erro de modo ausente. Portanto, omitir `--train` não transforma o ponto de entrada real em uma simulação segura sem carregamento. Essas funções do código não foram chamadas; nenhum download ou carregamento de modelo foi observado.

Sources: [entry:main](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L379-L398), [entry:run](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L344-L376).

### Todo valor da configuração substitui um padrão do parser?

A combinação preenche um argumento pela configuração somente quando `args.get(k, None) is None`, e depois preenche os valores ainda ausentes com os padrões. Assim, padrões não nulos do parser impedem os valores correspondentes da configuração: as observações com o construtor próprio mantiveram `trust_remote_code=False` e `clear_cache_threshold=0` apesar de configuração conflitante. Valores da configuração também não passam pela análise de tipos e opções do argparse. Esta é uma análise de admissão pelo código, não uma alegação de que todo valor posterior executará com sucesso.

Sources: [entry:build_parser](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L86-L223), [entry:main](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L379-L398), [entry:preamble](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L1-L85).

### Um formato de dataset suportado estabelece aprovação para treinamento?

`create_dataset` examina `data[0]`: chaves de prompt/completion têm precedência, seguidas pela chave de chat e pela chave de texto. Ele não inspeciona os campos de aprovação do proprietário ou de exclusão de avaliação da Engineering Library. Linhas próprias nos formatos nativos de chat, completion e texto foram processadas apesar dos indicadores falsos de aprovação; essas linhas não são o esquema dos305 registros congelados. Entrada externa vazia provocou erro de índice, e formatos mistos falharam ao acessar a linha posterior incompatível. Aceitação de formato não é autorização para treinamento.

Sources: [datasets:create_dataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L178-L205).

### Um deslocamento de prompt comprova supervisão válida e não vazia do assistente?

`ChatDataset.process` retorna os tokens completos do template e, quando a máscara está habilitada, um deslocamento calculado por outra chamada ao template com todas as mensagens exceto a última. Ele compara o último papel com `assistant` para selecionar o indicador de prompt de geração, mas não valida prefixos de tokens correspondentes, limites do deslocamento ou conteúdo não vazio do assistente. Quatro controles com retornos de métodos próprios expõem essas premissas não verificadas. Seus intervalos brutos de alvo não são contagens de supervisão após o deslocamento do trainer nem evidência de defeito em um tokenizer real.

Sources: [datasets:ChatDataset.process](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L59-L79), [datasets:CompletionsDataset.process](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L109-L129), [trainer:default_loss](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L88-L101).

### O comprimento de um item em cache sempre conta os tokens processados?

`CacheDataset` memoriza linhas processadas enquanto `itemlen` retorna o comprimento do item bruto subjacente. `iterate_batches` usa esse método quando seu dataset é um wrapper de cache. No exemplo com dicionários próprios, comprimentos brutos1e4 divergiram dos comprimentos de tokens processados11e3 e inverteram a ordenação correspondente. Isso estabelece uma diferença de aproximação na composição mostrada, não um resultado de vazão, memória ou qualidade de treinamento.

Sources: [datasets:CacheDataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L161-L175), [trainer:iterate_batches](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L104-L175), [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319).

### Chaves omitidas selecionam somente adapters de query/value em duas camadas?

Quando `keys` está ausente, `linear_to_lora_layers` descobre caminhos de módulos suportados, em vez de limitar a seleção às projeções de query/value. Seu recorte de camadas usa `-max(num_layers, 0)`, de modo que valores zero e negativos selecionam a lista inteira de camadas pelo recorte do Python. Uma passagem separada pelo modelo completo pode selecionar módulos nomeados explicitamente fora do recorte das últimas camadas. Uma lista explícita vazia de chaves não seleciona módulos na aritmética limitada de seleção. Esses são fatos condicionais de seleção pelo código, não um inventário inspecionado de um modelo treinável.

Sources: [selection:linear_to_lora_layers](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/utils.py#L46-L126), [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319).

### Carregar pesos salvos de adapter restaura o estado exato do treinamento?

`train_model` carrega pesos opcionais de adapter antes de construir um novo otimizador. O código selecionado de `train` salva parâmetros treináveis achatados em arquivos de adapter periodicamente e na conclusão; a carga salva mostrada não inclui otimizador, estado aleatório ou posição nos dados. Assim, o caminho inspecionado baseado apenas em pesos não é uma continuação verificada de estado exato. Persistência atômica, gravações interrompidas e recuperação real de treinamento permanecem não executadas.

Sources: [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319), [trainer:train](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L221-L380).
