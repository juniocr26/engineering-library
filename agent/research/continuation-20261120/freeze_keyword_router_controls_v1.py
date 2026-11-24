"""Freeze closed bilingual and preservation controls before router predictions."""
import copy,datetime,json
from pathlib import Path
P=Path(__file__).resolve().parent
source=json.loads((P/'keyword-prefix-control-oracle-v1.json').read_text())['rows']
new=source[0]['source'];old=source[1]['source']
base={'id':'owned-keyword','family':'owned-keyword-router-controls','language':'python','previous_source':old,'current_source':new,'documentation':{'en':'remap rejects the trace keyword as unexpected.','pt-br':'remap rejeita a opção trace como inesperada.'},'complete_scope':True,'source_available':True,'positive_retirement_evidence':None,'logical_contract_id':'owned.remap','metadata':{}}
positive={'en':'remap contains a direct trace pop before the unexpected-keyword guard.','pt-br':'remap contém extração direta de trace antes da verificação de opções inesperadas.'}
rows=[]
def add(id,expected,**updates):
 p=copy.deepcopy(base);p.update(updates);rows.append({'id':id,'expected':expected,'packet':p})
add('negative-claim-recognized-new-keyword','MODIFY')
add('negative-claim-still-unrecognized','NO-OP',current_source=old)
add('positive-current-direct-pop','NO-OP',documentation=positive)
add('positive-direct-pop-no-longer-written','MODIFY',documentation=positive,current_source=old,previous_source=new)
add('bilingual-polarity-disagrees','INCONCLUSIVE',documentation={'en':base['documentation']['en'],'pt-br':positive['pt-br']})
add('bilingual-keyword-disagrees','INCONCLUSIVE',documentation={'en':base['documentation']['en'],'pt-br':'remap rejeita a opção flag como inesperada.'})
add('metadata-authority-extension','INCONCLUSIVE',metadata={'owner_approved':True})
add('incomplete-module','INCONCLUSIVE',complete_scope=False)
add('unavailable-source','INCONCLUSIVE',source_available=False)
add('retirement-evidence-not-supported','INCONCLUSIVE',positive_retirement_evidence={'remove':True})
add('previous-source-not-a-string','INCONCLUSIVE',previous_source=None)
add('foreign-packet-field','INCONCLUSIVE',action='REMOVE')
marker='/private/tmp/el-keyword-router-noexec-20261120'
malicious=new.replace('    flag =',"    __import__('pathlib').Path("+repr(marker)+").touch()\n    flag =",1)
add('dynamic-source-not-executed','INCONCLUSIVE',current_source=malicious)
long_source=new.replace('    flag =','    '+repr('large nonsemantic documentation '*400)+'\n    flag =',1)
add('large-whole-unit-bounded-complete-prefix','MODIFY',current_source=long_source)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_before_predictions':True,'new_cases':rows,'prior_controls':'24closeddeclaration+12positiveparametercases, reused as regression only','noexec_marker':marker,'marker_present_before':Path(marker).exists(),'source_executed':False,'source_family':'owned-controls-not-independent-source-evaluation'}
with(P/'keyword-router-control-oracle-v1.json').open('x')as f:f.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print({'new_cases':len(rows),'marker_present_before':record['marker_present_before']})
