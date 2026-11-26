# Testes do Portal: suíte atual e limites da verificação

> Consolidação atual de loading/testes: consulte a seção final da fase 4 abaixo. Disponibilidade de runner e contagens 54/190 no registro preservado de 10/11/2026 são históricas.

[Sumário](../index.md) | [English](../../en/operations/backend-testing.md)

Revisado/executado em 2026-11-10 na revisão `d412cc7`. Público: mantenedores e revisores. Substitui descrição desatualizada da suíte de 2026-11-04; contagens antigas permanecem históricas. Nenhum teste, runner, fixture, dependência ou código foi alterado.

<!-- reading-section: harness -->
## Harness real e isolamento

`phpunit.xml` carrega `vendor/autoload.php` e descobre `tests/Unit` e `tests/Feature`. `vendor/bin/phpunit` local agora existe; é desnecessário emprestar runner de outro repositório. `tests/TestCase.php` estende PHPUnit diretamente, cria aplicação/container Laravel em memória, configura SQLite `:memory:`, registra providers de banco/hash, fornece view/logger mockados e chama `Http::preventStrayRequests`.

Não inicializa `bootstrap/app.php` completo ou providers do produto. Não é `tests/TesteIsolado.php`, que está ausente. Escritas de schema/dados SQLite nesses testes são estado temporário em memória, sem migrações contra banco implantado. Bloqueio HTTP Laravel cobre essa facade; não é sandbox de sistema operacional para todo transporte. Casos existentes foram inspecionados antes da execução.

<!-- reading-section: coverage -->
## Cobertura contratual existente

| Arquivo existente | Asserções e fronteira |
| --- | --- |
| `tests/Unit/AutenticacaoTest.php` | Senha atual/legada e rehash; segredo ausente falha fechado; exclusão de credenciais da serialização |
| `tests/Unit/AgendaFinanceiraTest.php` | Situação/estorno por participação; valores liquidados; limite temporal e avaliação emergencial |
| `tests/Unit/ConflitosAgendaTest.php` | Ambos os participantes, limites abertos/sobreposição, atendimento excluído e estados em SQLite em memória |
| `tests/Unit/ValidacaoDisponibilidadeTest.php` | Sintaxe Pix e disponibilidade sem autorização/durante consulta |
| `tests/Feature/LoginTest.php` | Senha inválida, ativação, web/remember/Android e destino permitido; autenticação mockada |
| `tests/Feature/CadastroPerfisTest.php` | Perfil não criado após falha do usuário; e-mail falho não desfaz cadastro bem-sucedido |
| `tests/Feature/NotificacoesTest.php` | Despacho após commit, rollback, falha de enqueue, reserva duplicada e retry transitório |
| `tests/Feature/RegistroPushTest.php` | Atualização/remoção pelo dono, rejeição de downgrade Android e usuário removido |
| `tests/Feature/VideoconferenciaTest.php` | Participante, estado e abertura cinco minutos antes com Jitsi mockado |

Nome Feature não comprova teste completo de kernel HTTP/browser. Vários casos invocam domínio diretamente. Suíte não certifica autorização Redis de sessão, callbacks completos, locks MySQL, rotas Cockpit, entrega broker/FCM ou Jitsi real. Links antigos para `DecisaoPushTest.php`, `SituacaoFinanceiraAtendimentoTest.php` e `TitularidadeAtendimentoTest.php` foram substituídos pelo mapa atual.

<!-- reading-section: execution -->
## Verificação executada

Na raiz do repositório Portal:

```sh
composer test
```

`composer.json` resolve para `php vendor/bin/phpunit --do-not-cache-result`. Saída real: **0**. Runtime: PHP 8.3.27, PHPUnit 11.5.56. Resultado: **54 testes, 190 asserções**, todos aprovados em 2026-11-10. Runner informou 0.262 segundos e 32 MiB; observações da execução, sem benchmark da aplicação. Percentual de cobertura não foi medido.

Utilizou dependências preexistentes, entradas sintéticas, SQLite em memória e doubles existentes. Nenhuma chamada a provedor, operação financeira real, scheduler, consumidor ou banco de produção foi iniciado. Aprovação não certifica plataformas não verificadas ou ramos sem cobertura.

<!-- reading-section: maintenance -->
## Manutenção e verificações restantes

Quando fonte/nomes mudarem, atualizar ambos os idiomas e coleção juntos. Registrar execuções novas com data/runtime/contagens, sem herdar resultado antigo como atual. Novos testes automatizados exigem autorização separada e ficam fora da tarefa documental.

Próximas fronteiras são integração da aplicação e verificações browser/operacionais em ambiente explicitamente isolado. Não foram executadas e não devem ser substituídas por chamadas administrativas ou financeiras em instalação real. Fontes: `composer.json`, `phpunit.xml`, `tests/TestCase.php` e nove arquivos acima. O [capítulo do Cockpit](technical-cockpit.md) registra riscos operacionais próprios.

