# Verificação criptográfica e limites de compatibilidade

[Sumário](../index.md) | [English](../../en/testing/strategy.md)

Revisado/executado em 2026-11-10. Público: mantenedores e revisores de consumidores. API: CriptoLib\Crypto com Configuration::validate, encrypt e decrypt; código/testes não alterados.

<!-- reading-section: contract -->
## Contrato verificado

Construtor aceita label exato RS256 e PEM privado RSA válido, mas cifra dados com AES-256-CBC mais HMAC-SHA256, sem criptografia RSA do conteúdo. HKDF deriva chaves separadas dos bytes originais. Envelope: CLIB:1:A256CBC:HS256: seguido de base64 canônico de IV/ciphertext/tag. Decrypt autentica header/corpo antes do OpenSSL e rejeita legado, versão não suportada, estrutura inválida ou adulterada. Reformatar PEM equivalente altera chaves derivadas; reparo da cópia de validação não normaliza entrada original.

`tests/security-cases.php` é compartilhado por tests/runtime.php e PHPUnit tests/CryptoTest.php. Usa chaves efêmeras sintéticas e referência independente; cobre roundtrips, aleatoriedade, framing, encoding, alteração de header/versão/IV/ciphertext/tag, chave errada, truncamento, legado e configuração. Wrapper OpenSSL de teste verifica que rejeições não chegam à decifração. Evidência de regressão, sem certificação formal ou validação de implantação.

<!-- reading-section: execution -->
## Resultado executado

Na raiz:

```sh
php tests/runtime.php
```

Saída 0, **292 asserções de segurança aprovadas** em PHP 8.3.27. Sem bootstrap de aplicação, chaves reais, ciphertext armazenado, banco ou Docker. Comando standalone não exige PHPUnit. Composer define test como phpunit, mas PHPUnit não foi executado nesta continuação; não confundir resultados.

<!-- reading-section: history -->
## Evidência histórica preservada

Relato de 2026-10-22 registrava 288 asserções. Relato de 2026-10-23 registrava 292 e um teste PHPUnit/292, com execução host/container e reprodução sintética da omissão histórica de MAC. Permanecem resultados datados, sem reexecução aqui. Relato de host de 2026-11-04 também registrava 292; verificação standalone atual confirmou independentemente a contagem.

<!-- reading-section: limits -->
## Limites e manutenção

Declara PHP >=8.1/OpenSSL, mas esta execução verificou somente PHP 8.3.27. Sem matriz PHP 8.1, migração de produção, suítes consumidoras, rotação, armazenamento real ou leitor em outra linguagem. Não fornece prevenção de replay, autorização ou hash de senha por criptografia reversível. Aplicações coordenam versão, custódia PEM original e falhas; suíte aprovada não comprova versão instalada nos consumidores.

Fontes: composer.json, src/Configuration.php, src/Crypto.php, tests/runtime.php, tests/security-cases.php, tests/CryptoTest.php. Rever idiomas/coleção após alteração de framing, KDF, PEM aceito, erros ou testes. Preservar histórico; não alterar algoritmos/testes para aprovar validação documental.
