import sys
import types

# TODO: We currently require a new module to be created and attached to an
#       existing module.  Perhaps we could attach a module loader to an
#       existing module, which will allow the flexible importing directly.
# XXX:  Relative imports such as "from . import hofs.doubled import one"
#       has not been tested.
# XXX:  Module reloading has not been tested.
# XXX:  What about docstrings of generated modules?
# IDEA: Perhaps provide an option that an hof can only be used once in a chain.
# IDEA: Instead of having 'source_module' and 'module_name', just have a one
#       input that is both, such as 'hof.hofs'.


_identity = lambda x: x


class ModuleLoader(object):
    """ Finds and loads modules when added to sys.meta_path (see PEP-302)"""
    def __init__(self, source):
        self._source = source

    def find_module(self, fullname, path=None):
        base, _, hof = fullname.rpartition('.')
        if base == self._source.__name__ and hof in self._source._hofs:
            return self

    def load_module(self, fullname):
        # if the module is already loaded, we must return it
        if fullname in sys.modules:
            return sys.modules[fullname]
        base, _, name = fullname.rpartition('.')
        item = MetaModule(name, self._source)
        item.__loader__ = self
        return item


class BaseModule(types.ModuleType):
    """ Base module to ensure proper adherence to module requirements"""
    def __init__(self, name, source):
        fullname = source.__name__ + '.' + name
        super(BaseModule, self).__init__(fullname)
        self.__package__ = fullname
        self.__file__ = __file__
        self.__path__ = []
        sys.modules[fullname] = self
        sys.meta_path.append(ModuleLoader(self))


class MetaModule(BaseModule):
    """ A chainable module that applies a higher-order function

    The first order functions will be automatically populated, and
    higher-order functions will be generated upon demand.
    """
    def __init__(self, name, source, doc=''):
        super(MetaModule, self).__init__(name, source)
        # Get parameters from the source module to ensure consistency
        self._fofs = source._fofs
        self._hofs = source._hofs
        self._reverse = source._reverse
        self._composition = source._composition
        self._func = self._hofs[name]
        self._rfunc = lambda x: source._rfunc(self._func(x))

        def composer(f):
            return lambda *args, **kwargs: self._func(f(*args, **kwargs))

        def rcomposer(f):
            return lambda *args, **kwargs: self._rfunc(f(*args, **kwargs))

        # Add first order functions and apply hofs in the manner as requested
        for first_name, first_func in self._fofs.items():
            prev_func = getattr(source, first_name)
            if self._composition:
                if self._reverse:
                    # func1(func2(orig_func(*args, **kwargs)))
                    setattr(self, first_name, rcomposer(first_func))
                else:
                    # func2(func1(orig_func(*args, **kwargs)))
                    setattr(self, first_name, composer(prev_func))
            else:
                if self._reverse:
                    # func1(func2(orig_func))(*args, **kwargs)
                    setattr(self, first_name, self._rfunc(first_func))
                else:
                    # func2(func1(orig_func))(*args, **kwargs)
                    setattr(self, first_name, self._func(prev_func))

    def __getattr__(self, name):
        # Allow attribute chaining of hofs
        if name in self._hofs:
            item = MetaModule(name, self)
            setattr(self, name, item)
            return item
        raise AttributeError


class FirstMetaModule(BaseModule):
    """ A module from which the higher-order functions originate"""
    def __init__(self, name, source, fofs, hofs, doc='', reverse=False,
                 composition=False):
        super(FirstMetaModule, self).__init__(name, source)
        self._fofs = fofs
        self._hofs = hofs
        self._reverse = reverse
        self._composition = composition
        self._func = _identity
        self._rfunc = _identity
        for item in self._hofs:
            setattr(self, item, MetaModule(item, self))
        setattr(source, name, self)

    def __getattr__(self, name):
        if name in self._fofs:
            return self._fofs[name]
        raise AttributeError


def metafunc(source_module, module_name, fofs, hofs, reverse=False,
             composition=False):
    """ Create a module of higher-order functions that can be chained on import

    For example:
    >>> from hof_module.inc.inc import one as one_plus_two  # doctest: +SKIP
    >>> one_plus_two()  # doctest: +SKIP
    3

    Arguments:
    source_module -- existing module (name or object) onto which `module_name`
                     will be added.
    module_name -- the name of the created module
    fofs -- list or dict of first order functions
    hofs -- list or dict of higher-order functions

    ``fofs`` and ``hofs`` may be a dict of {name: function}, or a list where
    each element is a function or a tuple of function name and function object.

    Keyword Arguments:
    reverse (default False) -- determines the order to apply the hofs
    composition (default False) -- determines how hofs are applied (see below)

    # Example import with hofs "higher1" and "higher2", and fof "first"
    >>> from hof_module.higher1.higher2 import first  # doctest: +SKIP

    If ``composition`` is False (the default), then hofs will be applied as:
        "higher2(higher1(first))(*args, **kwargs)"
    and if ``composition is True:
        "higher2(higher1(first(*args, **kwargs)))"

    If ``reverse`` is True, then the order of "higher1" and "higher2" from
    above are reversed.
    """
    if source_module in sys.modules:
        source_module = sys.modules[source_module]

    if not isinstance(fofs, dict):
        fofs = dict((func.__name__, func) if callable(func) else func
                    for func in fofs)
    if not isinstance(hofs, dict):
        hofs = dict((func.__name__, func) if callable(func) else func
                    for func in hofs)

    hof_module = FirstMetaModule(module_name, source_module, fofs, hofs,
                                 reverse=reverse, composition=composition)
    return hof_module
