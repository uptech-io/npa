from functools import cache

from hashlib import md5
from pathlib import Path


@cache
def fingerprint(on_hash: bool = False) -> str:
    """
    Returns a node identifier.

    Args:
        on_hash (bool): If True, returns the MD5 hash.

    Returns:
        str: The hostname or its MD5 hex digest.
    """

    hostname = Path("/etc/hostname").read_bytes().strip()

    if on_hash:
        return md5(hostname).hexdigest()

    return hostname.decode()
