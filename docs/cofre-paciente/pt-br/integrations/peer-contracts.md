# Fronteiras de integração — Cofre Paciente

[Index / Índice](../index.md)

<!-- reading-section: contracts -->

## Contratos e autoridades

A política fechada contém nove caminhos POST: links insert/get/update; cartoes insert/get/delete; avaliacoes insert/avaliados/buscar-media-avaliacoes, todos sob /api/. JwtMiddleware exige HS256, credenciais configuradas, iat/exp inteiros, duração positiva de no máximo 60 segundos e validade atual. Falha de autenticação é 401, transporte externo 422 e vínculo da operação 403. Query strings, métodos incorretos, scopes curingas e bytes cifrados alterados falham. Replay exato ainda pode passar dentro da validade do token.

Os links abaixo navegam à contraparte documentada. Não comprovam compatibilidade entre versões implantadas. Revisões e caminhos inspecionados ficam nos registros source-review; as relações acima se limitam aos consumidores inspecionados.

- [VivaBem](../../../vivabem/pt-br/architecture/contracts.md)
- [Criptografia Lib](../../../criptografia-lib/pt-br/architecture/contracts.md)

[Evidence and limits / Evidências e limites](../operations/source-review.md)

[Current HTTP / HTTP atual](../../../../../cofre-paciente/docs/pt-br/api/http-contracts.md).
