# Fronteiras de integração — acesso-servidor

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contratos e autoridades

A CLI aceita --validate, --dry-run ou --deploy, com --migrate apenas em deploy. Ambas as flags de validação escolhem o mesmo modo e chamam cleanup_dependencies antes do preflight: removem vendor/node_modules dos três projetos PHP, node-server/node_modules do Hub e quatro arquivos .env.audit exatos. Não são somente leitura. A seleção de branch exige refs server existentes e rejeita árvores sujas/staged/divergentes/conflitantes. Probes de readiness têm timeout positivo validado e não implementam rollback.

Os links abaixo navegam à contraparte documentada. Não comprovam compatibilidade entre versões implantadas. Revisões e caminhos inspecionados ficam nos registros source-review; as relações acima se limitam aos consumidores inspecionados.

- [VivaBem](../../../vivabem/pt-br/architecture/contracts.md)
- [Carteira Digital](../../../carteira-digital/pt-br/architecture/contracts.md)
- [Cofre Paciente](../../../cofre-paciente/pt-br/architecture/contracts.md)
- [Hub VivaBem](../../../hub-vivabem/pt-br/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)
