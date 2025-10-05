""""""

from typing import TYPE_CHECKING, override

from typed_classproperties import classproperty

from flake8_carrot.utils import BasePlugin, TeXBotRule

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__: "Sequence[str]" = ("TeXBotPlugin", "TeXBotRule")


class TeXBotPlugin(BasePlugin):
    """"""

    @classproperty
    @override
    def RULES(cls) -> frozenset[type[TeXBotRule]]:  # type: ignore[override]
        return frozenset()
