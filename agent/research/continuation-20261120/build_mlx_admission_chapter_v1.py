"""Isolated bilingual source-architecture chapter for MLX-LM admission boundaries."""
import datetime
import hashlib
import json
from pathlib import Path
import re

P = Path(__file__).resolve().parent
pack_path = P / 'mlx-admission-chapter-source-pack-v1.json'
pack = json.loads(pack_path.read_text())
claims = []

def add(identity, section, en, pt, evidence, observations=()):
    assert re.findall(r'`([^`]+)`', en) == re.findall(r'`([^`]+)`', pt), identity
    assert all(key in pack['units'] for key in evidence)
    claims.append({'id': identity, 'section': section, 'en': en, 'pt-br': pt, 'evidence_ids': evidence,
                   'observation_artifacts': list(observations), 'review_status': 'AGENT_SOURCE_REVIEWED_NOT_OWNER_GOLD'})

add('purpose', 'Purpose and dependency boundary / Propósito e dependências',
    'The selected `mlx_lm.lora` entrypoint coordinates arguments, model and dataset loading, adapter selection, training and optional evaluation. Its module imports `mlx.core`, `mlx.nn`, `mlx.optimizers`, `numpy` and `yaml`; this chapter inspects source without importing that module. Earlier isolated observations executed only the admitted pure argument builder and dataset adapters with owned method sinks. No real tokenizer, model, tensor, trainer or optimizer was executed.',
    'O ponto de entrada selecionado `mlx_lm.lora` coordena argumentos, carregamento de modelo e dados, seleção de adapters, treinamento e avaliação opcional. Seu módulo importa `mlx.core`, `mlx.nn`, `mlx.optimizers`, `numpy` e `yaml`; este capítulo inspeciona o código sem importar esse módulo. Observações isoladas anteriores executaram somente o construtor puro de argumentos e os adapters de dados admitidos, com métodos próprios que registram chamadas. Nenhum tokenizer real, modelo, tensor, trainer ou otimizador foi executado.',
    ['entry:preamble', 'entry:run', 'entry:train_model'], ['pilot-argument-admission-results-v1.json', 'pilot-data-adapter-cross-context-v1.json'])

add('entry-order', 'Architecture and loading order / Arquitetura e ordem de carregamento',
    '`main` merges configuration and calls `run`. In `run`, reporting setup, `load` and `load_dataset` precede the decision between testing, training and the missing-mode error. Therefore omitting `--train` does not make the actual entrypoint a safe no-load dry run. These source functions were not invoked; no download or model loading was observed.',
    '`main` combina a configuração e chama `run`. Em `run`, a preparação de relatórios, `load` e `load_dataset` precedem a decisão entre avaliação, treinamento e erro de modo ausente. Portanto, omitir `--train` não transforma o ponto de entrada real em uma simulação segura sem carregamento. Essas funções do código não foram chamadas; nenhum download ou carregamento de modelo foi observado.',
    ['entry:main', 'entry:run'])

add('merge', 'Configuration precedence / Precedência de configuração',
    'The merge fills an argument from configuration only when `args.get(k, None) is None`, then fills remaining unspecified values from defaults. Non-null parser defaults therefore block matching configuration values: the owned builder observations retained `trust_remote_code=False` and `clear_cache_threshold=0` despite conflicting configuration. Configuration values also bypass argparse choice/type parsing. This is source admission analysis, not a claim that every downstream value will execute successfully.',
    'A combinação preenche um argumento pela configuração somente quando `args.get(k, None) is None`, e depois preenche os valores ainda ausentes com os padrões. Assim, padrões não nulos do parser impedem os valores correspondentes da configuração: as observações com o construtor próprio mantiveram `trust_remote_code=False` e `clear_cache_threshold=0` apesar de configuração conflitante. Valores da configuração também não passam pela análise de tipos e opções do argparse. Esta é uma análise de admissão pelo código, não uma alegação de que todo valor posterior executará com sucesso.',
    ['entry:build_parser', 'entry:main', 'entry:preamble'], ['pilot-argument-admission-results-v1.json'])

