""""""

from collections.abc import Sequence
from typing import Final

__all__: Final[Sequence[str]] = ("TestRuleCAR001",)

from collections.abc import Set

import pytest

from flake8_carrot import CarrotPlugin
from tests._testing_utils import apply_plugin_to_ast


def _apply_carrot_plugin_to_ast(raw_testing_ast: str) -> Set[str]:
    """"""
    return apply_plugin_to_ast(raw_testing_ast, CarrotPlugin)


class TestRuleCAR001:
    """"""

    @classmethod
    def _get_message(cls, line_number: int, column_number: int) -> str:
        return (
            f"{line_number}:{column_number} CAR001 "
            "Missing `__all__` export at the top of the module"
        )

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        ("RAW_TEST_AST", "EXPECTED_ERROR_POSITION"),
        (
            ("", (1, 1)),
            (" ", (1, 1)),
            ("\n", (1, 1)),
            ("class Foo:\n    pass", (1, 1)),
            ("\nclass Foo:\n    pass", (1, 1)),
            ("class Foo:\n    pass\n", (1, 1)),
            ("\"\"\"This is a docstring.\"\"\"", (1, 27)),
            ("\"\"\"This is a docstring.\"\"\"\n", (2, 1)),
            *(
                (
                    f"\"\"\"This is a docstring.\"\"\"\n{"\n" * count}",
                    (3, 1),
                ) for count in range(1, 5)
            ),
            ("\"\"\"\nThis is a docstring.\nwow!\n\"\"\"", (4, 4)),
            ("\"\"\"\nThis is a docstring.\nwow!\n\"\"\"\n", (5, 1)),
            *(
                (
                    f"\"\"\"\nThis is a docstring.\nwow!\n\"\"\"\n{"\n" * count}",
                    (6, 1),
                ) for count in range(1, 5)
            ),
            *(
                (
                    f"\"\"\"This is a docstring.\"\"\"{"\n" * count}x=3\n",
                    (2, 1),
                ) for count in range(1, 4)
            ),
            *(
                (
                    f"\"\"\"This is a docstring.\"\"\"\n\n\n{"\n" * count}x=3\n",
                    (3, 1),
                ) for count in range(1, 4)
            ),
            *(
                (
                    f"\"\"\"\nThis is a docstring.\nwow!\n\"\"\"{"\n" * count}x=3\n",
                    (5, 1),
                ) for count in range(1, 4)
            ),
            *(
                (
                    f"\"\"\"\nThis is a docstring.\nwow!\n\"\"\"\n\n\n{"\n" * count}x=3\n",
                    (6, 1),
                ) for count in range(1, 4)
            ),
            (
                "\"\"\"This is a docstring.\"\"\"\n\nfrom collections.abc import Sequence",
                (3, 37),
            ),
            (
                "\"\"\"This is a docstring.\"\"\"\n\nfrom collections.abc import Sequence\n",
                (4, 1),
            ),
            *(
                (
                    f"\"\"\"This is a docstring.\"\"\"\n\nfrom collections.abc import Sequence\n{"\n" * count}",  # noqa: E501
                    (5, 1),
                ) for count in range(1, 5)
            ),
            (
                "\"\"\"\nThis is a docstring.\nwow!\n\"\"\"\n\nfrom collections.abc import Sequence",  # noqa: E501
                (6, 37),
            ),
            *(
                (
                    f"\"\"\"\nThis is a docstring.\nwow!\n\"\"\"\n\nfrom collections.abc import Sequence\n{"\n" * count}",  # noqa: E501
                    (8, 1),
                ) for count in range(1, 5)
            ),
            *(
                (
                    f"\"\"\"This is a docstring.\"\"\"\n\nfrom collections.abc import Sequence{"\n" * count}x=3\n",  # noqa: E501
                    (4, 1),
                ) for count in range(1, 4)
            ),
            *(
                (
                    f"\"\"\"This is a docstring.\"\"\"\n\nfrom collections.abc import Sequence\n\n\n{"\n" * count}x=3\n",  # noqa: E501
                    (5, 1),
                ) for count in range(1, 4)
            ),
            *(
                (
                    f"\"\"\"\nThis is a docstring.\nwow!\n\"\"\"\n\nfrom collections.abc import Sequence{"\n" * count}x=3\n",  # noqa: E501
                    (7, 1),
                ) for count in range(1, 4)
            ),
            *(
                (
                    f"\"\"\"\nThis is a docstring.\nwow!\n\"\"\"\n\nfrom collections.abc import Sequence\n\n\n{"\n" * count}x=3\n",  # noqa: E501
                    (8, 1),
                ) for count in range(1, 3)
            ),
        ),
    )
    def test_missing_all_export(self, RAW_TEST_AST: str, EXPECTED_ERROR_POSITION: tuple[int, int]) -> None:  # noqa: N803, E501
        """"""
        assert self._get_message(*EXPECTED_ERROR_POSITION) in _apply_carrot_plugin_to_ast(
            RAW_TEST_AST,
        )

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        "RAW_TEST_AST",
        (
            "__all__ = ()",
            "\"\"\"This is a docstring.\"\"\"\n__all__ = ()\n",
            (
                "\"\"\"This is a docstring.\"\"\"\n"
                "from collections.abc import Sequence\n__all__: Sequence[str] = ()\n"
            ),
            "from collections.abc import Sequence\nx=3\n__all__: Sequence[str] = (\"x\",)\n",
        ),
    )
    def test_successful_all_export_provided(self, RAW_TEST_AST: str) -> None:  # noqa: N803
        """"""
        assert _apply_carrot_plugin_to_ast(RAW_TEST_AST) == set()
