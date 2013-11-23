from metafunc.core import metafunc
from zmm.firstorder import one, two, three, inc, double, triple, identity
from zmm.higherorder import incremented, doubled, tripled, identified


fofs1 = [one, two, three, identity]
hofs1 = [inc, double, triple]


def test_composed():
    metafunc('zmm', 'comp', fofs1, hofs1, composition=True, reverse=False)
    # check simple import
    from zmm.comp.inc import one
    assert one() == 2
    # check multi-import
    from zmm.comp.inc import one, two, three
    assert one() == 2
    assert two() == 3
    assert three() == 4
    # check nested import
    from zmm.comp.inc.inc.inc.inc import one
    assert one() == 5
    # check order
    from zmm.comp.inc.double import one
    assert one() == 4
    # check attribute access
    import zmm
    assert zmm.comp.triple.double.triple.double.one() == 36
    # check renaming (just because)
    from zmm.comp.inc.inc.inc import one as one_plus_three
    assert one_plus_three() == 4


def test_composed_reversed():
    metafunc('zmm', 'rcomp', fofs1, hofs1, composition=True, reverse=True)
    # check simple import
    from zmm.rcomp.inc import one
    assert one() == 2
    # check multi-import
    from zmm.rcomp.inc import one, two, three
    assert one() == 2
    assert two() == 3
    assert three() == 4
    # check nested import
    from zmm.rcomp.inc.inc.inc.inc import one
    assert one() == 5
    # check order
    from zmm.rcomp.inc.double import one
    assert one() == 3
    # check attribute access
    import zmm
    assert zmm.rcomp.triple.double.triple.double.one() == 36
    # check renaming (just because)
    from zmm.rcomp.inc.inc.inc import one as one_plus_three
    assert one_plus_three() == 4


fofs2 = [one, two, three, identity, inc, double, triple]
hofs2 = [incremented, doubled, tripled, identified]


def test_hof():
    metafunc('zmm', 'hofs', fofs2, hofs2, reverse=False)
    # check simple import
    from zmm.hofs.doubled import one
    assert one() == 2
    # check multi-import
    from zmm.hofs.doubled import one, two, three
    assert one() == 2
    assert two() == 4
    assert three() == 6
    # check nested import
    from zmm.hofs.doubled.tripled.doubled import one
    assert one() == 12
    # check order
    from zmm.hofs.incremented.doubled import one
    assert one() == 4
    # check attribute access
    import zmm
    assert zmm.hofs.tripled.doubled.tripled.one() == 18
    # check renaming (just because)
    from zmm.hofs.incremented.tripled import one as six
    assert six() == 6


def test_hof_reversed():
    metafunc('zmm', 'rhofs', fofs2, hofs2, reverse=True)
    # check simple import
    from zmm.rhofs.doubled import one
    assert one() == 2
    # check multi-import
    from zmm.rhofs.doubled import one, two, three
    assert one() == 2
    assert two() == 4
    assert three() == 6
    # check nested import
    from zmm.rhofs.doubled.tripled.doubled import one
    assert one() == 12
    # check order
    from zmm.rhofs.incremented.doubled import one
    assert one() == 3
    # check attribute access
    import zmm
    assert zmm.rhofs.tripled.doubled.tripled.one() == 18
    # check renaming (just because)
    from zmm.rhofs.incremented.tripled import one as four
    assert four() == 4

