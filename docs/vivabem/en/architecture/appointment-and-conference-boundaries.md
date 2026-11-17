# Appointment and conference boundaries

[Index / Índice](../index.md) · [Evidence / Evidências](../operations/source-review.md)

<!-- reading-section: retirement -->

## Creation after financial confirmation

ControladorTransacao and current Use Cases implement purchase paths. CasoDeUsoAtendimentoEmergencial::iniciar refuses unpaid creation; iniciarAposPagamentoAprovado implements attempt, owner, amount and approved-outcome binding with a cache lock and SQL transaction. Late conversion to balance must not recreate an appointment. These paths do not establish homologation or a distributed transaction across SQL, Redis and Cofre. Some legacy automatic-refund methods remain unavailable; this does not mean all purchases are unavailable.

<!-- reading-section: existing -->

## Existing appointment authority

CasoDeUsoAtendimento::getDetalheAtendimento validates usuario/psicologo perspective, rejects psychologist perspective without that role, and requests details scoped to authenticated identity. The sampled emergency aceitar path requires an authenticated psychologist and locks the appointment row inside a local SQL transaction before checking assignment, active search and scheduled state. These checks are local; they do not atomically commit Redis reservation or Cofre writes. Inspection of method entry points is not a complete audit of every state transition.

<!-- reading-section: conference -->

## Conference reference and cleanup

ServicoLinkGoogleMeetAtendimento keeps a historical class name but creates an encrypted jitsi:// room identifier derived with HMAC-SHA256 from user/professional/start/end using the application key. inserir sends encrypted JSON to Cofre /api/links/insert. This is not proof of a Google Meet API call. Monthly cleanup publishes the stored encrypted reference, marks local in-memory removal only after adapter success, and explicitly distinguishes queued remote cleanup from confirmed remote deletion. Conferencing references, browser participation and provider lifecycle have different acceptance boundaries.

## Inspected sources

- `vivabem/routes/web.php`
- `vivabem/app/UseCases/CasoDeUsoAtendimento.php`
- `vivabem/app/UseCases/CasoDeUsoAtendimentoEmergencial.php`
- `vivabem/app/Http/Controllers/ControladorTransacao.php`
- `vivabem/app/Jobs/ProcessarBuscaAtendimentoEmergencial.php`
- `vivabem/app/Services/ServicoLinkGoogleMeetAtendimento.php`
- `vivabem/app/Services/ServicoLimpezaGoogleMeetAtendimentoMensal.php`
