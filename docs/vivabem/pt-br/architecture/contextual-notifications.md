# Notificações contextuais: persistência, Redis e entrega

Padrões generalizados a partir de fonte privada revisada em 12/11/2026. Chaves, entidades e exemplos abaixo são conceituais, não contratos da instalação. [Índice](../index.md) · [Identidade](../security/personal-identification.md).

## Responsabilidades e eventos

A transição de agenda altera o estado de negócio; um efeito durável registra a intenção de notificar; Redis mantém a lista consultável; um canal de eventos atualiza a interface aberta; uma fila encaminha push ao provedor. Sucesso em uma etapa não comprova as outras. Recuperar envio não deve reagendar consulta, refazer compra ou repetir cancelamento.

Os eventos revisados incluem agendamento aprovado, solicitação/proposta de novo horário, confirmação, cancelamento e entrada/início da sessão. Proposta deve comunicar confirmação pendente; confirmação deve informar novo horário; cancelamento deve preservar referência ao horário original. Entrada de uma pessoa e disponibilidade da sala para outra produzem textos distintos.

Destinatários vêm dos participantes da consulta. Nome/CRP são do profissional daquela consulta; paciente não ganha CRP por também ter conta profissional. A foto prioriza o perfil da contraparte no papel do atendimento, com fallback à conta e depois avatar. A imagem contextual não modifica a imagem global. Caminho relativo persistido, raiz do disk público, symlink e URL são camadas distintas: concatenar ou remover segmentos sem conferir essas camadas quebra fotos. O layout físico privado fica no guia interno.

## Modelo canônico no Redis

Um índice ordenado por usuário referencia hashes individuais de conteúdo. Uma string separada guarda evidência de despacho versionada. Exemplo conceitual:

```text
produto:inbox:usuario-sintetico -> sorted set de IDs
produto:item:evento-sintetico -> hash de conteúdo e leitura
produto:dispatch:evento-sintetico -> estado, dono e prazo
```

Esses nomes são sintéticos. O comportamento atual consulta exclusivamente o índice canônico; não mantém leitura de índices legados. Uma única representação reduz divergências entre listagem, exclusão e recuperação. Prefixo de conexão e namespace de domínio são camadas diferentes e devem ser conferidos ao diagnosticar chave aparentemente ausente.

A escrita Lua reúne hash, índice, expiração e evidência de envio em uma operação Redis. Não abrange commit SQL, broker ou provedor. A implementação revisada usa retenção padrão de 30 dias. Índice ordena por score temporal com pequena perturbação aleatória, preservado em atualização: não garante ordem cronológica exata entre eventos próximos.

Leitura usa ordem reversa e páginas por offset; referências sem hash são removidas e podem deixar páginas curtas. Inserções concorrentes podem deslocar offsets: não prometer snapshot ou ausência absoluta de repetição. Timestamp do conteúdo tem prioridade, com fallback ao score para registros incompletos. Campos ausentes recebem defaults sem recorrer a estruturas antigas.

Marcar como lida altera o hash e renova seu TTL, sem mudar score/TTL do índice. Renovar conteúdo não garante retenção da referência na lista. Atualização de mensagem pode preservar estado de leitura sem criar novo envio. Distinguir lida, expirada, removida e entregue ao provedor.

## Identidade, leases e recuperação

IDs estáveis devem derivar de destinatário, entidade e evento, evitando repetir o mesmo sino. Eventos distintos precisam de discriminadores próprios. Inserção idempotente verifica existência sem regravar estado; não significa que todo produtor da aplicação usa identidade estável.

Evidência criada antes de commit fica aguardando confirmação; só depois fica elegível para despacho. Reservas com dono e prazo evitam concorrência. Compare-and-set impede que worker antigo sobrescreva dono novo. Tentativas e backoff são limitados e preservam TTL. Aceite incerto da fila exige manter identidade do dono, pois o job pode ter sido recebido mesmo quando o emissor perdeu a resposta.

Recuperação procura apenas evidências elegíveis e exige item ainda presente no índice e hash. Não recria o evento de negócio. SCAN evita uma operação KEYS bloqueante, mas localizar um lote pequeno pode percorrer um namespace grande. Não há garantia de custo constante. Evidências ambíguas antigas ou aguardando commit não autorizam replay automático.

Rollback SQL pode deixar registro Redis aguardando commit até expirar; isso é uma limitação da fronteira entre sistemas. Estado concluído do job não comprova entrega visível ou leitura pelo usuário. Repetição de envio após resultado externo incerto impede prometer exatamente uma vez no dispositivo.

## Drawer, Web, Android e iOS

O drawer recupera histórico persistido e apresenta leitura, texto e foto; evento ao vivo acelera atualização sem substituir consulta autoritativa. FCM usa inscrições ativas e fila assíncrona. Push normal e crítico têm prioridades/TTL diferentes; o crítico pode preservar contexto de entrada/início. Nem todo crítico é texto anônimo. CPF é excluído nos produtores revisados, sem filtro universal para texto arbitrário.

Web pode usar foto contextual apenas em eventos permitidos e URL HTTPS da mesma origem com caminho autorizado; badge permanece da aplicação. Fallback usa ícone genérico. O contrato Android nativo observado é data-only e não carrega essa foto: a renderização pertence ao cliente. Payload APNs no servidor não prova aplicativo iOS nativo.

Permissões, instalação do app web no iOS, Foco/Não Perturbe e restrições de energia afetam exibição. Essas condições precisam de validação em dispositivos e ambiente de produção; esta revisão não certifica plataformas. Som, heads-up e apresentação não são garantidos por aceite FCM.

## Verificação e diagnóstico

Testes existentes inspecionados cobrem texto por papel/evento, exclusão de CPF, fotos, reconstrução Redis, paginação/órfãos e transporte HTTP simulado. Não foram executados nesta atualização. Mock de Redis/HTTP não comprova servidor real, credenciais, worker, imagem acessível ou exibição pelo SO.

Investigar na ordem das fronteiras: transição confirmada, efeito durável, item persistido, publicação ao vivo, aceite da fila, resposta do provedor e dispositivo. Preservar estado de resultado incerto; não apagar locks ou repetir negócio para recuperar alerta. Sessões, presença, cache e histórico operacional também podem usar Redis, mas têm contratos de retenção e conexão distintos.
