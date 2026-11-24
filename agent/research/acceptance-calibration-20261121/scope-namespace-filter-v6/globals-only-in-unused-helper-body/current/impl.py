CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
def replacement():
    return 2
def inspect_namespace_later():
    return limit_value.__globals__
