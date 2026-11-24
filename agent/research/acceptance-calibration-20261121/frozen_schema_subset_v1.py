"""Validate only the explicitly frozen research schema subset; never semantic support."""
import json
class DuplicateKey(ValueError): pass
def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise DuplicateKey(key)
        result[key]=value
    return result
ALLOWED={'type','properties','required','additionalProperties','items','minItems','maxItems','enum'}
def validate(value,schema,path='$'):
    unknown=set(schema)-ALLOWED
    if unknown: raise ValueError('Unsupported schema keywords: '+repr(sorted(unknown)))
    errors=[]
    kind=schema.get('type')
    expected={'object':dict,'array':list,'string':str}
    if kind not in expected:raise ValueError('Unsupported type '+repr(kind))
    if type(value) is not expected[kind]:return [{'path':path,'error':'type','expected':kind}]
    if 'enum' in schema and value not in schema['enum']:errors.append({'path':path,'error':'enum'})
    if kind=='object':
        props=schema.get('properties',{})
        for name in schema.get('required',[]):
            if name not in value:errors.append({'path':path,'error':'missing-required','key':name})
        if schema.get('additionalProperties') is False:
            for name in set(value)-set(props):errors.append({'path':path,'error':'additional-property','key':name})
        for name,item in value.items():
            if name in props:errors.extend(validate(item,props[name],path+'/'+name))
    if kind=='array':
        if len(value)<schema.get('minItems',0):errors.append({'path':path,'error':'minItems'})
        if 'maxItems' in schema and len(value)>schema['maxItems']:errors.append({'path':path,'error':'maxItems'})
        for index,item in enumerate(value):errors.extend(validate(item,schema['items'],path+'/'+str(index)))
    return errors
