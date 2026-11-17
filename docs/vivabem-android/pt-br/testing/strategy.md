# Verificação Android: DAL e fronteiras nativas não testadas

[Sumário](../index.md) | [English](../../en/testing/strategy.md)

Revisado/executado em 2026-11-10 em b2287cf. Público: mantenedores Android e revisores de release. Cliente Java TWA; testes não exercitam backend próprio separado.

<!-- reading-section: suite -->
## Suíte offline existente

`tools/tests/test_verify_twa.py` usa Python unittest e importa tools/verify-twa.py. Sete testes cobrem certificados correspondentes/divergentes, package/namespace/relation, statements múltiplos/inválidos, fingerprints minúsculos, redirects, payload inválido e recusa de sobrescrever associação canônica do Portal. Último caso lê JSON público e confere ausência de alteração; não lê chave/credencial. Não solicita HTTPS real nem inicia Gradle.

<!-- reading-section: execution -->
## Resultado real

Na raiz:

```sh
python3 -B -m unittest discover -s tools/tests -v
```

Saída 0: **7 testes aprovados**, em 2026-11-10. Sem APK/AAB, emulador, dispositivo, Firebase ou publicação. Relatos de build debug/release sem assinatura e seis testes em 2026-10-04 permanecem históricos; relato de sete testes de 2026-11-04 não substituiu a execução nova.

<!-- reading-section: native -->
## Comportamento nativo inspecionado, sem teste em dispositivo

LauncherActivity aceita somente host HTTPS configurado sem userinfo/porta explícita, usa app-entry seguro no fallback, acrescenta source=android, pede permissão Android 13+ e fecha PonteRegistroPush no destroy. Marcador não autentica no backend.

PonteRegistroPush valida relação de origem Custom Tabs, aguarda navegação/canal, aceita request IDs limitados, envia token armazenado apenas sob requisição ativa e limpa canal/requisição/listeners ao fechar. Não troca senha da conta. ServicoMensagensFirebaseVivaBem armazena token renovado, suporta cancel/display, verifica permissão e restringe origem de navegação; notificação crítica tem timeout de 120 segundos. Essas decisões nativas não são cobertas pela suíte Python DAL.

<!-- reading-section: build -->
## Build, segurança e limites de aceite

app/build.gradle declara Firebase Messaging/Android Browser Helper, validação de assinatura debug fixa, assinatura release condicional, MP4 original e recursos launcher/store gerados. Parser DAL aprovado não comprova associação implantada, suporte postMessage, assinatura release, permissão ou entrega background. Nenhuma chave foi regenerada e conteúdo de credenciais google-services não foi inspecionado.

Antes do aceite de release, verificar separadamente identidade aprovada, DAL implantado sem redirect, deep links hostis, permissão negada, reset/navegação da ponte, rotação de token, revogação do contexto e push atrasado/cancelado em dispositivos. São fronteiras sem validação, sem criar testes ou aprovar release. Portal detém contas, atendimentos/pagamentos e autorização; token nativo não é banco financeiro/clínico offline.

Fontes: app/build.gradle; app/src/main/java/br/com/vivabem/app/LauncherActivity.java, PonteRegistroPush.java, ServicoMensagensFirebaseVivaBem.java; tools/tests/test_verify_twa.py. Rever idiomas/coleção após mudança de origem, protocolo, assinatura, SDK ou suíte.
