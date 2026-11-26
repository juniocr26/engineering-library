# Fronteiras de confiança — Hub VivaBem

[English](../../en/security/boundaries.md) | [Português brasileiro](boundaries.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `e0ab75952946bc3f764dcb4144e404097277933f`.

<!-- reading-section: mechanisms -->

## Mecanismos e limites

Políticas controlam kid/chave/issuer/subject/project confiáveis e permissões de canal/evento/scope. Tokens usam audience hub-publication e duração máxima de 60 segundos; chaves vêm da configuração do operador, não de URLs no token. A identidade do destinatário vem de probe de sessão do Portal e verificações de origem/cookie. Credencial de publicação não concede recepção de navegador. CORS não é autenticação; ownership de namespace ainda depende das ACLs Redis efetivas. Nomes de eventos permitidos podem persistir após retirada da execução financeira.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
