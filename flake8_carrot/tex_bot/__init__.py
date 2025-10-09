""""""

from typing import TYPE_CHECKING, override

from typed_classproperties import classproperty

from flake8_carrot.utils import BasePlugin, TeXBotRule

if TYPE_CHECKING:
    from collections.abc import Collection, Sequence

__all__: Sequence[str] = ("TeXBotPlugin", "TeXBotRule")


class TeXBotPlugin(BasePlugin):
    """"""

    @classproperty
    @override
    def RULES(cls) -> Collection[type[TeXBotRule]]:
        return frozenset()
