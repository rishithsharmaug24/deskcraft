"""Put `src/` on the path, and refuse the network for the whole test process.

**The path.** A stopgap, and the same one curvecast carries with the same caveat: the
project is a src-layout package and the right answer is an editable install. Until there
is an environment to install into, this file is how imports work -- which is a thing to
delete rather than to settle into, because a conftest that silently fixes the path is
how a package ends up never actually being installable.

**The network** (D3a, DD25). Installed here, at collection, so every test -- and every
line of engine code a test calls -- runs under a runtime refusal of network access that
backs the static egress ban. `tests/egress_guard.py` says what it reaches and, more to the
point, what it does not.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

_TESTS = Path(__file__).resolve().parent
if str(_TESTS) not in sys.path:
    sys.path.insert(0, str(_TESTS))

import egress_guard  # noqa: E402

egress_guard.install()
