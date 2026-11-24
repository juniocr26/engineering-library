def __getattr__(name):
    return globals()[name]
