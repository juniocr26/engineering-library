# rust-event-relay: Revisão factual do rascunho gerado

Revisor: Codex, 2026-11-16. Esta revisão separada não é sucesso autônomo do modelo local, aprovação do proprietário ou substituição do rascunho preservado.

Parecer: rascunho retido rejeitado.

RetryState.initial define máximo 10; can_acquire aplica o orçamento restante. AcquisitionBudgetExhausted é rótulo diagnóstico, não o mecanismo de aplicação. FailureEvidence permite ausência de referência e rejeita UUID nil quando fornecido; referência não é obrigatória. RetryDelay significa atraso de repetição, não retenção. Respostas posteriores com citações inadequadas foram rejeitadas, preservando o rascunho anterior sem fallback silencioso para Codex.

## Identidade e atualidade da revisão

Esta revisão vale para os bytes exatos abaixo. Geração posterior ou mudança de fonte exige nova revisão. Rejeição na versão atual pode preservar rascunho controlado mais antigo; isso não comprova que sua redação existente esteja correta.

SHA-256 do rascunho revisado: `4e1a840546b930a429dc1782c1bf7296b523615d59bef15dfb7f31e2539a6e05`.

- `backend/src/domain/retry.rs`: `108edcc00edda09a8f3becd83053ca5cceb01143283e52f5d354159e95567744`

[Rascunho preservado](generated-source-summary.md) · [Sumário](../index.md)
