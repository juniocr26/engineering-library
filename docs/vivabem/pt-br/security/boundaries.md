# Fronteiras de acesso e segurança após commit parcial

[Sumário](../index.md) | [English](../../en/security/boundaries.md)

Revisado em 2026-11-10 em `d412cc7`. Público: mantenedores e revisores de segurança. A: inspeção, sem pentest/certificação. Distingue autorização do produto, sessões técnicas e callbacks, sem alterar mecanismos.

<!-- reading-section: product -->
## Identidade e atualização de perfil

`config/auth.php` seleciona guard web com driver redis-session e provider `Usuario`. `GuardaSessaoRedis` resolve credencial por `SessaoAutenticacaoRedis`, confere usuário da sessão e aceita fallback de cookie apenas para credencial persistente. Probes passivos não qualificam renovação. Login gira contexto e revoga associação FCM anterior; logout revoga esse contexto. Não comprova logout de todos os dispositivos ou atestação Android.

`Controller::captureProfileAuthorization` exige OID correspondente, papel profissional/paciente e autorização resolvida antes da edição. `preserveProfileAuthorization` é chamado após commit: recarrega usuário, compara fingerprints de senha e tenta preservar autorização após troca. Falha Redis pós-commit pode gerar HTTP 503 informando que perfil foi salvo mas autenticação não pôde ser confirmada. Autorização inválida redireciona ao login. Não orientar presunção de rollback ou reenvio cego de atualização já persistida.

Formulários de leitura, cadastro e atualização não compartilham toda checagem de titularidade; auth na rota não é auditoria completa de toda leitura. `Usuario` oculta password/remember_token/chave_pix na serialização, mas banco bruto, exportações e payloads não revisados permanecem sensíveis. Conversão/limpeza de foto são separadas do rollback SQL.

<!-- reading-section: recipient -->
## Probe de destinatário Hub

`SessaoHubControlador` suporta drivers configurados database/file/redis/memcached, exige ID alfanumérico de 40 caracteres, clona driver e lê sem salvar. Resolve credencial já armazenada e exige igualdade entre ID do guard na sessão e usuário resolvido. Não recupera login por cookie persistente quando a sessão está ausente.

Resposta contém purpose hub-recipient-session, project vivabem, userId e psychologist, com no-store/private e Vary Cookie. `routes/web.php` exclui startup/save normal, CSRF e renovação de presença desse probe, mantendo decifração do cookie. Autentica contexto atual inspecionado, sem aceitar userId arbitrário do browser. Entrega/revalidação Hub é contrato de outro repositório e não foi executada aqui.

<!-- reading-section: operator -->
## Autorização do operador técnico

`AutenticarSaude` exige identidade configurada, fingerprint correspondente e `SessaoPainelTecnico` válida. Estado inválido limpa autorização e retorna JSON 401 ou login próprio. Registro técnico Redis tem TTL de 90 segundos. Somente heartbeat já autorizado estende chave existente; ausente nunca é recriada, e falha Redis retorna false. Separação de sessões não significa Cockpit atual independente da disponibilidade Redis.

`AcessoPainel` e `config/panel_access.php` governam desafios de confirmação separados, com TTL de fonte de 600 segundos. Desafio, sessão técnica, autorização do produto, cookie e presença são registros/durações distintos. Entrega de login/confirmação e acesso implantado não foram verificados; documentação não contorna mecanismos.

Acesso Cockpit pode permitir edição de bancos, CSV e mutações broker conforme checagens e permissões efetivas. Deve permanecer privado. Coleta Docker somente leitura e execução Docker da auditoria de ambiente são capacidades diferentes; não inferir fronteira de infraestrutura globalmente read-only. Consultar [Cockpit](../operations/technical-cockpit.md).

<!-- reading-section: service -->
## Claims, criptografia e saída sensível

Callbacks financeiros validam HS256 issuer/audience/scope/tempo/subject e vinculação de corpo/caminho; `JwtMiddleware` genérico possui ramo mais fraco sem claims e não representa contrato completo. Criptografia/integridade, identidade de serviço e autorização de negócio são responsabilidades separadas. Credencial aprovada não autoriza atendimento de outro dono. [HTTP](../api/index.md) detalha campos/erros.

Não registrar corpos financeiros criptografados brutos, JWTs, chaves, prontuários ou CSV em exemplos de diagnóstico. Dados criptografados ainda podem ser sensíveis. Callbacks inspecionados registram etapa/classe/status, sem comprovar auditoria de todo logging do corpus. Não foram adicionados snapshots ou valores reais de ambiente.

`DetectorRequisicaoAplicativoOficial` reconhece query/header/user-agent configurados e flag de sessão; são sinais de contexto, sem atestação ou identidade independente. `ExecutorAuditoria::request` é operacional até em list, que pode criar proposta ausente. Submit invoca `--apply-audit` global e depois refresh do projeto; seleção na interface não comprova aplicação restrita ao diretório. Não chamar list/submit como probe documental. Fronteiras preservadas foram reconferidas sem ler ambientes reais.

<!-- reading-section: validation -->
## Evidências, lacunas e manutenção

Fontes: `config/auth.php`, `config/panel_access.php`, `app/Auth/GuardaSessaoRedis.php`, `app/Http/Controllers/{Controller,SessaoHubControlador,ResultadoCompraSaldoControlador,OperacaoFinanceiraInternaControlador}.php`, `app/Http/Middleware/{AutenticarSaude,JwtMiddleware}.php`, `app/Services/{AcessoPainel,SessaoPainelTecnico}.php`, `routes/web.php`, `bootstrap/app.php`.

A [suíte](../operations/backend-testing.md) verifica regras selecionadas de login, cadastro, participação, notificação e push com doubles/SQLite. Não testa guard Redis completo, desafio técnico, permissões implantadas, toda autorização de leitura, coletor ou navegador. Rever idiomas/coleção após mudanças em autenticação, scopes, edição, duração ou capacidades. Nenhuma correção de segurança ou teste novo foi implementado nesta tarefa documental.
