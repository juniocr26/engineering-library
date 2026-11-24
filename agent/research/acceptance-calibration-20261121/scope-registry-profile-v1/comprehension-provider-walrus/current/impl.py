CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
unrelated = [(limit_value := 0) for item in (1,)]
