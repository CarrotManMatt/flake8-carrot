
""""""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "CarrotPlugin",
    "RuleCAR101",
    "RuleCAR102",
    "RuleCAR103",
    "RuleCAR104",
    "RuleCAR105",
    "RuleCAR106",
    "RuleCAR107",
    "RuleCAR201",
)


from typing import override

from classproperties import classproperty

from flake8_carrot.utils import BasePlugin, BaseRule

from .CAR101 import RuleCAR101
from .CAR102 import RuleCAR102
from .CAR103 import RuleCAR103
from .CAR104 import RuleCAR104
from .CAR105 import RuleCAR105
from .CAR106 import RuleCAR106
from .CAR107 import RuleCAR107
from .CAR201 import RuleCAR201


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
        return frozenset(
            {
                RuleCAR101,
                RuleCAR102,
                RuleCAR103,
                RuleCAR104,
                RuleCAR105,
                RuleCAR106,
                RuleCAR107,
                RuleCAR201,
            },
        )
