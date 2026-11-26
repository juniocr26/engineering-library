# Raciocínio sobre falhas — Hub VivaBem

[English](../../en/faq/failure-scenarios.md) | [Português brasileiro](failure-scenarios.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `e0ab75952946bc3f764dcb4144e404097277933f`.

<!-- reading-section: q004 -->

## Q004 — Onde termina a consistência?

Pub/Sub não mantém log de replay para destinatário desconectado. Sucesso no transporte Redis não é commit financeiro. O envelope contém channel/event/payload e identidade source/project; publicações diretas assinadas vinculam o envelope completo interpretado ao token RS256. O namespace Node transporta envelope e publisherToken e usa autorização própria. Recuperação exige releituras autorizadas do estado de domínio, sem presumir retenção de todos os avisos.

<!-- reading-section: q005 -->

## Q005 — Como conduzir a investigação?

Leia configuracao.js, politicaPublicador.js, autenticacaoPublicador.js, envelopeRedis.js, roteamentoDestinatario.js, destinatarios.js e assinaturas.js nessa ordem. Para aceitação isolada futura, compare /health e /ready sem Redis, atrase ACKs, reconecte, revogue sessão do Portal e tente entregar a outro usuário sintético. Brokers/Portal reais e limites de tráfego exigem aceitação separada. Não inicie o repositório nem publique eventos de teste na infraestrutura compartilhada para validar documentação.

[Evidence and limits / Evidências e limites](../operations/source-review.md)
