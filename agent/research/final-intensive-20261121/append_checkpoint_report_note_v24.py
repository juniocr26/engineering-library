"""Reconstruct post-checkpoint report notes from archived code plus sidecar receipt."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import tempfile

REPORTS=['AI_TRAINING_CAMPAIGN_REPORT.md','AI_TRAINING_FILE_INVENTORY.md',
         'AI_FINE_TUNING_READINESS.md','AI_TRAINING_RESUME.md']
RELATIVE=Path('agent/research/final-intensive-20261121')
STAGES=['consumer_replay','exception_scope_consumer_replay','helper_admission_consumer_replay',
        'zod_jsc_parser_consumer_replay','priority_pair_syntax_consumer_replay','faq_binding_consumer_replay',
        'cpp_AST_IR_consumer_replay','public_exposure_consumer_replay','chi_revision_consumer_replay','openshot_case_binding_consumer_replay','tokenizer_metadata_consumer_replay','esp_hal_js_syntax_consumer_replay','helper_dynamic_delivery_consumer_replay','helper_job_delivery_consumer_replay','report_bundle_recovery_consumer_replay','owned_go_type_relations_consumer_replay','stdlib_go_type_relations_consumer_replay','shellwords_version_scope_consumer_replay','gguf_tensor_directory_consumer_replay','bilingual_screen_metric_consumer_replay','go_image_original_target_consumer_replay','go_image_compression_consumer_replay','go_source_graph_consumer_replay','go_image_configuration_consumer_replay','config_inline_faq_consumer_replay','starlette_server_error_consumer_replay','frontend_dimensions_consumer_replay','httpguts_snapshot_consumer_replay','starlette_task_iteration_consumer_replay','go_image_quality_consumer_replay','go_image_dimensions_consumer_replay','checkpoint_paths_consumer_replay','rails_request_consumer_replay','redis_targets_consumer_replay','ruff_target_consumer_replay','opencv_targets_consumer_replay','duckdb_target_consumer_replay','prometheus_targets_consumer_replay','fastify_target_consumer_replay','sqlx_targets_consumer_replay','sdk_retry_target_consumer_replay','chi_targets_consumer_replay']


def make_note(receipt):
    assert all(receipt[key]['exit_code']==0 for key in STAGES)
    assert len(receipt['raylib_owned_fragment_replays'])==3
    assert all(case['matched'] for case in receipt['raylib_owned_fragment_replays'])
    assert receipt['active_campaign'] is True and receipt['neural_calls']==0
    number=receipt['checkpoint']
    return f'''
### Recuperação verificada do corte — checkpoint {number:03d}

Em {receipt['at']}, o checkpoint {number:03d} restaurou {receipt['regular_files_restored_and_hash_verified']} arquivos regulares com hashes/modos verificados. {len(STAGES)+1} grupos de consumidores foram reexecutados; os controles C incluem recusas sintáticas esperadas. Isso não é execução das aplicações fonte, aprovação semântica geral, clone limpo, recuperação de pesos/otimizador, validação Windows ou backup remoto.

Recibo: `agent/research/final-intensive-20261121/checkpoint-{number:03d}.json`. Este apêndice posterior ao arquivo é reconstruível a partir do script arquivado `append_checkpoint_report_note_v17.py`, dos quatro prefixos de relatório arquivados e do `receipt.json` lateral do checkpoint. A reconstrução dos quatro relatórios foi comparada byte a byte antes da aplicação do apêndice. Preserve o diretório completo do checkpoint, incluindo os recibos laterais. A campanha continua ACTIVE; aproximadamente 12 horas e novas comparações neurais ainda não foram concluídas.
'''.encode()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--checkpoint',required=True,type=int)
    args=parser.parse_args()
    P=Path(__file__).resolve().parent
    ROOT=P.parents[2]
    sha=lambda raw:hashlib.sha256(raw).hexdigest()
    receipt_path=P/f'checkpoint-{args.checkpoint:03d}.json'
    receipt_bytes=receipt_path.read_bytes()
    receipt=json.loads(receipt_bytes)
    folder=(ROOT/receipt['archive']).parent
    assert (folder/'receipt.json').read_bytes()==receipt_bytes
    assert sha((ROOT/receipt['input_manifest']).read_bytes())==receipt['input_manifest_sha256']
    manifest=json.loads((ROOT/receipt['input_manifest']).read_text())
    expected={entry['path']:entry for entry in manifest}
    restored=Path(receipt['restored_root'])
    relative_script=str(RELATIVE/Path(__file__).name)
    archived_script=restored/relative_script
    assert sha(archived_script.read_bytes())==expected[relative_script]['sha256']
    assert archived_script.read_bytes()==Path(__file__).read_bytes()
    spec=importlib.util.spec_from_file_location('restored_checkpoint_note',archived_script)
    archived_module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(archived_module)
    note=make_note(receipt)
    assert archived_module.make_note(receipt)==note
    reconstructed=Path(tempfile.mkdtemp(prefix=f'el-report-reconstruction-{args.checkpoint:03d}-',dir='/private/tmp'))
    candidates=[]
    for name in REPORTS:
        original=(ROOT/name).read_bytes()
        archived_prefix=(restored/name).read_bytes()
        assert sha(original)==expected[name]['sha256']
        assert archived_prefix==original
        candidate=original+note
        rebuilt=archived_prefix+archived_module.make_note(receipt)
        assert rebuilt==candidate
        with (reconstructed/name).open('xb') as stream:stream.write(rebuilt)
        candidates.append({'name':name,'before':original,'after':candidate,
                           'before_sha256':sha(original),'after_sha256':sha(candidate)})
    preimages=P/f'root-preimages-checkpoint-{args.checkpoint:03d}-note'
    preimages.mkdir()
    for item in candidates:
        with (preimages/(item['name']+'.bin')).open('xb') as stream:stream.write(item['before'])
        with (ROOT/item['name']).open('ab') as stream:stream.write(note)
        assert (ROOT/item['name']).read_bytes()==(reconstructed/item['name']).read_bytes()
    result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'checkpoint':args.checkpoint,'source_receipt_sha256':sha(receipt_bytes),
            'archived_script_sha256':sha(archived_script.read_bytes()),'note_sha256':sha(note),
            'note_utf8':note.decode(),'reconstructed_root':str(reconstructed),
            'reports':[{'path':item['name'],'before_sha256':item['before_sha256'],
                        'after_sha256':item['after_sha256'],'append_only':True} for item in candidates],
            'exact_final_reports_reconstructed':4,
            'reconstruction_inputs':'Pre-note root prefixes and script inside archive, plus external checkpoint receipt.json. Sidecar receipt is deliberately outside its own archive, avoiding self-hash recursion.',
            'scope':'Exact four report bytes only; not full application/source/model/runtime reconstruction.',
            'campaign_active':True,'neural_calls':0,'gold':0}
    for path in [P/f'root-report-checkpoint-{args.checkpoint:03d}-postnote-v1.json',folder/'final-report-reconstruction-receipt-v1.json']:
        with path.open('x') as stream:
            json.dump(result,stream,indent=2,ensure_ascii=False)
            stream.write('\n')
        os.chmod(path,0o600)
    print(json.dumps({'checkpoint':args.checkpoint,'exact_final_reports_reconstructed':4,
                      'source_receipt_and_archived_script_verified':True,'campaign_active':True}))


if __name__=='__main__':main()