add('format-admission', 'Data inputs and admission / Entradas de dados e admissão',
    '`create_dataset` examines `data[0]`: prompt/completion keys take precedence, followed by the chat key, then the text key. It does not inspect Engineering Library owner approval or evaluation exclusion fields. Owned native-shaped chat, completion and text rows were processed despite false approval flags; those rows are not the frozen305 schema. Empty outer input raised an indexing error, and mixed row formats failed when accessing the incompatible later row. Format acceptance is not training authorization.',
    '`create_dataset` examina `data[0]`: chaves de prompt/completion têm precedência, seguidas pela chave de chat e pela chave de texto. Ele não inspeciona os campos de aprovação do proprietário ou de exclusão de avaliação da Engineering Library. Linhas próprias nos formatos nativos de chat, completion e texto foram processadas apesar dos indicadores falsos de aprovação; essas linhas não são o esquema dos305 registros congelados. Entrada externa vazia provocou erro de índice, e formatos mistos falharam ao acessar a linha posterior incompatível. Aceitação de formato não é autorização para treinamento.',
    ['datasets:create_dataset'], ['pilot-data-adapter-cross-context-v1.json'])

add('local-remote', 'Local and remote dataset boundaries / Limites dos dados locais e remotos',
    '`load_local_dataset` names `train.jsonl`, `valid.jsonl` and `test.jsonl`; a missing subset returns an empty list. A present empty file instead reaches first-row format selection. In `load_dataset`, a nonexistent local data path falls through to the remote dataset branch. Training with an empty validation set produces a warning rather than an independent evaluation guarantee. No file loader or remote dataset loader was executed in the owned adapter study.',
    '`load_local_dataset` usa os nomes `train.jsonl`, `valid.jsonl` e `test.jsonl`; um subconjunto ausente retorna uma lista vazia. Um arquivo presente e vazio chega à seleção de formato pela primeira linha. Em `load_dataset`, um caminho local de dados inexistente segue para o ramo de dataset remoto. Treinamento com conjunto de validação vazio produz um aviso, e não uma garantia de avaliação independente. Nenhum carregador de arquivos ou de dataset remoto foi executado no estudo com adapters próprios.',
    ['datasets:load_local_dataset', 'datasets:load_dataset', 'datasets:create_dataset'])

add('mask-interface', 'Token and prompt interfaces / Interfaces de tokens e prompt',
    '`ChatDataset.process` returns full template tokens and, when masking is enabled, an offset computed from a separate template call on all but the last message. It compares the last role with `assistant` to select the generation-prompt flag, but does not validate matching token prefixes, offset bounds or nonempty assistant content. Four owned method-return controls expose those unchecked assumptions. Their raw target intervals are not shifted trainer supervision counts or evidence of a real tokenizer defect.',
    '`ChatDataset.process` retorna os tokens completos do template e, quando a máscara está habilitada, um deslocamento calculado por outra chamada ao template com todas as mensagens exceto a última. Ele compara o último papel com `assistant` para selecionar o indicador de prompt de geração, mas não valida prefixos de tokens correspondentes, limites do deslocamento ou conteúdo não vazio do assistente. Quatro controles com retornos de métodos próprios expõem essas premissas não verificadas. Seus intervalos brutos de alvo não são contagens de supervisão após o deslocamento do trainer nem evidência de defeito em um tokenizer real.',
    ['datasets:ChatDataset.process', 'datasets:CompletionsDataset.process', 'trainer:default_loss'], ['pilot-template-interface-results-v1.json'])

add('batch-arithmetic', 'Batching and loss scope / Escopo de lotes e perda',
    '`iterate_batches` pads with zeros, truncates retained lengths and supplies offset/length pairs. `default_loss` shifts targets by one and writes an inclusive upper length comparison. Earlier source-derived integer cases showed padding positions or zero eligible positions for particular inputs. Those conditional arithmetic findings do not execute MLX or measure actual training loss. A future preflight must inspect real token identity, prefix alignment and the effective shifted target domain together.',
    '`iterate_batches` preenche com zeros, trunca os comprimentos retidos e fornece pares de deslocamento/comprimento. `default_loss` desloca os alvos em uma posição e escreve uma comparação inclusiva do limite superior do comprimento. Casos anteriores de inteiros derivados do código mostraram posições de preenchimento ou nenhuma posição elegível para entradas específicas. Esses resultados condicionais de aritmética não executam MLX nem medem perda de treinamento real. Uma verificação futura deve inspecionar em conjunto a identidade real dos tokens, o alinhamento de prefixos e o domínio efetivo dos alvos deslocados.',
    ['trainer:iterate_batches', 'trainer:default_loss'], ['training-arithmetic-audit-v1.json'])

