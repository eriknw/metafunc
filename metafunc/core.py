import sys
import types


def _identity(x):
    return x


class ModuleLoader(object):
    """ Finds and loads modules when added to sys.meta_path (see PEP-302)"""
    def __init__(self, source):
        self._source = source

    def find_module(self, fullname, path=None):
        base, dot, name = fullname.rpartition('.')
        if base == self._source.__name__ and name in self._source._metafuncs:
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
        self._funcs = source._funcs
        self._metafuncs = source._metafuncs
        self._reverse = source._reverse
        self._composition = source._composition
        self._func = self._metafuncs[name]
        self._rfunc = lambda x: source._rfunc(self._func(x))
        self.__all__ = list(self._funcs)
        for funcname in self._funcs:
            setattr(self, funcname, self._apply(funcname))

    def _apply(self, funcname):
        if self._reverse:
            first_func = self._funcs[funcname]
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
        # Allow attribute chaining of metafuncs
        if name in self._metafuncs:
            item = MetaModule(name, self)
            setattr(self, name, item)
            return item
        raise AttributeError


class FirstMetaModule(BaseModule):
    """ A module from which the higher-order functions originate"""
    def __init__(self, name, source, metafuncs, funcs, doc='', reverse=False,
                 composition=False):
        super(FirstMetaModule, self).__init__(name, source)
        self._funcs = funcs
        self._metafuncs = metafuncs
        self._reverse = reverse
        self._composition = composition
        self._func = _identity
        self._rfunc = _identity
        self.__all__ = []
        for funcname in self._metafuncs:
            self._apply_metafunc(funcname)
        if source:
            setattr(source, name, self)

    def _apply_metafunc(self, funcname):
        setattr(self, funcname, MetaModule(funcname, self))

    def __getattr__(self, name):
        if name in self._funcs:
            return self._funcs[name]
        raise AttributeError


class HiddenMetaModule(BaseModule):
    """ A module from which the higher-order functions originate

    This module is used to mirror an existing module and provide higher-order
    functions to originate from the existing module.  It is hidden so it
    doesn't replace the original module.
    """
    def __init__(self, name, metafuncs, funcs, doc='', reverse=False,
                 composition=False):
        super(HiddenMetaModule, self).__init__(name, None, hidden=True)
        self._funcs = funcs
        self._metafuncs = metafuncs
        self._reverse = reverse
        self._composition = composition
        self._func = _identity
        self._rfunc = _identity
        self.__all__ = []
        for funcname in self._metafuncs:
            self._apply_metafunc(funcname)
        source_module = sys.modules[self.__package__]
        setattr(source_module, '_hidden_metamodule_', self)

    def _apply_metafunc(self, funcname):
        source_module = sys.modules[self.__package__]
        fullname = '%s.%s' % (self.__package__, funcname)
        if fullname in sys.modules:
            raise ValueError('Cannot override module %s' % fullname)
        setattr(self, funcname, MetaModule(funcname, self))
        setattr(source_module, funcname, getattr(self, funcname))

    def __getattr__(self, name):
        if name in self._funcs:
            return self._funcs[name]
        raise AttributeError


def _process_funcs(funcs):
    if not funcs:
        funcs = {}
    elif callable(funcs) and hasattr(funcs, '__name__'):
        funcs = {funcs.__name__: funcs}
    elif not isinstance(funcs, dict):
        funcs = dict((func.__name__, func) if callable(func) else func
                     for func in funcs)
    else:
        funcs = funcs.copy()
    return funcs


def metafunc(module_name, metafuncs, funcs, reverse=False, composition=False):
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
        if (isinstance(source_module, BaseModule) or
                isinstance(getattr(source_module, '_hidden_metamodule_', None),
                           BaseModule)):
            raise ValueError('Calling "metafunc" on MetaModules not supported')

    funcs = _process_funcs(funcs)
    metafuncs = _process_funcs(metafuncs)
    if set(funcs).intersection(metafuncs):
        raise ValueError('Cannot use same name for funcs and metafuncs')

    if module_name in sys.modules:
        HiddenMetaModule(module_name, metafuncs, funcs, reverse=reverse,
                         composition=composition)
        meta_module = sys.modules[module_name]
    else:
        meta_module = FirstMetaModule(meta_name, source_module, metafuncs,
                                      funcs, reverse=reverse,
                                      composition=composition)
    return meta_module


def addfuncs(module_name, funcs):
    # if input is a module object, get its name
    module_name = getattr(module_name, '__name__', module_name)
    if module_name not in sys.modules:
        raise ValueError('Bad module name')
    module = sys.modules[module_name]
    if not isinstance(module, BaseModule):
        raise ValueError('Bad module type')
    while isinstance(module._source, BaseModule):
        module = module._source

    funcs = _process_funcs(funcs)
    funcset = set(funcs)
    if funcset.intersection(module._funcs):
        raise ValueError('First order function already defined')
    if funcset.intersection(module._metafuncs):
        raise ValueError('Function name already used by higher-order function')
    module._funcs.update(funcs)
    nextmodules = [getattr(module, item) for item in module._metafuncs]
    while nextmodules:
        module = nextmodules.pop()
        for funcname in funcs:
            setattr(module, funcname, module._apply(funcname))
        nextmodules.extend(getattr(module, item) for item in module._metafuncs
                           if module.__package__ + '.' + item in sys.modules)


def addmetafuncs(module_name, metafuncs):
    # if input is a module object, get its name
    module_name = getattr(module_name, '__name__', module_name)
    if module_name not in sys.modules:
        raise ValueError('Bad module name')
    module = sys.modules[module_name]
    if not isinstance(module, BaseModule):
        raise ValueError('Bad module type')
    while isinstance(module._source, BaseModule):
        module = module._source

    metafuncs = _process_funcs(metafuncs)
    metafuncset = set(metafuncs)
    if metafuncset.intersection(module._metafuncs):
        raise ValueError('Higher-order function already defined')
    if metafuncset.intersection(module._funcs):
        raise ValueError('Function name already used by first order function')
    module._metafuncs.update(metafuncs)
    for funcname in metafuncs:
        module._apply_metafunc(funcname)
