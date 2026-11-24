# MLX-LM: source contracts at the training boundary

**SOURCE-REVIEWED CANDIDATE — NOT OWNER GOLD — NOT PUBLISHED**

Revision: `2d4df8d94a80c0f9f8794e54fafee08728b04fc6`. Group: `mlx-framework-readiness-development-exposed`.

## Purpose and dependency boundary

The selected `mlx_lm.lora` entrypoint coordinates arguments, model and dataset loading, adapter selection, training and optional evaluation. Its module imports `mlx.core`, `mlx.nn`, `mlx.optimizers`, `numpy` and `yaml`; this chapter inspects source without importing that module. Earlier isolated observations executed only the admitted pure argument builder and dataset adapters with owned method sinks. No real tokenizer, model, tensor, trainer or optimizer was executed.

Sources: [entry:preamble](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L1-L85), [entry:run](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L344-L376), [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319).

## Architecture and loading order

`main` merges configuration and calls `run`. In `run`, reporting setup, `load` and `load_dataset` precede the decision between testing, training and the missing-mode error. Therefore omitting `--train` does not make the actual entrypoint a safe no-load dry run. These source functions were not invoked; no download or model loading was observed.

Sources: [entry:main](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L379-L398), [entry:run](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L344-L376).

## Configuration precedence

The merge fills an argument from configuration only when `args.get(k, None) is None`, then fills remaining unspecified values from defaults. Non-null parser defaults therefore block matching configuration values: the owned builder observations retained `trust_remote_code=False` and `clear_cache_threshold=0` despite conflicting configuration. Configuration values also bypass argparse choice/type parsing. This is source admission analysis, not a claim that every downstream value will execute successfully.

Sources: [entry:build_parser](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L86-L223), [entry:main](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L379-L398), [entry:preamble](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L1-L85).

## Data inputs and admission

`create_dataset` examines `data[0]`: prompt/completion keys take precedence, followed by the chat key, then the text key. It does not inspect Engineering Library owner approval or evaluation exclusion fields. Owned native-shaped chat, completion and text rows were processed despite false approval flags; those rows are not the frozen305 schema. Empty outer input raised an indexing error, and mixed row formats failed when accessing the incompatible later row. Format acceptance is not training authorization.

Sources: [datasets:create_dataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L178-L205).

## Local and remote dataset boundaries

`load_local_dataset` names `train.jsonl`, `valid.jsonl` and `test.jsonl`; a missing subset returns an empty list. A present empty file instead reaches first-row format selection. In `load_dataset`, a nonexistent local data path falls through to the remote dataset branch. Training with an empty validation set produces a warning rather than an independent evaluation guarantee. No file loader or remote dataset loader was executed in the owned adapter study.

Sources: [datasets:load_local_dataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L208-L222), [datasets:load_dataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L312-L335), [datasets:create_dataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L178-L205).

## Token and prompt interfaces

`ChatDataset.process` returns full template tokens and, when masking is enabled, an offset computed from a separate template call on all but the last message. It compares the last role with `assistant` to select the generation-prompt flag, but does not validate matching token prefixes, offset bounds or nonempty assistant content. Four owned method-return controls expose those unchecked assumptions. Their raw target intervals are not shifted trainer supervision counts or evidence of a real tokenizer defect.

Sources: [datasets:ChatDataset.process](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L59-L79), [datasets:CompletionsDataset.process](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L109-L129), [trainer:default_loss](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L88-L101).

## Batching and loss scope

`iterate_batches` pads with zeros, truncates retained lengths and supplies offset/length pairs. `default_loss` shifts targets by one and writes an inclusive upper length comparison. Earlier source-derived integer cases showed padding positions or zero eligible positions for particular inputs. Those conditional arithmetic findings do not execute MLX or measure actual training loss. A future preflight must inspect real token identity, prefix alignment and the effective shifted target domain together.

Sources: [trainer:iterate_batches](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L104-L175), [trainer:default_loss](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L88-L101).

## Caching and length proxies

`CacheDataset` memoizes processed rows while `itemlen` returns the length of the underlying raw item. `iterate_batches` uses this method when its dataset is a cache wrapper. In the owned dictionary example, raw lengths1and4 disagreed with processed token lengths11and3 and reversed the corresponding sort order. This establishes a proxy difference in the shown composition, not a throughput, memory or training-quality result.

Sources: [datasets:CacheDataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L161-L175), [trainer:iterate_batches](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L104-L175), [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319).

## Concatenation and row identity

`ConcatenatedDataset.__getitem__` writes `_dataset` into the returned original row and later uses that field for processing dispatch. Owned shared-row accesses changed the held row routing metadata. With two and three rows in separate datasets, indexing at the declared length returned a row, while Python fallback iteration yielded eight rows rather than five. These bounded observations do not establish that the native indexed batching path performs the same fallback iteration.

Sources: [datasets:ConcatenatedDataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L138-L158), [trainer:iterate_batches](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L104-L175).

## Adapter selection

When `keys` is absent, `linear_to_lora_layers` discovers supported module paths rather than restricting selection to query/value projections. Its layer slice uses `-max(num_layers, 0)`, so zero and negative values select the entire layer list under Python slicing. A separate full-model pass can select explicitly named modules outside the last-layer slice. An empty explicit key list selects none in the bounded selection arithmetic. These are conditional source selection facts, not an inspected trainable model inventory.

