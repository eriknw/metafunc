import sys
import types


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


class MetaModule(types.ModuleType):
    """ A chainable module that applies a higher-order function

    The first order functions will be automatically populated, and
    higher-order functions will be generated upon demand.
    """
    def __init__(self, name, source=None, metafuncs=None, funcs=None,
                 reverse=False, composition=False):
        # ensure proper adherence to module requirements
        try:
            fullname = source.__name__ + '.' + name
        except AttributeError:
            fullname = name
        super(MetaModule, self).__init__(fullname)
        self.__package__ = fullname
        self.__file__ = __file__
        self.__path__ = []
        self._source = source
        if source is not None:
            sys.modules[fullname] = self
        sys.meta_path.append(ModuleLoader(self))

        self._isfirst = not isinstance(source, MetaModule)
        if self._isfirst:
            if funcs is None:  # pragma: no cover
                raise ValueError('"funcs" keyword required for root MetaModule')
            if metafuncs is None:  # pragma: no cover
                raise ValueError('"metafuncs" keyword required for root MetaModule')
            self._funcs = funcs
            self._metafuncs = metafuncs
            self._reverse = reverse
            self._composition = composition

            self._func = None
            self.__all__ = []
            for funcname in metafuncs:
                self._apply_metafunc(funcname)
            if source is None:
                source_module = sys.modules[self.__package__]
                setattr(source_module, '_hidden_metamodule_', self)
            elif source:
                setattr(source, name, self)
        else:
            self._funcs = source._funcs
            self._metafuncs = source._metafuncs
            self._reverse = source._reverse
            self._composition = source._composition

            self._func = self._metafuncs[name]
            self.__all__ = list(self._funcs)
            for funcname in self._funcs:
                self._apply(funcname)

    def _apply(self, funcname):
        orig_func = self._funcs[funcname]
        funcs = []
        module = self
        while not module._isfirst:
            funcs.append(module._func)
            module = module._source

        funcs.reverse()
        # TODO: support callbacks for better user-control
        # if self._funcfilter:
        #     res = self._funcfilter(self.__name__, funcs)
        #     if not res:
        #         return None
        #     elif callable(res):
        #         return res
        #     elif isinstance(res, (list, tuple)):
        #         funcs = list(res)
        if self._reverse:
            funcs.reverse()

        if self._composition:
            # func1(func2(orig_func(*args, **kwargs)))
            # reverse: func2(func1(orig_func(*args, **kwargs)))
            def inner(*args, **kwargs):
                rv = orig_func(*args, **kwargs)
                for func in funcs:
                    rv = func(rv)
                return rv
            rv = inner
        else:
            # func1(func2(orig_func))(*args, **kwargs)
            # reverse: func2(func1(orig_func))(*args, **kwargs)
            rv = orig_func
            for func in funcs:
                rv = func(rv)
        setattr(self, funcname, rv)
        return rv

    def _apply_metafunc(self, funcname):
        if self._source is None:
            source_module = sys.modules[self.__package__]
            fullname = '%s.%s' % (self.__package__, funcname)
            if fullname in sys.modules:
                raise ValueError('Cannot override module %s' % fullname)
        # TODO: support callbacks for better user-control
        # if self._metafuncfilter:
        #     res = self._metafuncfilter(fullname, funcs)
        #     ...
        val = MetaModule(funcname, self)
        setattr(self, funcname, val)
        if self._source is None:
            setattr(source_module, funcname, val)
        return val

    def __getattr__(self, name):
        # Allow functions to be obtained from base module if requested
        if self._isfirst:
            if name in self._funcs:
                return self._funcs[name]
        # Allow attribute chaining of metafuncs
        elif name in self._metafuncs:
            val = self._apply_metafunc(name)
            if val is not None:
                return val
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
        if (isinstance(source_module, MetaModule) or
                isinstance(getattr(source_module, '_hidden_metamodule_', None),
                           MetaModule)):
            raise ValueError('Calling "metafunc" on MetaModules not supported')

    funcs = _process_funcs(funcs)
    metafuncs = _process_funcs(metafuncs)
    if set(funcs).intersection(metafuncs):
        raise ValueError('Cannot use same name for funcs and metafuncs')

    if module_name in sys.modules:
        MetaModule(module_name, None, metafuncs, funcs, reverse=reverse,
                   composition=composition)
        meta_module = sys.modules[module_name]
    else:
        meta_module = MetaModule(meta_name, source_module, metafuncs,
                                 funcs, reverse=reverse,
                                 composition=composition)
    return meta_module


def getrootmodule(module_name):
    # if input is a module object, get its name
    module_name = getattr(module_name, '__name__', module_name)
    if module_name not in sys.modules:
        raise ValueError('Bad module name')
    module = sys.modules[module_name]
    if not isinstance(module, MetaModule):
        raise ValueError('Bad module type')
    while not module._isfirst:
        module = module._source
    return module


def addfuncs(module_name, funcs):
    module = getrootmodule(module_name)

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
            module._apply(funcname)
        nextmodules.extend(getattr(module, item) for item in module._metafuncs
                           if module.__package__ + '.' + item in sys.modules)


def addmetafuncs(module_name, metafuncs):
    module = getrootmodule(module_name)

    metafuncs = _process_funcs(metafuncs)
    metafuncset = set(metafuncs)
    if metafuncset.intersection(module._metafuncs):
        raise ValueError('Higher-order function already defined')
    if metafuncset.intersection(module._funcs):
        raise ValueError('Function name already used by first order function')
    module._metafuncs.update(metafuncs)
    for funcname in metafuncs:
        module._apply_metafunc(funcname)
