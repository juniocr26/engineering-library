# ENV Auditor — Guia de Estudo para Entrevista Técnica

[English](../en/env-auditor.md) | [Português brasileiro](env-auditor.md)

Material baseado no [contrato da CLI](../../../env-auditor/README.pt-BR.md), na [implementação](../../../env-auditor/scripts/audit-envs.py) e nos [testes](../../../env-auditor/tests/test_audit_envs.py). Respostas em primeira pessoa descrevem o portfólio, sem inventar experiência profissional. Justificativas são interpretações arquiteturais, salvo registro explícito; alternativas são comparações para estudo, não avaliações históricas confirmadas. Revisão estática em 2026-10-09; nenhum comando do auditor ou teste foi executado nesta revisão.

## 1. VISÃO GERAL

#### Pergunta: Explique o projeto.

**Resposta modelo:** “É uma CLI local em Python que sincroniza atribuições literais de ambiente com exemplos do mesmo diretório. Descobre arquivos recursivamente, escolhe uma referência por alvo, preserva valores existentes das chaves permitidas, acrescenta atribuições ausentes e remove chaves fora da referência. Faz backup dos alvos existentes alterados antes da substituição atômica. Dois modos de prévia calculam o mesmo plano sem escrever.”

Resolve divergência estrutural, não validação da configuração em execução. Não consulta código-fonte, detecta secrets, gera exemplos a partir de arquivos reais, expande valores ou prova que chaves removidas não são usadas.

**Aprofundamento:** Uma chave usada no código pode ser removida? Sim: a única regra de remoção é sua ausência no exemplo selecionado. Revise o contrato antes de sincronizar.

## 2. ARQUITETURA E FLUXO

```text
main → resolve_root → run
  → discover (grupos no filesystem, erros, links ignorados)
  → selecionar pares alvo/referência
  → read_document / parse → plan
  → relatório de prévia OU backup → atomic_write
  → resultados / totais / código de saída
```

`Document` guarda bytes originais e entradas ordenadas `(chave, bloco literal)`. Linhas vazias/comentários são blocos sem chave. Atribuições multilinha são preservadas ou removidas inteiras. `plan` separa transformação de escrita; a prévia calcula os mesmos bytes. `run` processa pares independentemente e continua após erros tratados. É uma CLI funcional pequena, não um framework ou serviço.

#### Pergunta: Por que Python sem dependências?

**Resposta modelo:** “Filesystem, regex, argumentos e arquivos temporários são atendidos pela biblioteca padrão. A distribuição fica pequena, mas o projeto precisa manter seu parser limitado de atribuições.”

Uma biblioteca dotenv poderia ampliar a sintaxe, mas uma API que só carrega valores pode perder a formatação necessária. Um schema tipado validaria valores com uma responsabilidade adicional. Nenhuma dessas alternativas está implementada.

## 3. RAIZ E DESCOBERTA NO FILESYSTEM

#### Pergunta: Por que derivar a raiz do script?

**Resposta modelo:** “`Path(__file__).resolve().parents[2]` escolhe a raiz compartilhada no layout atual `env-auditor/scripts/audit-envs.py`. Executar a partir do portfólio, repositório ou diretório scripts mantém o escopo padrão. Uma raiz relativa explícita é resolvida a partir do diretório do chamador.”

Mover o script muda o padrão: há acoplamento ao layout. Exigir raiz explícita daria controle com menos conveniência. Não existe busca por marcadores em ancestrais. Links na raiz são resolvidos; links encontrados abaixo dela são ignorados.

#### Pergunta: Por que não usar arquivos rastreados pelo Git?

**Resposta modelo:** “Configuração real costuma estar ignorada pelo Git. `os.scandir` encontra projetos irmãos, aninhados, diretórios ocultos e arquivos ignorados, sem consultar Git. Exclusões explícitas limitam a busca; o agrupamento é por diretório, não por fronteira de repositório.”

