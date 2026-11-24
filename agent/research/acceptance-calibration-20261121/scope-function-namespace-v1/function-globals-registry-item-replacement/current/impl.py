CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
def replacement():
    return 2
limit_value.__globals__['CONTRACTS']['owned.limit-value'] = 'replacement'
