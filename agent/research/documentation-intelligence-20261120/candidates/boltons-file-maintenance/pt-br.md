# Manutenção de arquivos no Boltons: filtro de profundidade e limites da rotação

Estado: candidato isolado revisado contra a fonte, **somente para avaliação**,
pendente de revisão do proprietário. Este capítulo não é documentação ativa nem
alvo de treinamento aprovado. Descreve a revisão Boltons
`c23dbdadb6fecdf505eb4231559561913b84c13f` (tag `25.0.0`) em comparação com
`992a58c1036fcf4d52cbf3313b6217b7c07b11d9` (`24.0.0`). Não descreve a versão
mais recente do projeto upstream.

## Finalidade e contexto

O `fileutils.py` inspecionado é um módulo Python de utilitários de sistema de
arquivos. Esta revisão abrange apenas `iter_find_files` e a nova declaração
`rotate_file`, além da sequência escrita de flush/fsync em `AtomicSaver.__exit__`.
Não estabelece composição de dependências de aplicação, implantação em produção
ou durabilidade contra falhas entre plataformas. Nenhum banco, serviço ou
projeto privado foi utilizado.

Snapshots completos da fonte e a licença upstream estão preservados em
[fonte 25.0.0](../../public-sources/25.0.0/boltons/fileutils.py),
[fonte 24.0.0](../../public-sources/24.0.0/boltons/fileutils.py) e
[licença](../../public-sources/25.0.0/LICENSE). URLs com commits exatos e hashes
dos arquivos completos estão na [proveniência](../../public-sources/provenance.json).

## Contratos públicos e configuração

A assinatura anterior de `iter_find_files` termina em `include_dirs=False`. A
assinatura atual acrescenta `max_depth=None`. O novo parâmetro é utilizado dentro
do laço de `os.walk` para pular o processamento de uma raiz quando a diferença
na contagem de separadores em relação ao diretório inicial excede `max_depth`.

| Entrada | Comportamento escrito | Limite |
|---|---|---|
| `max_depth=None` | O `continue` baseado em profundidade não é selecionado | Os demais filtros existentes de padrões continuam se aplicando |
| `max_depth=0` | Raízes abaixo do diretório inicial são ignoradas na emissão | Esse ramo não poda a travessia alterando `dirs` |
| `max_depth=1` | O diretório inicial e um nível de subdiretório podem contribuir com resultados | É uma regra escrita de contagem de separadores; casos extremos de caminhos/sistema de arquivos não foram executados |
| `include_dirs=False` | O padrão existente de inclusão de diretórios é preservado | Acrescentar um parâmetro de profundidade não prova que toda resposta existente precisa mudar |

A implementação conta componentes usando `os.path.sep`. Não reescreva isso como
um algoritmo verificado de profundidade de caminhos canônicos. A raiz ignorada
é tratada com `continue`; o novo ramo não limpa nem substitui a lista `dirs` da
travessia. Portanto, a fonte sustenta o filtro dos resultados emitidos, sem
provar que diretórios mais profundos nunca sejam visitados por `os.walk`.

## Nova função de rotação

O módulo atual declara `rotate_file(filename, *, keep: int = 5)`; o anterior não
contém declaração com esse nome. A posição keyword-only e o padrão literal são
fatos da fonte. A anotação não realiza validação em execução.

O corpo lança `ValueError` para `keep < 1`, retorna se a origem não existe e
lança `ValueError` quando uma origem existente não é um arquivo. Monta nomes
numerados, renomeia em ordem inversa e depois remove o nome no limite `keep` se
ele existir. Falhas de sistema de arquivos podem se propagar; a função
selecionada não possui rollback nem handler de exceção.

A remoção final é relevante. Nos três controles confinados de caminho normal,
as quantidades observadas de backups foram:

| Argumento `keep` | Backups restantes | Nome original após a rotação |
|---|---:|---|
| `1` | `0` | Ausente |
| `2` | `1` | Ausente |
| `5` | `4` | Ausente |

