# Validação de contexto, diagnóstico e privacidade

[Sumário](../index.md) | [English](../../en/security/context-and-diagnostics.md)

Revisado em 2026-11-10. Público: autores de catálogo, integradores e revisores de segurança. A: inspeção da implementação atual. Escopo: minimização antes do despacho; sem presumir certificação regulatória, criptografia ou auditoria de acesso em produção.

<!-- reading-section: context -->
## Contexto escalar aprovado

`Dominio\CampoContexto` define `nome`, `tipo='string'`, `anulavel=false`, `minimo=null`, `valoresPermitidos=[]`. Nomes seguem `[a-z][a-z0-9_]{0,63}`. Tipos: `string`, `integer`, `number` finito e `boolean`. Verificação estrita rejeita strings numéricas, booleanos como números, arrays, objetos e null não anulável. Campos aprovados ausentes são opcionais e omitidos; null permitido, zero, false e string vazia permanecem distintos.

`CampoContexto::normalizar` permite até 32 campos únicos. Forma abreviada textual associa `attempt/retry_delay_ms` a inteiro não negativo, `duration_ms` a número não negativo, `retry_scheduled/success` a booleano e nomes comuns a string. `dependency/operation` exigem `CampoContexto` explícito com lista não vazia. Campos convencionais reservados não podem ter tipos contraditórios. Listas aceitam até 100 valores tipados, comparados estritamente; strings aprovadas precisam de UTF-8 válido e até 1024 bytes. Mínimos devem ser numéricos e finitos; campos convencionais não negativos não aceitam mínimo negativo.

`Aplicacao\SanitizadorContexto::sanitizar` percorre definições aprovadas, sem percorrer o grafo de objetos da entrada. Campos desconhecidos são descartados sem serialização. Mesmo nomes aprovados correspondentes ao padrão sensível são descartados antes da validação: password/senha, token, authorization, cookie, secret/private, patient/paciente, medical/medic, financial/finance, payment/pagamento, payload/body/corpo, binding/sql, request/response, prontuario/cartao/credential. É filtro de nomes, sem detecção semântica de valores sensíveis em nomes inocentes.

Valores aprovados são validados; strings são truncadas a 1024 bytes, UTF-8 inválido é substituído e o limite final é ajustado para UTF-8 válido. Chaves são ordenadas. Listas são verificadas antes do truncamento. Revisar significado antes de aprovar: permitir `text` não torna seguro texto clínico arbitrário. Identidades do produtor, IDs de correlação/requisição, mensagem/impacto estáticos, taxonomia e mensagens diagnósticas aprovadas também exigem revisão; validadores sintáticos não removem seu conteúdo sensível.

<!-- reading-section: diagnostics -->
## Diagnóstico de exceções

`Aplicacao\DiagnosticoExcecao` não copia mensagens de Throwable diretamente nem inclui argumentos do rastro. Emite `type`, `message` fixa aprovada ou `[REDACTED]`, `message_redacted`, `source`, `frames` limitados, `previous` limitado e `truncation` (`frames_omitted`, `cause_chain_truncated`, `source_omitted`). Tipos anônimos tornam-se `anonymous_throwable`.

Sem raiz configurada, omite localizações. Quando informada, a raiz precisa resolver para diretório existente diferente de `/`; `localizacao` inclui apenas arquivos canônicos dentro dela, com caminho relativo até 256 bytes usando letras/dígitos/underscore/ponto/barra/hífen, mais linha. Quadros mantêm apenas file/line permitidos e strings class/function/type até 160 bytes compatíveis com o padrão de símbolos do código. Padrão: 12 quadros e 3 causas totais; configurável para 0–16 e 1–4. Truncamento é explícito, sem comprovar ausência de causas mais profundas.

`mensagensAprovadas` associa nome exato da classe de exceção a string estática UTF-8 não vazia até 256 bytes. Substitui por texto aprovado, sem aprovar conteúdo da mensagem em execução ou corresponder automaticamente às classes ancestrais. Nomes de classes e símbolos permitidos ainda revelam estrutura; corpus e armazenamento continuam privados. Configurar somente raiz aprovada e mensagens estáticas revisadas.

<!-- reading-section: trust -->
## Confiança e responsabilidades de armazenamento

O registrador é a fronteira de privacidade. Construir `Dominio\Evento` e enviá-lo diretamente ao gravador contorna essa fronteira; `Evento::paraArray` não revalida conteúdo. `Gravador` customizado também pode reter dados de outra forma. Revisar adaptadores e destinos antes da adoção. A biblioteca não implementa autenticação/autorização do chamador, criptografia de logs, custódia de credenciais ou exclusão por retenção.

O gravador solicita `0700` para diretórios novos e inicializa permissões de marcador/arquivo diário novo vazio com `0600`. Diretórios existentes são canonicalizados, sem endurecimento por chmod; arquivos diários existentes não vazios não têm permissões automaticamente reparadas. Operadores precisam verificar propriedade, mounts e acessos existentes. Verificações de symlink, arquivo regular com link único e identidade inode/device reduzem riscos de substituição, sem garantir proteção geral contra atacantes privilegiados ou toda corrida de filesystem. Entrada de diretório é resolvida por `realpath`; não afirmar proibição de todo symlink no caminho fornecido.

Usar armazenamento privado exclusivo. Exemplos não devem conter dotenv real, credenciais, prontuários, payloads de pagamento, snapshots ou mensagens reais de exceção. Causas de falhas do gravador podem conter mensagens externas sensíveis: não renderizar cadeias cegamente em saídas públicas nem enviá-las recursivamente ao logger quebrado.

<!-- reading-section: evidence -->
## Verificação e manutenção

Evidências: `src/Dominio/CampoContexto.php::{validar,normalizar}`, `src/Aplicacao/SanitizadorContexto.php::{sanitizar,excecao}`, `src/Aplicacao/DiagnosticoExcecao.php::{causa,localizacao}`, `src/Infraestrutura/GravadorArquivoDiario.php`. Asserções: `tests/Aplicacao/{ContextoTest,DiagnosticoTest}.php`, `tests/Dominio/CampoContextoTest.php`, `tests/Infraestrutura/{PsrTest,ArquivoDiarioTest}.php`. Consultar [verificação executada](../testing/verification.md).

Mantenedores devem rever os dois idiomas após mudanças em campos, padrão sensível, classe/raiz diagnóstica, serialização, permissões ou adaptadores. Testes com sentinelas sintéticas sustentam os casos descritos, sem provar detecção de todo dado sensível. Permissões implantadas, coletores, controles do registry privado e políticas de entrada dos consumidores permanecem fora desta verificação.
