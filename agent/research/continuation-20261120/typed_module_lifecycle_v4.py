"""Written-source typed claim recommendations, separate from prose planning."""
import ast
import copy
import json
import keyword
import re
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("typed_module_observer",HERE/"module_contract_observer_v5.py")
observer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(observer)


def expression(text):
    return ast.parse(text,mode="eval").body



def valid_name(value):
    return type(value)is str and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}",value) is not None and not keyword.iskeyword(value)


def validate_claim(claim):
    fields={
        "undocumented-declaration":{"kind"},
        "no-explicit-parameter":{"kind","parameter"},
        "written-tuple-return":{"kind","elements"},
        "written-return-composition":{"kind","outer","inner","shared_argument"},
        "written-list-materialization":{"kind","callee"},
        "no-direct-returned-class-methods":{"kind","methods"},
        "fixed-written-callback":{"kind","callee","keyword"},
        "rejects-keyword":{"kind","keyword"},
    }
    kind=claim.get("kind")
    if type(kind)is not str or kind not in fields or set(claim)!=fields[kind]:
        raise ValueError("unsupported typed predicate or fields")
    for key in set(claim)-{"kind","elements","methods"}:
        if not valid_name(claim[key]):
            raise ValueError("typed claim name is not an admitted identifier: "+key)
    for key in ("elements","methods"):
        if key in claim:
            values=claim[key]
            if type(values)is not list or len(values)>8 or not all(valid_name(v)for v in values):
                raise ValueError("typed claim name list outside profile: "+key)
            if key=="methods"and(not values or len(set(values))!=len(values)):
                raise ValueError("method predicate needs unique nonempty names")


