
""""""

from collections.abc import Sequence

__all__: Sequence[str] = ("CarrotPlugin", "RuleCAR001")


from typing import override

from classproperties import classproperty

from flake8_carrot.utils import BasePlugin, BaseRule

from .CAR001 import RuleCAR001
from .CAR002 import RuleCAR002
from .CAR003 import RuleCAR003


class CarrotPlugin(BasePlugin):
    """"""

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @override
    def name(cls) -> str:  # noqa: N805
        return cls._name(__name__)

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @override
    def RULES(cls) -> frozenset[type[BaseRule]]:  # noqa: N805
        return frozenset({RuleCAR001, RuleCAR002, RuleCAR003})
