import imp
import sys
from metafunc.core import metafunc, addfuncs, addmetafuncs
from metafunc.utils import raises
from zmm.firstorder import one, two, three, inc, double, triple, identity
from zmm.higherorder import incremented, doubled, tripled, identified


fofs1 = [one, two, three, identity]
hofs1 = [inc, double, triple]


def test_composed():
    metafunc('zmm.comp', hofs1, fofs1, composition=True, reverse=False)
    # (1) check simple import
    from zmm.comp.inc import one
    assert one() == 2
    # (2) check multi-import
    from zmm.comp.inc import one, two, three
    assert one() == 2
    assert two() == 3
    assert three() == 4
    # (3) check nested import
    from zmm.comp.inc.inc.inc.inc import one
    assert one() == 5
    # (4) check order
    from zmm.comp.inc.double import one
    assert one() == 4
    # (5) check attribute access
    import zmm
    assert zmm.comp.triple.double.triple.double.one() == 36
    # (6) check renaming (just because)
    from zmm.comp.inc.inc.inc import one as one_plus_three
    assert one_plus_three() == 4


def test_composed_new():
    # check new package creation
    metafunc('comp', hofs1, fofs1, composition=True, reverse=False)
    # (1) check simple import
    from comp.inc import one
    assert one() == 2
    # (2) check multi-import
    from comp.inc import one, two, three
    assert one() == 2
    assert two() == 3
    assert three() == 4
    # (3) check nested import
    from comp.inc.inc.inc.inc import one
    assert one() == 5
    # (4) check order
    from comp.inc.double import one
    assert one() == 4
    # (5) check attribute access
    import comp
    assert comp.triple.double.triple.double.one() == 36
    # (6) check renaming (just because)
    from comp.inc.inc.inc import one as one_plus_three
    assert one_plus_three() == 4


def test_composed_reversed():
    metafunc('zmm.rcomp', hofs1, fofs1, composition=True, reverse=True)
    # (1) check simple import
    from zmm.rcomp.inc import one
    assert one() == 2
    # (2) check multi-import
    from zmm.rcomp.inc import one, two, three
    assert one() == 2
    assert two() == 3
    assert three() == 4
    # (3) check nested import
    from zmm.rcomp.inc.inc.inc.inc import one
    assert one() == 5
    # (4) check order
    from zmm.rcomp.inc.double import one
    assert one() == 3
    # (5) check attribute access
    import zmm
    assert zmm.rcomp.triple.double.triple.double.one() == 36
    # (6) check renaming (just because)
    from zmm.rcomp.inc.inc.inc import one as one_plus_three
    assert one_plus_three() == 4


def test_composed_reversed_new():
    metafunc('rcomp', hofs1, fofs1, composition=True, reverse=True)
    # (1) check simple import
    from rcomp.inc import one
    assert one() == 2
    # (2) check multi-import
    from rcomp.inc import one, two, three
    assert one() == 2
    assert two() == 3
    assert three() == 4
    # (3) check nested import
    from rcomp.inc.inc.inc.inc import one
    assert one() == 5
    # (4) check order
    from rcomp.inc.double import one
    assert one() == 3
    # (5) check attribute access
    import rcomp
    assert rcomp.triple.double.triple.double.one() == 36
    # (6) check renaming (just because)
    from rcomp.inc.inc.inc import one as one_plus_three
    assert one_plus_three() == 4


fofs2 = [one, two, three, identity, inc, double, triple]
hofs2 = [incremented, doubled, tripled, identified]


def test_hof():
    metafunc('zmm.hofs', hofs2, fofs2, reverse=False)
    # (1) check simple import
    from zmm.hofs.doubled import one
    assert one() == 2
    # (2) check multi-import
    from zmm.hofs.doubled import one, two, three
    assert one() == 2
    assert two() == 4
    assert three() == 6
    # (3) check nested import
    from zmm.hofs.doubled.tripled.doubled import one
    assert one() == 12
    # (4) check order
    from zmm.hofs.incremented.doubled import one
    assert one() == 4
    # (5) check attribute access
    import zmm
    assert zmm.hofs.tripled.doubled.tripled.one() == 18
    # (6) check renaming (just because)
    from zmm.hofs.incremented.tripled import one as six
    assert six() == 6


def test_hof_new():
    metafunc('hofs', hofs2, fofs2, reverse=False)
    # (1) check simple import
    from hofs.doubled import one
    assert one() == 2
    # (2) check multi-import
    from hofs.doubled import one, two, three
    assert one() == 2
    assert two() == 4
    assert three() == 6
    # (3) check nested import
    from hofs.doubled.tripled.doubled import one
    assert one() == 12
    # (4) check order
    from hofs.incremented.doubled import one
    assert one() == 4
    # (5) check attribute access
    import hofs
    assert hofs.tripled.doubled.tripled.one() == 18
    # (6) check renaming (just because)
    from hofs.incremented.tripled import one as six
    assert six() == 6