def recommend(previous,current,selector,paired_claim):
    result={"version":"0.0.4-research","action":"INCONCLUSIVE","source_executed":False,
            "runtime_bindings_verified":False,"owner_approved":False,"training_gold":False,
            "publication_authorized":False,"writes":0,"model_calls":0,
            "scope":"EXPLICIT_OPERATOR_MAPPED_WRITTEN_SOURCE_CLAIM_NOT_ARBITRARY_PROSE",
            "automatic_candidate_applier_supported":False}
    def finish(action,reason):
        result.update(action=action,reason=reason)
        return result
    try:
        previous = dict(previous) if type(previous) is dict else previous
        current = dict(current) if type(current) is dict else current
        if len(json.dumps(paired_claim,ensure_ascii=False,allow_nan=False).encode())>16384:
            raise ValueError("typed claim byte bound exceeded")
        paired_claim = copy.deepcopy(paired_claim)
        if type(paired_claim)is not dict or set(paired_claim)!={"en","pt-br"}:
            raise ValueError("paired typed claims required")
        claim=copy.deepcopy(paired_claim["en"])
        if claim!=paired_claim["pt-br"] or type(claim)is not dict:
            raise ValueError("bilingual typed claims disagree")
        validate_claim(claim)
        before,after=observer.observe(previous,selector),observer.observe(current,selector)
        result["evidence"]={"previous":before,"current":after}
        if after["status"]!="WRITTEN_CALLABLE_FACTS":
            raise ValueError("current declaration facts not established: "+after.get("reason","unknown"))
        kind=claim.get("kind")
        if kind=="undocumented-declaration":
            if set(claim)!={"kind"}:
                raise ValueError("unknown undocumented declaration fields")
            if before["status"]=="NO_WRITTEN_MODULE_BINDING":
                return finish("ADD","Positive current written declaration and no prior written binding under the explicit empty-documentation mapping; document only observed facts.")
            raise ValueError("new written declaration need not established")
        if before["status"]!="WRITTEN_CALLABLE_FACTS":
            raise ValueError("previous declaration comparison not established; never infer retirement")
        sig=after["signature"]
        params=sig["positional_only"]+sig["positional_or_keyword"]+sig["keyword_only"]+[name for name in (sig["vararg"],sig["kwarg"])if name is not None]
        if kind=="no-explicit-parameter":
            if set(claim)!={"kind","parameter"} or type(claim["parameter"])is not str:
                raise ValueError("invalid explicit parameter claim")
            return finish("MODIFY" if claim["parameter"]in params else"NO-OP",
                          "Compare the positively established written signature only; runtime call/annotation/default execution remains unverified.")
        if kind=="written-tuple-return":
            if set(claim)!={"kind","elements"}or type(claim["elements"])is not list:
                raise ValueError("invalid tuple claim")
            shape=after["direct_return"]
            if shape["kind"]!="tuple-of-written-names":
                raise ValueError("return shape is not a proven direct tuple; helper behavior remains unknown")
            if not all(name in params for name in shape["elements"]):
                raise ValueError("tuple names are not established parameters")
            return finish("NO-OP" if shape["elements"]==claim["elements"]else"MODIFY",
                          "Exact direct written tuple/parameter order compared; no helper behavior is inferred.")
        if kind in ("written-return-composition","written-list-materialization"):
            shape=after["direct_return"]
            if shape["kind"]!="written-return-call":
                raise ValueError("exact direct return call not established")
            call=expression(shape["expression"])
            if not isinstance(call,ast.Call)or not isinstance(call.func,ast.Name):
                raise ValueError("return call identity is unresolved")
            if kind=="written-list-materialization":
                if set(claim)!={"kind","callee"}:
                    raise ValueError("unknown materialization claim fields")
                if "list"in after["module_written_binding_names"]or"list"in params or sig["vararg"]=="list"or sig["kwarg"]=="list":
                    raise ValueError("written list name is lexically shadowed")
                if call.func.id!="list"or call.keywords or len(call.args)!=1:
                    raise ValueError("not a direct written list call; semantic equivalence is unresolved")
                inner=call.args[0]
                if not isinstance(inner,ast.Call)or not isinstance(inner.func,ast.Name):
                    raise ValueError("inner materialization call identity unresolved")
                if inner.func.id in params or inner.func.id in (sig["vararg"],sig["kwarg"]):
                    raise ValueError("inner helper name is a caller-supplied parameter")
                matches=inner.func.id==claim["callee"]
            else:
                if set(claim)!={"kind","outer","inner","shared_argument"}:
                    raise ValueError("unknown composition claim fields")
                if len(call.args)!=2 or call.keywords or not isinstance(call.args[0],ast.Call):
                    raise ValueError("closed two-argument composition shape not established")
                inner=call.args[0]
                if not isinstance(inner.func,ast.Name)or len(inner.args)!=2 or inner.keywords:
                    raise ValueError("inner composition shape outside profile")
                shared=claim["shared_argument"]
                if shared not in params:
                    raise ValueError("shared argument is not an established parameter")
                if any(not isinstance(n,ast.Name)for n in (inner.args[0],inner.args[1],call.args[1])):
                    raise ValueError("composition expressions require separate semantics")
                if any(name in params or name in (sig["vararg"],sig["kwarg"]) for name in (call.func.id,inner.func.id)):
                    raise ValueError("composition helper names are caller-supplied parameters")
                matches=(call.func.id==claim["outer"]and inner.func.id==claim["inner"]and
                         inner.args[1].id==shared and call.args[1].id==shared)
            return finish("NO-OP"if matches else"MODIFY","Written call-expression predicate compared only; runtime helper and built-in bindings are not guaranteed.")
        if kind=="no-direct-returned-class-methods":
            if set(claim)!={"kind","methods"}or type(claim["methods"])is not list:
                raise ValueError("invalid direct method absence mapping")
            local=after["returned_local_class"]
            if not local:
                raise ValueError("returned local-class ownership not established")
            found=[name for name in claim["methods"]if name in local["unconditional_direct_methods"]]
            if found:
                return finish("MODIFY","Positive direct method declarations contradict the mapped absence claim; the written return calls the local class constructor;its runtime result type is not inferred.")
            raise ValueError("lack of admitted direct methods is not proof of absence; preserve for review")
        if kind=="fixed-written-callback":
            if set(claim)!={"kind","callee","keyword"}:
                raise ValueError("invalid callback mapping")
            wires=[]
            for text in after["direct_statement_calls"]:
                call=expression(text)
                for keyword in call.keywords:
                    if keyword.arg==claim["keyword"]and isinstance(keyword.value,ast.Name):
                        nested=after["direct_nested_functions"].get(keyword.value.id)
                        if nested:
                            for returned in nested["direct_body_return_calls"]:
                                value=expression(returned)
                                if isinstance(value.func,ast.Name):
                                    wires.append(value.func.id)
            if len(wires)!=1:
                raise ValueError("unique written callback forwarding wire not established")
            if wires[0]in params:
                return finish("MODIFY","The written wrapper forwards a caller-supplied parameter rather than a fixed helper; execution of the downstream traversal remains unknown.")
            if wires[0]==claim["callee"]:
                return finish("NO-OP","The admitted written wrapper still directly names the mapped helper; runtime binding remains unverified.")
            raise ValueError("different helper name does not prove behavior; review required")
        raise ValueError("typed predicate outside admitted profile")
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError)as error:
        return finish("INCONCLUSIVE",str(error))
