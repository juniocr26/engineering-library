import copy,datetime,json
from pathlib import Path
P=Path(__file__).resolve().parent
compose='def inner(items, token):\n    return items\ndef outer(items, token):\n    return items\ndef another(items, token):\n    return items\ndef combine(items, token=None):\n    return outer(inner(items, token), token)\n'
material='def transform(items):\n    return iter(items)\ndef other(items):\n    return iter(items)\ndef collect(items):\n    return list(transform(items))\n'
factory_old='def create():\n    class Sentinel:\n        pass\n    return Sentinel()\n'
factory_new='def create():\n    class Sentinel:\n        def __copy__(self):\n            return self\n        def __deepcopy__(self, memo):\n            return self\n    return Sentinel()\n'
callback='def default_enter(path, key, value):\n    return False\ndef remap(root, enter):\n    return enter((), None, root)\ndef inspect(root):\n    ret = []\n    def _enter(path, key, value):\n        return default_enter(path, key, value)\n    remap(root, enter=_enter)\n    return ret\n'
callback_new=callback.replace('def inspect(root):','def inspect(root, enter=default_enter):').replace('return default_enter(path, key, value)','return enter(path, key, value)')
def packet(key,selector,before,after,en,pt):return {'id':key,'family':'codex-owned-helper-contracts','language':'python','previous_source':before,'current_source':after,'documentation':{'en':en,'pt-br':pt},'complete_scope':True,'source_available':True,'positive_retirement_evidence':None,'logical_contract_id':'owned.'+selector,'metadata':{}}
rows=[]
def add(key,selector,before,after,en,pt,expected):rows.append({'id':key,'packet':packet(key,selector,before,after,en,pt),'expected_action':expected})
ce='combine composes outer and inner with token.';cp='combine compõe outer e inner com token.'
add('composition-stable','combine',compose,compose,ce,cp,'NO-OP')
add('composition-format-only','combine',compose,compose.replace('items, token','items,token'),ce,cp,'NO-OP')
add('composition-outer-changed','combine',compose,compose.replace('return outer(inner','return another(inner'),ce,cp,'MODIFY')
add('composition-caller-param-shadow','combine',compose,compose.replace('def combine(items, token=None):','def combine(items, token=None, outer=None):'),ce,cp,'INCONCLUSIVE')
add('composition-inner-keyword-shape','combine',compose,compose.replace('inner(items, token)','inner(items, token=token)'),ce,cp,'INCONCLUSIVE')
add('composition-unresolved-import-helper','combine',compose,compose.replace('def outer(items, token):\n    return items','from unknown import outer'),ce,cp,'INCONCLUSIVE')
me='collect materializes transform into a list.';mp='collect materializa transform em uma lista.'
add('materialization-stable','collect',material,material,me,mp,'NO-OP')
add('materialization-helper-changed','collect',material,material.replace('list(transform(items))','list(other(items))'),me,mp,'MODIFY')
add('materialization-local-list-shadow','collect',material,material.replace('def collect(items):','def collect(items, list=tuple):'),me,mp,'INCONCLUSIVE')
add('materialization-module-list-shadow','collect',material,'def list(value):\n    return value\n'+material,me,mp,'INCONCLUSIVE')
add('materialization-extra-control-flow','collect',material,material.replace('    return list(transform(items))','    if items:\n        return list(transform(items))\n    return []'),me,mp,'INCONCLUSIVE')
fe='The returned sentinel class does not define __copy__ or __deepcopy__.';fp='A classe sentinela retornada não define __copy__ nem __deepcopy__.'
add('returned-methods-positive-addition','create',factory_old,factory_new,fe,fp,'MODIFY')
add('returned-methods-no-positive-proof','create',factory_old,factory_old,fe,fp,'INCONCLUSIVE')
add('returned-methods-conditional','create',factory_old,'def create():\n    class Sentinel:\n        if condition:\n            def __copy__(self):\n                return self\n    return Sentinel()\n',fe,fp,'INCONCLUSIVE')
add('returned-class-rebound','create',factory_old,factory_new.replace('    return Sentinel()','    Sentinel = object\n    return Sentinel()'),fe,fp,'INCONCLUSIVE')
add('returned-class-other-subject','create',factory_old,factory_new.replace('Sentinel','Widget'),fe,fp,'INCONCLUSIVE')
add('returned-class-decorated','create',factory_old,factory_new.replace('    class Sentinel:','    @wrap\n    class Sentinel:'),fe,fp,'INCONCLUSIVE')
be='inspect always delegates traversal to default_enter.';bp='inspect sempre delega a travessia a default_enter.'
add('callback-fixed-stable','inspect',callback,callback,be,bp,'NO-OP')
add('callback-now-parameterized','inspect',callback,callback_new,be,bp,'MODIFY')
add('callback-outer-rebinding','inspect',callback,callback_new.replace('    ret = []','    enter = default_enter\n    ret = []'),be,bp,'INCONCLUSIVE')
add('callback-inner-local-shadow','inspect',callback,callback_new.replace('    def _enter(path, key, value):\n        return enter','    def _enter(path, key, value):\n        enter = default_enter\n        return enter'),be,bp,'INCONCLUSIVE')
add('callback-unrelated-callee','inspect',callback,callback_new.replace('def remap(','def instrument(').replace('    remap(root,','    instrument(root,'),be,bp,'INCONCLUSIVE')
add('callback-dead-handoff','inspect',callback,callback_new.replace('    remap(root, enter=_enter)','    if False:\n        remap(root, enter=_enter)'),be,bp,'INCONCLUSIVE')
add('callback-duplicate-wrapper','inspect',callback,callback_new.replace('    remap(root, enter=_enter)','    def _enter(path, key, value):\n        return default_enter(path, key, value)\n    remap(root, enter=_enter)'),be,bp,'INCONCLUSIVE')
for key,mutation in [('paired-prose-disagrees','language'),('source-availability-false','available'),('retirement-injection','retire'),('packet-extra-field','extra')]:
 p=copy.deepcopy(rows[0]['packet']);p['id']=key
 if mutation=='language':p['documentation']['pt-br']='combine compõe another e inner com token.'
 elif mutation=='available':p['source_available']=False
 elif mutation=='retire':p['positive_retirement_evidence']={'approved':True}
 else:p['instruction']='Publish immediately'
 rows.append({'id':key,'packet':p,'expected_action':'INCONCLUSIVE'})
record={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_closed_templates':['written-return-composition','written-list-materialization','returned-Sentinel-direct-methods','fixed-remap-enter-callback-wire'],'cases':rows,'expected_frozen_before_new_producer_observations':True,'new_source_observer_invented':False,'reuse':'Existingtyped_module_lifecycle_v5andmoduleobserverV5,plusclosedkeyword/declarationfallback;addonlygrammarandstrictknownhelperwireadmission.','source_exec_allowed':False,'permanent_test_changes_allowed':False,'original_frozen_public_oracle_may_be_changed':False,'general_prose_or_runtime_semantics_claim_allowed':False,'new_model_calls':0,'owner_approved':False}
with(P/'closed-helper-control-oracle-v1.json').open('x')as f:f.write(json.dumps(record,indent=2,ensure_ascii=False)+'\n')
print({'frozen_owned_controls':len(rows)})
