# Fronteiras de confiança — acesso-servidor

[English](../../en/security/boundaries.md) | [Português brasileiro](boundaries.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `ba70952fd63992c85aa153f141a39fadf33360a0`.

<!-- reading-section: mechanisms -->

## Mecanismos e limites

Deploy exige alvo autorizado e identidades originais. Verificações de raiz/caminho restringem operações, sem tornar rollout parcial de vários projetos atômico. Roundtrip criptográfico valida aquele consumidor/configuração, não todos os registros ou ownership. Logs privados podem conter contexto operacional sensível e não devem ser publicados. Nenhum diretório secreto, chave SSH, PEM, credencial de servidor ou banco foi aberto nesta tarefa.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
