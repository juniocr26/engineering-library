import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 054 — Prometheus original/correção e quarta falha de atribuição

O par original Builder.Set/Del e a cópia integral corrigida de Keep passaram G1–G9 após o checkpoint038. O original Keep permanece FAIL_HISTORICAL_ATTRIBUTION: a resposta real fala em remover labels do namespace se estiverem presentes, mas não vincula present à lista ns. O capítulo original atribui uma inversão explícita do filtro que esses bytes não demonstram. A cópia completa altera uma frase por língua para registrar descrição de namespace sem suporte e omissão do teste de inclusão. Fonte, código, três FAQs e demais proposições permanecem iguais. Não foram alterados dados, rejeição histórica ou original.

O histórico Builder.Set confirma caller recusado pelo nome de declaração ausente, mas com retorno mencionado; helper com Set/Del passou estrutura, cita somente S1 e omite contrato Del e retornos. Ambas as respostas foram preservadas com hashes brutos históricos conferidos. Isso não prova ganho factual completo nem causa neural controlada.

O código comum Set testa valor vazio, delega e retorna Del; os caminhos não vazios atualizam a primeira adição correspondente ou acrescentam e retornam b. Del registra cada nome e altera add pela expressão escrita, sem deduplicação ou garantia para estados internos arbitrários. Keep retorna no callback para nomes incluídos, acrescenta del para os demais e retorna b após Range concluir normalmente; não limpa del nem filtra add. Get consulta add antes de del e base. Range copia add/del antes dos callbacks e visita adições após os labels base filtrados.

As três variantes de representação e suas tags foram lidas como contexto, sem afirmar variante executada. O caminho inexistente labels.go foi preservado como tentativa falha; labels_slicelabels.go foi localizado pela árvore Git. A fonte instalada slices.Contains/Index esclarece lista vazia sem afirmar identidade do runtime alvo. Quatro arquivos Go passaram gofmt apenas sintático; um controle inválido foi recusado. Sem resolução de imports, tipos, build ou execução Prometheus. Licença Apache2 e NOTICE foram preservados.

O checkpoint038 restaurou4.437arquivos regulares, arquivo compactado119.734.997bytes e39grupos finitos de consumidores com resultados esperados, incluindo originais reprovados. As quatro notas de relatório foram reconstruídas. A auditoria v16 tem34versões relacionadas:29aceitas,1lacuna de citação e4falhas históricas de atribuição; helper interno separado. O lote v16 contém22pares públicos,3prioritários+19suplementares; originais reprovados fora da seleção. Sem aprovação de publicação/Gold/treino.

A correspondência v7 encontrou104referências diretas exatas a58hashes de documentos aceitos,92diferentes e101sem referência nos campos selecionados;8privados excluídos. Sete arquivos originais seguem idênticos. Isso não aprova registro/FAQ/treino. A reconciliação v15 mantém16métricas e nenhum denominador neural inventado. A auditoria de linhagem v5 verificou348/348arestas de acréscimo, sem estado preservado fora do prefixo dos relatórios atuais no corte053/checkpoint037; bytes do arquivo falho031 são apenas história, não recuperação. O registro de ações v17 mantém42repositórios e comandos efetivos adicionais, sem mutação Git. A campanha continua ativa antes de12horas reais.
'''
j=p/'root-report-bundle-progress-054';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v54.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
