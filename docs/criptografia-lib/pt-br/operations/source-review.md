> Registro histórico de revisão. Contratos e verificação atuais estão ligados em [Arquitetura](../architecture/overview.md). Datas, revisões e resultados abaixo mantêm o escopo original.

# Revisão das fontes — Criptografia Lib

[English](../../en/operations/source-review.md) | [Português brasileiro](source-review.md) · [Index / Índice](../index.md)

Revisão estática do código: 2026-10-26, `dae407f6be676365babe3c21ba133ca2c8cc6bab`.

<!-- reading-section: scope -->

## Cobertura da inspeção

Continuação: ambos os repositórios estavam na `main` com árvores limpas. Os marcadores de conflito dos READMEs já estavam versionados. Guias internos foram conciliados com a implementação; a branch `tag` foi inspecionada somente para leitura e não contém documentação interna. Fontes runtime, manifest Composer e testes coincidem com a `main`. A revisão anterior na branch de release permanece válida para observações runtime, mas não cobriu a documentação interna agora revista na `main`.

Árvore fonte inicialmente limpa. Leitura estática seletiva dos caminhos listados sustenta esta coleção; enumeração não é revisão integral. Símbolos/consumidores são identificados nos capítulos. Nenhum comando de aplicação consumidora, banco operacional, broker ou deploy foi executado. A manutenção do catálogo da biblioteca é separada e está indicada abaixo.

<!-- reading-section: sources -->

## Arquivos fonte

- `criptografia-lib/composer.json`
- `criptografia-lib/src/Configuration.php`
- `criptografia-lib/src/Crypto.php`
- `criptografia-lib/tests/CryptoTest.php`
- `criptografia-lib/docs/pt-BR/security/envelope-v1.md`
- `criptografia-lib/docs/pt-BR/architecture/implementation-map.md`
- `criptografia-lib/docs/pt-BR/integrations/integrations.md`

<!-- reading-section: history -->

## Reaproveitamento histórico e correções

O mapa histórico fornece a divisão de responsabilidades e a necessidade de custódia dos bytes exatos. Descrições de 11 de outubro sobre IV não autenticado referem-se a formato retirado. O `src/Crypto.php` atual autentica cabeçalho literal, IV e ciphertext e rejeita envelopes legados sem marca. Preservar o PEM não torna esse formato antigo legível.

Revision / Revisão: `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0`.

- `engineering-library_old/docs/pt-BR/architecture/criptografia-lib.md`
- `engineering-library_old/docs/pt-BR/interviews/criptografia-lib-interview.md`

<!-- reading-section: access -->

## Verificações e acesso ao código

Caminhos de código são referências apenas para checkout autorizado. São spans de código intencionalmente: nenhum snapshot/catálogo privado foi aprovado ou gerado, portanto o leitor não pode expandi-los. Navegação documental usa links de coleção. A revisão anterior não executou sincronização do catálogo. Verificações documentais/de catálogo e sincronização desta continuação são relatadas separadamente na entrega; nenhuma suíte de aplicação ou criptografia foi executada.

<!-- reading-section: gaps -->

## Evidência ausente e trabalho restante

Permanecem pendentes revisão criptográfica independente, procedimento de migração legada, rotação, aceitação de restauração e verificação das dependências instaladas nos consumidores. Nenhuma suíte de runtime/segurança foi executada.

[Library review / Revisão da biblioteca](../../../engineering-library/pt-br/operations/vivabem-documentation-review.md)
