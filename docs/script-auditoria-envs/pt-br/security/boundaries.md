# Fronteiras de confiança — script-auditoria-envs

[English](../../en/security/boundaries.md) | [Português brasileiro](boundaries.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `2e5d5de71d1323b4e588e04f06784324802ae0d3`.

<!-- reading-section: mechanisms -->

## Mecanismos e limites

A descoberta ignora diretórios/arquivos simbólicos e exclusões exatas de dependências/build; não constitui sandbox universal de diretórios secretos. O modo de propostas usa descritores no-follow e bloqueio cooperativo. Editores não cooperantes e semântica da plataforma/filesystem continuam como limites. Backups são material sensível em texto; permissões restritas não são criptografia. A varredura padrão pode incluir irmãos não relacionados e nunca deve ser usada como verificação documental.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
