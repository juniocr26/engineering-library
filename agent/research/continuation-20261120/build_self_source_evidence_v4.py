"""Refresh working-source citations without rewriting any historical source cut."""
import datetime
import hashlib
import json
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parents[2]
old=json.loads((P/'self-chapter-supplement-evidence-v3.json').read_text())
units=[]


def add(identity,path,first,last,kind):
    raw=(ROOT/path).read_bytes();lines=raw.decode().splitlines(keepends=True);quote=''.join(lines[first-1:last])
    assert quote and len(quote.encode())<=6144
    units.append({'id':identity,'source_path':path,'first_line':first,'last_line':last,'kind':kind,'source_sha256':hashlib.sha256(raw).hexdigest(),'quote':quote,'quote_sha256':hashlib.sha256(quote.encode()).hexdigest(),'scope':'Exact physical working-source range; no application/model execution.'})


def ruby_method(identity,name,kind):
    path='backend/lib/documentation/command.rb';lines=(ROOT/path).read_text().splitlines();starts=[i for i,line in enumerate(lines)if line.startswith('    def '+name+'(')or line=='    def '+name]
    assert len(starts)==1,name
    start=starts[0];finish=next(i for i in range(start+1,len(lines))if lines[i]=='    end')
    add(identity,path,start+1,finish+1,kind)


ruby_method('E1','evidence_cards','evidence-mode-routing')
ruby_method('E2','python_fragments','AST-range-metadata-transfer')
ruby_method('E3','quoted_caught_identifier_mismatch?','caught-reference-guard-entry')
ruby_method('E12','quoted_identifier_reference_mismatch?','bounded-common-reference-presence-check')
ruby_method('E13','quoted_return_mapping_identifier_mismatch?','direct-returned-map-guard-entry')
path='backend/lib/documentation/command.rb';lines=(ROOT/path).read_text().splitlines();indices=[i for i,line in enumerate(lines)if "raise Error, 'quoted Python "in line];assert len(indices)==2;add('E4',path,min(indices)+1,max(indices)+1,'two-identifier-guard-invocations')
path='backend/lib/documentation/python_structure.py';add('E5',path,1,len((ROOT/path).read_text().splitlines()),'bounded-written-AST-metadata-and-range-producer')
for identity,path in [('E6','agent/tools/documentation_lifecycle.py'),('E7','agent/tools/documentation_maintenance.py'),('E8','agent/tools/documentation_retrieval.py'),('E9','backend/lib/documentation/command.rb')]:
 lines=(ROOT/path).read_text().splitlines();matches=[i for i,line in enumerate(lines)if line.strip().startswith('VERSION =')];assert len(matches)==1;add(identity,path,matches[0]+1,matches[0]+1,'current-source-version')
ruby_method('E10','infer','direct-model-inference-path')
ruby_method('E11','source_model_request','model-request-construction-path')
import ast
path='agent/tools/documentation_retrieval.py';raw=(ROOT/path).read_text();tree=ast.parse(raw)
for identity,name,kind in [('E14','validate_unit','complete-cached-lexical-unit-validation'),('E15','extract','read-only-language-extractor-dispatch'),('E16','receipt_for','nonkeyed-canonical-result-receipt'),('E18','validate_cached','closed-cached-request-source-producer-correlation')]:
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)
 add(identity,path,node.lineno,node.end_lineno,kind)
lines=raw.splitlines();matches=[i for i,line in enumerate(lines)if 'if not isinstance(cached, dict) or cached.get("version") != VERSION:'in line];assert len(matches)==1
first=matches[0];last=next(i for i in range(first+1,len(lines))if lines[i].strip()=='return response')
add('E17',path,first+1,last+1,'older-result-version-no-automatic-migration-branch')
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_cut':'Caller1.9.43workingbytes,planner0.3.6,maintenance0.1.5,helper0.1.5;not an asserted new Git commit.','units':units,'historical_documents':old['historical_documents'],'historical_records_unchanged':True,'scope':'Current working-source code supplement, no active catalog change, owner approval or semantic certification.','owner_approved':False,'training_gold':False,'training_exclusion':True,'supersedes':'self-chapter-supplement-evidence-v3.json','historical_cut_exact_source_preimages':'returned-map-guard-source-preimages-v1.json','source_executed':False}
with(P/'self-chapter-supplement-evidence-v4.json').open('x')as f:f.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print({'source_units':len(units),'caller':'1.9.43','historical_records_preserved':True})
