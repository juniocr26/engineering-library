"""Physical citation integrity for unchanged owner files, separate from semantic review."""
import datetime,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
package=json.loads((P/'owner-review-package-v2.json').read_text())
mapping={}
for task in json.loads((P/'bounded-task-freeze-v2.json').read_text())['tasks']:
    for f in task['source_inventory']:mapping[(task['task'],f['path'])]={'snapshot':f['snapshot'],'sha256':f['sha256']}
for f in json.loads((P/'chapter-context-source-freeze-v1.json').read_text())['files']:mapping[(f['repository'],f['source_path'])]={'snapshot':f['snapshot'],'sha256':f['sha256']}
R=r'\d+(?:[-–]\d+)?(?:,\s*\d+(?:[-–]\d+)?)*'
pattern=re.compile(r'(?P<path>[A-Za-z0-9_./-]+\.(?:py|go|ts)):(?P<ranges>'+R+r')|`:(?P<short>'+R+r')`')
records=[];errors=[]
for chapter in package['chapters']:
    task=chapter['task']
    for meta in chapter['documents']:
        path=Path(meta['path']);raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==meta['sha256'];locators=[]
        for line,text in enumerate(raw.decode().splitlines(),1):
            last=None
            for match in pattern.finditer(text):
                if match.group('path'):last=match.group('path');ranges=match.group('ranges')
                else:ranges=match.group('short')
                if last is None:errors.append({'document':str(path),'line':line,'error':'Unresolved citation shorthand'});continue
                key=(task,last)
                if key not in mapping:errors.append({'document':str(path),'line':line,'error':'Unmapped frozen source','source_path':last});continue
                source=mapping[key];body=Path(source['snapshot']).read_bytes();assert hashlib.sha256(body).hexdigest()==source['sha256'];ls=body.decode().splitlines()
                for part in ranges.split(','):
                    ends=re.split('[-–]',part.strip());start=int(ends[0]);end=int(ends[-1]);valid=1<=start<=end<=len(ls)
                    row={'document_line':line,'locator_text':match.group(0),'source_path':last,'source_sha256':source['sha256'],'source_snapshot':source['snapshot'],'source_lines':[start,end],'physical_range_valid':valid,'exact_source_quote':'\n'.join(ls[start-1:end]) if valid else None,'not_semantic_support_by_itself':True};locators.append(row)
                    if not valid:errors.append({'document':str(path),'line':line,'error':'Invalid physical range','source_path':last,'range':[start,end]})
        records.append({'task':task,'language':meta['language'],'document':str(path),'document_sha256':meta['sha256'],'locators':locators,'locator_range_occurrences':len(locators)})
result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'documents':records,'document_count':len(records),'physical_range_occurrences':sum(r['locator_range_occurrences'] for r in records),'errors':errors,'source_and_document_bytes_unchanged':True,'semantic_relevance':'Separately source-reviewed in the owner claim/paragraph ledgers; this script checks only file identity and physical citation ranges.','not_training_or_owner_approval':True,'model_calls':0,'gold':0,'optimizer_updates':0}
with (P/'owner-citation-physical-integrity-v3.json').open('x') as f:json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps({k:v for k,v in result.items() if k!='documents'},indent=2));assert not errors
