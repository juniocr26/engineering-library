# Local recovery handoff — V6 source and evidence cut

This handoff describes the cut independently restored at 09:59 UTC on 2026-11-20.
Read the final campaign report and latest checkpoint for later metadata. Recovery
was exercised in another directory on the same host; remote backup, disk-loss
recovery, cold model boot and training are not demonstrated.

## Preserve the complete chain

Retain all six archives below, each `creation-receipt.json` and `file-manifest.json`,
`restore_source_evidence_delta_v6.py`, and later checkpoints. Apply components in
order. V6 alone does not contain all sources. Retain older evidence, including
failed experiments, instead of cleaning it away.

| Order | Archive relative to the library root | Bytes | SHA-256 |
|---|---|---:|---|
| 1 | `.local-backups/documentation-intelligence-20261119/source-evidence-recovery-v1/source-evidence.tar.gz` | 315908501 | `4ca675a73f24d18d39d9cab257c9d26860476e871f3d900ef86844c8860e1e95` |
| 2 | `.local-backups/documentation-intelligence-20261119/source-evidence-delta-v2/evidence-delta.tar.gz` | 64502095 | `30adabed7c9614454dec0ec81ad520bdfc96344c41d25f18a84bd1f1e80ea8aa` |
| 3 | `.local-backups/documentation-intelligence-20261119/source-evidence-delta-v3/evidence-delta.tar.gz` | 7082627 | `d303cf268fdc6016df0f19ee0b1a77892bd37661b2f70285c97f53e3ca32de24` |
| 4 | `.local-backups/documentation-intelligence-20261119/source-evidence-delta-v4/evidence-delta.tar.gz` | 7859580 | `3616d18531ee58d136ce8635ec1312e7b8ce837a594f52a5a590fc5445046e4d` |
| 5 | `.local-backups/documentation-intelligence-20261119/source-evidence-delta-v5/evidence-delta.tar.gz` | 11767034 | `ca1da97490b7f1a46f523bdb115d2048bc8fcd86f57e6876e906c3974f8379f0` |
| 6 | `.local-backups/documentation-intelligence-20261119/source-evidence-delta-v6/evidence-delta.tar.gz` | 3315397 | `96054ee2abb8af21c5cf943ae86c558287d5e8a934f0422344aece649c8256d8` |

Paths are under `.local-backups/documentation-intelligence-20261119/`. Git ignores
do not create backups: a clone or later commit does not preserve these files.
There was no upload or remote synchronization. Hashes detect changes relative to
trusted receipts; they are neither signatures nor protection against consistent
replacement of both an archive and its receipt.

## Verified procedure and limits

The executed command, from the `engineering-library` root, was:

```sh
python3 .local-backups/documentation-intelligence-20261119/restore_source_evidence_delta_v6.py
```

This is an available verification recipe, not an automatic resume action. It
creates a new directory under `/private/tmp`, reads the sealed components in order,
and writes local receipts. Each run consumes additional disk space. Do not run
with `python -O`: this research recipe uses assertions. Never extract over the
checkout, a model store, or an earlier recovery. The completed exercise is at
`/private/tmp/el-source-evidence-base-delta-v6-1oz1fzl1`.

It verified 8,920 files, 77 content-preserved overlays, 1,951 knowledge items,
305 records and 1,271 direct references, 77 FAQ pairs, 279 physical source spans,
588 document spans and 192 reader documents with 392 edges. Its 83 code/test files
match operational V7, which passed 278 tests on macOS and Linux. The recipe did
not repeat those tests. Historical absolute fixture paths were lexically relocated
into the restored copy; original fixture paths were not used as evidence.

## Separate retained components

Operational V7 (`operational-recovery-v7/operational-code.tar.gz`) is 25,293,922 bytes,
SHA-256 `ab6fd71e975b0a83c0485f0a816972f7ee19117e0b55ae6d8d8b0d5e914a8678`.
It captures the tested code. Some public receipt filenames were corrected later;
source chain V6 overlays the correct receipts without rewriting that capsule.

Model weights, the Ollama image and extracted runtimes are separate components.
`agent/recovery/model-bundle.json` indexes the 14 model parts; local paths are in
`agent/recovery/manifest.json`. Retaining the JSON without its parts is insufficient.
The GGUF SHA-256 is
`dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff`,
distinct from runtime digest
`a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72`.
The legacy metadata wrapper has its own identity; do not replace it with native
namespace bytes merely because both resolve to the same weights.

The preserved image is 2,872,640,512 bytes, SHA-256
`18da54da82a8fb31195048d6664559cf582c84bc531f96d8db95a21257bf6f6e`.
Its four Linux ARM64 layers were verified; amd64 payload is absent. No image load
or restored model serving occurred. The V3 main catalog and seven-restored-tree
supplement describe separate files; catalogs do not contain those payloads.

## Interrupted operations

Preserve partial candidate roots and process receipts. An existing `result.json`
is not proof of completion: one of three exercises ended after writing it but
before the CLI reply. Do not blindly repeat inference with uncertain completion.
The CLI refused all three same-path retries. Only explicit new requests into new
roots prepared candidates while preserving partial evidence. These exercises
killed three owned processes after synchronized writes; they did not establish
power-loss or filesystem-crash durability.

Keep the backend stopped and all changes unstaged. Recovery does not authorize
publication, commits, gold data, training, service startup, or replacement stores.
Sources and documentation still require owner review. The restore receipt and
final report postdate the V6 seal and belong in the final metadata/checkpoint layer.
