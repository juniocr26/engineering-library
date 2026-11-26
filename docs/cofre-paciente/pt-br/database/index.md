# Coleções MongoDB e exclusão observada

2026-11-04. As coleções de domínio atuais são cartoes, cartoes_debito, links, avaliacoes_psicologos e media_avaliacoes. Mapas de cartões são vinculados ao titular e armazenam referências mínimas cifradas do provedor; não são armazenamento de PAN/CVC. Hashes observados e comparação/exclusão do valor exato protegem substituição concorrente. Resultados parciais/ilegíveis diferem de armazenamento vazio. Atomicidade de documento único não abrange SQL ou efeitos remotos; índices implantados e formatos legados não foram inspecionados.

O repositório de origem mantém detalhes e evidências de código; a revisão foi estática, sem acesso a banco ou provedor.

- [Collections / Coleções](../../../../../cofre-paciente/docs/pt-br/database/database-audit.md)
- [Lifecycle / Ciclo de vida](../../../../../cofre-paciente/docs/pt-br/architecture/current-implementation.md)

[Index / Índice](../index.md)