add('cache', 'Caching and length proxies / Cache e aproximações de comprimento',
    '`CacheDataset` memoizes processed rows while `itemlen` returns the length of the underlying raw item. `iterate_batches` uses this method when its dataset is a cache wrapper. In the owned dictionary example, raw lengths1and4 disagreed with processed token lengths11and3 and reversed the corresponding sort order. This establishes a proxy difference in the shown composition, not a throughput, memory or training-quality result.',
    '`CacheDataset` memoriza linhas processadas enquanto `itemlen` retorna o comprimento do item bruto subjacente. `iterate_batches` usa esse método quando seu dataset é um wrapper de cache. No exemplo com dicionários próprios, comprimentos brutos1e4 divergiram dos comprimentos de tokens processados11e3 e inverteram a ordenação correspondente. Isso estabelece uma diferença de aproximação na composição mostrada, não um resultado de vazão, memória ou qualidade de treinamento.',
    ['datasets:CacheDataset', 'trainer:iterate_batches', 'entry:train_model'], ['pilot-data-adapter-cross-context-v1.json'])

add('concatenation', 'Concatenation and row identity / Concatenação e identidade de linhas',
    '`ConcatenatedDataset.__getitem__` writes `_dataset` into the returned original row and later uses that field for processing dispatch. Owned shared-row accesses changed the held row routing metadata. With two and three rows in separate datasets, indexing at the declared length returned a row, while Python fallback iteration yielded eight rows rather than five. These bounded observations do not establish that the native indexed batching path performs the same fallback iteration.',
    '`ConcatenatedDataset.__getitem__` escreve `_dataset` na linha original retornada e depois usa esse campo para direcionar o processamento. Acessos próprios a uma linha compartilhada mudaram os metadados de direcionamento da linha retida. Com duas e três linhas em datasets separados, acessar o índice do comprimento declarado retornou uma linha, enquanto a iteração implícita do Python produziu oito linhas em vez de cinco. Essas observações limitadas não estabelecem que o caminho nativo de lotes por índice realiza a mesma iteração implícita.',
    ['datasets:ConcatenatedDataset', 'trainer:iterate_batches'], ['pilot-data-adapter-cross-context-v1.json'])

add('selection', 'Adapter selection / Seleção de adapters',
    'When `keys` is absent, `linear_to_lora_layers` discovers supported module paths rather than restricting selection to query/value projections. Its layer slice uses `-max(num_layers, 0)`, so zero and negative values select the entire layer list under Python slicing. A separate full-model pass can select explicitly named modules outside the last-layer slice. An empty explicit key list selects none in the bounded selection arithmetic. These are conditional source selection facts, not an inspected trainable model inventory.',
    'Quando `keys` está ausente, `linear_to_lora_layers` descobre caminhos de módulos suportados, em vez de limitar a seleção às projeções de query/value. Seu recorte de camadas usa `-max(num_layers, 0)`, de modo que valores zero e negativos selecionam a lista inteira de camadas pelo recorte do Python. Uma passagem separada pelo modelo completo pode selecionar módulos nomeados explicitamente fora do recorte das últimas camadas. Uma lista explícita vazia de chaves não seleciona módulos na aritmética limitada de seleção. Esses são fatos condicionais de seleção pelo código, não um inventário inspecionado de um modelo treinável.',
    ['selection:linear_to_lora_layers', 'entry:train_model'], ['lora-target-shape-audit-v1.json'])

