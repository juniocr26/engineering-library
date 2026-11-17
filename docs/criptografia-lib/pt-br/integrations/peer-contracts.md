# Fronteiras de integração — Criptografia Lib

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contratos e autoridades

Interface pública: `new Crypto(string $algorithm, string $privateKey)`, `encrypt(string): string`, `decrypt(string): string`. O prefixo exato é `CLIB:1:A256CBC:HS256:`. O restante é Base64 canônico de IV + ciphertext + tag de 32 bytes. A leitura valida prefixo, codificação canônica, tamanho mínimo/alinhado e igualdade da tag em tempo constante antes da decifragem OpenSSL. Cabeçalho/codificação/estrutura inválidos lançam InvalidArgumentException; falha de autenticação/decifragem lança RuntimeException.

Os links abaixo navegam à contraparte documentada. Não comprovam compatibilidade entre versões implantadas. Revisões e caminhos inspecionados ficam nos registros source-review; as relações acima se limitam aos consumidores inspecionados.

- [VivaBem](../../../vivabem/pt-br/architecture/contracts.md)
- [Carteira Digital](../../../carteira-digital/pt-br/architecture/contracts.md)
- [Cofre Paciente](../../../cofre-paciente/pt-br/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)
