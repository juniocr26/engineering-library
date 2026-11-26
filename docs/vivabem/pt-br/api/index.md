# Contratos HTTP do Portal e callbacks financeiros

[Sumário](../index.md) | [English](../../en/api/index.md)

Revisado em 2026-11-10 em `d412cc7`. Público: mantenedores de integração/backend. A: rotas/controllers inspecionados, sem execução HTTP ou homologação. Prefixo `/api` é registrado por `AppServiceProvider`; web/auth usam middleware web. Middleware JWT genérico não é o contrato completo dos callbacks.

<!-- reading-section: routes -->
## Famílias de rotas e autorização

| Fronteira | Rotas / responsável | Acesso e efeitos |
| --- | --- | --- |
| Login/ativação/reset | `routes/auth.php`, `ControladorAutenticacao` | Ciclo de sessão do produto; credenciais de ativação/reset são sensíveis |
| Perfis | `routes/web.php`, controllers/FormRequests | Cadastro público e edição autenticada; auth não comprova titularidade de toda leitura |
| Atendimentos | `/atendimento/*`, `/psicologos/agendamento/*` | Auth, participante/estado na operação; agenda, cancelamento, reagendamento e conferência |
| Compras/cartões | `/transacoes/*`, `ControladorTransacao` | Coordenação autenticada Carteira/Cofre; token/referência não é aprovação |
| Push web | `PUT/DELETE /notificacoes/push/inscricao` | Auth do produto e CSRF web |
| Push API | `PUT/DELETE /api/fcm/registrations` | `auth:sanctum`; registro/remoção |
| Resultado de compra | `POST /api/internal/balance-purchases/results` | JWT validado no controller, corpo criptografado e efeitos obrigatórios |
| Operações financeiras | `POST /api/internal/financial-operations/{acao}` | Capacidade de serviço; somente authorize/results |
| Compatibilidade de estorno | `POST /api/internal/financial-refunds/{acao}` | Somente estorno, com prefixo de scope próprio |
| Probe de destinatário Hub | `GET /hub/recipient-session` | Autorização existente, probe sem salvar sessão; exclui middleware normal de persistência/presença |
| Operadores técnicos | `/health/*`, `/audit/*` | Sessões técnicas e CSRF independentes do login do produto |

Mapa de fronteiras, sem afirmar status/corpo idêntico em toda rota. Formulários podem redirecionar, controllers JSON validam campos e domínio pode rejeitar titularidade/estado. A [referência Cockpit](../operations/technical-cockpit.md) detalha operadores. `/api/compra` e `psychologists/payments/webhook-results` não são entradas atuais em `routes/api.php` inspecionado.

<!-- reading-section: callback-auth -->
## Autenticação dos callbacks financeiros

`ResultadoCompraSaldoControlador` e `OperacaoFinanceiraInternaControlador` exigem `body` externo textual, decodificam Bearer HS256 e exigem usuário/senha de serviço configurados não vazios correspondentes às claims, issuer `carteira-digital`, audience `vivabem`, scope esperado, iat/exp inteiros válidos e janela de até 60 segundos. Vinculação usa SHA-256 de `POST`, newline, caminho real iniciado por barra, newline e corpo criptografado. Sub deve corresponder a oid_usuario decifrado e environment ao ambiente Mercado Pago configurado.

Assinatura válida isolada não autoriza alterar qualquer dono/caminho/corpo. Não se documentam valores secretos ou criação de chaves. Controllers decifram JSON com profundidade limitada antes de validar campos. Não enviar callbacks sintéticos para instalação real: aceite pode produzir efeitos duráveis.

<!-- reading-section: purchase -->
## Entrada e resultado do callback de compra

Scope: `wallet:purchases:complete`. Contrato decifrado:

| Campo | Validação / significado |
| --- | --- |
| `oid_usuario` | String obrigatória, até 36; subject correspondente e usuário existente |
| `transaction_id`, `attempt_id` | UUIDs obrigatórios |
| `purchase_status` | approved/refused/pending obrigatório |
| `environment` | teste/producao obrigatório, correspondente à configuração |
| `event_id` | String até 100, exatamente balance-purchase: mais transaction_id |
| `amount_cents` | Inteiro opcional 1–9999999999; obrigatório na conversão |
| `payment_method` | Marcador pix opcional |
| `purpose` | Opcional compra_saldo/atendimento_emergencial/atendimento_agendado/atendimento_imediato |
| `appointment_id`, `duration_minutes` | UUID anulável / inteiro 1–1440 |
| `outcome_unconfirmed` | Booleano opcional; true obrigatório para pending |
| `convertida_em_saldo`, `data_compra_original` | Conversão exige approved para finalidade de atendimento, valor e data original |
| `pix_simulado` | Booleano opcional; true exige teste configurado e ambiente local/testing coerente |

