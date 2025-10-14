"""Linting rules under the "TXB" category."""

from typing import TYPE_CHECKING, override

from typed_classproperties import classproperty

from flake8_carrot.utils import BasePlugin, TeXBotRule

if TYPE_CHECKING:
    from collections.abc import Collection, Sequence

__all__: Sequence[str] = ("TeXBotPlugin", "TeXBotRule")


class TeXBotPlugin(BasePlugin):
    """Plugin class holding all "TXB" rules to be run on some code provided by Flake8."""

    @classproperty
    @override
    def RULES(cls) -> Collection[type[TeXBotRule]]:
        return frozenset()
