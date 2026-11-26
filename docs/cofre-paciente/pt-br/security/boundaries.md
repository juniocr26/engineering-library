# Fronteiras de confiança — Cofre Paciente

[English](../../en/security/boundaries.md) | [Português brasileiro](boundaries.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `85edbcb16fd029235dc74eba12c7b14b164d3d62`.

<!-- reading-section: mechanisms -->

## Mecanismos e limites

PoliticaRequisicaoCofre vincula issuer vivabem, audience cofre-paciente e scope específico do caminho ao SHA-256 de método em maiúsculas + nova linha + caminho exato + nova linha + corpo cifrado. A contraparte do Portal usa o mesmo mapa e rejeita sobrescrita de claims protegidas/redirecionamentos. A cifra é seletiva; não presuma todos os campos Mongo cifrados. A política autentica a capacidade do Portal, sem provar autonomamente autorização de cada ator do navegador nem impedir replay.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
