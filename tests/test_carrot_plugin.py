""""""

from collections.abc import Sequence

__all__: Sequence[str] = ("TestTrivialCases",)

from collections.abc import Set

from flake8_carrot import CarrotPlugin
from tests._testing_utils import apply_plugin_to_ast


def _apply_carrot_plugin_to_ast(raw_testing_ast: str) -> Set[str]:
    """"""
    return apply_plugin_to_ast(raw_testing_ast, CarrotPlugin)


class TestTrivialCases:
    """"""

    def test_empty_case(self) -> None:
        assert _apply_carrot_plugin_to_ast("") == set()