Sources: [selection:linear_to_lora_layers](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/utils.py#L46-L126), [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319).

## Low-rank shapes and scale

The shown `LoRALinear` constructor declares adapter shapes `(input_dims, r)` and `(r, output_dims)`. It stores the supplied scale in `self.scale` before reusing the local variable for initialization; the forward expression multiplies the update by `self.scale` without dividing by rank. Custom module conversion hooks may follow another path. No adapter object, tensor or forward pass was created or executed here.

Sources: [adapter:LoRALinear.__init__](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/lora.py#L67-L93), [adapter:LoRALinear.__call__](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/lora.py#L95-L98), [selection:linear_to_lora_layers](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/utils.py#L46-L126).

## Conditional size example

For the pinned community3B metadata, the declared last-two-layer/rank-four model gives434176adapter elements when all seven supported projections are selected, versus81920for explicit query/value projections. The count assumes the reviewed shapes and conversion route. Element-byte illustrations are hypothetical; they omit actual dtype, optimizer state, activations, transient allocations and Metal behavior. They do not demonstrate feasibility on the16GiB host.

Sources: [selection:linear_to_lora_layers](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/utils.py#L46-L126), [adapter:LoRALinear.from_base](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/lora.py#L12-L32).

## Persistence and resume

`train_model` loads optional adapter weights before constructing a new optimizer. The selected `train` source saves flattened trainable parameters to adapter files periodically and at completion; its shown save payload does not include optimizer, random state or data position. Thus the inspected weights-only path is not verified exact-state continuation. Atomic persistence, interrupted writes and actual training recovery remain unexecuted.

Sources: [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319), [trainer:train](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L221-L380).

## Limits and review boundary

The source package license is preserved, while training rights, owner-approved targets and evaluation independence remain unapproved. No training launch command or executable trainer configuration is provided. The example below is an owned review record, not native training input. Parser admission, small metadata, compiler recovery and repeated Python contexts do not satisfy all nine readiness gates; the current decision remains NO-GO.

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

### Does omitting the training flag prevent model loading?

`main` merges configuration and calls `run`. In `run`, reporting setup, `load` and `load_dataset` precede the decision between testing, training and the missing-mode error. Therefore omitting `--train` does not make the actual entrypoint a safe no-load dry run. These source functions were not invoked; no download or model loading was observed.

Sources: [entry:main](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L379-L398), [entry:run](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L344-L376).

### Does every configuration value override a parser default?

The merge fills an argument from configuration only when `args.get(k, None) is None`, then fills remaining unspecified values from defaults. Non-null parser defaults therefore block matching configuration values: the owned builder observations retained `trust_remote_code=False` and `clear_cache_threshold=0` despite conflicting configuration. Configuration values also bypass argparse choice/type parsing. This is source admission analysis, not a claim that every downstream value will execute successfully.

Sources: [entry:build_parser](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L86-L223), [entry:main](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L379-L398), [entry:preamble](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L1-L85).

### Does a supported dataset format establish training approval?

`create_dataset` examines `data[0]`: prompt/completion keys take precedence, followed by the chat key, then the text key. It does not inspect Engineering Library owner approval or evaluation exclusion fields. Owned native-shaped chat, completion and text rows were processed despite false approval flags; those rows are not the frozen305 schema. Empty outer input raised an indexing error, and mixed row formats failed when accessing the incompatible later row. Format acceptance is not training authorization.

Sources: [datasets:create_dataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L178-L205).

### Does a prompt offset prove valid nonempty assistant supervision?

`ChatDataset.process` returns full template tokens and, when masking is enabled, an offset computed from a separate template call on all but the last message. It compares the last role with `assistant` to select the generation-prompt flag, but does not validate matching token prefixes, offset bounds or nonempty assistant content. Four owned method-return controls expose those unchecked assumptions. Their raw target intervals are not shifted trainer supervision counts or evidence of a real tokenizer defect.

Sources: [datasets:ChatDataset.process](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L59-L79), [datasets:CompletionsDataset.process](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L109-L129), [trainer:default_loss](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L88-L101).

### Does cached item length always count processed tokens?

`CacheDataset` memoizes processed rows while `itemlen` returns the length of the underlying raw item. `iterate_batches` uses this method when its dataset is a cache wrapper. In the owned dictionary example, raw lengths1and4 disagreed with processed token lengths11and3 and reversed the corresponding sort order. This establishes a proxy difference in the shown composition, not a throughput, memory or training-quality result.

Sources: [datasets:CacheDataset](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/datasets.py#L161-L175), [trainer:iterate_batches](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L104-L175), [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319).

### Do omitted keys select only query/value adapters in two layers?

When `keys` is absent, `linear_to_lora_layers` discovers supported module paths rather than restricting selection to query/value projections. Its layer slice uses `-max(num_layers, 0)`, so zero and negative values select the entire layer list under Python slicing. A separate full-model pass can select explicitly named modules outside the last-layer slice. An empty explicit key list selects none in the bounded selection arithmetic. These are conditional source selection facts, not an inspected trainable model inventory.

Sources: [selection:linear_to_lora_layers](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/utils.py#L46-L126), [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319).

### Does loading saved adapter weights restore exact training state?

`train_model` loads optional adapter weights before constructing a new optimizer. The selected `train` source saves flattened trainable parameters to adapter files periodically and at completion; its shown save payload does not include optimizer, random state or data position. Thus the inspected weights-only path is not verified exact-state continuation. Atomic persistence, interrupted writes and actual training recovery remain unexecuted.

Sources: [entry:train_model](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/lora.py#L226-L319), [trainer:train](https://github.com/ml-explore/mlx-lm/blob/2d4df8d94a80c0f9f8794e54fafee08728b04fc6/mlx_lm/tuner/trainer.py#L221-L380).
