# Política de Privacidade e Aviso de Cookies

[Sumário](../index.md) | [English](../../en/security/privacy-cookies.md)

Verificação estática em 15/11/2026, com base no VivaBem `031acf0`. Esta página descreve implementação local; não comprova implantação, homologação visual ou aprovação jurídica.

## Informação de privacidade

A Política de Privacidade está em `/politica-de-privacidade`, disponível pelos rodapés público e autenticado. O botão “aviso de cookies” na seção de coleta de dados abre o diálogo sem sair da política. A política trata do uso de dados pessoais e direitos; o aviso complementar explica cookies em linguagem simples. O texto do aviso menciona a política, mas não contém um link de retorno.

A data de vigência vem da configuração da política (valor padrão: 22 de julho de 2026), não da data de login. O fluxo inspecionado não apresenta identificador de versão, histórico de versões ou registro de aceite do aviso. O texto jurídico publicado foi preservado; sua presença no código não comprova revisão especializada atual.

## Ciclo de exibição

| Evento | Comportamento implementado |
| --- | --- |
| Login bem-sucedido de paciente ou psicólogo | Autentica e marca exibição pendente. |
| Ativação de conta bem-sucedida | Autentica automaticamente, redireciona ao dashboard e envia snackbar de sucesso. |
| Redefinição de senha bem-sucedida | Autentica automaticamente, redireciona ao dashboard e envia snackbar de sucesso. |
| Solicitação do link de recuperação | Não autentica nem marca exibição. |
| Logout e novo login | Invalida a sessão anterior; o novo login marca nova exibição. |
| Sessão já autenticada, restauração de autenticação, navegação e refresh | Não criam nova pendência por si só. |

A primeira renderização autenticada do dashboard ou da tela de chave Pix consome a pendência e monta o aviso com abertura automática. Outras páginas não consomem essa marca. Após consumida, navegação e refresh não reabrem automaticamente; o usuário ainda pode abrir pela política. O consumo ocorre no servidor ao renderizar, não ao fechar ou comprovar leitura: JavaScript indisponível ou uma resposta não exibida podem consumir a pendência sem leitura. Não é garantia de uma única abertura entre requisições concorrentes.

## Componente reutilizável

Blade monta um componente Alpine.js com diálogo HTML nativo. A política usa seu slot para o botão acionador; o layout autenticado reutiliza o mesmo componente em modo automático. O diálogo usa `showModal()`, backdrop, título acessível e região de conteúdo rolável. Ao abrir, move o foco para fechar e bloqueia a rolagem de fundo; Tab/Shift+Tab circulam pelos controles. Escape e botão fecham, restaurando rolagem e foco ao acionador ainda conectado. Não há fechamento por clique no backdrop.

O botão compartilhado de fechar é circular, vermelho, com ícone X branco no canto superior direito e rótulo acessível. Largura e altura se limitam ao viewport, com rolagem interna e espaçamento/fonte menores em telas estreitas. Variáveis do tema integram cores claras/escuras e foco visível. Essas são propriedades verificadas no código, sem ensaio de navegador ou leitor de tela nesta revisão.

## Snackbar e prioridade visual

A ordem pretendida é página, backdrop, diálogo e snackbar de sucesso. Ao abrir, o componente move temporariamente o snackbar existente para dentro do diálogo usando mutação controlada pelo Alpine e restaura sua posição ao fechar/desmontar. Isso o inclui na camada superior do diálogo nativo; um z-index da página isoladamente não resolveria essa sobreposição. Ativação e redefinição preservam suas mensagens de sucesso nesse caminho. O temporizador normal do snackbar continua ativo; o aviso não mantém a mensagem indefinidamente.

## Informação não é consentimento

O aviso atual contém uma abertura curta e seções sobre cookies necessários, preferências e funcionalidades adicionais, gerenciamento pelo navegador e privacidade/proteção de dados. Explica sessão, proteção de formulários, agendamentos e serviços. A referência a cookies não essenciais é condicional: não comprova categorias opcionais ativas ou escolhas implementadas. Não há tabela comparativa no conteúdo atual, ainda que existam estilos de tabela no componente.

Abrir ou fechar o aviso não registra consentimento, aceitação, retirada, preferências ou autorização de rastreamento. Não há gerenciador de consentimento nesse fluxo. Cookies essenciais sustentam operação, autenticação, sessão e segurança; bloqueá-los pode interromper funcionalidades e exigir novo login. WebSocket, Redis, pagamentos e presença profissional são infraestrutura operacional, não categorias de cookies opcionais livremente desativáveis com garantia de funcionamento integral.

## Limites e manutenção

Validar em navegador os dois perfis, abertura manual/automática, foco, Escape, mobile, temas e sucesso sobre o diálogo permanece pendente. Aprovação jurídica do conteúdo e eventual inventário/gestão de cookies opcionais exigem trabalho separado; não são funcionalidades concluídas por esta documentação. Nenhum código ou texto jurídico foi alterado.
