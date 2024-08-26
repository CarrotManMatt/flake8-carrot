""""""

from collections.abc import Sequence

__all__: Sequence[str] = ("TeXBotPlugin",)


from typing import override

from classproperties import classproperty

from flake8_carrot.utils import BasePlugin, TeXBotRule


class TeXBotPlugin(BasePlugin):
    """"""

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @override
    def RULES(cls) -> frozenset[type[TeXBotRule]]:  # type: ignore[override] # noqa: N805
        return frozenset()