Reexecutado na reconciliação do ecossistema em 2026-11-10: `composer test`, saída 0, 54 testes / 190 asserções, PHP 8.3.27 / PHPUnit 11.5.56, 0,306 segundos. Esta execução é independente da anterior acima. A orquestração de compras continua sem cobertura integrada completa nesta suíte.


## Estratégia de testes de interfaces reativas

Revisão documental da fase 4 em 12/11/2026. Consulte a [arquitetura do loading](../architecture/shared-loading.md). Os resultados 54/190 e a disponibilidade de runner local acima são observações históricas de 10/11/2026. O checkout atual inspecionado não contém o executável PHPUnit local. O parágrafo anterior não garante reprodução atual.

### Camadas e asserções

| Camada | Cenários úteis e resultados esperados | Fronteira |
| --- | --- | --- |
| Renderização Blade | Default/null/branco/customizado; escaping; props; classes versus atributos Alpine; modal opt-in | Confirma HTML gerado, não execução de expressão/foco |
| Controlador de estado isolado | Tentativa/transação correspondente; retry/max inválido; duplicata, regressão, evento tardio e resultado ambíguo | Eventos sintéticos não comprovam entrega do servidor/liquidação |
| Navegador + Alpine real | Fallback visível, estático/reativo; atualização oculto/reabertura; mesma imagem; instâncias independentes | DOM é evidência mais forte que strings, mas página completa exige outra camada |
| Integração de posse HTTP | Duas/três requisições em qualquer ordem; sucesso/erro/abort; tabelas compartilhando indicador; destroy/reinit; cleanup Pix | Espera pendente continua visível e liberação é idempotente; sem requests operacionais |
| Transporte Socket.IO isolado | Envelope objeto/string; JSON inválido; contexto alheio; retry; duplicata/fora de ordem; reconnect/remount | Endpoint compatível valida cliente/ponte/store/DOM, não autenticação Hub real |
| Foco/layout | Foco só após visibilidade; genérico preserva teclado; Tab/Escape bloqueante; cleanup; texto longo, temas e tamanhos | Leitor de tela físico e outros motores são verificações separadas |
| Frontend financeiro | Cartão, Pix, contextos de consulta, estorno/recebimento sintéticos; eventos atrasados/duplicados e incerteza | Fechar indicador nunca basta para afirmar sucesso |
| Build/regressão | Manifesto resolve assets; suites backend continuam verdes | Build não certifica navegador ou integração distribuída |

Use fixtures sintéticas controladas, sem dados de clientes ou credenciais. Preserve Alpine/controllers/ponte reais sob teste; simule dependências HTTP/negócio nas fronteiras em vez de substituir a lógica que pretende verificar. Para pagamentos, separe preparação, envio, pendência, recusa e incerteza. HTTP 5xx/resposta perdida pode indicar resultado desconhecido; não deve fabricar aprovação ou incentivar pagamento duplicado. Estado de QR sozinho não confirma compra. Diferencie submissão completa de simples instanciação de controller de consulta.

Sequência útil de posse: adquirir A, adquirir B, concluir A, verificar visível, concluir B, verificar estado inicial restaurado, liberar A novamente, verificar que nada mudou. Repita com erro, abort, ordem inversa, terceiro dono e overlay já visível. Destrua com request pendente e monte nova instância; callbacks antigos não podem ocultar ou desenhar na nova. Classes alteradas diretamente fora do helper ficam fora dessas garantias.

Em Socket.IO, use endpoint compatível restrito a loopback, identidades sintéticas e desconexões controladas. Observe transporte real e texto visível final, não apenas eventos despachados. Verifique exatamente um handler próprio após várias remontagens, ausência dos antigos após destroy e nenhum crescimento após reconnect. Canal selecionado no cliente não comprova autorização do servidor. Não afirme cobertura de polling/upgrade a partir de fixture somente WebSocket nem trate endpoint mínimo compatível Engine.IO como Hub real.

### Matriz de evidências da consolidação

Os JSONs finais temporários Chromium e JUnit PHPUnit foram inspecionados nesta revisão documental. Não houve reexecução de testes de aplicação ou operações financeiras. O registro corretivo considera D01–D06 corrigidos, coerente com o código atual. O relatório final original está ausente no checkout; seu registro corretivo temporário e outputs oferecem proveniência parcial, não relatório permanentemente arquivado.