add('scale-shapes', 'Low-rank shapes and scale / Formatos de baixo rank e escala',
    'The shown `LoRALinear` constructor declares adapter shapes `(input_dims, r)` and `(r, output_dims)`. It stores the supplied scale in `self.scale` before reusing the local variable for initialization; the forward expression multiplies the update by `self.scale` without dividing by rank. Custom module conversion hooks may follow another path. No adapter object, tensor or forward pass was created or executed here.',
    'O construtor `LoRALinear` mostrado declara os formatos dos adapters `(input_dims, r)` e `(r, output_dims)`. Ele armazena a escala fornecida em `self.scale` antes de reutilizar a variável local na inicialização; a expressão de propagação multiplica a atualização por `self.scale` sem dividir pelo rank. Hooks personalizados de conversão de módulos podem seguir outro caminho. Nenhum objeto de adapter, tensor ou propagação foi criado ou executado aqui.',
    ['adapter:LoRALinear.__init__', 'adapter:LoRALinear.__call__', 'selection:linear_to_lora_layers'])

add('conditional-counts', 'Conditional size example / Exemplo condicional de tamanho',
    'For the pinned community3B metadata, the declared last-two-layer/rank-four model gives434176adapter elements when all seven supported projections are selected, versus81920for explicit query/value projections. The count assumes the reviewed shapes and conversion route. Element-byte illustrations are hypothetical; they omit actual dtype, optimizer state, activations, transient allocations and Metal behavior. They do not demonstrate feasibility on the16GiB host.',
    'Para os metadados fixados do modelo comunitário3B, o modelo declarado com as últimas duas camadas e rank quatro resulta em434176elementos de adapter quando as sete projeções suportadas são selecionadas, contra81920para projeções explícitas de query/value. A contagem pressupõe os formatos e o caminho de conversão revisados. Ilustrações de bytes por elemento são hipotéticas; omitem dtype real, estado do otimizador, ativações, alocações transitórias e comportamento do Metal. Elas não demonstram viabilidade no host de16GiB.',
    ['selection:linear_to_lora_layers', 'adapter:LoRALinear.from_base'], ['lora-target-shape-audit-v1.json'])

add('resume', 'Persistence and resume / Persistência e retomada',
    '`train_model` loads optional adapter weights before constructing a new optimizer. The selected `train` source saves flattened trainable parameters to adapter files periodically and at completion; its shown save payload does not include optimizer, random state or data position. Thus the inspected weights-only path is not verified exact-state continuation. Atomic persistence, interrupted writes and actual training recovery remain unexecuted.',
    '`train_model` carrega pesos opcionais de adapter antes de construir um novo otimizador. O código selecionado de `train` salva parâmetros treináveis achatados em arquivos de adapter periodicamente e na conclusão; a carga salva mostrada não inclui otimizador, estado aleatório ou posição nos dados. Assim, o caminho inspecionado baseado apenas em pesos não é uma continuação verificada de estado exato. Persistência atômica, gravações interrompidas e recuperação real de treinamento permanecem não executadas.',
    ['entry:train_model', 'trainer:train'])

add('review-boundary', 'Limits and review boundary / Limites e revisão',
    'The source package license is preserved, while training rights, owner-approved targets and evaluation independence remain unapproved. No training launch command or executable trainer configuration is provided. The example below is an owned review record, not native training input. Parser admission, small metadata, compiler recovery and repeated Python contexts do not satisfy all nine readiness gates; the current decision remains NO-GO.',
    'A licença do pacote de código está preservada, enquanto direitos de treinamento, alvos aprovados pelo proprietário e independência de avaliação permanecem sem aprovação. Nenhum comando de início de treinamento ou configuração executável do trainer é fornecido. O exemplo abaixo é um registro próprio de revisão, não uma entrada nativa de treinamento. Admissão pelo parser, metadados pequenos, recuperação de compiladores e contextos repetidos de Python não satisfazem os nove requisitos de prontidão; a decisão atual permanece NO-GO.',
    ['entry:run', 'entry:main'])

