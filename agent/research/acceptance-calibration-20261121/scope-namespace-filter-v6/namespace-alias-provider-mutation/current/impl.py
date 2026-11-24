CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
def replacement():
    return 2
ns = limit_value.__globals__
ns['limit_value'] = replacement
