import asyncio

from typing import Literal
from ipaddress import ip_address


async def ipinfo(
    family: Literal[4, 6] = 6,
    timeout: float = 5.0,
) -> str | None:
    """
    Ask Google's DNS for the public address of this node in one family.

    Args:
        family (Literal[4, 6]): The address family of the query.
        timeout (float): Seconds to wait for ``dig`` before it is killed.

    Returns:
        str | None: The public address, or None when the query gives none.
    """

    r = await asyncio.subprocess.create_subprocess_exec(
        "dig",
        f"-{family}",
        "TXT",
        "+short",
        "+time=2",
        "+tries=2",
        "o-o.myaddr.l.google.com",
        "@ns1.google.com",
        stdout=asyncio.subprocess.PIPE,
    )

    try:
        out, _ = await asyncio.wait_for(r.communicate(), timeout)
    except TimeoutError:
        return None
    finally:
        if r.returncode is None:
            r.kill()
            await r.wait()

    for line in out.decode(errors="replace").splitlines():
        try:
            address = ip_address(line.strip().strip("\""))
        except ValueError:
            continue

        if address.version == family:
            return str(address)

    return None
