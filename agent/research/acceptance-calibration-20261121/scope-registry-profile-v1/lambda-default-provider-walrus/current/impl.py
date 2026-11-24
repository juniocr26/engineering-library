CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
unrelated = lambda item=(limit_value := 0): item
