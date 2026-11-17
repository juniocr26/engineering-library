# Revisão documental VivaBem — 2026-10-26

[English](../../en/operations/vivabem-documentation-review.md) | [Português brasileiro](vivabem-documentation-review.md)

## Mapeamento inicial

As fontes e a biblioteca histórica estavam limpas. O destino estava limpo em `d641b17e5285407c2f717d3bb5555993d56bcbd2`. Nenhuma coleção autorizada existia. Novos IDs estáveis usam os slugs exatos das fontes; nomes de exibição seguem títulos documentados quando disponíveis.

| Fonte | Material histórico | Destino / novo ID | Trabalho planejado inicialmente | Lacunas |
| --- | --- | --- | --- | --- |
| `acesso-servidor/` | `docs/<lang>/architecture/acesso-servidor.md`; `docs/<lang>/interviews/acesso-servidor-interview.md` | `docs/acesso-servidor/`; `acesso-servidor` | Síntese bilíngue atual, contratos, configuração, segurança, guias, FAQ e procedência | Aceitação em runtime; ver revisão do projeto |
| `carteira-digital/` | `docs/<lang>/architecture/carteira-digital.md`; `docs/<lang>/interviews/carteira-digital-interview.md` | `docs/carteira-digital/`; `carteira-digital` | Síntese bilíngue atual, contratos, configuração, segurança, guias, FAQ e procedência | Aceitação em runtime; ver revisão do projeto |
| `cofre-paciente/` | `docs/<lang>/architecture/cofre-paciente.md`; `docs/<lang>/interviews/cofre-paciente-interview.md` | `docs/cofre-paciente/`; `cofre-paciente` | Síntese bilíngue atual, contratos, configuração, segurança, guias, FAQ e procedência | Aceitação em runtime; ver revisão do projeto |
| `criptografia-lib/` | `docs/<lang>/architecture/criptografia-lib.md`; `docs/<lang>/interviews/criptografia-lib-interview.md` | `docs/criptografia-lib/`; `criptografia-lib` | Síntese bilíngue atual, contratos, configuração, segurança, guias, FAQ e procedência | Aceitação em runtime; ver revisão do projeto |
| `hub-vivabem/` | `docs/<lang>/architecture/hub-vivabem.md`; `docs/<lang>/interviews/hub-vivabem-interview.md` | `docs/hub-vivabem/`; `hub-vivabem` | Síntese bilíngue atual, contratos, configuração, segurança, guias, FAQ e procedência | Aceitação em runtime; ver revisão do projeto |
| `script-auditoria-envs/` | `docs/<lang>/architecture/script-auditoria-envs.md`; `docs/<lang>/interviews/script-auditoria-envs-interview.md` | `docs/script-auditoria-envs/`; `script-auditoria-envs` | Síntese bilíngue atual, contratos, configuração, segurança, guias, FAQ e procedência | Aceitação em runtime; ver revisão do projeto |
| `vivabem/` | `docs/<lang>/architecture/vivabem.md`; `docs/<lang>/interviews/vivabem-interview.md` | `docs/vivabem/`; `vivabem` | Síntese bilíngue atual, contratos, configuração, segurança, guias, FAQ e procedência | Aceitação em runtime; ver revisão do projeto |
| `vivabem-android/` | `docs/<lang>/architecture/vivabem-android.md`; `docs/<lang>/interviews/vivabem-android-interview.md` | `docs/vivabem-android/`; `vivabem-android` | Síntese bilíngue atual, contratos, configuração, segurança, guias, FAQ e procedência | Aceitação em runtime; ver revisão do projeto |

## Revisões das fontes

