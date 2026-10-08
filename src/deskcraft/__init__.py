"""deskcraft -- a paper-only macro risk engine.

It answers **"what is the risk of this book?"** and never **"should you hold it?"**
That sentence is the whole boundary, and `tests/test_deskcraft_boundary.py` is what
makes it a property of the build rather than of whoever remembers it.

**Why this package is empty at D1.** The boundary test has to be live before there
is anything to guard, or its first real exercise is also the first time anyone finds
out whether it was inert. curvecast made the same call at WP-0 with
`news/scoring.py`, for the same reason, and it is the only ordering under which a
guard can be trusted. `Direction`, `Notional` and the book types arrive at D2.

**The boundary is inverted relative to curvecast's, and the inversion is the point.**
curvecast bans an order by banning the words that would express one -- `notional`,
`direction`, `position`, `size`, `weight`, `side`, `order` -- because its output is
text and a directive is one field name away from a forecast. That is precisely why
a risk engine cannot live there: portfolio VaR is a function *of positions*, so no
version of this repo could keep that boundary, and `EXEMPT_FIELDS` is `{}` and has
never been anything else.

Here the forbidden vocabulary is the subject matter, so the ban is on **capability**
instead:

    no egress        no socket, urllib, requests, httpx, http, aiohttp,
                     websockets, smtplib. With no way out of the process there is
                     no order path, whatever a function is called.
    no execution     no subprocess, no os.system, no os.exec*.
    no credentials   no os.environ, no os.getenv, no getpass, no keyring, no
                     dotenv. Not "secrets via env only" -- no environment access
                     at all, because this repo needs none.
    no broker SDK    not a dependency, not imported, and not in sys.modules after
                     importing this package in a fresh interpreter.

**Since D3a the ban is a property of the working tree, not of this package.** Every
Python file carries exactly one policy, decided by where it sits: `tests/` keeps the
egress, broker and LLM-edge bans, and everything else -- including a `scripts/`
directory that does not exist yet -- carries all of them. The engine's imports are an
exact census, so capability cannot arrive under a name no list carries, and the network
is refused at run time for the whole test process. The lists themselves live in
`tests/test_deskcraft_boundary.py`, and the list above is their D1 form.

One half of curvecast's boundary *does* transfer and is ported verbatim: the
imperative phrase ban. A risk decomposition of a stated book never needs to say
"you should", "overweight" or "take profit", and that list is what keeps a
description from turning into advice on its way to a page.

**It is a craft artifact and cannot become a trading system.** Three independent
reasons, all already on the record: the RATES-X audit tested 138 configurations and
nothing cleared the bars; RBI's IRD Master Direction §5.4(i) makes retail INR IRD
hedging-only, and LRS closes UST futures; and the reference book carries a $200m 2Y
leg, which is institutional by three orders of magnitude. The deliverable is
fluency, not a position.
"""

from __future__ import annotations

__all__: list[str] = []
