import json
from pathlib import Path
from report_bundle_append_v1 import prepare,apply,REPORTS
p=Path(__file__).resolve().parent;root=p.parents[2]
common="""

### Progresso intensivo 066 — máscaras e estado LoRA confrontados com fonte fixada

A auditoria atual H71/H72 verificou14unidades físicas do framework no commit1bf8da05a1ef30a3eb2e8a634180be6557fd3ca0, quatro membros do TAR de congelamento e os seis vetores históricos de índices. Não executou o produtor antigo, framework, tokenizer, modelo ou otimizador. O offset vem de um prefixo templated separadamente: seu comprimento não prova igualdade de tokens com o prefixo da sequência completa, e o método selecionado não exige mensagem final assistant.

Na fórmula selecionada de perda, o limite superior inclusivo pode admitir o primeiro alvo de padding em uma linha curta preenchida. O exemplo no limite exato tem domínio diferente e não admite esse índice. Os casos preservados incluem contagem positiva só de padding, alvo parcialmente truncado com contagem positiva e denominador zero após truncamento completo. São projeções inteiras de seis condições escolhidas; não foi observada perda MLX, NaN ou falha real de treino. O preflight futuro precisa distinguir posições reais, não simplesmente excluir um token ID que também possa ser legítimo.

O estado model/optimizer/RNG mantido em memória pelo trecho de treino não corresponde ao payload selecionado de save, que contém parâmetros treináveis. O carregamento de adapter seguido de novo otimizador não comprova retomada exata. O entrypoint carrega modelo e datasets antes da decisão train/test e permite fallback remoto em caminho local ausente. Nenhum entrypoint foi invocado. A avaliação atual v3 mantém as nove condições NO_GO e zero autorização; o pacote de piloto continua não executável.

Três pares FAQ escolhidos tiveram revisão de apoio físico: DuckDB separa payload bool e flag nula; o frontend limita a ordem de validação ao modo pixels; SQLx exige os três escopos helper/dispatcher/chamador para sustentar o descarte do resultado parcial. São observações selecionadas pelo mesmo agente, não benchmark independente nem aprovação dos148registros. A reconciliação v21 mantém as16métricas e denominador neural atual vazio, acrescentando os achados das FAQs sem convertê-los em precisão semântica. O fechamento v40 de564dependências ainda aguarda nova recuperação.
"""
j=p/'root-report-bundle-progress-066';prepare(root,j,{n:common.encode() for n in REPORTS});out=apply(root,j);assert out['status']=='APPLIED_OR_ALREADY_APPLIED'
with (p/'root-report-append-receipt-v66.json').open('x') as f:json.dump({'bundle':str(j.relative_to(root)),'outcome':out},f,indent=2);f.write('\n')
print(out['status'])
