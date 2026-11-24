CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
def unrelated():
    CONTRACTS = {}
    return CONTRACTS
