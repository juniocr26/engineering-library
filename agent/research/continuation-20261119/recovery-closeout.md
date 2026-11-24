# Final recovery cut and evidence boundary

This note records the recovery procedure and artifact locations before the final
operational cut. It does not invent that cut's future archive hash or claim that
an archive can contain its own final creation receipt.

The original verified base remains at
`.local-backups/continuation-20261119/capsule-cuts/base-v1/base.tar`.
Its SHA-256 is
`390d7057dad9b4146c0d769ae010ae60c653854a35429da28f4dca6fe4cb3b03`.
The first dated operational cut remains under `capsule-cuts/final-op-v1/`;
its proof is indexed by `current-aggregate-recovery.json`.

The closing operational complement is written into a new
`.local-backups/continuation-20261119/capsule-cuts/final-op-v2/` directory.
A fresh APFS copy of the original verified base restoration is the only overlay
target. The original base archive, original base restoration, original model
store and first operational cut remain unchanged.

Read the adjacent `aggregate-verification.json`, `operational-cut/creation.json`,
`operational-cut/restoration.json` and `current-source-catalog.json` for actual
completion, archive/manifest hashes, individually reconstructed files, contained
links and current knowledge/model checks. The catalog assigns an origin, purpose
and inspection scope to each entry; a byte check does not imply individual manual
semantic review. Sidecars and archive outputs exclude themselves to prevent hash
cycles and recursive archive capture. The top-level `closing-receipt.json` in
`final-op-v2` supplies the actual closing time and final working-file hashes.

The base plus closing complement reconstruct the selected current working files,
private research history and approved model store. Retained earlier cut archives
remain separate local artifacts; their omission from a recursive inner archive
does not mean they were deleted. This is local same-host recovery. No remote LFS
upload/download, cold Docker import, different-OS restoration or training pilot
is implied. Two earlier independently restored stores already passed actual
inference; no third smoke was scheduled merely to repeat that evidence.

The owner requested approximately two additional hours after the power restart.
The content close at 21:14 UTC records more than two hours since that request and
about 8.91 calendar hours from the original campaign start. The previously
communicated 22:19 UTC planning target is preserved as a plan, not presented as
elapsed execution. Exact content and closing times remain in the report and
closing receipt. Fifty-three queue candidates remain pending distinct preflight;
none is silently marked complete or used to repeat a rejected experiment.
