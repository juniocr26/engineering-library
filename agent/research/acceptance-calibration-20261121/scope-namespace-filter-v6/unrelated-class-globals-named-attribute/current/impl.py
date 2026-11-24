CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
def replacement():
    return 2
class Unrelated:
    __globals__ = {}
Unrelated.__globals__['unrelated'] = 17
