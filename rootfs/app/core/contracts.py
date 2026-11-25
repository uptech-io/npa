from typing import Any, Self

from functools import cache
from threading import RLock


class MetaComposer(type):

    @cache
    def __or__(cls, other: type) -> type:
        """
        Combines two metaclasses with ``|``.

        Allows ``metaclass=SingletonMeta | type(Class)``, where a class
        needs both its base's metaclass and the singleton one.
        """
        if not isinstance(other, type) or not issubclass(other, type):
            return NotImplemented

        if issubclass(cls, other):
            return cls

        if issubclass(other, cls):
            return other

        return type(
            f"{cls.__name__}_{other.__name__}",
            (cls, other),
            {},
        )


class SingletonMeta(
    type,
    metaclass=MetaComposer
):
    _instances = {}
    _lock = RLock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Self:
        """
        Returns the single instance of ``cls``, creating it on the first call.

        Args:
            *args (Any): Positional arguments for the first instantiation.
            **kwargs (Any): Keyword arguments for the first instantiation.

        Returns:
            Self: The instance shared by every call on ``cls``.
        """
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(
                        *args, **kwargs)

        return cls._instances[cls]

    def reset(cls) -> None:
        """Forget the instance of ``cls`` so the next call builds a new one."""
        with cls._lock:
            cls._instances.pop(cls, None)
