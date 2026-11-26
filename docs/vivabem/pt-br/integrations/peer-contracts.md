# Fronteiras de integração — VivaBem

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contratos e autoridades

ClienteHttpCofrePaciente rejeita sobrescrita de claims protegidas, caminhos não suportados, query/fragment/userinfo e redirects; assina o mapa fechado de operações com duração máxima de 60 segundos. Exige sucesso HTTP e status=success no corpo, converte erro de conexão em 504 e outras falhas em 500. ClienteHttpCarteiraDigital possui rotas permitidas de compra, cartões, histórico e status; consultarEstorno permanece legado indisponível. AssinadorEventoHub emite eventos Redis diretos vinculados ao conteúdo por RS256; autenticação de sessão do destinatário é capacidade separada.

Os links abaixo navegam à contraparte documentada. Não comprovam compatibilidade entre versões implantadas. Revisões e caminhos inspecionados ficam nos registros source-review; as relações acima se limitam aos consumidores inspecionados.

- [Carteira Digital](../../../carteira-digital/pt-br/architecture/contracts.md)
- [Cofre Paciente](../../../cofre-paciente/pt-br/architecture/contracts.md)
- [Hub VivaBem](../../../hub-vivabem/pt-br/architecture/contracts.md)
- [Criptografia Lib](../../../criptografia-lib/pt-br/architecture/contracts.md)
- [script-auditoria-envs](../../../script-auditoria-envs/pt-br/architecture/contracts.md)
- [VivaBem Android](../../../vivabem-android/pt-br/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Current HTTP / HTTP atual](../../../../../vivabem/docs/pt-br/api/http-contracts.md).
