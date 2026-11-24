raise RuntimeError('owned source must never execute')

def mark(fn):
    return fn

@mark
async def selected(value=1):
    return value + 1

def other(value=2):
    return value + 2
