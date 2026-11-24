CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
def mutate():
    global CONTRACTS
    CONTRACTS = {}
