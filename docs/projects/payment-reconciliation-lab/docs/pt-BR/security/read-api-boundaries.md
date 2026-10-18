# Segurança da API de leitura e futuras fronteiras de pagamento

[English](../../en/security/read-api-boundaries.md) | [Português brasileiro](read-api-boundaries.md)

Revisão estática do código: 2026-10-10. Fatos implementados, teoria geral e mudanças hipotéticas são separados abaixo. Comandos runtime não foram executados.

Spring Security permite GETs específicos de produtos/health e OpenAPI no perfil dev; depois nega todas as outras rotas. Não há login persistido, modelo de roles ou administrador autenticado. CORS permite origens configuradas, GET, Accept/Content-Type e nenhuma credencial; clientes fora do navegador não aplicam CORS. Sessões stateless e CSRF desabilitado correspondem à superfície atual somente leitura, mas não garantem futuro projeto seguro de escrita autenticada por cookie. Rotas bloqueadas produzem 403 Problem Details genérico.

A configuração base oculta mensagens/stack traces/erros de binding nas respostas. `ApiExceptionHandler` registra exceções inesperadas e retorna 500 genérico. Logs detalhados exigem acesso restrito/redação: sanitizar o cliente não sanitiza diagnóstico do servidor. Credenciais de banco por ambiente são configuração, não documentação pública incorporada; esta revisão não leu arquivos reais de ambiente. Portas locais do banco têm bind em loopback; é isolamento de desenvolvimento, não perímetro produtivo auditado.

Stripe não está implementado: não há consumidor SDK, binding, verificação de webhook, chamada de provedor ou chave Stripe injetada no Compose. Entrada reservada em template não muda isso. Conciliação futura exigiria revisão autorizada, autenticação de eventos do provedor, política de duplicata/replay e auditoria. Payload assinado, TLS, identidade de aplicação e idempotência protegem fronteiras distintas; nenhuma pode ser atribuída à política atual de CORS/catálogo. São requisitos hipotéticos, não controles entregues.
