from .zmm.firstorder import one, two, three, inc, double, triple, identity
from .zmm.higherorder import incremented, doubled, tripled, identified


__all__ = list(name for name in locals()
               if not name.startswith('_'))

from .core import metafunc


_fofs = [one, two, three, identity]
_hofs = [inc, double, triple]
metafunc(__package__, 'comp', _fofs, _hofs, composition=True,
         reverse=False)
metafunc(__package__, 'rcomp', _fofs, _hofs, composition=True,
         reverse=True)

_fofs = [one, two, three, identity, inc, double, triple]
_hofs = [incremented, doubled, tripled, identified]
metafunc(__package__, 'hofs', _fofs, _hofs, reverse=False)
metafunc(__package__, 'rhofs', _fofs, _hofs, reverse=True)

__version__ = '0.0.1'
