# Fronteiras de consulta e conferência

[Index / Índice](../index.md) · [Evidence / Evidências](../operations/source-review.md)

<!-- reading-section: retirement -->

## Criação após confirmação financeira

ControladorTransacao e os Use Cases atuais possuem caminhos de compra. CasoDeUsoAtendimentoEmergencial::iniciar recusa criação sem pagamento; iniciarAposPagamentoAprovado implementa vínculo da tentativa, titular, valor e resultado aprovado, com lock de cache e transação SQL. Conversão tardia em saldo não deve recriar atendimento. A presença desses caminhos não comprova homologação nem transação distribuída entre SQL, Redis e Cofre. Alguns métodos legados de estorno automático permanecem indisponíveis; não estender isso para toda compra.

<!-- reading-section: existing -->

## Autoridade de consultas existentes

CasoDeUsoAtendimento::getDetalheAtendimento valida perspectiva usuario/psicologo, rejeita perspectiva profissional sem o papel e consulta detalhes restritos à identidade autenticada. O trecho aceitar emergencial exige psicólogo autenticado e bloqueia a linha da consulta em transação SQL local antes de verificar atribuição, busca ativa e estado agendado. As verificações são locais; não fazem commit atômico de reserva Redis ou escrita Cofre. Inspeção de entradas de métodos não é auditoria de todas as transições.

<!-- reading-section: conference -->

## Referência de conferência e limpeza

ServicoLinkGoogleMeetAtendimento mantém nome histórico, mas cria identificador jitsi:// cifrado, derivado por HMAC-SHA256 de usuário/profissional/início/fim com a chave da aplicação. inserir envia JSON cifrado ao Cofre /api/links/insert. Isso não prova chamada à API Google Meet. Limpeza mensal publica referência cifrada e marca remoção local em memória apenas após sucesso do adaptador, distinguindo enfileiramento de exclusão remota confirmada. Referências, participação no navegador e ciclo do provedor têm fronteiras de aceitação diferentes.

## Fontes inspecionadas

- `vivabem/routes/web.php`
- `vivabem/app/UseCases/CasoDeUsoAtendimento.php`
- `vivabem/app/UseCases/CasoDeUsoAtendimentoEmergencial.php`
- `vivabem/app/Http/Controllers/ControladorTransacao.php`
- `vivabem/app/Jobs/ProcessarBuscaAtendimentoEmergencial.php`
- `vivabem/app/Services/ServicoLinkGoogleMeetAtendimento.php`
- `vivabem/app/Services/ServicoLimpezaGoogleMeetAtendimentoMensal.php`
