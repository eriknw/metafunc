from functools import wraps


def incremented(f):
    @wraps(f)
    def inner(*args, **kwargs):
        return f(*args, **kwargs) + 1
    return inner


def doubled(f):
    @wraps(f)
    def inner(*args, **kwargs):
        return 2 * f(*args, **kwargs)
    return inner


def tripled(f):
    @wraps(f)
    def inner(*args, **kwargs):
        return 3 * f(*args, **kwargs)
    return inner


def identified(f):
    @wraps(f)
    def inner(*args, **kwargs):
        return f(*args, **kwargs)
    return inner
