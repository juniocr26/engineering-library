# Testes backend do Hub e limites de execução

[Sumário](../index.md) | [English](../../en/operations/backend-testing.md)

Revisado em 2026-11-10 em `2338ad3`. Público: mantenedores Node e revisores de segurança. Asserções de fonte são distintas de resultados executados; nenhum teste/runtime foi alterado.

<!-- reading-section: runner -->
## Runner e isolamento

`node-server/package.json` define npm test como `node scripts/run-tests.mjs`. Runner descobre arquivos comuns .test.js/.mjs/.cjs em tests/node-server, ordena e invoca Node atual com --test e TAP. Descoberta vazia, falha ou zero testes reportados reprovam. Não é a suíte obsoleta de arquivo único contratos-backend.test.mjs.

Testes importam módulos específicos sem iniciar server.js. Usam sockets/Redis/probes sintéticos em memória; fixtures criam/removem arquivos temporários próprios. Testes de publicador usam chaves RS256 efêmeras e tokens reais jose em memória. Existem asserções criptográficas no código, embora não executadas nesta sessão. Casos não exigem Redis, broker, site de destinatário ou chaves de produção.

<!-- reading-section: modules -->
## Módulos atuais

| Arquivo existente | Asserções |
| --- | --- |
| `tests/node-server/aplicacao.test.mjs` | Handler público publish, ACK negado/falho, liveness/404 HTTP, prontidão e retry de assinatura |
| `tests/node-server/configuracao.test.mjs` | Ambiente, padrões obrigatórios, papéis ACL limitados, políticas e rejeição de runner vazio |
| `tests/node-server/publicadores.test.mjs` | RS256/jose real, issuer/audience/subject/scope/tempo/type/kid e política canal/evento/transporte |
| `tests/node-server/destinatarios.test.mjs` | Origem/cookie exatos, sem redirects, identidade inválida, revalidação, remoção de token e papel profissional |
| `tests/node-server/roteamento.test.mjs` | Identidade, rotas/audiência, correlação financeira, adulteração e transporte Node dedicado |

Subtestes e dados dirigidos fazem quantidade de arquivos diferir da contagem executada. Não manter nove casos anteriores como resultado atual.

<!-- reading-section: execution -->
## Tentativa real

Diretório node-server:

```sh
node scripts/run-tests.mjs
```

Saída real 127: node não encontrado no host. Não houve contagem ou aprovação observada. npm test é alias, não outra suíte. Nenhum container foi iniciado ou dependência instalada para ocultar limitação. Executar comando existente no runtime Node 22 aprovado com dependências do lockfile quando disponível.

<!-- reading-section: limits -->
## Significado operacional e manutenção

Asserções não certificam handshake/housekeeping real, reconexão Redis, rollout ACL ou sessões browser. Ready exige publicador/subscriber conectados e assinaturas completas; liveness não comprova prontidão. ACK segue aceite Redis, sem confirmar recebimento. Pub/Sub não garante replay/deduplicação duráveis; aplicações detêm releituras e recuperação financeira.

Fontes: node-server/scripts/run-tests.mjs, package.json, src/aplicacao.js, src/assinaturas.js, src/envelopeRedis.js, src/roteamentoDestinatario.js e cinco arquivos acima. Atualizar idiomas/coleção após mudança de handlers, políticas, dependências ou descoberta. Testes/infraestrutura novos ficam fora da tarefa.
