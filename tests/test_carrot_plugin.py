""""""

from collections.abc import Sequence

__all__: Sequence[str] = ("TestRuleCAR001",)


import abc
import itertools
import re
from collections.abc import Set as AbstractSet

import pytest

from flake8_carrot import CarrotPlugin
from flake8_carrot.utils import CarrotRule
from tests._testing_utils import apply_plugin_to_ast


class BaseTestCarrotPlugin(abc.ABC):  # noqa: B024
    @classmethod
    def _apply_carrot_plugin_to_ast(cls, raw_testing_ast: str) -> AbstractSet[str]:
        """"""
        return apply_plugin_to_ast(raw_testing_ast, CarrotPlugin)


class TestRuleMessages(BaseTestCarrotPlugin):
    """"""

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        "RULE_CLASS",
        CarrotPlugin.RULES,
    )
    def test_message_never_ends_with_full_stop(self, RULE_CLASS: type[CarrotRule]) -> None:  # noqa: N803
        """"""
        assert not RULE_CLASS.format_error_message(ctx={}).endswith(".")

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        "RULE_CLASS",
        CarrotPlugin.RULES,
    )
    def test_no_double_zero_in_rule_code(self, RULE_CLASS: type[CarrotRule]) -> None:  # noqa: N803
        """"""
        assert "00" not in RULE_CLASS.__name__

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        "RULE_CLASS",
        CarrotPlugin.RULES,
    )
    def test_all_rule_classes_named_with_rule_code(self, RULE_CLASS: type[CarrotRule]) -> None:  # noqa: N803
        """"""
        assert re.fullmatch(r"\ARuleCAR[0-9]{1,3}\Z", RULE_CLASS.__name__)

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        "RULE_CLASS",
        CarrotPlugin.RULES,
    )
    def test_correct_rule_code_in_error_message(self, RULE_CLASS: type[CarrotRule]) -> None:  # noqa: N803
        """"""
        rule_number_match: re.Match[str] | None = re.fullmatch(
            r"\A(?:Rule)?CAR([0-9]{1,3})\Z",
            RULE_CLASS.__name__,
            re.IGNORECASE,
        )

        assert re.fullmatch(
            fr"\ACAR{
                rule_number_match.group(1) if rule_number_match is not None else r"[0-9]{1,3}"
            } .+\Z",
            RULE_CLASS.format_error_message(ctx={}),
        )

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        "RULE_CLASS",
        CarrotPlugin.RULES,
    )
    def test_no_double_rule_code_in_error_message(self, RULE_CLASS: type[CarrotRule]) -> None:  # noqa: N803
        """"""
        assert not re.fullmatch(
            r"\A\s*CAR\s*[0-9]{1,4}.*\Z",
            RULE_CLASS._format_error_message(ctx={}),  # noqa: SLF001
        )
        assert not re.fullmatch(
            r"\A\s*CAR\s*[0-9]{1,4}\s*CAR\s*[0-9]{1,4}.*\Z",
            RULE_CLASS.format_error_message(ctx={}),
        )


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


class TestRuleCAR101(BaseTestCarrotPlugin):
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
            "CAR101" not in problem
            for problem in self._apply_carrot_plugin_to_ast(RAW_TEST_AST)
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
                        f"{"\n" * count_pre}"
                        f"\"\"\"This is a docstring.\"\"\"{"\n" * count_post}"
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
                        f"{"\n" * count_pre}"
                        f"\"\"\"This is a docstring.\"\"\"{"\n" * count_post1}"
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
                        f"{"\n" * count_pre}"
                        f"\"\"\"This is a docstring.\"\"\"{"\n" * count_post1}"
                        f"from collections.abc import Sequence{"\n" * count_post2}"
                        "__all__: Sequence[str] = ()\n"
                    ),
                    (3 + count_pre + count_post1, 1),  # NOTE: Test that always second newline is flagged when > 1 newlines (second break) and newlines above
                )
                for count_post1 in range(1, 6)
                for count_pre in range(0, 4)
                for count_post2 in range(3, 6)
                if count_post1 != 2
            ),
        ),
    )
    def test_no_multiple_newlines_between_preamble(self, RAW_TEST_AST: str, EXPECTED_ERROR_POSITION: tuple[int, int]) -> None:  # noqa: N803, E501
        assert (
            self._get_message(*EXPECTED_ERROR_POSITION) in self._apply_carrot_plugin_to_ast(
                RAW_TEST_AST,
            )
        )