faq_specs = [
    ('no-train', 'Does omitting the training flag prevent model loading?', 'Omitir o indicador de treinamento impede o carregamento do modelo?', 'entry-order'),
    ('merge', 'Does every configuration value override a parser default?', 'Todo valor da configuração substitui um padrão do parser?', 'merge'),
    ('approval', 'Does a supported dataset format establish training approval?', 'Um formato de dataset suportado estabelece aprovação para treinamento?', 'format-admission'),
    ('mask', 'Does a prompt offset prove valid nonempty assistant supervision?', 'Um deslocamento de prompt comprova supervisão válida e não vazia do assistente?', 'mask-interface'),
    ('cache', 'Does cached item length always count processed tokens?', 'O comprimento de um item em cache sempre conta os tokens processados?', 'cache'),
    ('targets', 'Do omitted keys select only query/value adapters in two layers?', 'Chaves omitidas selecionam somente adapters de query/value em duas camadas?', 'selection'),
    ('resume', 'Does loading saved adapter weights restore exact training state?', 'Carregar pesos salvos de adapter restaura o estado exato do treinamento?', 'resume'),
]
by_id = {claim['id']: claim for claim in claims}
faqs = []
for identity, en, pt, claim_id in faq_specs:
    claim = by_id[claim_id]
    faqs.append({'id': identity, 'claim_ids': [claim_id], 'question': {'en': en, 'pt-br': pt},
                 'answer': {'en': claim['en'], 'pt-br': claim['pt-br']}, 'evidence_ids': claim['evidence_ids'],
                 'owner_approved': False, 'training_gold': False, 'training_use_approved': False})

example = {'kind': 'owned-review-record-not-trainer-input', 'source_revision': pack['revision'],
           'owner_approved': False, 'training_use_approved': False, 'evaluation_excluded_from_training': True,
           'launch_allowed': False, 'decision': 'NO-GO'}
directory = P / 'mlx-admission-chapter-candidates-v1'
directory.mkdir(exist_ok=False)
for language in ['en', 'pt-br']:
    title = 'MLX-LM: source contracts at the training boundary' if language == 'en' else 'MLX-LM: contratos do código na fronteira do treinamento'
    lines = ['# ' + title, '', '**SOURCE-REVIEWED CANDIDATE — NOT OWNER GOLD — NOT PUBLISHED**', '',
             'Revision: `' + pack['revision'] + '`. Group: `mlx-framework-readiness-development-exposed`.', '']
    for claim in claims:
        heading = claim['section'].split(' / ')[0 if language == 'en' else 1]
        lines += ['## ' + heading, '', claim[language], '',
                  'Sources: ' + ', '.join('[' + key + '](' + pack['units'][key]['git_url'] + ')' for key in claim['evidence_ids']) + '.', '']
    lines += ['## Review record / Registro de revisão', '', '```json', json.dumps(example, ensure_ascii=False, indent=2), '```', '', '## FAQ', '']
    for faq in faqs:
        lines += ['### ' + faq['question'][language], '', faq['answer'][language], '',
                  'Sources: ' + ', '.join('[' + key + '](' + pack['units'][key]['git_url'] + ')' for key in faq['evidence_ids']) + '.', '']
    (directory / (language + '.md')).write_text('\n'.join(lines))

record = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'repository': 'ml-explore/mlx-lm',
          'revision': pack['revision'], 'source_pack': pack_path.name,
          'source_pack_sha256': hashlib.sha256(pack_path.read_bytes()).hexdigest(), 'claims': claims, 'faq': faqs,
          'example': example, 'files': [{'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(directory.iterdir())],
          'source_family_group': 'mlx-framework-readiness-development-exposed', 'license': pack['license'],
          'owner_approved': False, 'training_gold': False, 'training_use_approved': False,
          'publication_authorized': False, 'automatic_candidate_applier_supported': False,
          'neural_generation_used': False, 'new_model_calls': 0, 'full_framework_execution': False,
          'interpretation': 'Source architecture candidate; prior pure function/class observations are explicitly scoped. FAQ answers derive from chapter claims and are not independent targets. No training command/configuration or actual dataset export.'}
with (P / 'mlx-admission-chapter-ledger-v1.json').open('x') as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'claims': len(claims), 'faq_pairs': len(faqs), 'candidate_files': len(record['files'])}))
