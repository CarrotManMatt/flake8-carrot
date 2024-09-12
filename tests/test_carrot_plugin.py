""""""

from collections.abc import Sequence

__all__: Sequence[str] = ("TestRuleCAR001",)


import abc
import itertools
from collections.abc import Set as AbstractSet
from typing import TYPE_CHECKING

import pytest

from flake8_carrot import CarrotPlugin
from tests._testing_utils import apply_plugin_to_ast

if TYPE_CHECKING:
    from flake8_carrot.utils import CarrotRule


class BaseTestCarrotPlugin(abc.ABC):
    @classmethod
    def _apply_carrot_plugin_to_ast(cls, raw_testing_ast: str) -> AbstractSet[str]:
        """"""
        return apply_plugin_to_ast(raw_testing_ast, CarrotPlugin)


class TestRuleMessages(BaseTestCarrotPlugin):
    """"""

    def test_message_never_ends_with_full_stop_without_ctx(self) -> None:
        """"""
        RuleClass: type[CarrotRule]
        for RuleClass in CarrotPlugin.RULES:
            assert not RuleClass.format_error_message(ctx={}).endswith(".")


class TestRuleCAR001(BaseTestCarrotPlugin):
    """"""

    @classmethod
    def _get_message(cls, line_number: int, column_number: int) -> str:
        return (
            f"{line_number}:{column_number} CAR101 "
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
        assert self._get_message(*EXPECTED_ERROR_POSITION) in self._apply_carrot_plugin_to_ast(
            RAW_TEST_AST,
        )


class TestRuleCar101(BaseTestCarrotPlugin):
    """"""

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
        assert all(
            "CAR101" not in problem for problem in self._apply_carrot_plugin_to_ast(RAW_TEST_AST)
        )


class TestRuleCAR111(BaseTestCarrotPlugin):
    """"""

    @classmethod
    def _get_message(cls, line_number: int, column_number: int) -> str:
        return (
            f"{line_number}:{column_number} CAR111 "
            "Preamble lines (imports, `__all__` declaration, module docstring, etc.) "
            "should be seperated by a single newline"
        )

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        "RAW_TEST_AST",
        (
            "",
            "  ",
            *("\n" * count for count in range(1, 6)),
            "  \n",
            (
                "#! /usr/bin/env python3\n"
                "\"\"\"This is a docstring.\"\"\"\n\n"
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = ()\n\n"
                "print(\"hello\")\n"
            ),
            (
                "#! /usr/bin/env python3\n\n"
                "\"\"\"This is a docstring.\"\"\"\n\n"
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = ()\n\n"
                "print(\"hello\")\n"
            ),
            (
                "\"\"\"This is a docstring.\"\"\"\n\n"
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = ()\n\n"
                "print(\"hello\")\n"
            ),
            (
                "\"\"\"This is a docstring.\"\"\"\n\n"
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = (\"foo\",)\n\n"
                "def foo():\n    "
                "print(\"hello\")\n"
            ),
            (
                "\n"
                "\"\"\"This is a docstring.\"\"\"\n\n"
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = (\"foo\",)\n\n"
                "def foo():\n    "
                "print(\"hello\")\n"
            ),
            (
                "\n\n"
                "\"\"\"This is a docstring.\"\"\"\n\n"
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = (\"foo\",)\n\n"
                "def foo():\n    "
                "print(\"hello\")\n"
            ),
            (
                "\"\"\"This is a docstring.\"\"\"\n\n"
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = (\"foo\",)\n\n"
                "import random\n\n"
                "def foo():\n    "
                "print(f\"hello {random.random()}\")\n"
            ),
            (
                "\n"
                "\"\"\"This is a docstring.\"\"\"\n\n"
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = (\"foo\",)\n\n"
                "import random\n\n"
                "def foo():\n    "
                "print(f\"hello {random.random()}\")\n"
            ),
            (
                "\"\"\"This is a docstring.\"\"\"\n\n"
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = (\"foo\",)\n\n"
                "import random\n"
            ),
            (
                "\"\"\"This is a docstring.\"\"\"\n\n"
                "import random\n"
            ),
            (
                "\n\"\"\"This is a docstring.\"\"\"\n\n"
                "import random\n"
            ),
            *(
                f"{"\n" * count_pre}\"\"\"This is a docstring.\"\"\"{"\n" * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            *(
                f"{"\n" * count_pre}from collections.abc import Sequence{"\n" * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            *(
                f"{"\n" * count_pre}__all__: Sequence[str] = (){"\n" * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            *(
                f"{"\n" * count_pre}__all__ = (){"\n" * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            *(
                f"{"\n" * count_pre}x = 5{"\n" * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            *(
                f"{"\n" * count_pre}import random{"\n" * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            "import random\nx = random.random()\n",
            "import random\nx = random.random()\n\nx = 5\n",
            (
                "\"\"\"This is a docstring.\"\"\"\n"
                "x = 4\n\n\n"
                "y = 5\n"
            ),
        ),
    )
    def test_successful_single_newline_between_preamble(self, RAW_TEST_AST: str) -> None:  # noqa: N803
        """"""
        problems: AbstractSet[str] = self._apply_carrot_plugin_to_ast(RAW_TEST_AST)
        assert not problems or any("CAR111" not in problem for problem in problems)

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        ("RAW_TEST_AST", "EXPECTED_ERROR_POSITION"),
        (
            *(
                (
                    (
                        f"{"\n" * count}{line1}\n"
                        f"{line2}\n"
                    ),
                    (2 + count, 1),  # NOTE: Test for missing single newline (first break)
                )
                for line1, line2 in itertools.combinations(
                    (
                        "\"\"\"This is a docstring.\"\"\"",
                        "from collections.abc import Sequence",
                        "__all__ = ()",
                    ),
                    2,
                )
                for count in range(0, 4)
            ),
            *(
                (
                    (
                        f"{"\n" * count_pre}\"\"\"This is a docstring.\"\"\"{"\n" * count_post}"
                        "from collections.abc import Sequence\n"
                    ),
                    (3 + count_pre, 1),  # NOTE: Test that always second newline is flagged when > 1 newlines (first break)
                )
                for count_post in range(3, 6)
                for count_pre in range(0, 4)
            ),
            *(
                (
                    (
                        f"{"\n" * count_pre}\"\"\"This is a docstring.\"\"\"{"\n" * count_post1}"
                        f"from collections.abc import Sequence{"\n" * count_post2}"
                        "__all__: Sequence[str] = ()\n"
                    ),
                    (3 + count_pre, 1),  # NOTE: Test that always second newline is flagged when > 1 newlines (first break) and incorrect newlines below
                )
                for count_post1 in range(3, 6)
                for count_pre in range(0, 4)
                for count_post2 in range(1, 6)
                if count_post2 != 2
            ),
            *(
                (
                    (
                        f"{"\n" * count}\"\"\"This is a docstring.\"\"\"\n\n"
                        "from collections.abc import Sequence\n"
                        "__all__: Sequence[str] = ()\n"
                    ),
                    (4 + count, 1),  # NOTE: Test for missing single newline (second break)
                )
                for count in range(0, 4)
            ),
            *(
                (
                    (
                        f"{"\n" * count_pre}\"\"\"This is a docstring.\"\"\"\n\n"
                        f"from collections.abc import Sequence{"\n" * count_post}"
                        "__all__: Sequence[str] = ()\n"
                    ),
                    (5 + count_pre, 1),  # NOTE: Test that always second newline is flagged when > 1 newlines (second break)
                )
                for count_pre in range(0, 4)
                for count_post in range(3, 6)
            ),
            *(
                (
                    (
                        f"{"\n" * count_pre}\"\"\"This is a docstring.\"\"\"{"\n" * count_post1}"
                        f"from collections.abc import Sequence{"\n" * count_post2}"
                        "__all__: Sequence[str] = ()\n"
                    ),
                    (3 + count_pre + count_post1, 1),  # NOTE: Test that always second newline is flagged when > 1 newlines (second break) and newlines above
                )
                for count_post1 in range(1, 6)
                for count_pre in range(0, 4)
                for count_post2 in range(3, 6)
                if count_post1 != 2
            )
        ),
    )
    def test_no_multiple_newlines_between_preamble(self, RAW_TEST_AST: str, EXPECTED_ERROR_POSITION: tuple[int, int]) -> None:  # noqa: N803, E501
        assert (
            self._get_message(*EXPECTED_ERROR_POSITION) in self._apply_carrot_plugin_to_ast(
                RAW_TEST_AST,
            )
        )
