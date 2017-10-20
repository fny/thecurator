import platform

# Are we running PyPy?
IS_PYPY = platform.python_implementation() == 'PyPy'


# Decorator that won't define a given function if incompatible
def pypy_incompatible(func):
    if not IS_PYPY:
        return func
