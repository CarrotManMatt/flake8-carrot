""""""

from collections.abc import Sequence

__all__: Sequence[str] = ("TeXBotPlugin",)


from collections.abc import Generator
from typing import override

from classproperties import classproperty

from .base import BasePlugin


class TeXBotPlugin(BasePlugin):
    """"""

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @override
    def name(cls) -> str:  # noqa: N805
        return cls._name(__name__)

    @override
    def run(self) -> Generator[tuple[int, int, str, type[BasePlugin]], None, None]:
        yield 1, 0, "TXB100 always error", type(self)