Pix aprovado de atendimento sem conversão delega a `CasoDeUsoAplicarCompraAtendimentoPix`; demais resultados a `CasoDeUsoAplicarResultadoCompraSaldo`. Aplicação comum bem-sucedida responde persisted=true; ramo Pix retorna resultado do caso de uso. Confirma efeitos locais, sem executar novo pagamento no provedor.

Falha responde `persisted=false, code=purchase_effects_unconfirmed`. Exceções HTTP preservam status; tratamento de assinatura/UnexpectedValueException usa 401; fallback 503. Falhas de validação/efeitos são registradas por etapa, classe/status, sem corpo financeiro. Resposta falha não autoriza repetir pagamento original.

<!-- reading-section: operations -->
## Autorização e resultado de estorno/pagamento

Scopes neutros: `wallet:operations:authorize` / `wallet:operations:results`; compatibilidade: `wallet:refunds:authorize` / `wallet:refunds:results`. Ações authorize/results. Compatibilidade rejeita payment. Campos obrigatórios: oid_usuario, environment e appointment_id UUID; operation assume refund ou aceita payment. original_transaction_id é obrigatório salvo payment.

Em results, estorno usa refund_transaction_id, refunded e refund_status; pagamento usa transaction_id, completed e operation_status. IDs/attempt_id são UUIDs, status approved/refused, conclusão booleana, valor inteiro 1–9999999999 e balance_after_cents opcional 0–9999999999. Pagamento exige purpose pagamento_saldo e breakdown com bruto/líquido positivos, taxa não negativa e percentual 0–100. Purpose de estorno, quando presente, é estorno_saldo/estorno_pix; retryable booleano opcional.

Despacho seleciona `CasoDeUsoEstornoAtendimento` ou `CasoDeUsoPagamentoPsicologo` e chama autorizar/concluir. Sucesso é JSON criptografado retornado como string JSON, distinto do objeto persisted do callback de compra. Falha: `persisted=false, code=financial_operation_unconfirmed`, status da exceção HTTP ou 503. Aceitar payload de pagamento no controller não comprova todo repasse funcional; [arquitetura](../architecture/overview.md) documenta funcionalidade financeira parcial.

<!-- reading-section: push-balance -->
## Registro push e leitura de saldo

`RegistroFcmControlador::store` aceita registration_id (aliases fid/token), target_type fid/token, platform opcional web/android/ios, device_id até 255 e context_proof com exatamente 64 caracteres hexadecimais minúsculos. Registro tem até 512 caracteres. Delega titularidade/contexto a `CasoDeUsoRegistroPush` e retorna ok/enabled; remoção aceita aliases e retorna ok. Registro armazenado não confirma entrega ou disponibilidade profissional. Testes verificam dono e impedimento de downgrade Android para web.

`LeitorSaldo::read` deriva dono de Auth, sem receber identidade arbitrária. Criptografa dono e assina scope `wallet:balance:read` com vinculação a `POST /api/get_saldo`, desabilita redirects e usa timeout configurado (padrão 10, mínimo 1 segundo). Exige HTTP 201, string JSON criptografada, status sucesso e content.saldo decimal textual com até oito dígitos inteiros e dois decimais, podendo ser negativo. Falha vira indisponibilidade, sem inventar saldo zero.

<!-- reading-section: evidence -->
## Evidências e manutenção

Fontes: `routes/{api,web,auth,health}.php`, `app/Providers/AppServiceProvider.php`, `app/Http/Controllers/{ResultadoCompraSaldoControlador,OperacaoFinanceiraInternaControlador,RegistroFcmControlador}.php`, `app/Services/LeitorSaldo.php`, `bootstrap/app.php`. Testes/lacunas em [testes](../operations/backend-testing.md). Rever produtores/consumidores, idiomas e coleção após mudanças em rotas, claims, campos, criptografia, estados ou erros. Homologação, replay de todo caso downstream e integração HTTP completa permanecem não verificados.
