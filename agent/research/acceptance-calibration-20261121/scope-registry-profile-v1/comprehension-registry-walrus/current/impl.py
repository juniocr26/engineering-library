CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
unrelated = [(CONTRACTS := {}) for item in (1,)]
