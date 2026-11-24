"""Frozen-artifact comparison with explicit, source-reviewed judgments.

Scores are operational heuristics, not scientifically validated estimates.
Judgments must be made against source/runtime evidence independently of agreement.
Missing judgments produce incomplete results rather than perfect scores.
"""
import argparse
import collections
import difflib
import hashlib
import json
from pathlib import Path
import re
import unicodedata

PROTOCOL = {
    'schema': 1, 'target': 95.0,
    'evidence': 'supported judgments require frozen source-file hashes and exact bounded line-span hashes; these mechanical checks do not establish semantic truth',
    'weights': {'semantic': .40, 'coverage': .25, 'bilingual': .15, 'structure': .10, 'textual': .10},
    'semantic': '100 * equivalent candidate claims / source-verified reference claims; unsupported shared claims excluded; candidate additions independently gated',
    'coverage': '100 * supported covered required topic IDs / frozen required topic IDs',
    'bilingual': '100 * reviewed equivalent EN/PT candidate claims / all candidate claims; unreviewed judgments make score incomplete',
    'structure': '100 * correctly mapped required section IDs / frozen required section IDs',
    'textual': 'mean EN/PT SequenceMatcher token ratio, autojunk=False, NFC/casefold normalization; fenced/indented code and generated/citation metadata excluded',
    'accuracy': 'source-supported candidate claims / all candidate claims; pending judgments make result incomplete',
    'acceptance': '>=95 plus all required topics/sections, complete independent review, no unsupported/contradictory claims, no critical failures, no bilingual mismatches, no gaming flags',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def normalize(text):
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'(?ms)^\s*```.*?^\s*```[^\n]*$', '', text)
    text = re.sub(r'(?ms)^\s*~~~.*?^\s*~~~[^\n]*$', '', text)
    text = re.sub(r'(?m)^(?: {4}|\t).*?(?:\n|$)', '', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = re.sub(r'(?m)^(Project|Projeto|Generation|Geração|Coverage|Cobertura|Source|Fonte|Source revision):.*$', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text)
    return re.findall(r'\w+(?:(?:::|\.)\w+)*|[<>!=]=?|\d+', text.casefold())


def ratio(numerator, denominator):
    return None if not denominator else 100.0 * numerator / denominator


def require_ids(values, label):
    if not isinstance(values, list) or any(not isinstance(i, str) or not i for i in values) or len(set(values)) != len(values):
        raise ValueError('Invalid or duplicate IDs: '+label)
    return set(values)


def score(packet):
    if packet.get('protocol_sha256') != sha(json.dumps(PROTOCOL, sort_keys=True).encode()):
        raise ValueError('Protocol differs from frozen methodology')
    if packet.get('scope') not in ['component', 'section', 'chapter', 'project']:
        raise ValueError('Explicit evaluation scope required')
    artifacts = packet['artifacts']; texts={}; hashes={}
    for side in ['reference', 'candidate']:
        texts[side]={};hashes[side]={}
        for lang in ['en','pt-br']:
            spec=artifacts[side][lang];data=Path(spec['path']).read_bytes()
            if len(data)>2_000_000 or sha(data)!=spec['sha256']:raise ValueError('Artifact missing, too large or changed after freeze')
            texts[side][lang]=data.decode('utf-8');hashes[side][lang]=sha(data)
    evidence={}
    for item in packet.get('evidence',[]):
        identifier=item['id']
        if identifier in evidence:raise ValueError('Duplicate evidence ID')
        data=Path(item['path']).read_bytes()
        if sha(data)!=item['source_sha256']:raise ValueError('Frozen source changed')
        lines=data.splitlines(keepends=True);start=item['line_start'];end=item['line_end']
        if type(start) is not int or type(end) is not int or not 1<=start<=end<=len(lines):raise ValueError('Invalid source citation range')
        if sha(b''.join(lines[start-1:end]))!=item['quote_sha256']:raise ValueError('Source citation span changed')
        evidence[identifier]=item
    claims=packet.get('claims',[])
    require_ids([c['id'] for c in claims],'claims')
    allowed={'supported','unsupported','contradictory','absent','pending'}
    if any(c.get('reference') not in allowed or c.get('candidate') not in allowed or c.get('equivalent') not in [True,False,None] or c.get('bilingual') not in [True,False,None] for c in claims):raise ValueError('Invalid claim judgment')
    if any(c.get('reference')=='supported' or c.get('candidate')=='supported' for c in claims):
        if any(not c.get('evidence') or any(identifier not in evidence for identifier in c['evidence']) for c in claims if c.get('reference')=='supported' or c.get('candidate')=='supported'):raise ValueError('Supported judgments require checked source/runtime evidence')
    reference=[c for c in claims if c['reference']=='supported']
    candidate=[c for c in claims if c['candidate']!='absent']
    pending=not claims or any(c['reference']=='pending' or c['candidate']=='pending' or (c['reference']=='supported' and c['candidate']=='supported' and c['equivalent'] is None) for c in claims)
    semantic=None if pending else ratio(sum(c['candidate']=='supported' and c['equivalent'] is True for c in reference),len(reference))
    topics=require_ids(packet.get('required_topics',[]),'required topics');covered=require_ids(packet.get('covered_topics',[]),'covered topics')
    sections=require_ids(packet.get('required_sections',[]),'required sections');mapped=require_ids(packet.get('mapped_sections',[]),'mapped sections')
    if covered-topics or mapped-sections:raise ValueError('Coverage IDs must belong to frozen denominators')
    # Review completeness is an explicit assertion, not inferred from matched text.
    reviewed=packet.get('inventory_complete') is True
    if not reviewed:semantic=None
    bilingual=None if not reviewed or any(c['bilingual'] is None for c in candidate) else ratio(sum(c['bilingual'] is True for c in candidate),len(candidate))
    tokens={side:{lang:normalize(text) for lang,text in texts[side].items()} for side in texts}
    textual=None if any(not part for side in tokens.values() for part in side.values()) else sum(100*difflib.SequenceMatcher(None,tokens['reference'][lang],tokens['candidate'][lang],autojunk=False).ratio() for lang in ['en','pt-br'])/2
    components={'semantic':semantic,'coverage':ratio(len(covered),len(topics)), 'bilingual':bilingual,'structure':ratio(len(mapped),len(sections)),
                'textual':textual}
    flags=[]
    for side in ['reference','candidate']:
        for lang,text in texts[side].items():
            paras=[tuple(normalize(p)) for p in re.split(r'\n\s*\n',text) if len(normalize(p))>=12]
            if any(n>1 for n in collections.Counter(paras).values()):flags.append(f'{side}:{lang}:duplicate-paragraph')
            if len(normalize(text))<40:flags.append(f'{side}:{lang}:short-document-review-required')
    if packet.get('leakage_check')!='passed':flags.append('independence-unverified')
    critical=packet.get('critical_errors',[])
    unsupported=sum(c['candidate'] in ['unsupported','contradictory'] for c in candidate)
    complete=all(v is not None for v in components.values()) and reviewed and not pending
    composite=sum(PROTOCOL['weights'][k]*v for k,v in components.items()) if complete else None
    accuracy=None if pending or not reviewed else ratio(sum(c['candidate']=='supported' for c in candidate),len(candidate))
    category='incomplete'
    if critical or unsupported:category='rejected'
    elif complete:
        category='accepted' if composite>=95 and components['coverage']==100 and components['structure']==100 and components['bilingual']==100 and accuracy==100 and not flags else 'conditionally accepted'
    return {'protocol':PROTOCOL,'scope':packet['scope'],'source_revision':packet['source_revision'],'reference_revision':packet['reference_revision'],'candidate_revision':packet['candidate_revision'],
            'feedback_assisted':packet.get('feedback_assisted'),'artifact_hashes':hashes,'scores':components,'composite':composite,'gap_to_95':None if composite is None else max(0,95-composite),
            'factual_accuracy':accuracy,'unsupported_claim_rate':None if pending or not reviewed else ratio(unsupported,len(candidate)),
            'critical_errors':critical,'gaming_flags':flags,'acceptance':category,'owner_acceptance':packet.get('owner_acceptance','not supplied'),
            'denominators':{'reference_verified_claims':len(reference),'candidate_claims':len(candidate),'required_topics':len(topics),'required_sections':len(sections),'covered_topics':len(covered),'mapped_sections':len(mapped)}}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('packet',type=Path,nargs='?');parser.add_argument('--protocol',action='store_true');args=parser.parse_args()
    if args.protocol:print(json.dumps({'protocol':PROTOCOL,'sha256':sha(json.dumps(PROTOCOL,sort_keys=True).encode())},indent=2))
    elif args.packet:print(json.dumps(score(json.loads(args.packet.read_text())),indent=2))
    else:parser.error('Provide --protocol or a review packet')
