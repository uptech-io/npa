import asyncio

from signal import SIGINT, SIGTERM

from core.utils import setup_logging
from core.ext.db import postgres, redis

from .connectors import napi
from .features import discover_builtin

# ------------------------------------------------------------------------------
log = setup_logging().getChild("app")

STOP_TIMEOUT = 8

HANDLED_SIGNALS = (
    SIGINT,
    SIGTERM,
)
# ------------------------------------------------------------------------------


def _ended(task: asyncio.Task[None]) -> None:
    """Log a feature that ended with an error."""

    if task.cancelled():
        return

    if task.exception() is not None:
        log.error(
            "feature %s ended",
            task.get_name(),
            exc_info=task.exception(),
        )


def restore() -> None:
    """Undo a change of host files that an earlier run left unconfirmed."""

    if napi.restore.call():
        log.warning("put back the host files of an unconfirmed change")


async def run() -> None:
    """Run every feature until the agent is told to stop."""

    stop = asyncio.Event()

    for signum in HANDLED_SIGNALS:
        asyncio.get_running_loop().add_signal_handler(signum, stop.set)

    tasks = [
        asyncio.create_task(loop(stop), name=name)
        for name, loop in discover_builtin().items()
    ]

    for task in tasks:
        task.add_done_callback(_ended)

    log.info("started with %d feature(s)", len(tasks))

    await stop.wait()

    log.info("stopping")

    if tasks:
        _, pending = await asyncio.wait(tasks, timeout=STOP_TIMEOUT)

        for task in pending:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    await postgres().aclose()
    await redis().aclose(close_connection_pool=True)

    log.info("stopped")