def test_hof_reversed():
    metafunc('zmm.rhofs', hofs2, fofs2, reverse=True)
    # (1) check simple import
    from zmm.rhofs.doubled import one
    assert one() == 2
    # (2) check multi-import
    from zmm.rhofs.doubled import one, two, three
    assert one() == 2
    assert two() == 4
    assert three() == 6
    # (3) check nested import
    from zmm.rhofs.doubled.tripled.doubled import one
    assert one() == 12
    # (4) check order
    from zmm.rhofs.incremented.doubled import one
    assert one() == 3
    # (5) check attribute access
    import zmm
    assert zmm.rhofs.tripled.doubled.tripled.one() == 18
    # (6) check renaming (just because)
    from zmm.rhofs.incremented.tripled import one as four
    assert four() == 4


def test_hof_reversed_new():
    metafunc('rhofs', hofs2, fofs2, reverse=True)
    # (1) check simple import
    from rhofs.doubled import one
    assert one() == 2
    # (2) check multi-import
    from rhofs.doubled import one, two, three
    assert one() == 2
    assert two() == 4
    assert three() == 6
    # (3) check nested import
    from rhofs.doubled.tripled.doubled import one
    assert one() == 12
    # (4) check order
    from rhofs.incremented.doubled import one
    assert one() == 3
    # (5) check attribute access
    import rhofs
    assert rhofs.tripled.doubled.tripled.one() == 18
    # (6) check renaming (just because)
    from rhofs.incremented.tripled import one as four
    assert four() == 4


def test_bad_module_name():
    assert raises(ValueError, lambda: metafunc('zmm.foo.bar.comp', hofs1,
                                               fofs1, composition=True))

fofs3 = [('f_one', one), ('two', two), three, identity]
hofs3 = [('f_inc', inc), ('double', double), triple]


def test_function_tuple():
    metafunc('zmm.fcomp', hofs3, fofs3, composition=True)
    from zmm.fcomp.f_inc import f_one
    assert f_one() == 2
    from zmm.fcomp.double.f_inc.triple import f_one, two, three
    assert f_one() == 9
    assert two() == 15
    assert three() == 21


fofs4 = {'d_one': one, 'two': two, 'three': three}
hofs4 = {'d_inc': inc, 'double': double, 'triple': triple}


def test_function_dict():
    metafunc('zmm.dcomp', hofs4, fofs4, composition=True)
    from zmm.dcomp.d_inc import d_one
    assert d_one() == 2
    from zmm.dcomp.double.d_inc.triple import d_one, two, three
    assert d_one() == 9
    assert two() == 15
    assert three() == 21


def test_empty():
    metafunc('zmm.empty_fofs', hofs1, {}, composition=True)
    from zmm.empty_fofs.double.triple import double
    metafunc('zmm.empty_hofs', {}, fofs1, composition=True)
    import zmm.empty_hofs
    metafunc('zmm.empty_fofs_hofs', {}, {}, composition=True)
    import zmm.empty_fofs_hofs
    metafunc('zmm.empty_fofs_hofs2', {}, {})
    import zmm.empty_fofs_hofs2
    metafunc('zmm.empty_fofs_hofs3', {}, {}, reverse=True)
    import zmm.empty_fofs_hofs3
    metafunc('zmm.empty_fofs_hofs4', {}, {}, composition=True, reverse=True)
    import zmm.empty_fofs_hofs4
    metafunc('zmm.empty_fofs_hofs5', (), None)
    import zmm.empty_fofs_hofs5


def test_mirror_module():
    sys.modules['empty1'] = imp.new_module('empty1')
    import empty1 as orig_empty
    meta_empty = metafunc('empty1', hofs1, fofs1, composition=True)
    import empty1 as new_empty
    assert orig_empty == meta_empty
    assert orig_empty == new_empty
    assert meta_empty.double.double.one() == 4
    from empty1.inc.inc.double import one
    assert one() == 6
    # don't override modules
    assert raises(ValueError, lambda: metafunc('empty1', hofs1, fofs1,
                                               composition=True))


def test_module_input():
    mod = sys.modules['empty2'] = imp.new_module('empty2')
    meta_empty = metafunc(mod, hofs1, fofs1, composition=True)
    assert mod == meta_empty
    from empty2.inc.inc.inc import one
    assert one() == 4


def test_attribute_failure():
    sys.modules['empty3'] = imp.new_module('empty3')
    metafunc('empty3.comp', hofs1, fofs1, composition=True)
    import empty3.comp
    assert raises(AttributeError, lambda: empty3.comp.foo)
    assert raises(AttributeError, lambda: empty3.comp.inc.double.foo)
    metafunc('empty3', hofs1, fofs1, composition=True)
    import empty3
    assert raises(AttributeError, lambda: empty3.inc._source.foo)


