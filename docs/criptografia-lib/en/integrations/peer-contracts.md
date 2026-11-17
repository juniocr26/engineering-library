# Integration boundaries — Criptografia Lib

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contracts and authorities

Public interface: `new Crypto(string $algorithm, string $privateKey)`, `encrypt(string): string`, `decrypt(string): string`. The exact prefix is `CLIB:1:A256CBC:HS256:`. The remainder is canonical Base64 of IV + ciphertext + 32-byte tag. Decryption validates prefix, canonical encoding, minimum/aligned length and constant-time tag equality before OpenSSL decryption. Malformed headers/encoding/structure throw InvalidArgumentException; failed authentication/decryption throws RuntimeException.

The following links navigate to the documented counterpart. They are not evidence of deployed version compatibility. Source revisions and inspected paths remain in each source-review record; relationships above are limited to those inspected consumers.

- [VivaBem](../../../vivabem/en/architecture/contracts.md)
- [Carteira Digital](../../../carteira-digital/en/architecture/contracts.md)
- [Cofre Paciente](../../../cofre-paciente/en/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)