Os controles começaram com um arquivo sintético atual e backups numerados até o
limite configurado. Seus [rastros de operações](../../public-rotate-observation-v1.json)
mostram a remoção do último backup de limite após as renomeações. Com `keep=1`,
o próprio arquivo atual renomeado é removido. Não prometa que esta revisão
inspecionada preserva `keep` backups. Isso não é uma afirmação sobre versões
posteriores.

## Dependências, erros e durabilidade

`iter_find_files` delega a travessia a `os.walk` e a correspondência de padrões
aos mecanismos existentes do módulo. `rotate_file` chama consultas de caminhos,
`os.rename` e `os.remove`. Essas chamadas escritas identificam a direção das
dependências; não verificam o comportamento de substituição e falha de todas
as plataformas.

`AtomicSaver.__exit__` agora chama `flush()` e `os.fsync()` em um arquivo parcial
presente antes de `close()`. É uma mudança relevante de efeito observável. Não
prova uma transação atômica de sistema de arquivos com várias operações nem
recuperação contra falhas. Os controles confinados de rotação não executaram
`AtomicSaver` nem simularam queda de energia.

Nenhum resultado numérico específico de tempo decorrido, latência de disco ou
desempenho decorre desta revisão. Nenhuma explicação gerada pelo modelo foi
utilizada como alvo factual.

## Exemplos e comandos de pesquisa executados

Na assinatura revisada, `iter_find_files(directory, patterns, max_depth=0)`
seleciona o novo filtro de profundidade, enquanto `rotate_file(filename, keep=1)`
seleciona o caso de limite observado. São ilustrações de API, não instruções para
rotacionar arquivos reais. Use apenas caminhos próprios descartáveis em um
experimento de execução.

A campanha executou este controle delimitado a partir da raiz da biblioteca:

```sh
python3 agent/research/documentation-intelligence-20261120/observe_public_rotate_v1.py
```

Ele compilou apenas a função AST pública selecionada, sem importar o módulo
completo, e forneceu uma fachada de sistema de arquivos confinada a novos
diretórios sintéticos. Raízes de saída existentes são recusadas; repetir na mesma
cópia do projeto não é uma operação de limpeza nem sobrescrita. Código,
protocolo, hash da fonte e recibos de operações estão preservados. Três controles
de caminho normal não estabelecem segurança contra falhas, escritores
concorrentes ou comportamento exaustivo de erros. Nenhum diagrama é necessário
para expressar este algoritmo sequencial delimitado.

## FAQ de engenharia

### `max_depth=0` impede toda travessia abaixo do diretório inicial?

O novo ramo ignora processamento e emissão de raízes mais profundas. Não poda
`os.walk` editando `dirs`. Afirmar que nenhuma travessia mais profunda ocorre
excederia a evidência inspecionada.

### `keep=1` preserva um backup rotacionado na revisão inspecionada?

Não. No controle confinado de caminho normal, a função renomeia o arquivo atual
para o primeiro nome de backup e depois remove esse nome de limite. Restam zero
backups. O nome original também está ausente após essa execução.

### A nova sequência flush/fsync prova gravação atômica contra falhas?

Não. A fonte estabelece duas chamadas antes de fechar o arquivo parcial presente.
Nem sua presença nem os controles de rotação demonstram transações atômicas
contra falhas, rollback ou recuperação após queda de energia.

### A FAQ sobre o comportamento padrão deve ser removida porque a assinatura mudou?

Não. O novo parâmetro tem padrão `None`, e afirmações ainda válidas precisam ser
revisadas individualmente. Uma mudança de fonte não prova automaticamente a
necessidade de remover ou regenerar documentação não relacionada.

## Revisão e limites da evidência

A avaliação pública congelada do planner se absteve nos oito casos Boltons
selecionados. Esse resultado permanece preservado; estas revisões de fonte não
são sucessos retroativos do modelo. A família não apareceu na busca histórica
local delimitada, mas os casos são correlacionados e não possuem revisão humana
independente. O capítulo e seus quatro pares de FAQ permanecem somente para
avaliação, fora dos 77 pares anteriores preservados e da linhagem de candidatos
de treinamento V10.
