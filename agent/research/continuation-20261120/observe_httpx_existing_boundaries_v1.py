"""Record actual existing tool scope before adding a new research source profile."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

P=Path(__file__).resolve().parent

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

module=load(P/'module_contract_observer_v5.py','httpx_existing_module')
owned=load(P.parent/'documentation-intelligence-20261120/assemble_architecture_facts_v2.py','httpx_owned_architecture')
freeze=json.loads((P/'httpx-source-family-freeze-v1.json').read_text());rows=[]
for cut in freeze['revisions']:
    base=P/'new-public-sources-v1/encode--httpx'/cut['revision'];paths=['httpx/_transports/default.py','httpx/_exceptions.py'];sources={name:(base/name).read_bytes()for name in paths}
    card={'path':paths[0],'revision':cut['revision'],'source':sources[paths[0]].decode(),'sha256':hashlib.sha256(sources[paths[0]]).hexdigest()}
    observed=module.observe(card,'map_httpcore_exceptions')
    try:
        owned.extract(sources);architecture={'status':'ADMITTED'}
    except ValueError as error:
        architecture={'status':'REFUSED','reason':str(error)}
    rows.append({'tag':cut['tag'],'revision':cut['revision'],'existing_module_observation':observed,'existing_owned_architecture_observation':architecture})
assert all(r['existing_module_observation']['status']=='INCONCLUSIVE'and'decorated'in r['existing_module_observation']['reason']for r in rows)
assert all(r['existing_owned_architecture_observation']['status']=='REFUSED'for r in rows)
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,'source_executed':False,'model_calls':0,'interpretation':'These are documented admission limits, not incorrect action predictions or a general architecture regression. A new explicitly decorated-context/mapping source profile must preserve this distinction.','production_changed':False}
with(P/'httpx-existing-profile-boundaries-v1.json').open('x')as stream:
    stream.write(json.dumps(record,indent=2)+'\n')
print({'existing_module_profile':'2decoratedcontractsrefused','owned_architecture_profile':'2registriesrefused','source_execution':False})