| Repositório | HEAD |
| --- | --- |
| `engineering-library_old` | `dfb5b7a5b8a9159af65a991872c34e78d8fd6fd0` |
| `acesso-servidor` | `ba70952fd63992c85aa153f141a39fadf33360a0` |
| `carteira-digital` | `9a6b795b6ebc16f0390e0fbdbf711f257e42fa2a` |
| `cofre-paciente` | `85edbcb16fd029235dc74eba12c7b14b164d3d62` |
| `criptografia-lib` | `c95a12038760a663f69bb576f7c172e8b021bece` |
| `hub-vivabem` | `e0ab75952946bc3f764dcb4144e404097277933f` |
| `script-auditoria-envs` | `2e5d5de71d1323b4e588e04f06784324802ae0d3` |
| `vivabem` | `f0b884ca536a26996d40bf4187981d8c7506d0d7` |
| `vivabem-android` | `07c3fa6cfcb8cd19cc6d271922684b304778ccd5` |

## Entrega e investigação efetiva

Oito coleções novas contêm 310 arquivos Markdown: 38 por projeto mais seis adições bilíngues focadas, incluindo pares README/bio e navegação. Páginas substantivas cobrem propósito/arquitetura/dados, interfaces implementadas, configuração inspecionada, integrações, segurança, investigação segura, cinco respostas de FAQ, asserções de testes inspecionadas e reconciliação histórica. Índices de categoria são apenas navegação. As seis coleções existentes foram preservadas. Nenhuma categoria vazia, snapshot de código ou PDF foi criado.

A inspeção atual foi seletiva, concentrada em retirada financeira/leitura de saldo, política Cofre e leitura parcial, envelope autenticado, publicação/assinaturas Hub, dashboard/autenticação/auditoria Portal, limpeza/seleção Compose do atualizador e abertura/assinatura Android. Não é auditoria integral das aplicações ou de segurança. `operations/source-review.md` por projeto e metadados identificam caminhos/revisões e cobertura efetiva. Mapas históricos e explicações selecionadas das entrevistas foram sintetizados, sem restauração cega; originais completos continuam intactos na biblioteca antiga somente leitura. O manifest registra seus hashes. Contagens históricas de execução não foram reutilizadas como atuais.

## Diferenças reconciliadas

- Narrativas de execução financeira/Stripe/Connect/outbox da carteira foram retiradas. Leitor específico de saldo e adaptador genérico indisponível são distintos; webhooks Mercado Pago válidos ainda retornam 503 sem aceite durável.
- Cofre possui nove rotas POST vinculadas à operação/corpo; rotas bancárias históricas estão ausentes. Replay exato continua possível. Cartões ilegíveis aparecem como resultados explicitamente parciais.
- A cifra atual autentica cabeçalho, IV e ciphertext; o formato antigo sem marca é rejeitado. Bytes exatos do PEM continuam necessários para compatibilidade da derivação.
- Autorização de publicação e de destinatário Hub são separadas. Liveness/readiness e sucesso AMQP/domínio são observações diferentes; POST /events não é suportado.
- Flags de validação do atualizador removem dependências/propostas e não são checks somente leitura. A seleção Compose atual substitui descrições de overlays gerados.
- Suporte CLI a diretório selecionado não prova uso pelo Portal: AuditExecutor inspecionado chama --apply-audit global e pode criar proposta até em list. Nenhum código foi alterado para resolver a diferença.
- Sessão TWA, DAL, permissão de notificação e entrega push são distintos. A política Portal atual usa inatividade móvel de 60 dias; heartbeat passivo não é uso qualificado.

## Contratos do destino e divergências

O catálogo efetivo lê árvores bilíngues por projeto e IDs/nomes de bio correspondentes. Descoberta de categorias e ordenação canônica frontend foram inspecionadas em Catalog::Files/Sync e documentation.ts. Links relativos de coleção são usados. Referências de código são spans para checkout autorizado: não há declaração de expansão no leitor. Ícones opcionais usam fallback existente; não eram exigidos para compatibilidade dos metadados.

O índice herdado descrevia catálogo público e a procedência mantém origens históricas do portfólio público. O usuário identifica este checkout como destino privado; o origin observado é o repositório da organização, diferente do remoto pessoal registrado historicamente. URL remota e licença MIT não comprovam visibilidade. O índice agora separa explicitamente material privado. Não houve alteração de visibilidade/remotos, consulta a serviço remoto ou publicação. A procedência histórica do portfólio foi preservada, sem virar evidência das fontes privadas.