As exclusões completas estão no [README](../../../env-auditor/README.pt-BR.md#descoberta-e-sincronização). São elegíveis `.env` e `.env.*`, exceto nomes contendo `.bak` ou terminando em `~`. Todo link descoberto é relatado/ignorado, mesmo que não seja de ambiente. `.cargo-cache` e `.dockerized-*` não estão na lista: storage ignorado ainda pode ser percorrido. Adicionar exclusões exigiria tarefa separada de código.

**Aprofundamento:** Oculto significa excluído? Não. São nomes exatos e os sufixos de caminho `bootstrap/cache` e `public/build`.

## 4. PARES ALVO/REFERÊNCIA

#### Pergunta: Como funcionam as variantes?

**Resposta modelo:** “`.env.prod` prefere `.env.prod.example`; na ausência dele, usa `.env.example` no mesmo diretório. O exemplo cria seu alvo correspondente ausente. O exemplo base cria `.env`, mas não inventa `.env.test` ou outras variantes. Sem referência, um alvo existente é ignorado e permanece intacto.”

Todo nome elegível terminado em `.example` é referência, nunca alvo. `.env.odd.example.example` não gera `.env.odd.example`. Não há fallback entre diretórios nem união das chaves de ambientes.

Exemplo: referência com `A=default` e `.env.local` com `A=` e `OLD=local`: A continua vazia e OLD é removida. Uma referência específica de produção contendo apenas PROD remove A do alvo de produção, independentemente de uso no código.

**Trade-off:** Exemplos específicos representam contratos distintos, com manutenção separada. Um exemplo base reduz referências, mas impõe suas chaves a variantes sem exemplo próprio.

## 5. PRESERVAÇÃO LITERAL E REMOÇÃO

#### Pergunta: O que a sincronização garante?

**Resposta modelo:** “Após sucesso, o conjunto de chaves do alvo corresponde ao exemplo validado escolhido. Blocos permitidos existentes ficam literais, incluindo valores vazios, duplicatas e multilinha. Chaves ausentes recebem blocos da referência. Isso não iguala valores nem prova que sejam válidos para a aplicação.”

Comentários/linhas vazias do alvo permanecem mesmo quando atribuições próximas são removidas. Blocos removidos têm backup separado. Alvos novos copiam o exemplo inteiro; alvos existentes recebem somente atribuições ausentes, não todos os comentários da referência. Duplicatas no exemplo causam erro; duplicatas permitidas no alvo permanecem. Exemplo vazio válido remove todas as atribuições ativas de um alvo existente e preserva comentários.

O parser rejeita UTF-8 inválido, NUL, atribuições malformadas, aspas sem fechamento e texto inesperado após aspas. Aceita `export` opcional, identificadores e literais multilinha entre aspas. Não executa, interpola ou expande conteúdo. Não é gramática shell completa, garantia universal dotenv, detector de secrets ou validador de tipos.

**Aprofundamento:** O exemplo pode propagar uma credencial acidental? Sim. É dado literal autoritativo; não há heurística de secrets. O relatório omitir valores não torna o exemplo seguro.

## 6. PRÉVIAS E SAÍDAS

#### Pergunta: Qual a diferença entre dry-run e audit-only?

**Resposta modelo:** “São aliases do mesmo plano sem escrita, mutuamente exclusivos na CLI. Leem/validam entradas e relatam criações, alterações e remoções propostas. Não criam alvos, backups, diretórios ou outros arquivos pelo auditor.”

Prévia não testa permissões futuras de escrita ou sucesso de backup/substituição. Mudanças propostas não falham: saída 0. Erros tratados de descoberta/pares dão 1; raiz inválida/argumentos dão 2. Referências ausentes e links ignorados não falham sozinhos. Relatórios exibem raiz absoluta, caminhos, pares, nomes/contagens de chaves, resultados e totais; não há redação geral de metadados.

A saída completa agora contém uma tabela Unicode por par validado: `Variável | Situação | Ação prevista`. Mostra todas as chaves iniciais, na ordem só no exemplo, só no alvo e compartilhadas, com ordenação alfabética dentro de cada categoria. Caminhos de alvo/referência identificam pares; o resumo agrupa diretórios aninhados pelo primeiro componente relativo (pares na raiz usam `.`). A descoberta continua agrupada por diretório.

O resumo final omite compartilhadas e preserva diferenças iniciais. Prévia usa `Proposta:`; escrita bem-sucedida, `Concluída:`. Pares com falha distinguem `Falhou:` de ações conhecidas marcadas `Não aplicada:`. Projetos sem achados imprimem `Nenhuma pendência de sincronização.` Alvos ausentes (inclusive com exemplo vazio), referências ausentes e erros permanecem visíveis. `added`/`removed`/`shared` incluem comparações planejadas mesmo após falha de escrita; `actual_created`/`actual_updated` contam somente escritas bem-sucedidas. Sincronização sem backup e classificações de baixo uso/ausência de referências no código continuam indisponíveis. Ausência no exemplo não prova desuso. Veja [exemplos sintéticos do terminal](../../../env-auditor/docs/pt-BR/terminal-report.md).

`--strict`, `--strict-unused`, `--show-usage` e `--no-backup` foram removidos e são rejeitados. `.env-audit.json` é ignorado com aviso. Notas antigas sobre uso strong/weak, heurísticas de secrets, união de chaves, strict e propagação real→exemplo estão substituídas por este guia.

## 7. BACKUPS E SUBSTITUIÇÃO ATÔMICA

#### Pergunta: O que acontece antes de escrever?

**Resposta modelo:** “Um alvo existente alterado recebe `.original` exato e `.removed` em sessão UTC única abaixo da raiz. Diretórios usam 0700; arquivos, 0600. Só depois um temporário no mesmo diretório substitui o alvo. Permissões existentes são preservadas; alvos novos usam 0600.”

O stream temporário recebe flush, chmod e fsync antes de `os.replace`. Atomicidade é por alvo, não transação do portfólio. Alvos novos/inalterados não geram backups. Falha anterior à substituição preserva o alvo; backups parciais podem ficar. Outros pares continuam. Backups são texto sensível: gitignore `*` e permissões não são criptografia.

**Aprofundamento:** Há durabilidade após crash e coordenação de escritores? Não há fsync do diretório pai, lock ou comparação com mudanças concorrentes. Dono, ACLs, xattrs e timestamps não são preservados. Rejeitar links estáticos não elimina corridas entre checagem, leitura e substituição.

## 8. FALHAS E EVIDÊNCIAS

| Cenário | Resposta implementada / limite |
| --- | --- |
| Exemplo ou alvo inválido | Erro tratado, alvo intacto, continua, saída final 1 |
| Exemplo ausente | Ignora intacto, sem erro |
| Falha de backup | Sem substituir alvo; cópias parciais podem ficar |
| Falha de replace | Original permanece; limpeza tentada; backups podem ficar |
| Permissão na descoberta | Registra erro, processa pares descobertos, saída 1 |
| Escritor altera alvo durante processamento | Sem coordenação; pode sobrescrever |
| Exemplo omite chave usada externamente | Remove; uso no código/runtime não é consultado |

A maioria dos OSErrors de descoberta/processamento é tratada. Nem toda exceção é capturada por `run`: recursão excessiva ou falhas de saída podem escapar. Não prometa 0/1/2 para qualquer falha ambiental. Falha de limpeza pode deixar temporário; nomes/caminhos não são uma fronteira completa de sigilo.

Há 22 casos `unittest`: raiz real/diretórios do chamador, overrides, recursão/ocultos/ignorados, exclusões, links, precedência/criação, blocos/backups/permissões/idempotência, entradas inválidas/ilegíveis, continuidade, falhas injetadas de backup/replace, snapshots de prévia, colisões e recursos removidos. Na atualização da apresentação em 2026-10-10, os 22 passaram em execução com fixtures temporárias isoladas. [Verificação](../../../env-auditor/docs/pt-BR/verification.md) mantém resultados anteriores separados. Alguns casos lançam subprocessos Python ou sincronizam somente fixtures temporárias; nenhum ambiente real foi sincronizado.

## 9. DECISÕES E ALTERNATIVAS

| Escolha implementada | Benefício | Custo | Alternativa de estudo / gatilho |
| --- | --- | --- | --- |
| Recursão no filesystem | Encontra entradas ignoradas | Storage não excluído; recursão profunda | Raízes explícitas em workspaces grandes |
| Raiz pelo script | Escopo estável entre diretórios | Acoplamento ao layout | Argumento obrigatório para CLI instalada separadamente |
| Exemplos autoritativos | Contrato estrutural determinístico | Remove chave necessária omitida | Schema tipado para validar valores |
| Blocos literais ordenados | Preserva valores/formatação | Gramática limitada; duplicatas mantidas | Parser de sintaxe concreta para ampliar suporte |
| Plano compartilhado | Mesma transformação em prévia/escrita | Prévia não prova escrita | Preflight adicional conforme requisitos |
| Backup e replace | Recuperação/visibilidade por arquivo | Cópias sensíveis; sem rollback global/lock | Lock ou transação coordenada |

## 10. ROTEIRO ORDENADO DE ESTUDO

1. Leia o contrato e siga `main`, `resolve_root`, `discover`; explique raiz relativa e descoberta de ignorados.
2. Resolva no papel referências base/específicas, alvos/referências ausentes e exemplo vazio.
3. Siga `parse` e `plan` com vazios, duplicatas e multilinha; separe conjunto de chaves de valores.
4. Siga prévia, backups e replace; explique atomicidade individual, continuidade e saídas.
5. Leia os 22 testes e separe suas asserções de resultados históricos e concorrência/crash não cobertos.
6. Discuta schemas, bibliotecas de parsing, locks, filtros e retenção depois de explicar os limites atuais.

A ordem é sugestão de estudo; não marca assuntos como estudados, dominados ou concluídos.

## 11. RESPOSTA DE TRINTA SEGUNDOS E APROFUNDAMENTO

“Esta CLI de portfólio alinha chaves de ambiente com exemplos autoritativos. Recursão encontra entradas ignoradas/aninhadas; a raiz derivada do script estabiliza o escopo. Preserva valores literais permitidos, acrescenta atribuições ausentes e remove chaves fora do contrato, com backup e replace individual. As prévias mostram o mesmo plano. Não valida uso em runtime, secrets, tipos ou transação global.”

Pratique: por que idempotência não prova correção em runtime? O que faz um exemplo vazio? Por que prévia com diferenças tem sucesso? Como checagem de link pode sofrer corrida? Como coordenar escritores? Quais garantias precisam de testes reais de filesystem/crash além das fixtures existentes?
