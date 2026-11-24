import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common='''

### Progresso intensivo 057 — SDK corrigido e pares Chi recuperados; cobertura original pública

A correção completa do SDK concluiu G1–G9 no checkpoint041, com4.888arquivos restaurados, arquivo compactado124.739.773bytes e42grupos finitos. O consumidor preserva os dois documentos corrigidos e os dois originais reprovados,207arquivos do censo, três respostas históricas, seis links e cinco arquivos sintaticamente verificados. O original mantém G2FAIL. As quatro notas dos relatórios foram reconstruídas pelo produtor arquivado e recibo; a rotina passou a manter os relatórios canônicos sem acréscimos enquanto o checkpoint está em execução. Isso é disciplina operacional, não certificação de bloqueio global ou atomicidade.

Os dois pares originais Chi middleware e throttle passaram G1–G9 após checkpoint042:4.954arquivos restaurados, arquivo compactado125.439.964bytes e43grupos finitos, incluindo quatro documentos, seis trechos, três respostas históricas, seis arquivos Go sintáticos e controle recusado. Oito valores de Retry-After foram derivados da fonte com aritmética inteira Python e coincidem com expectativas escritas nos testes. Nenhuma função Go desses casos, teste upstream ou servidor HTTP foi executado. O contraexemplo histórico que rejeitou o guard por palavras-chave de defer permanece preservado, sem repetição ou alteração de produção.

As atribuições originais Chi foram confirmadas: Recoverer baseline afirma corpo adiado antes do próximo handler e inventa variável panic/outros eventos de logging; throttle baseline exige backlog positivo por seguir a mensagem de pânico, enquanto a guarda aceita zero. Timeout preserva fábrica, callback, cancelamento antes da consulta de erro e chamada síncrona do próximo handler. Recoverer repropaga ErrAbortHandler antes de logging/status e usa a comparação exata Connection!=Upgrade. Throttle distingue admissão/processamento, timer de espera e devoluções adiadas LIFO, sem interrupção forçada ou prioridade fixa de cancelamento.

A auditoria v20 conta41versões relacionadas:35aceitas tecnicamente,1lacuna de citação e5falhas históricas de atribuição. O helper interno continua separado. O lote v19 reúne28pares públicos,3prioritários+25suplementares, com cinco originais reprovados fora da seleção. A reconciliação v18 cobre16métricas sem denominadores neurais inventados. A correspondência v9 encontrou144referências diretas exatas a70hashes aceitos,52diferentes,101sem referência nos campos selecionados e8registros privados excluídos; sete arquivos originais permanecem idênticos. Referências não concedem aprovação de registro/FAQ/direitos/Gold.

A matriz de cobertura v2 distingue23tópicos públicos originais:18aceitos e5reprovados por atribuição. Correções não substituem a decisão dos originais. O capítulo documentation-agent-contracts é escopo interno adicional: não tem referência direta nos dois campos examinados do dataset, seus bytes atuais não aparecem no blobstorev4 e sua proveniência mistura arquivos históricos de trabalho e suplementos posteriores. O preflight recusou a suposição de identidade antes da leitura semântica, preservou a falha e abriu investigação separada. Não é um alvo público implicitamente aceito ou um Gold.

O inventário complementar de relatórios temporários v2 verificou124/124arquivos em31raízes declaradas,67.356.006bytes, todos com afterhash dos recibos. Complementa as36raízes de restauração inventariadas antes; os cortes são datados, não inventário final automático de tudo posterior. O registro de ações v19 mantém42blocos e acrescenta16comandos SDK/Chi, incluindo a falha de caminho de teste, sem mutação Git. Às06:31UTC decorreram cerca de7h49desde a linha de base desta campanha, sem somar as oito horas anteriores. A campanha permanece ativa, com zero nova geração local e nenhuma aprovação de publicação/Gold/treino.
'''
j=p/'root-report-bundle-progress-057';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v57.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
