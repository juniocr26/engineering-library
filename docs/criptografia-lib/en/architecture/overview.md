# Architecture and integration boundaries

[Contents](../index.md)

## Verified state and public boundaries — 2026-11-11

Preserved identity: `parceiro-vivabem/criptografia-lib`, namespace `CriptoLib`, version locked by all three consumers `1.1.3.4`. PHP >=8.1 and OpenSSL; construction requires algorithm and key bytes. Authenticated envelopes and explicit configuration do not provide central key management. The TracePaw migration changes no algorithms, key formats or persistence.

Source inspection and local metadata do not confirm Docker image contents, deployment, mounts or external acceptance. This public summary omits internal endpoints, topology, identifiers and private rules; full operational contracts remain in source repositories. No database catalog synchronization was performed.
