# Query Plan: diagnóstico de consultas com fronteiras de execução

Revisão de implementação privada em 12/11/2026, apresentada como padrão de engenharia. Exemplos são sintéticos; políticas, endpoints e identidades de servidores ficam internos. [Índice](../index.md) · [Cockpit](../operations/technical-cockpit.md).

## Três ações distintas

| Ação | Efeito e evidência |
| --- | --- |
| Explicar | Obtém estratégia e estimativas; não retorna linhas da consulta como resultado de negócio |
| Consultar | Executa leitura e retorna dados sujeitos à autorização e limites próprios |
| Analisar execução | Executa consulta instrumentada; consome recursos mesmo em transação read-only |

O Database Explorer possui editor e aba Query Plan junto às visualizações dos registros. Plano estimado pode carregar ao abrir a aba; medição exige ação explícita. Alterar consulta, conexão, banco ou objeto invalida contexto. Descartar resposta HTTP atrasada evita mostrar plano errado, mas não garante cancelamento imediato no banco.

Esse módulo é uma parte do Cockpit, não um otimizador automático. Administração de dados em outras ações pode alterar registros/estrutura; a presença de uma aba de leitura não torna todo explorador somente leitura. Gerar SQL também não concede permissão para executá-lo.

## MySQL estimado e medido

O caminho estimado inspecionado tenta EXPLAIN FORMAT=JSON em transação read-only e recorre ao formato tabular somente para erros específicos de sintaxe/recurso. Limites de tamanho/linhas impedem resposta sem limite; o normalizador visual recusa fallback tabular por não conter a hierarquia JSON exigida. Duração do handler não é tempo real do SELECT explicado.

O filtro aceita uma consulta SELECT ou WITH não recursivo de leitura, com funções permitidas. Recusa comentários, variáveis, múltiplas instruções, escrita, bloqueios e recursos fora do subconjunto. Essa validação defensiva pode recusar SQL legítimo e não substitui validação do banco nem privilégios mínimos da conta.

A medição observada usa EXPLAIN ANALYZE FORMAT=TREE e exige MySQL 8.0.21+ da série 8.0, ambiente local e política correspondente à identidade real da conexão/servidor. Um parser aceitar TREE de versão anterior não amplia o suporte do executor. Não afirmar suporte genérico a MariaDB, outras séries MySQL ou PostgreSQL.

Execução medida usa conexão dedicada, transação read-only, recusa acesso entre schemas e objetos descobertos fora do subconjunto permitido, e aplica limite de aproximadamente um segundo no banco. Lock exclusivo e UUID de solicitação com histórico temporário controlam concorrência/repetição. Avisos, interrupções ou resultado malformado impedem apresentar uma medição concluída. Finally libera recursos. Essas proteções reduzem risco sem tornar a execução gratuita ou cancelar imediatamente uma consulta ao fechar o navegador.

## MongoDB e Redis

O adaptador explain observado é delimitado ao MongoDB 7.0.x. Aceita find, aggregate, count e distinct em collections autorizadas, com operadores/etapas permitidos. Rejeita escrita, JavaScript, views, acesso entre bancos e etapas de saída como $out/$merge. Pipelines e respostas têm limites de tamanho/profundidade.

queryPlanner fornece planejamento sem estatísticas de execução. executionStats e allPlansExecution executam análise e exigem ação explícita, identidade local autorizada, limite temporal, controle de concorrência/taxa e UUID não reutilizado. Respostas incompletas são recusadas. Estatísticas dos candidatos em allPlansExecution podem ser parciais: não comparar como se cada alternativa tivesse executado completamente.

Redis não oferece plano SQL equivalente nesse módulo. Mostrar mensagem de recurso não suportado é correto; não inventar EXPLAIN para uma chave. Outros usos de Redis como cache/locks do próprio diagnóstico são distintos da conexão explorada.

## Interpretar sem inventar otimização

O frontend normaliza planos em grafo e detalhes, preservando propriedades originais. Dependendo do retorno, MySQL informa tabelas, acesso, índice escolhido/candidatos, cardinalidade estimada, filtros, custos, joins, sort, temporárias e materialização. Valores ausentes devem permanecer ausentes. Há diagnósticos heurísticos; não há criação automática de índice nem otimização garantida.

Exemplo de laboratório com tabela fictícia:

```sql
SELECT category, COUNT(*)
FROM sample_events
WHERE active = 1
GROUP BY category;
```

Verificar seletividade e volume antes de interpretar scan ou índice como “bom” ou “ruim”. Filesort não significa necessariamente escrita em disco; tabela temporária não comprova gargalo; custo não é milissegundo. Só comparar estimativa e valor real do mesmo iterador. Tempos TREE são inclusivos dos filhos e por loop: somar pais/filhos gera dupla contagem. Não assumir correspondência automática entre nós JSON e TREE.

Uma consulta instrumentada mede uma execução com cache, concorrência e dados específicos. Não certifica latência futura. Preservar contexto/hash/timestamp e identificar plano anterior mantido após refresh falho. Não converter erro em plano vazio nem métricas ausentes em zero.

## Segurança, falhas e validação

Sessão técnica e lista de conexões habilitadas limitam acesso; conta do banco mantém seus próprios privilégios. A aplicação não concede grants automaticamente. SQL de leitura pode revelar dados e nomes de objetos; plano e exportação merecem tratamento privado. Políticas locais de medição precisam conferir o servidor efetivo, não apenas um rótulo “dev”.

Distinguir consulta recusada, conexão não autorizada, objeto ausente, concorrência, limite de taxa, timeout e indisponibilidade. Não repetir automaticamente execução medida após resposta incerta. UI deve exigir nova ação e evitar apresentar resultado parcial como completo.

Nesta tarefa foram inspecionados handlers, validadores, executores, interpretadores e apresentação; não foi encontrada suíte atual dedicada de Query Plan. Nenhum EXPLAIN, ANALYZE, grant, benchmark ou teste de browser foi executado. Verificações futuras devem usar ambiente autorizado, dados sintéticos e consultas permitidas/recusadas, cobrindo timeout, mudança de contexto e falha parcial. Isso é orientação de validação, sem alegar testes já realizados ou autorizar nova infraestrutura.