| Área | Cenário | Fonte de teste | Nível de evidência | Último resultado verificado | Limitações |
| --- | --- | --- | --- | --- | --- |
| Componente/default/props | Omitida/null/branco/customizado, status, escaping, opt-in e wrapper removido | Suíte PHPUnit focada existente | Teste declarativo permanente; output anterior inspecionado | 12 testes/55 asserções aprovados | PHP não executa Alpine |
| Alpine/custom/classes | Mensagem real, identificador simples ausente, imagem, reabertura, múltiplas instâncias | Harness temporário Chromium | Componente/navegador isolado | Passou dentro dos 544 | Não é suíte browser versionada |
| Concorrência/DataTables | Sobreposição, erro, abort, ordem inversa, múltiplas tabelas, destroy/reinit | Harness direcionado temporário | Controller/biblioteca reais com HTTP controlado | 19/19 checks focados | Não coordena mutação DOM arbitrária |
| Ciclo Pix form | Abort/destroy pendente, stale e outro dono preservado | Harness direcionado temporário | Controller real com HTTP sintético | 40/40 checks focados | Sem escrita operacional |
| Retry/Socket.IO | 1–5; parser, contexto, duplicata, regressão, reconnect/remount e DOM | Harness de transporte compatível temporário | Cliente/ponte/estado/DOM reais | 41/41 Socket.IO, incluídos no total | Sem auth Hub/Carteira ou provedor real |
| Foco/acessibilidade | Reabrir, opt-in, teclado e cleanup | Harness browser + PHP declarativo | Navegador isolado | 48/48 checks focados | Sem certificação de leitor de tela físico |
| Texto longo/responsivo | Quatro larguras, dois temas, curto/médio/longo e scroll | Harness de layout temporário | Geometria/DOM Chromium | 48/48 checks focados | Outros motores não verificados |
| Frontend financeiro | Cartão/Pix, contextos de consulta, estornos/recebimentos, incerteza e prevenção de sucesso prematuro | Cenários sintéticos temporários | Controller/componente isolado | Passou dentro dos 544 | Sem certificar submissões distribuídas completas |
| Doze superfícies genéricas | Transações; histórico tabela/calendário; listagem; três auth; quatro perfis; chave Pix | Isolamento temporário de componentes/integração | Superfícies exercitadas individualmente | Passaram | Sem páginas autenticadas completas; profundidade varia |
| Regressão Chromium | Cenários originais e focados D01–D06 | Doze conjuntos temporários de resultados | Outputs anteriores inspecionados | 544/544; zero exceções globais inesperadas | Inclui 41 Socket.IO, não 585; artefatos podem desaparecer |
| PHPUnit completo | Suites existentes, inclusive componente focado | JUnit final | Regressão anterior | 127 testes/957 asserções; zero falhas/erros/skips | 12/55 já incluídos; runner emprestado |
| Vite/assets | Build em container e validação de manifesto | Registro corretivo e manifesto preservado | Aprovação relatada com artefato | Passou no registro corretivo | Logs brutos completos ausentes; sem reexecução |

Checks focados D01 passaram 26/26 e D05 28/28; são partes dos 544, não suites adicionais. Cinco foi uma sequência sintética de retry, não máximo universal de deployment. Contagem de asserts não é percentual de cobertura.

### Reprodução e limites da evidência

O setup PHPUnit existente usa container Laravel mínimo, SQLite em memória, bloqueio de HTTP e mocks, sem kernel operacional completo. Execução padrão requer dependências dev PHPUnit/Mockery do projeto, autoload dev correto e PHP/extensões compatíveis. Quando disponíveis, use composer test documentado pelo projeto e filtro PHPUnit para a suíte focada do componente. O checkout atual não oferece esse runner; não foram instaladas dependências para documentação.

A execução final anterior reutilizou runner de desenvolvimento existente em repositório vizinho (PHP 8.3.27, PHPUnit 11.5.56, Mockery 1.6.15). O bootstrap temporário priorizou explicitamente o namespace de testes do projeto-alvo para evitar selecionar TestCase vizinho. É workaround local, não comando universal; nenhum bootstrap ou caminho de máquina foi publicado aqui. Dependências dev do próprio projeto são pré-requisito para invocação portátil.

O frontend oferece comandos build/dev, sem comando permanente que reproduza os 544 checks. A verificação temporária precisou de Chromium/Playwright, componentes renderizados reais, módulos empacotados, HTTP controlado e endpoint de transporte compatível isolado. Esses artefatos não foram promovidos a suíte mantida. Vite usou dependências Linux do container existente, saída temporária e verificador do manifesto; módulos nativos do host não devem substituir as dependências nativas do container.

O proprietário confirmou separadamente o funcionamento em ambiente real. Não informou data, dispositivos, transações individuais ou screenshots. O aceite manual não elimina a ausência de cobertura de páginas autenticadas completas, provedor real, autenticação Hub, conciliação ponta a ponta entre serviços, BFCache genuíno, outros motores e leitor de tela físico. São limites de evidência, não defeitos reabertos.

Testes permanentes de DOM reativo, posse HTTP e ciclo socket melhorariam reprodução. Permanecem recomendações que exigem autorização separada; esta fase não alterou testes, fixtures, dependências ou UI do leitor. Testes unitários verdes não comprovam efeitos externos de um sistema financeiro distribuído.