def test_module_loader():
    sys.modules['empty4'] = imp.new_module('empty4')
    metafunc('empty4.comp', hofs1, fofs1, composition=True)
    import empty4.comp.inc
    tested = 0
    for item in sys.meta_path:
        if hasattr(item, 'find_module'):
            loader = item.find_module('empty4.comp.inc')
            if loader:
                assert empty4.comp.inc is loader.load_module('empty4.comp.inc')
                tested += 1
    assert tested > 0


def test_dunder_all():
    sys.modules['empty5'] = imp.new_module('empty5')
    metafunc('empty5.comp', hofs1, fofs1, composition=True)
    from empty5.comp.inc.inc.inc import one
    import empty5
    assert empty5.comp.__all__ == []
    assert sorted(empty5.comp.inc.__all__) == sorted(['one', 'two', 'three',
                                                      'identity'])


def test_single_callable():
    sys.modules['empty6'] = imp.new_module('empty6')
    metafunc('empty6.comp', inc, one, composition=True)
    import empty6
    assert empty6.comp.inc.inc.inc.one() == 4


def test_has_attr():
    sys.modules['empty7'] = imp.new_module('empty7')
    metafunc('empty7.comp', inc, one, composition=True)
    import empty7
    assert hasattr(empty7.comp.inc, 'one') is True
    assert hasattr(empty7.comp.inc, 'two') is False
    assert hasattr(empty7.comp.inc, 'inc') is True  # it gets created
    assert empty7.comp.inc.__package__ + '.inc' in sys.modules
    assert empty7.comp.inc.inc.__package__ + '.inc' not in sys.modules


def test_add_fofs():
    sys.modules['empty8'] = imp.new_module('empty8')
    metafunc('empty8.comp', inc, one, composition=True)
    import empty8
    assert empty8.comp.inc.one() == 2
    addfuncs('empty8.comp', two)
    assert empty8.comp.inc.two() == 3
    assert empty8.comp.inc.inc.two() == 4
    assert raises(ValueError, lambda: addfuncs('empty8.comp', two))
    assert raises(ValueError, lambda: addfuncs('empty8.comp', inc))
    assert raises(ValueError, lambda: addfuncs('empty8', three))
    assert raises(ValueError, lambda: addfuncs('empty8.comp.foo.bar', three))
    addfuncs('empty8.comp.inc.inc', three)
    assert empty8.comp.inc.three() == 4


def test_add_hofs():
    sys.modules['empty9'] = imp.new_module('empty9')
    metafunc('empty9.comp', inc, one, composition=True)
    import empty9
    assert empty9.comp.inc.inc.one() == 3
    addmetafuncs('empty9.comp', double)
    assert empty9.comp.double.one() == 2
    assert empty9.comp.inc.inc.inc.double.one() == 8
    assert raises(ValueError, lambda: addmetafuncs('empty9.comp', double))
    assert raises(ValueError, lambda: addmetafuncs('empty9.comp', one))
    assert raises(ValueError, lambda: addmetafuncs('empty9', triple))
    assert raises(ValueError, lambda: addmetafuncs('empty9.comp.foo.bar',
                                                   triple))
    addmetafuncs('empty9.comp.inc.inc', triple)
    assert empty9.comp.triple.one() == 3


def test_metafunc_on_metamodules():
    sys.modules['empty10'] = imp.new_module('empty10')
    metafunc('empty10.comp', inc, one, composition=True)
    import empty10.comp.inc.inc.inc
    assert raises(ValueError, lambda: metafunc('empty10.comp.inc', double,
                                               two, composition=True))
    # It is allowed to do this on a base module as long as names don't clash
    # XXX: perhaps this should be a convenient way to add fofs and hofs
    metafunc('empty10.comp', double, [one, two, three], composition=True)
    import empty10
    assert empty10.comp.double.double.one() == 4
    assert raises(AttributeError, lambda: empty10.comp.double.inc.one())
    assert raises(AttributeError, lambda: empty10.comp.inc.double.one())
    assert raises(ValueError, lambda: (metafunc('empty10.comp', [inc, triple],
                                       one, composition=True)))
    # same tests on a hidden metamodule
    metafunc('empty10', inc, one, composition=True)
    assert raises(ValueError, lambda: metafunc('empty10.inc', double,
                                               two, composition=True))
    metafunc('empty10', double, [one, two, three], composition=True)
    assert empty10.double.double.one() == 4
    assert raises(AttributeError, lambda: empty10.double.inc.one())
    assert raises(AttributeError, lambda: empty10.inc.double.one())
    assert raises(ValueError, lambda: (metafunc('empty10', [inc, triple],
                                       one, composition=True)))


def test_fofs_and_hofs_dont_intersect():
    sys.modules['empty11'] = imp.new_module('empty11')
    assert raises(ValueError, lambda: metafunc('empty11.comp', [one, inc],
                                               inc, composition=True))
