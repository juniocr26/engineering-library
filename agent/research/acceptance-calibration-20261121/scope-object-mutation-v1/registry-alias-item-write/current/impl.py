CONTRACTS = {"owned.limit-value": "limit_value"}
def limit_value():
    return 1
alias = CONTRACTS
alias['owned.limit-value'] = 'missing'
