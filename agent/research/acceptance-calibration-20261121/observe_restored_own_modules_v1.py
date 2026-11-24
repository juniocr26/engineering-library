"""Import six restored own libraries, without dispatching helpers or suites."""
import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path.cwd()/'agent/tools'))
import documentation_workspace as w
import documentation_job_budget as j
import documentation_lifecycle as l
import documentation_candidates as c
import documentation_retrieval as r
import documentation_maintenance as m
mods=[w,j,l,c,r,m]
assert all(Path(mod.__file__).is_relative_to(Path.cwd())for mod in mods)
print(json.dumps({'module_paths':[mod.__file__ for mod in mods],
                  'versions':{mod.__name__:getattr(mod,'VERSION',None)for mod in mods},
                  'helper_dispatched':False,'test_suites_run':False}))
