"""Written context-manager exception-map and local target-ancestry facts only."""
import ast
import collections
import copy
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('mapping_shared_source', P/'module_contract_observer_v5.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
OWN_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
SHARED_SHA = hashlib.sha256(Path(shared.__file__).read_bytes()).hexdigest()
sha = lambda data: hashlib.sha256(data).hexdigest()
dump = lambda node: ast.dump(node, include_attributes=False)


def parse_statement(text):
    return ast.parse(text).body[0]


def namespace(tree):
    counts = collections.Counter()
    imports = {}
    for statement in tree.body:
        bound, dynamic = shared.module_bindings(ast.Module(body=[statement], type_ignores=[]))
        if dynamic or '*' in bound:
            raise ValueError('dynamic/wildcard module binding outside map profile')
        counts.update(bound)
        if isinstance(statement, ast.Import):
            for alias in statement.names:
                local = alias.asname or alias.name.split('.')[0]
                if local in imports:
                    raise ValueError('duplicate import identity')
                imports[local] = {'kind':'import','module':alias.name}
        elif isinstance(statement, ast.ImportFrom):
            for alias in statement.names:
                local = alias.asname or alias.name
                if local in imports:
                    raise ValueError('duplicate import identity')
                imports[local] = {'kind':'from','module':statement.module,'level':statement.level,'symbol':alias.name}
    return counts, imports


def source_unit(card, node, kind):
    first = min([node.lineno] + [decorator.lineno for decorator in getattr(node,'decorator_list',[])])
    lines = card['source'].encode().splitlines(keepends=True)
    quote = b''.join(lines[first-1:node.end_lineno])
    if not quote or len(quote) > 6144:
        raise ValueError('complete selected unit exceeds6144byte quote bound')
    return {'path':card['path'],'revision':card['revision'],'source_sha256':card['sha256'],'first_line':first,'last_line':node.end_lineno,'quote':quote.decode(),'quote_sha256':sha(quote),'kind':kind,'source_executed':False}


def declared_path(name, classes):
    result, seen = [], set()
    while name in classes:
        if name in seen:
            raise ValueError('cyclic declared exception ancestry')
        seen.add(name)
        result.append(name)
        node = classes[name]
        if node.decorator_list or node.keywords or len(node.bases) != 1 or not isinstance(node.bases[0],ast.Name):
            raise ValueError('target hierarchy outside simple undecorated single-base declarations')
        name = node.bases[0].id
    if name not in {'Exception','RuntimeError','BaseException'}:
        raise ValueError('target ancestry terminates at an unresolved imported/dynamic base')
    result.append(name)
    return result


def imported_module_path(owner, ref):
    if ref['kind'] != 'from' or not ref['module']:
        raise ValueError('target must have a static from-import source')
    if ref['level']:
        parts = list(PurePosixPath(owner).parent.parts)
        drop = ref['level'] - 1
        if drop >= len(parts):
            raise ValueError('relative import escapes supplied package registry')
        parts = parts[:len(parts)-drop] if drop else parts
        return str(PurePosixPath(*parts,*ref['module'].split('.')).with_suffix('.py'))
    return str(PurePosixPath(*ref['module'].split('.')).with_suffix('.py'))


def observe(registry, transport_path='httpx/_transports/default.py', exception_path='httpx/_exceptions.py', context_selector='map_httpcore_exceptions', map_name='HTTPCORE_EXC_MAP', external_module='httpcore'):
    result = {'version':'0.0.2-research','status':'INCONCLUSIVE','source_executed':False,'runtime_bindings_verified':False,'physical_source_paths_authenticated':False,'owner_approved':False,'training_gold':False,'publication_authorized':False,'model_calls':0,'writes':0,'producer_sha256':OWN_SHA}
    try:
        if sha(Path(__file__).read_bytes()) != OWN_SHA or sha(Path(shared.__file__).read_bytes()) != SHARED_SHA:
            raise ValueError('loaded mapping/shared producer changed; reload required')
        registry = copy.deepcopy(registry)
        if type(registry) is not dict or set(registry) != {transport_path,exception_path}:
            raise ValueError('exact paired transport/exception source registry required')
        trees, cards, namespaces = {}, {}, {}
        for name, card in registry.items():
            if type(card) is not dict or set(card) != {'source','sha256','revision'} or any(type(v) is not str for v in card.values()):
                raise ValueError('closed string source cards required')
            shared.retrieval.relative_path(name)
            raw = card['source'].encode()
            if not name.endswith('.py') or len(raw)>65536 or b'\0' in raw or sha(raw)!=card['sha256'] or not 1<=len(card['revision'].encode())<=256:
                raise ValueError('source identity/byte bounds')
            tree = ast.parse(card['source'],type_comments=True)
            if sum(1 for _ in ast.walk(tree))>16384:
                raise ValueError('source AST bound')
            compile(tree,name,'exec',dont_inherit=True)
            trees[name] = tree
            cards[name] = {**card,'path':name}
            namespaces[name] = namespace(tree)
            counts,_ = namespaces[name]
            if any(counts[name] for name in {'Exception','RuntimeError','BaseException','isinstance','issubclass','str','len','__builtins__'}):
                raise ValueError('selected builtins have written module bindings')
        transport = trees[transport_path]
        counts, imports = namespaces[transport_path]
        functions = [node for node in transport.body if isinstance(node,ast.FunctionDef) and node.name==context_selector]
        if len(functions)!=1 or counts[context_selector]!=1:
            raise ValueError('unique unconditional context function not established')
        function = functions[0]
        if function.args.posonlyargs or function.args.args or function.args.kwonlyargs or function.args.vararg or function.args.kwarg:
            raise ValueError('zero-argument map context profile required')
        decorators = function.decorator_list
        if len(decorators)!=1 or not isinstance(decorators[0],ast.Attribute) or decorators[0].attr!='contextmanager' or not isinstance(decorators[0].value,ast.Name):
            raise ValueError('explicit contextlib contextmanager source decorator required')
        contextlib_name = decorators[0].value.id
        if imports.get(contextlib_name)!={'kind':'import','module':'contextlib'} or counts[contextlib_name]!=1:
            raise ValueError('contextlib source import is unresolved/rebound')
        body = shared.without_docstring(function.body)
        initialization, loader, core_alias = None, None, None
        map_bindings = [node for node in transport.body if isinstance(node,(ast.Assign,ast.AnnAssign)) and ((isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id==map_name) or (isinstance(node,ast.AnnAssign) and isinstance(node.target,ast.Name) and node.target.id==map_name))]
        if len(map_bindings)!=1 or counts[map_name]!=1 or not isinstance(map_bindings[0].value,ast.Dict):
            raise ValueError('unique literal module map initializer required')
        literal = map_bindings[0].value
        units = {'context':source_unit(cards[transport_path],function,'complete-decorated-context-function')}
        if literal.keys:
            if len(body)!=1:
                raise ValueError('eager map context has additional unsupported prefix statements')
            initialization = 'eager_module_literal'
            units['mapping_provider'] = source_unit(cards[transport_path],map_bindings[0],'complete-module-map-statement')
        else:
            if len(body)!=3 or not isinstance(body[0],ast.Global) or body[0].names!=[map_name] or not isinstance(body[1],ast.If):
                raise ValueError('empty map needs the reviewed global/lazy initializer shape')
            initial_if = body[1]
            if initial_if.orelse or len(initial_if.body)!=1 or not isinstance(initial_if.body[0],ast.Assign):
                raise ValueError('lazy initialization assignment shape differs')
            assigned = initial_if.body[0]
            if len(assigned.targets)!=1 or not isinstance(assigned.targets[0],ast.Name) or assigned.targets[0].id!=map_name or not isinstance(assigned.value,ast.Call) or not isinstance(assigned.value.func,ast.Name) or assigned.value.args or assigned.value.keywords:
                raise ValueError('lazy map assignment is not a direct zero-argument loader')
            loader = assigned.value.func.id
            expected = parse_statement(f'if len({map_name}) == 0:\n    {map_name} = {loader}()\n')
            if dump(initial_if)!=dump(expected) or counts[loader]!=1:
                raise ValueError('lazy map predicate/loader identity differs')
            loaders = [n for n in transport.body if isinstance(n,ast.FunctionDef) and n.name==loader]
            if len(loaders)!=1 or loaders[0].decorator_list or loaders[0].args.args or loaders[0].args.posonlyargs or loaders[0].args.kwonlyargs or loaders[0].args.vararg or loaders[0].args.kwarg:
                raise ValueError('unique zero-argument undecorated loader required')
            loader_body = shared.without_docstring(loaders[0].body)
            if len(loader_body)!=2 or not isinstance(loader_body[0],ast.Import) or len(loader_body[0].names)!=1 or loader_body[0].names[0].name!=external_module or not isinstance(loader_body[1],ast.Return) or not isinstance(loader_body[1].value,ast.Dict):
                raise ValueError('loader must import the declared external module and return a literal dictionary')
            core_alias = loader_body[0].names[0].asname or external_module
            literal = loader_body[1].value
            initialization = 'empty_module_map_then_loader_before_try_yield'
            units['mapping_provider'] = source_unit(cards[transport_path],loaders[0],'complete-loader-function')
        protected = body[-1]
        if not isinstance(protected,ast.Try) or protected.orelse or protected.finalbody or len(protected.handlers)!=1 or len(protected.body)!=1 or not isinstance(protected.body[0],ast.Expr) or not isinstance(protected.body[0].value,ast.Yield) or protected.body[0].value.value is not None:
            raise ValueError('one direct try/yield/handler required')
        handler = protected.handlers[0]
        if not isinstance(handler.type,ast.Name) or handler.type.id!='Exception' or not handler.name or len(handler.body)!=5:
            raise ValueError('direct Exception handler shape differs')
        first,loop,unmapped,message,translated = handler.body
        if not isinstance(first,ast.Assign) or len(first.targets)!=1 or not isinstance(first.targets[0],ast.Name) or not isinstance(first.value,ast.Constant) or first.value.value is not None:
            raise ValueError('mapped exception accumulator must start at None')
        mapped, caught = first.targets[0].id, handler.name
        if not isinstance(loop,ast.For) or loop.orelse or not isinstance(loop.target,ast.Tuple) or len(loop.target.elts)!=2 or not all(isinstance(n,ast.Name) for n in loop.target.elts) or len(loop.body)!=2:
            raise ValueError('direct map pair loop differs')
        from_name,to_name = [n.id for n in loop.target.elts]
        if dump(loop.iter)!=dump(ast.parse(map_name+'.items()',mode='eval').body):
            raise ValueError('loop does not iterate the selected map')
        skip = parse_statement(f'if not isinstance({caught}, {from_name}):\n    continue\n')
        choose = parse_statement(f'if {mapped} is None or issubclass({to_name}, {mapped}):\n    {mapped} = {to_name}\n')
        if dump(loop.body[0])!=dump(skip) or dump(loop.body[1])!=dump(choose):
            raise ValueError('match/specificity predicates differ from reviewed direct profile')
        if dump(unmapped)!=dump(parse_statement(f'if {mapped} is None:\n    raise\n')):
            raise ValueError('unmapped path is not the direct bare raise')
        if not isinstance(message,ast.Assign) or len(message.targets)!=1 or not isinstance(message.targets[0],ast.Name):
            raise ValueError('message binding differs')
        message_name = message.targets[0].id
        used_globals = {'Exception','isinstance','issubclass','str',map_name}
        if loader is not None:
            used_globals.update({'len',loader})
        if {mapped,caught,from_name,to_name,message_name}.intersection(used_globals):
            raise ValueError('local handler/loop/message binder shadows a required builtin, map or loader')
        if len({mapped,caught,from_name,to_name,message_name})!=5 or dump(message)!=dump(parse_statement(f'{message_name} = str({caught})\n')):
            raise ValueError('message/loop/catch bindings ambiguous')
        if dump(translated)!=dump(parse_statement(f'raise {mapped}({message_name}) from {caught}\n')):
            raise ValueError('translated exception/cause ownership differs')
        exception_counts,_ = namespaces[exception_path]
        class_nodes = [n for n in trees[exception_path].body if isinstance(n,ast.ClassDef)]
        classes = {node.name:node for node in class_nodes}
        if len(classes)!=len(class_nodes) or any(exception_counts[name]!=1 for name in classes):
            raise ValueError('exception class source identity ambiguous')
        for name in classes:
            declared_path(name,classes)
        pairs, seen = [], set()
        if not 1<=len(literal.keys)<=32:
            raise ValueError('bounded nonempty literal map required')
        for key,value in zip(literal.keys,literal.values,strict=True):
            if not isinstance(key,ast.Attribute) or not isinstance(key.value,ast.Name) or not isinstance(value,ast.Name):
                raise ValueError('literal mapping must have external class attributes -> imported local class names')
            if core_alias is None:
                core_alias = key.value.id
                if imports.get(core_alias)!={'kind':'import','module':external_module} or counts[core_alias]!=1:
                    raise ValueError('external source namespace not established')
            if key.value.id!=core_alias or ast.unparse(key) in seen:
                raise ValueError('mixed source namespace or duplicate map key')
            seen.add(ast.unparse(key))
            if loader is not None and value.id == core_alias:
                raise ValueError('loader-local import alias shadows the mapped target class name')
            ref = imports.get(value.id)
            if not ref or counts[value.id]!=1 or imported_module_path(transport_path,ref)!=exception_path or ref['symbol'] not in classes:
                raise ValueError('mapped target is not a uniquely imported class from the supplied exception module')
            path = declared_path(ref['symbol'],classes)
            pairs.append({'source_expression':ast.unparse(key),'target_local_name':value.id,'target_declared_class':ref['symbol'],'target_declared_ancestry':path,'runtime_class_identity_verified':False})
            for name in path:
                if name in classes:
                    units.setdefault('exception:'+name,source_unit(cards[exception_path],classes[name],'complete-declared-exception-class'))
        result.update(status='WRITTEN_MAPPING_FACTS',initialization=initialization,loader_function=loader,context_selector=context_selector,map_name=map_name,mapping_pairs=pairs,mapping_pair_count=len(pairs),handler={'caught_type_expression':'Exception','binding':caught,'specificity_condition':ast.unparse(loop.body[1].test),'unmapped':'bare raise','translated_raise':ast.unparse(translated),'initializer_before_protected_yield':initialization!='eager_module_literal'},
                      all_mapped_targets_have_declared_requesterror_ancestor=all('RequestError' in pair['target_declared_ancestry'] for pair in pairs),evidence=units,
                      source_identities={name:{k:v for k,v in card.items() if k!='source'} for name,card in cards.items()},
                      limitations=['Only reviewed direct written context/map/declared single-base target ancestry profile.','Imports/decorators/classes/contexts are not executed; actual external exception classes, runtime receivers and all error paths remain unverified.','No physical current-file or upstream Git authenticity, general semantic equivalence, publication or owner approval.'])
    except (ValueError,TypeError,KeyError,SyntaxError,UnicodeError,RecursionError) as error:
        result['reason'] = str(error)
    if len(json.dumps(result,ensure_ascii=False).encode())>131072:
        return {'status':'INCONCLUSIVE','reason':'mapping response bound','source_executed':False,'model_calls':0,'writes':0}
    return result