class TestRuleCAR112(BaseTestCarrotPlugin):
    """"""

    @classmethod
    def _get_message(cls, line_number: int, column_number: int, definition_type: str) -> str:
        return (
            f"{line_number}:{column_number} CAR112 "
            f"{definition_type} definition should not spread over multiple lines"
        )

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        "RAW_TEST_AST",
        (
            "def foo(bar: str) -> None: ...",
            "def foo() -> None: ...",
            "def foo(): ...",
            "def foo[T](): ...",
            "def foo[T]() -> T: ...",
            "def foo[T](bar: str) -> T: ...",
            "def foo[T](bar: str): ...",
            "def foo[T](bar: str): pass",
            "def foo[T](): pass",
            "def foo(bar: str): ...",
            "async def foo(bar: str) -> None: ...",
            "async def foo() -> None: ...",
            "async def foo(): ...",
            "def foo(bar: str) -> None: ...\n",
            "@dec\ndef foo(bar: str) -> None: ...\n",
            "def foo(bar: str) -> None: pass\n",
            "@dec\ndef foo(bar: str) -> None: pass\n",
            "async def foo(bar: str) -> None: pass\n",
            "@dec\nasync def foo(bar: str) -> None: pass\n",
            "def foo(bar: str) -> str: ...\n",
            "async def foo(bar: str) -> str: ...\n",
            "def foo(bar: str) -> str: pass\n",
            "def foo() -> str: pass\n",
            "def foo(): pass\n",
            "def foo(bar: str): pass\n",
            "async def foo(bar: str) -> str: pass\n",
            "class Foo:\n    def foo(self, bar: str) -> None: ...\n",
            "class Foo:\n    async def foo(self, bar: str) -> None: ...\n",
            "class Foo:\n    @abc.abstractmethod\n    def foo(self, bar: str) -> None: ...\n",
            (
                "class Foo(abc.ABC):\n"
                "    @abc.abstractmethod\n"
                "    def foo(self, bar: str) -> None: ...\n"
            ),
            (
                "class Foo(abc.ABC):\n"
                "    @abc.abstractmethod\n"
                "    async def foo(self, bar: str) -> None: ...\n"
            ),
            "class Foo(Protocol):\n    def foo(self, bar: str) -> None: ...\n",
            "class Foo(Protocol):\n    async def foo(self, bar: str) -> None: ...\n",
            "class Foo(Protocol):\n    def foo(self, bar: str) -> None: pass\n",
            "class Foo(Protocol):\n    async def foo(self, bar: str) -> None: pass\n",
            "class Foo:\n    @abc.abstractmethod\n    def foo(self, bar: str) -> None: pass\n",
            (
                "class Foo:\n"
                "    @abc.abstractmethod\n"
                "    async def foo(self, bar: str) -> None: pass\n"
            ),
            (
                "class Foo(abc.ABC):\n"
                "    @abc.abstractmethod\n"
                "    def foo(self, bar: str) -> None: pass"
            ),
            (
                "class Foo(abc.ABC):\n"
                "    @abc.abstractmethod\n"
                "    async def foo(self, bar: str) -> None: pass"
            ),
            (
                "class Foo(abc.ABC):\n"
                "    @abc.abstractmethod\n"
                "    def foo(self, bar: str) -> None:\n"
                "        \"\"\"A test docstring.\"\"\""
            ),
            (
                "class Foo(abc.ABC):\n"
                "    @abc.abstractmethod\n"
                "    async def foo(self, bar: str) -> None:\n"
                "        \"\"\"A test docstring.\"\"\""
            ),
            "class Foo: ...",
            "class Foo: ...\n",
            "class Foo: pass",
            "while True: ...",
            "while True: pass",
            "for count in range(10): ...",
            "async for count in range(10): ...",
            "for count in range(10): pass",
            "async for count in range(10): pass",
            "if True: ...",
            "if True: pass",
        ),
    )
    def test_allow_body_and_heading_on_single_line(self, RAW_TEST_AST: str) -> None:  # noqa: N803
        assert not any(
            "CAR112" in error.upper()
            for error in self._apply_carrot_plugin_to_ast(RAW_TEST_AST)
        )

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        "RAW_TEST_AST",
        (
            (
                    "class Foo:\n"
                    "    def foo(self, bar: str) -> str:\n"
                    "\n"
                    "        return f\"A Test {bar}.\""
            ),
            (
                    "class Foo:\n"
                    "    async def foo(self, bar: str) -> str:\n"
                    "\n"
                    "        return f\"A Test {bar}.\""
            ),
            "def foo(bar: str) -> str:\n\n    return f\"A Test {bar}.\"",
            "async def foo(bar: str) -> str:\n\n    return f\"A Test {bar}.\"",
            "def foo() -> str:\n\n    return \"A Test Message.\"",
            "def foo() -> None:\n\n    print(\"A Test Message.\")",
            "async def foo() -> None:\n\n    print(\"A Test Message.\")",
            "for count in range(10):\n\n    print(f\"Test Message {count}.\")",
            "async for count in range(10):\n\n    print(f\"Test Message {count}.\")",
            "for count in range(10):\n\n    print(f\"Test Message {count}.\")\n",
            "async for count in range(10):\n\n    print(f\"Test Message {count}.\")\n",
            "while True:\n\n    print(f\"A Test Message.\")\n",
            "if True:\n\n    print(f\"A Test Message.\")\n",
            (
                "def foo() -> None:\n"
                "    \"\"\"A docstring.\"\"\"\n"
                "\n"
                "    print(\"A Test Message.\")"
            ),
            (
                "async def foo() -> None:\n"
                "    \"\"\"A docstring.\"\"\"\n"
                "\n"
                "    print(\"A Test Message.\")"
            ),
            (
                "def foo() -> None:\n"
                "\n"
                "    \"\"\"A docstring.\"\"\"\n"
                "    print(\"A Test Message.\")"
            ),
            (
                "async def foo() -> None:\n"
                "\n"
                "    \"\"\"A docstring.\"\"\"\n"
                "    print(\"A Test Message.\")"
            ),
        ),
    )
    def test_allow_gap_between_body_and_single_line_heading(self, RAW_TEST_AST: str) -> None:  # noqa: N803
        assert not any(
            "CAR112" in error.upper()
            for error in self._apply_carrot_plugin_to_ast(RAW_TEST_AST)
        )

    # noinspection PyPep8Naming
    @pytest.mark.parametrize(
        ("RAW_TEST_AST", "EXPECTED_ERROR_POSITION", "DEFINITION_TYPE"),
        (
            ("for count in range(\n    10): ...", (2, 5), "for"),
            ("for count in range(\n    10,\n): ...", (2, 5), "for"),
            ("async for count in range(\n    10,\n): ...", (2, 5), "for"),
            ("def foo(\n    bar: str,\n): ...", (2, 5), "function"),
            ("def foo(\n    bar: str,\n):\n    ...", (2, 5), "function"),
            ("async def foo(\n    bar: str,\n): ...", (2, 5), "function"),
            ("async def foo(\n    bar: str,\n) -> None: ...", (2, 5), "function"),
            ("def foo(\n    bar: str,\n) -> None: pass", (2, 5), "function"),
            ("def foo(\n    bar: str,\n) -> None:\n    pass", (2, 5), "function"),
            ("def foo(\n    bar: str) -> None: pass", (2, 5), "function"),
            ("def foo(\n    bar: str,\n): pass", (2, 5), "function"),
            ("def foo(\n    bar: str): pass", (2, 5), "function"),
            ("def foo(\n    bar: str):\n    pass", (2, 5), "function"),
            ("async def foo(\n    bar: str,\n) -> None: pass", (2, 5), "function"),
            ("def foo[\n    T,\n]() -> None: pass", (2, 5), "function"),
            ("def foo[\n    T,\n](): pass", (2, 5), "function"),
            ("def foo[\n    T, **P\n]() -> None: pass", (2, 5), "function"),
            ("async def foo[\n    T, **P\n](): pass", (2, 5), "function"),
            ("def foo[\n    T, **P,\n]() -> None: pass", (2, 5), "function"),
            ("def foo[\n    T, **P,\n]() -> None:\n    pass", (2, 5), "function"),
            ("async def foo[\n    T, **P]() -> None: pass", (2, 5), "function"),
            ("def foo[T,\n    **P]() -> None: pass", (2, 5), "function"),
            ("def foo[T,\n    **P]() -> None:\n    ...", (2, 5), "function"),
            ("async def foo() -> (\n    None\n): pass", (2, 5), "function"),
            ("async def foo() -> (\n    None): pass", (2, 5), "function"),
            ("def foo() -> (\n    None):\n    ...", (2, 5), "function"),
            ("def foo() -> (\n):\n    pass", (2, 1), "function"),
            ("def foo() -> (\n): pass", (2, 1), "function"),
            ("def foo() -> (\n    ):\n    pass", (2, 5), "function"),  # TODO: Add tests for classes, method functions, while-loops & if-statements
        ),
    )
    def test_multilines(self, RAW_TEST_AST: str, EXPECTED_ERROR_POSITION: tuple[int, int], DEFINITION_TYPE: str) -> None:  # noqa: N803, E501
        assert any(
            (
                error_message.startswith(
                    f"{EXPECTED_ERROR_POSITION[0]}:{EXPECTED_ERROR_POSITION[1]} CAR112",
                )
                and DEFINITION_TYPE in error_message.lower()
                and error_message.endswith("definition should not spread over multiple lines")
            )
            for error_message in self._apply_carrot_plugin_to_ast(RAW_TEST_AST)
        )
