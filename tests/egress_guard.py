"""A runtime refusal of network access, for the whole test process. D3a, DD25, bar C29.

The boundary scan reads source. It cannot see `importlib.import_module("soc" + "ket")`, a
library that opens a URL on a code path nobody named, or a network module no list thought of.
An audit hook sees all three, because CPython raises an audit event at the point a socket is
created or a name is resolved, whatever route reached it -- and installing one needs only `sys`,
so the guard trips none of the bans it backs up.

Measured 2026-09-11 on 3.12.10: `socket.socket()` raises `socket.__new__` before the object
exists, and `socket.create_connection` raises `socket.getaddrinfo` before any lookup, so a
refusal here lands before a packet could. The suite as it stood raised **zero** such events.

**What it does not reach, stated where the next reader will look.** Code no test executes.
Any child process -- an audit hook is per-interpreter and is not inherited. And execution
itself, which the harness keeps because C5 needs a fresh interpreter: a test that starts a
process can leave through it, and the static scan is the only thing watching that route.

Audit hooks cannot be removed once added. That is the property wanted here, and the reason
this is installed from `conftest.py` and never from `src/`: the engine does not get to change
the process it is imported into.
"""

from __future__ import annotations

import sys

#: Audit events that open, resolve or address a network endpoint. `socket.__new__` alone
#: would stop every route that needs a socket; the rest are refused too so that a refusal
#: names the operation that was attempted, and so that a library raising a resolver event
#: before creating anything is stopped at that event.
EGRESS_EVENTS = frozenset(
    {
        "socket.__new__",
        "socket.bind",
        "socket.connect",
        "socket.getaddrinfo",
        "socket.gethostbyaddr",
        "socket.gethostbyname",
        "socket.getnameinfo",
        "socket.sendmsg",
        "socket.sendto",
        "urllib.Request",
        "http.client.connect",
        "ftplib.connect",
        "imaplib.open",
        "nntplib.connect",
        "poplib.connect",
        "smtplib.connect",
        "webbrowser.open",
    }
)


class EgressRefused(PermissionError):
    """Raised by the guard. Its own type, so a bar can tell the guard's refusal from the OS's."""


def _refuse(event: str, args: tuple[object, ...]) -> None:
    if event in EGRESS_EVENTS:
        raise EgressRefused(
            f"audit event {event!r} refused: tests never touch the network, and this guard "
            "backs the static egress ban at run time (tests/egress_guard.py)"
        )


_installed = False


def install() -> None:
    """Add the hook to this interpreter, once. Idempotent within a process."""
    global _installed
    if not _installed:
        sys.addaudithook(_refuse)
        _installed = True


def installed() -> bool:
    return _installed
