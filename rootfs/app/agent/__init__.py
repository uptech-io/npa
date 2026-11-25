import asyncio
import sys

from ._app import restore, run


def main() -> None:
    """
    Run the agent until it is told to stop.

    With the argument ``restore`` it only undoes a change of host files
    that an earlier run left unconfirmed. Any other argument is an error.
    """

    if sys.argv[1:] == ["restore"]:
        restore()
    elif sys.argv[1:]:
        sys.exit("usage: agent [restore]")
    else:
        asyncio.run(run())
