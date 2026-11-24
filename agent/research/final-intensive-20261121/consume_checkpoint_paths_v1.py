import argparse,json,hashlib
from pathlib import Path
from checkpoint_paths_v1 import resolve_relative_regular
ap=argparse.ArgumentParser();ap.add_argument('--root',required=True,type=Path);a=ap.parse_args();root=a.root.resolve();p=root/'agent/research/final-intensive-20261121';name='agent/research/documentation-intelligence-20261119/chapters/go-image-dimensions/../go-image-animation/en.md';canonical='agent/research/documentation-intelligence-20261119/chapters/go-image-animation/en.md';f=resolve_relative_regular(root,name);assert f==root/canonical;assert '..' not in f.relative_to(root).parts
cases=[('absolute',str(root/canonical)),('escape','..'),('missing','agent/research/final-intensive-20261121/owned-known-absent-dependency-v1.no-file')];records=[]
for ident,path in cases:
 try:resolve_relative_regular(root,path)
 except (ValueError,FileNotFoundError):records.append({'id':ident,'verdict':'REFUSED'})
 else:raise AssertionError('unsafe/missing dependency admitted: '+ident)
print(json.dumps({'status':'PASS_FINITE_CHECKPOINT_PATH_RESOLUTION_RECOVERY','actual_internal_parent_alias':1,'refusal_controls':records,'canonical_source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'scope':'Finite path confinement/normalization procedure only, not hostile filesystem race, symlink-parent exploit, crash durability, archive semantic acceptance or general security certification.'}))
