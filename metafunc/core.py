import sys
import types


_identity = lambda x: x


class ModuleLoader(object):
    """ Finds and loads modules when added to sys.meta_path (see PEP-302)"""
    def __init__(self, source):
        self._source = source

    def find_module(self, fullname, path=None):
        base, dot, hof = fullname.rpartition('.')
        if base == self._source.__name__ and hof in self._source._hofs:
            return self

    def load_module(self, fullname):
        # if the module is already loaded, we must return it
        if fullname in sys.modules:
            return sys.modules[fullname]
        base, dot, name = fullname.rpartition('.')
        item = MetaModule(name, self._source)
        item.__loader__ = self
        return item


class BaseModule(types.ModuleType):
    """ Base module to ensure proper adherence to module requirements"""
    def __init__(self, name, source, hidden=False):
        try:
            name = source.__name__ + '.' + name
        except AttributeError:
            pass
        super(BaseModule, self).__init__(name)
        self.__package__ = name
        self.__file__ = __file__
        self.__path__ = []
        self._source = source
        if not hidden:
            sys.modules[name] = self
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
        for funcname in self._fofs:
            setattr(self, funcname, self._apply(funcname))

    def _apply(self, funcname):
        if self._reverse:
            first_func = self._fofs[funcname]
            if self._composition:
                # func1(func2(orig_func(*args, **kwargs)))
                return lambda *args, **kwargs: (
                    self._rfunc(first_func(*args, **kwargs)))
            else:
                # func1(func2(orig_func))(*args, **kwargs)
                return self._rfunc(first_func)
        else:
            prev_func = getattr(self._source, funcname)
            if self._composition:
                # func2(func1(orig_func(*args, **kwargs)))
                return lambda *args, **kwargs: (
                    self._func(prev_func(*args, **kwargs)))
            else:
                # func2(func1(orig_func))(*args, **kwargs)
                return self._func(prev_func)

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
        if source:
            setattr(source, name, self)

    def __getattr__(self, name):
        if name in self._fofs:
            return self._fofs[name]
        raise AttributeError


class HiddenMetaModule(BaseModule):
    """ A module from which the higher-order functions originate"""
    def __init__(self, name, fofs, hofs, doc='', reverse=False,
                 composition=False):
        super(HiddenMetaModule, self).__init__(name, None, hidden=True)
        self._fofs = fofs
        self._hofs = hofs
        self._reverse = reverse
        self._composition = composition
        self._func = _identity
        self._rfunc = _identity
        source_module = sys.modules[name]
        for item in self._hofs:
            itemname = '%s.%s' % (name, item)
            if itemname in sys.modules:
                raise ValueError('Cannot override module %s' % itemname)
            setattr(self, item, MetaModule(item, self))
            setattr(source_module, item, getattr(self, item))

    def __getattr__(self, name):
        if name in self._fofs:
            return self._fofs[name]
        raise AttributeError


def metafunc(module_name, fofs, hofs, reverse=False, composition=False):
    """ Create a module of higher-order functions that can be chained on import

    For example:
    >>> from hof_module.inc.inc import one as one_plus_two
    >>> one_plus_two()
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
    >>> from hof_module.higher1.higher2 import first

    If ``composition`` is False (the default), then hofs will be applied as:
        "higher2(higher1(first))(*args, **kwargs)"
    and if ``composition is True:
        "higher2(higher1(first(*args, **kwargs)))"

    If ``reverse`` is True, then the order of "higher1" and "higher2" from
    above are reversed.
    """
    # if input is a module object, get its name
    module_name = getattr(module_name, '__name__', module_name)
    # partition package name into module path name and module name
    source_module, dot, meta_name = module_name.rpartition('.')
    if source_module and source_module not in sys.modules:
        raise ValueError("Bad module name (base module doesn't exist)")
    if source_module in sys.modules:
        source_module = sys.modules[source_module]

    if not fofs:
        fofs = {}
    elif not isinstance(fofs, dict):
        fofs = dict((func.__name__, func) if callable(func) else func
                    for func in fofs)
    if not hofs:
        hofs = {}
    elif not isinstance(hofs, dict):
        hofs = dict((func.__name__, func) if callable(func) else func
                    for func in hofs)

    if module_name in sys.modules:
        HiddenMetaModule(module_name, fofs, hofs, reverse=reverse,
                         composition=composition)
        meta_module = sys.modules[module_name]
    else:
        meta_module = FirstMetaModule(meta_name, source_module, fofs, hofs,
                                      reverse=reverse, composition=composition)
    return meta_module
