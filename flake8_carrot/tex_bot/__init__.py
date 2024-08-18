""""""

from collections.abc import Sequence

__all__: Sequence[str] = ("TeXBotPlugin",)


from typing import override

from classproperties import classproperty

from flake8_carrot.utils import BasePlugin, BaseRule


class TeXBotPlugin(BasePlugin):
    """"""

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @override
    def name(cls) -> str:  # noqa: N805
        return cls._name(__name__)

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @override
    def RULES(cls) -> frozenset[type[BaseRule["TeXBotPlugin"]]]:  # noqa: N805
        return frozenset()