check_catalog.py sem limitação exige que todos os irmãos coincidam com o manifest e calcula hashes de imports. Esse comportamento excede o escopo e não foi executado nem alterado. Entradas novas descrevem sínteses autorais com imports vazios e fontes históricas registradas separadamente. Não houve sincronização/ingestão de banco; ativação do catálogo em runtime não foi validada.

## Verificações e falhas

`python3 -B -m unittest discover -s tools -p 'test_*.py' -v`: 27 testes passaram. São fixtures existentes das ferramentas documentais, não testes das aplicações. Python host foi usado como exceção estabelecida para validadores de biblioteca padrão; nenhum runtime foi instalado.

A primeira validação limitada tratou o arquivo index do idioma como diretório de categoria e gerou 32 falsos achados. A travessia foi corrigida para apenas diretórios e verificada novamente; era erro do checker ad hoc, não defeito documental. A primeira tentativa de geração também parou antes de escrever coleção porque faltava criar o diretório pai; a geração foi corrigida. Nenhuma falha alterou fontes.

A inspeção Docker inicialmente não tinha permissão no socket; a consulta somente leitura aprovada depois funcionou e não encontrou serviços ativos. Nenhum container/serviço foi iniciado. Portanto não houve execução de navegador/renderer ou Rails/Node. Testes/PDF registrados no manual fornecido continuam históricos, sem serem apresentados como execução atual.

Resultados finais de estrutura/links/paridade/padrões de segredos e inventário de arquivos alterados estão no [artefato de validação](../../en/operations/validation/vivabem-documentation-2026-10-26.json). Checks Git de whitespace e escopo/status final estão registrados nele. Padrões não certificam ausência de todo conteúdo sensível. EN/PT foram redigidos como sínteses técnicas pareadas com IDs canônicos de seção/pergunta correspondentes; não é certificação independente de tradução.

## Evidências e trabalho restantes

Cada projeto mantém lacunas explícitas de runtime/restauração/produção em sua revisão. Referências de configuração cobrem consumidores inspecionados, não todas as entradas de framework/deploy. Máquinas de estado de consulta/conferência Portal, ciclo completo de avaliações, handoff/recuperação de filas, inventário integral de configuração e reconciliação detalhada de runbooks precisam de revisão mais profunda antes de chamar a documentação do ecossistema de exaustiva. Nenhuma feature ausente foi implementada. A entrega estabelece oito coleções bilíngues fundamentadas, sem declarar concluída a cobertura exaustiva.

Nenhum ambiente/configuração efetivo, comportamento, banco/schema, infraestrutura, conta ou identidade mudou. Fontes e engineering-library_old permaneceram somente leitura e foram conferidos com Git limpo ao final. Não havia alterações iniciais no destino. Apenas documentação/procedência do destino mudou. Não houve stage, commit, amend, rebase, push ou publicação.

Adições focadas cobrem janelas de confirm/ACK e resumo/marcador de avaliações Cofre, além de retirada da criação paga Portal e referência Jitsi sob nome histórico GoogleMeet. Caminhos foram acrescentados à procedência.

A paridade literal inicial também sinalizou caminhos históricos de idiomas diferentes; a verificação foi refeita normalizando apenas o segmento documental do idioma. Os 14 IDs de bio do catálogo atual são únicos. Títulos H1 colocam o assunto antes do travessão para preservar títulos distintos no reader, que remove o sufixo.

## Portabilidade dos diretórios de idioma — 04/11/2026

O índice Git dos oito repositórios de origem do VivaBem registra docs/pt-BR, enquanto a enumeração deste filesystem macOS mostra docs/pt-br. Os validadores existentes usam pt-br; a coleção central também usa essa forma. Validação de existência neste volume não comprova resolução em filesystem sensível a maiúsculas/minúsculas. Nenhum rename de diretório, escrita no índice Git ou ajuste nos validadores foi executado nesta revisão documental. Normalização rastreada e validação em checkout Linux permanecem pendentes; preservar slugs e conteúdo bilíngue ao tratar essa divergência.
