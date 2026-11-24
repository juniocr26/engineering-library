CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
def replacement():
    return 2
del (lambda: None).__globals__['CONTRACTS']['owned.limit-value']
