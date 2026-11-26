> Registro histórico de revisão. Contratos e verificação atuais estão ligados em [Arquitetura](../architecture/overview.md). Datas, revisões e resultados abaixo mantêm o escopo original.

# Revisão das fontes — VivaBem Android

[English](../../en/operations/source-review.md) | [Português brasileiro](source-review.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `07c3fa6cfcb8cd19cc6d271922684b304778ccd5`.

<!-- reading-section: scope -->

## Cobertura da inspeção

Árvore fonte inicialmente limpa. Leitura estática seletiva dos caminhos listados sustenta esta coleção; enumeração não é revisão integral. Símbolos/consumidores são identificados nos capítulos. Nenhum comando de aplicação, banco, broker ou deploy foi executado.

<!-- reading-section: sources -->

## Arquivos fonte

- `vivabem-android/app/build.gradle`
- `vivabem-android/app/src/main/java/br/com/vivabem/app/LauncherActivity.java`
- `vivabem-android/app/src/main/java/br/com/vivabem/app/VivaBemFirebaseMessagingService.java`
- `vivabem-android/tools/tests/test_verify_twa.py`

<!-- reading-section: history -->

## Reaproveitamento histórico e correções

O mapa/entrevista antigos fornecem as fronteiras de TWA/navegador, DAL e entrega de notificações. Diferenças antigas de duração por papel cedem à implementação Portal de inatividade móvel para registros da política atual. Declarações de loja existentes são rascunhos, não prova de publicação. Variáveis históricas de fingerprint pertencem à configuração Portal quando consumidas lá, sem pertencer automaticamente ao ambiente Android.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/pt-BR/architecture/vivabem-android.md`
- `engineering-library_old/docs/pt-BR/interviews/vivabem-android-interview.md`

<!-- reading-section: access -->

## Verificações e acesso ao código

Caminhos de código são referências apenas para checkout autorizado. São spans de código intencionalmente: nenhum snapshot/catálogo privado foi aprovado ou gerado, portanto o leitor não pode expandi-los. Navegação documental usa links de coleção. Não houve ingestão do catálogo no banco. Veja a revisão central para checks efetivamente executados.

<!-- reading-section: gaps -->

## Evidência ausente e trabalho restante

Verificação do certificado instalado, resposta DAL real, ciclo de aparelho/navegador, push negado/obsoleto, release assinado e publicação Play continuam sem validação. Associação token/autorização e filtragem completa por sessão exigem investigação adicional.

[Library review / Revisão da biblioteca](../../../engineering-library/pt-br/operations/vivabem-documentation-review.md)
