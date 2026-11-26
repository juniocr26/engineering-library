# Raciocínio sobre falhas — VivaBem

[English](../../en/faq/failure-scenarios.md) | [Português brasileiro](failure-scenarios.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `f0b884ca536a26996d40bf4187981d8c7506d0d7`.

<!-- reading-section: q004 -->

## Q004 — Onde termina a consistência?

Identidade/consulta SQL, autenticação Redis, documentos Cofre e saldo da carteira têm autoridades de commit diferentes. Abrir projeção de leitura não é transação distribuída nem conciliação com provedor. Lotes do dashboard limitam cada consulta, sem provar memória constante no resultado final. SessaoAutenticacaoRedis mantém referência de credencial hasheada e fingerprint da senha; a política persistente atual usa inatividade móvel de 60 dias. Duração do cookie é distinta. Presença passiva, Hub e heartbeats de vídeo ficam fora da renovação qualificada.

<!-- reading-section: q005 -->

## Q005 — Como conduzir a investigação?

Comece por CasoDeUsoLeituraPainel, depois LeitorSaldo específico e os dois clientes de pares, seguidos da sessão de autenticação e do signer. Rastreie contrapartes Carteira/Cofre antes de diagnosticar falhas entre serviços. Em testes isolados futuros, use usuários sintéticos e doubles HTTP/Redis, verificando aviso perdido seguido de releitura autorizada, resposta cifrada inválida, negativa de vínculo, timeout e revogação de contexto. Timeout pode deixar efeito remoto incerto; resposta ausente não prova rollback.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
