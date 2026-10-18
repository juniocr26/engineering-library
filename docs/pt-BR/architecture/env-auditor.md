# env-auditor: dossiê de implementação

[English](../../en/architecture/env-auditor.md) | [Português brasileiro](env-auditor.md)

Revisão estática: 2026-10-10. Este projeto independente não tem chamadas runtime verificadas a outro repositório do portfólio. Links de evidência sustentam as explicações completas abaixo.

## Execução, representação e decisões

O produto implementado é uma CLI Python local com biblioteca padrão que alinha as chaves literais de arquivos de ambiente a exemplos autoritativos. Não é um serviço nem um analisador de uso no código. `main` interpreta argumentos, `resolve_root` define o escopo, `discover` agrupa arquivos por diretório, `parse` constrói um `Document`, `plan` calcula bytes e `run` apresenta ou grava cada par. A raiz padrão fica dois pais acima do script resolvido; raízes relativas explícitas usam o diretório do chamador. Não há API entre projetos: percorrer diretórios irmãos é uma capacidade de filesystem, não integração de aplicações.

`Document.raw` conserva bytes originais e `blocks` é uma lista ordenada de `(chave ou None, texto literal)`. Um bloco pode abranger linhas entre aspas; comentários não têm chave. Conjuntos auxiliam a comparação e `Counter` rejeita chaves duplicadas no exemplo. Duplicatas existentes no alvo sobrevivem quando permitidas. O planejamento conserva blocos permitidos, coleta removidos e acrescenta atribuições ausentes do exemplo. Um alvo novo copia toda a referência validada, incluindo comentários. Uma referência vazia remove todas as atribuições do alvo existente, preservando comentários. Esse comportamento estrutural não prova que a aplicação funcionará depois.

A descoberta usa recursão ordenada com `os.scandir` e exclusões exatas, independentemente do Git. Exemplos específicos de variantes prevalecem sobre o exemplo base do mesmo diretório. Alvos sem referência são ignorados e exemplos base não inventam variantes arbitrárias. A descoberta encontra configurações ignoradas pelo Git, mas pode percorrer armazenamento não excluído; percurso e ordenação crescem com as entradas, enquanto interpretação e planejamento crescem com bytes e blocos. `key in added` usa atualmente uma lista, portanto muitas chaves ausentes podem tornar quadráticas as comparações ao acrescentar blocos. É análise estática de complexidade, não um gargalo medido. Um conjunto adicional à lista ordenada seria uma otimização possível.

Separar planejamento de mutação torna a prévia fiel à transformação e facilita testes. Uma biblioteca dotenv que preserve formatação poderia ampliar a gramática; schemas tipados poderiam validar valores; raízes de inclusão explícitas limitariam o percurso. São alternativas hipotéticas. Nenhuma justificaria executar a entrada arbitrária. O parser atual não executa nem interpola valores, mas aceita apenas sua gramática literal documentada.

## Segurança do filesystem e recuperação em texto puro

As entradas precisam ser arquivos regulares; a descoberta ignora links simbólicos e o processamento verifica novamente o tipo do arquivo. O parser rejeita UTF-8 inválido, bytes NUL, atribuições malformadas e aspas sem fechamento. Essas verificações reduzem percurso acidental e transformações inválidas; não há bloqueio de arquivos nem percurso por descritores livre de corridas. Um caminho pode mudar entre a verificação e o uso. Isso não deve ser descrito como sandbox de filesystem adversarial.

Valores não aparecem no terminal, mas caminhos e nomes de chaves permanecem visíveis. Valores de referência são literais confiados: o programa não detecta segredos. Backups contêm bytes originais e blocos removidos em texto puro. Diretórios de sessão usam 0700, arquivos usam 0600 e o ignore da raiz de backup contém `*`. Isso reduz acesso comum e inclusão acidental no Git, mas não cifra backups, não protege contra o mesmo usuário e não define retenção. Bits de permissão do alvo existente são preservados; proprietário, ACLs e atributos estendidos não são.

Um alvo existente alterado recebe backup antes da substituição. O temporário no mesmo diretório recebe flush, fsync, chmod e substitui o alvo com `os.replace`. Isso oferece substituição por arquivo, não transação de múltiplos arquivos. O diretório não recebe fsync e escritores concorrentes podem ser sobrescritos. Durabilidade mais forte exigiria sincronização do diretório; coordenação de escritores exigiria bloqueio e detecção de mudanças. Ambas são alterações hipotéticas. Nenhum ambiente real ou backup foi inspecionado nesta revisão documental.

## Operação, falhas e limites de evidência

Consulte o contrato da CLI no README antes de sincronizar. `--dry-run` e `--audit-only` são aliases mutuamente exclusivos da mesma prévia somente leitura. Não criam alvos nem backups. Uma diferença proposta sozinha termina com 0; erros tratados de descoberta/par retornam 1; raiz ou argumentos inválidos retornam 2. Links ignorados e referências ausentes, isoladamente, não são erros. A prévia não comprova futura permissão ou sucesso do backup.

A gravação acontece ao invocar o comando normal, não por daemon em segundo plano. Erros são tratados por par, permitindo continuar os demais; gravações anteriores bem-sucedidas não são revertidas. Se o backup falha, a substituição não começa. Se a substituição falha, backups ou artefatos temporários parciais podem permanecer. O operador deve analisar o relatório de identificadores, localizar a sessão exata de backup e restaurar deliberadamente o original desejado após verificar edições concorrentes. Não há rollback em massa, retenção ou recuperação automática de crash. Falhas de saída e recursão patológica podem escapar do mapeamento usual de erros.

A suíte `unittest` existente usa fixtures temporárias isoladas para parser, variantes, prévia, backups, falhas de substituição, permissões e idempotência. Registros de verificação existentes são históricos, não execuções desta revisão. Nenhum teste de aplicação ou runtime foi executado aqui. A instalação distribui o script com Python 3.10+; mover o script altera sua raiz padrão. Não há implantação de serviço, banco, topologia Docker, pagamentos ou API de rede a documentar. Uma comparação na biblioteca pode abordar esses conceitos sem sugerir que as outras aplicações do portfólio chamam a CLI.

Lacunas de evidência: durabilidade sob crash/queda de energia, escritores concorrentes e corridas no filesystem, portabilidade de ACL/proprietário, árvores muito profundas, retenção de backups e medições de escala. Exigem implementação autorizada separadamente e experimentos isolados; não há alegação de vazão ou compatibilidade completa com parser shell.

## Evidência de apoio

- [architecture/implementation-review](../../../../env-auditor/docs/pt-BR/architecture/implementation-review.md)
- [security/filesystem-boundaries](../../../../env-auditor/docs/pt-BR/security/filesystem-boundaries.md)
- [operations/recovery-and-evidence](../../../../env-auditor/docs/pt-BR/operations/recovery-and-evidence.md)
- [Interview / Entrevista](../interviews/env-auditor.md)

## Conciliação com o código — 2026-10-18

`000949ff926fcc71428855193a2a029520f7e887`. Código, entradas API/CLI, limites de persistência/recursos e definições de testes foram revisados estaticamente. Explicações e respostas existentes continuam aplicáveis nos limites registrados. Não foram produzidos resultados de runtime. Consulte o [roteiro autossuficiente de implementação e entrevista](../../../../env-auditor/docs/pt-BR/guides/implementation-study.md).
