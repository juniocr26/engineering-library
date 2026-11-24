"""Append an explicitly active, recoverable cut to exactly four canonical reports."""
from pathlib import Path
import datetime
import hashlib
import json

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
now = datetime.datetime.now(datetime.timezone.utc)
baseline = json.loads((P/'baseline.json').read_text())
elapsed = (now-datetime.datetime.fromisoformat(baseline['started_at'])).total_seconds()
prefix = 'agent/research/final-intensive-20261121/'
sections = {
    'AI_TRAINING_CAMPAIGN_REPORT.md': f'''
## Campanha intensiva final — corte ativo {now.isoformat()}

**ACTIVE — pesquisa em andamento; não é conclusão de 12 horas.** Início desta execução: {baseline['started_at']}; decorrido neste corte: {elapsed:.1f}s. Tempo da campanha anterior não é somado. O estado inicial era HEAD `{baseline['head']}`, sem alterações preexistentes indicadas por `git status`; os quatro relatórios não existiam na raiz e não eram rastreados. Foram recuperados byte a byte do checkpoint016 anterior, após conferir o hash do archive e os quatro hashes finais. Os `.recovered.bin` preservam as versões recuperadas antes dos apêndices atuais.

O [contrato congelado v3]({prefix}documentation-done-v3.json) explicita G1 identidade, G2 fatos, G3 arquitetura, G4 completude, G5 exemplos/testes, G6 equivalência EN/PT, G7 manutenção, G8 verificação separada e G9 recuperação/proveniência. Todos os gates aplicáveis devem passar; N/A precisa de justificativa anterior; incerteza crítica não conta como PASS. TECHNICALLY_ACCEPTED, PUBLICATION_APPROVED e TRAINING_GOLD_APPROVED têm autoridades separadas. O status de prontidão do modelo continua INSUFFICIENT_EVIDENCE; as metas 80%/95% são provisórias, não resultados.

A baseline atual conferiu42 repositórios,32Portfólio e10VivaBem; os41 externos mantêm HEAD/status anteriores. Os7 arquivos/305 registros mantêm os hashes; isto não é reaprovação semântica de305 exemplos. Caller1.9.43, planner0.3.6, HelperRetrieval0.1.5 e Maintenance0.1.5 foram lidos na fonte atual. Docker recusou acesso ao socket; nenhuma escalada foi tentada, nenhum modelo externo foi usado. Identidade/runtime atual do Ollama não foi revalidado; digest e testes anteriores são históricos.

No [estudo de vínculos]({prefix}binding-study-results-v1.json),60/60 mutações foram recusadas e3/3 envelopes intactos preservados: falsa admissão de integridade0/60; falsa recusa de integridade0/3. São controles correlacionados de três tarefas DEV, sem comparador de produção. Não são taxas semânticas de falsos positivos/negativos e não provam resistência se o próprio anchor confiável for substituído. A verificação de symlink é preflight estático, sem garantia contra corrida concorrente.

A [reaquisição Git]({prefix}source-claim-reacquisition-results-v1.json) recuperou quatro arquivos públicos nas revisões congeladas e conferiu28/28 proposições selecionadas,56 ocorrências linguísticas. Todos os spans e hashes conferem, e os pares exatos têm suporte estático no contexto lido. É nova conferência das mesmas28 proposições K, pelo mesmo agente, sem nova amostra independente ou inferência. O histórico K3/3 continua cópia de fatos fornecidos; T2/2 continua template manual;0/9 e0/13 históricos não mudam.

Foi preparado [outro par Zod]({prefix}zod-clarification-results-v1.json) que esclarece em ambos os idiomas que revisão separada não significa revisor humano independente. Os originais, exemplos de código e citações permanecem idênticos; o diff é isolado. Status: candidato para revisão, com nova aceitação G1–G9 ainda INCONCLUSIVE. Não há promoção de status original, publicação ou Gold.

Checkpoint001 restaurou67 arquivos, verificou bytes/modos e executou o consumidor restaurado dos três envelopes: [recibo]({prefix}checkpoint-001.json). Isso prova recuperação local e consumo desse perfil finito; não clone limpo, restore remoto ou estado neural. Nenhuma suíte permanente ou projeto externo foi executado neste corte; os312 Python/242 Ruby/100de102frontend pertencem à execução anterior.

Próximas hipóteses: revisões reais com evidência de antes/depois e limites de histórico local; revisão completa dos candidatos sob G1–G9; desafios à recuperação e ao consumo do estado; preparação não executável do piloto. A campanha permanece ativa. Treino, adapters, updates, Gold e publicação:0.
''',
    'AI_TRAINING_FILE_INVENTORY.md': f'''
## Inventário da campanha intensiva — corte ativo {now.isoformat()}

Projeto: engineering-library. Alterações desta execução: quatro relatórios canônicos recuperados/criados e estendidos; pesquisa isolada em `{prefix}`; checkpoints em `.local-backups/final-intensive-20261121/`. Nenhum arquivo foi excluído; código de aplicação, testes permanentes, catálogo e Git não receberam alterações. O estado anterior foi registrado em `baseline.json`.

Arquivos de pesquisa: `documentation-done-v3.json` e `research-queue-v1.json` congelam critérios e hipóteses; `baseline-verification-v1.json` identifica cada um dos42 repositórios e7datasets, comandos e resultados; `canonical-recovery-v1.json` comprova a recuperação exata dos relatórios; `.recovered.bin` preservam seus bytes anteriores. `binding-study-protocol-v1.json`, `trusted-binding-anchor-v1.json`, `binding-validator-freeze-v1.json`, `binding_envelope_v1.py` e `binding-study-results-v1.json` registram os63 controles. `source-claim-reacquisition-*` e `reacquired-public-sources/` preservam28 proposições e quatro fontes públicas. `zod-clarification-*` e `zod-provenance-candidate-v3/` contêm plano, novo par e dois diffs. Os scripts produtores permanecem preservados, incluindo o preparo v1 que falhou antes de emitir protocolo por incluir uma linha sem source_path; v2 seleciona somente os IDs obrigatórios congelados.

A lista completa por arquivo/categoria será emitida no próximo inventário técnico. Inspeção externa de corpos de código neste corte: `fastapi` (`fastapi/dependencies/models.py`, `fastapi/dependencies/utils.py`), `cobra` (`args.go`) e `zod` (`packages/zod/src/v4/core/parse.ts`), todos **sem alterações**. Os demais externos tiveram apenas HEAD/status conferidos; seus nomes exatos e comandos estão na baseline atual. Material privado/evaluation-reserve não foi usado em inferência ou treinamento.

Validações atuais: scripts de pesquisa executados;28/28 hashes/spans;63/63 controles com resultado esperado; restore de67 arquivos e replay dos três envelopes. Docker: permission denied. Nenhum teste de aplicação novo executado. Ainda ACTIVE, sem alegação de12horas ou de conclusão de toda a missão.
''',
    'AI_FINE_TUNING_READINESS.md': f'''
## Campanha intensiva final — prontidão no corte {now.isoformat()}

**NO_GO nos nove gates; MODEL_READY_FOR_ASSISTED_DOCUMENTATION: INSUFFICIENT_EVIDENCE.** Não houve instalação, download de pesos, tokenizer nativo, adapter, optimizer ou treinamento. Docker inacessível ao sandbox atual; último digest/runtime continua evidência histórica, não verificação atual.

Gates:1base/tokenizer nativos não aprovados/carregados;2direitos/alvos/Gold não aprovados;3avaliação independente por famílias não estabelecida;4pares supervisionados finais não aprovados;5tokenização/máscara reais não verificadas;6framework Apple Silicon não validado;7pico/tempo de treino não medidos;8inventário Q/V e recuperação neural completos não demonstrados;9lançamento não autorizado. Os resultados atuais de integridade/recuperação de documentos não satisfazem esses gates de treinamento.

O [contrato v3]({prefix}documentation-done-v3.json) mantém80% de aceitação completa, zero erro crítico aceito/REMOVE inseguro,95% de identificadores, cobertura bilíngue total e ausência de regressão como metas propostas. Não existe amostra independente suficiente para declarar READY. Os305 registros e os28 fatos K conferidos continuam excluídos por suas políticas atuais; conferência de fonte não concede treinamento. Tetos históricos16/batch1/acumulação1/512/rank4/QV/600s/1800s não foram validados nem alterados.
''',
    'AI_TRAINING_RESUME.md': f'''
## Retomada da campanha intensiva final — ACTIVE em {now.isoformat()}

Esta execução começou em {baseline['started_at']}. Ler primeiro `{prefix}baseline.json`, `research-queue-v1.json`, `documentation-done-v3.json`, os resultados de vínculos/reaquisição e `checkpoint-001.json`. Os parágrafos COMPLETE_VERIFIED anteriores descrevem outra campanha; a presente é uma nova execução autorizada, ainda não concluída.

Já realizado: recuperação exata dos quatro relatórios ausentes; baseline de42 repositórios e305registros;63 controles de integridade;28 proposições K reconferidas em quatro objetos Git; par Zod isolado com redação explícita de mesmo agente; checkpoint001 com restore e consumo real. Não repetir essas hipóteses sem nova pergunta falsificável. Nenhuma nova inferência ocorreu.

Continuar H5 com revisão real de `engineering-library` e seus chamadores/documentação existente, congelando escopo antes da avaliação. Os clones públicos selecionados mostram apenas um commit no histórico por caminho; verificar disponibilidade de ancestrais antes de inferir comportamento antigo. Falta de objeto implica INCONCLUSIVE, não REMOVE. Depois executar H6 com desafios de restauração/portabilidade e reavaliar candidato completo. Atualizar somente os quatro relatórios por apêndices, preservando hashes/preimages antes de cada corte. Próximo checkpoint em cerca de30min ou após resultado crítico.

Não pedir ao proprietário; sem Docker, continuar análise estática e protótipos locais. Não instalar framework, baixar pesos, executar treino, alterar produção/testes/catálogo/externos ou escrever Git. Todos os gates nativos permanecem NO_GO. Produção e dois testes frontend historicamente falhos continuam pendentes; não declarar nova execução. Sem conclusão ou duração de12horas neste corte.
''',
}
backup = P/'root-preimages-cut-001'
backup.mkdir()
rows = []
for name, addition in sections.items():
    path = ROOT/name
    raw = path.read_bytes()
    with (backup/(name+'.bin')).open('xb') as stream:
        stream.write(raw)
    with path.open('ab') as stream:
        stream.write(addition.encode())
    after = path.read_bytes()
    assert after.startswith(raw)
    rows.append({'path': name, 'before_sha256': hashlib.sha256(raw).hexdigest(), 'after_sha256': hashlib.sha256(after).hexdigest(),
                 'preimage': str((backup/(name+'.bin')).relative_to(ROOT)), 'append_start_line': len(raw.splitlines())+1})
with (P/'root-report-append-cut-001.json').open('x') as stream:
    json.dump({'at': now.isoformat(), 'elapsed_seconds': elapsed, 'status': 'ACTIVE', 'reports': rows}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'status': 'ACTIVE', 'elapsed_seconds': elapsed, 'reports_updated': len(rows)}))
