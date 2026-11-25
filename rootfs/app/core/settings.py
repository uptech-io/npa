from typing import Annotated, ClassVar

from pathlib import Path

from pydantic import AnyUrl, UrlConstraints, BaseModel, IPvAnyAddress, RedisDsn
from pydantic_settings import BaseSettings

from annotated_types import MinLen

from .contracts import SingletonMeta

# ------------------------------------------------------------------------------
PostgresDsn = Annotated[
    AnyUrl,
    UrlConstraints(
        host_required=True,
        allowed_schemes=[
            "postgresql+asyncpg",
            "postgresql+psycopg",
        ],
    ),
]


class GateSettings(
    BaseModel,
    frozen=True,
    validate_default=True,
):
    resolvers: Annotated[
        tuple[IPvAnyAddress, ...],
        MinLen(1),
    ] = ("1.1.1.1", "8.8.8.8")
# ------------------------------------------------------------------------------


class settings(
    BaseSettings,
    frozen=True,
    case_sensitive=False,
    validate_default=True,
    nested_model_default_partial_update=True,
    env_file=".env",
    env_nested_delimiter="__",
    metaclass=SingletonMeta | type(BaseSettings),
):
    data_dir: ClassVar[Path] = Path("/data")

    nginx_pid_file: ClassVar[Path] = Path("/run/nginx/nginx.pid")

    certs_passphrase_file: ClassVar[Path] = Path(
        "/run/secrets/certs_passphrase",
    )

    debug: bool = False

    pg_url: PostgresDsn = "postgresql+asyncpg://dev:dev@127.0.0.1:5432/dev"
    redis_url: RedisDsn = "redis://127.0.0.1:6379/0"

    gate: GateSettings = GateSettings()
