"""Test suite to check the functionality of all CAR plugin rules."""

import abc
import itertools
import re
from typing import TYPE_CHECKING

import pytest

from flake8_carrot import CarrotPlugin
from flake8_carrot.utils import CarrotRule
from tests._testing_utils import apply_plugin_to_ast

if TYPE_CHECKING:
    from collections.abc import Sequence
    from collections.abc import Set as AbstractSet

    from flake8_carrot.utils import CarrotRule

__all__: Sequence[str] = ("TestRuleCAR001",)


class BaseTestCarrotPlugin(abc.ABC):  # noqa: B024
    @classmethod
    def _apply_carrot_plugin_to_ast(cls, raw_testing_ast: str) -> AbstractSet[str]:
        return apply_plugin_to_ast(raw_testing_ast, CarrotPlugin)


class TestRuleMessages(BaseTestCarrotPlugin):
    """Test suite to ensure all CAR rules have consistent message formatting."""

    @pytest.mark.parametrize("rule_class", CarrotPlugin.RULES)
    def test_message_never_ends_with_full_stop(self, rule_class: type[CarrotRule]) -> None:
        """Ensure each rule message is formatted correctly without a trailing full-stop."""
        assert not rule_class.format_error_message(ctx={}).endswith(".")

    @pytest.mark.parametrize("rule_class", CarrotPlugin.RULES)
    def test_no_double_zero_in_rule_code(self, rule_class: type[CarrotRule]) -> None:
        """Ensure each rule code is indexed correctly without double zeros."""
        assert "00" not in rule_class.__name__

    @pytest.mark.parametrize("rule_class", CarrotPlugin.RULES)
    def test_all_rule_classes_named_with_rule_code(self, rule_class: type[CarrotRule]) -> None:
        """Ensure each message contains some sort of rule code."""
        assert re.fullmatch(r"\ARuleCAR[0-9]{1,3}\Z", rule_class.__name__)

    @pytest.mark.parametrize("rule_class", CarrotPlugin.RULES)
    def test_correct_rule_code_in_error_message(self, rule_class: type[CarrotRule]) -> None:
        """Ensure each message contains the correct corresponding rule code."""
        rule_number_match: re.Match[str] | None = re.fullmatch(
            r"\A(?:Rule)?CAR([0-9]{1,3})\Z", rule_class.__name__, re.IGNORECASE
        )

        assert re.fullmatch(
            (
                rf"\ACAR{
                    rule_number_match.group(1)
                    if rule_number_match is not None
                    else r'[0-9]{1,3}'
                } .+\Z"
            ),
            rule_class.format_error_message(ctx={}),
        )

    @pytest.mark.parametrize("rule_class", CarrotPlugin.RULES)
    def test_no_double_rule_code_in_error_message(self, rule_class: type[CarrotRule]) -> None:
        """Ensure rule messages don't statically contain the rule code (twice)."""
        assert not re.fullmatch(
            r"\A\s*CAR\s*[0-9]{1,4}.*\Z",
            rule_class._format_error_message(ctx={}),  # noqa: SLF001
        )
        assert not re.fullmatch(
            r"\A\s*CAR\s*[0-9]{1,4}\s*CAR\s*[0-9]{1,4}.*\Z",
            rule_class.format_error_message(ctx={}),
        )


class TestRuleCAR001(BaseTestCarrotPlugin):
    """Test suite for rule CAR001."""

    @classmethod
    def _get_message(cls, line_number: int, column_number: int) -> str:
        return (
            f"{line_number}:{column_number} CAR101 "
            "Missing `__all__` export at the top of the module"
        )

    @pytest.mark.parametrize(
        ("raw_test_ast", "expected_error_position"),
        (
            ("", (1, 1)),
            (" ", (1, 1)),
            ("\n", (1, 1)),
            ("class Foo:\n    pass", (1, 1)),
            ("\nclass Foo:\n    pass", (1, 1)),
            ("class Foo:\n    pass\n", (1, 1)),
            ('"""This is a docstring."""', (1, 27)),
            ('"""This is a docstring."""\n', (2, 1)),
            *(
                (f'"""This is a docstring."""\n{"\n" * count}', (3, 1))
                for count in range(1, 5)
            ),
            ('"""\nThis is a docstring.\nwow!\n"""', (4, 4)),
            ('"""\nThis is a docstring.\nwow!\n"""\n', (5, 1)),
            *(
                (f'"""\nThis is a docstring.\nwow!\n"""\n{"\n" * count}', (6, 1))
                for count in range(1, 5)
            ),
            *(
                (f'"""This is a docstring."""{"\n" * count}x=3\n', (2, 1))
                for count in range(1, 4)
            ),
            *(
                (f'"""This is a docstring."""\n\n\n{"\n" * count}x=3\n', (3, 1))
                for count in range(1, 4)
            ),
            *(
                (f'"""\nThis is a docstring.\nwow!\n"""{"\n" * count}x=3\n', (5, 1))
                for count in range(1, 4)
            ),
            *(
                (f'"""\nThis is a docstring.\nwow!\n"""\n\n\n{"\n" * count}x=3\n', (6, 1))
                for count in range(1, 4)
            ),
            ('"""This is a docstring."""\n\nfrom collections.abc import Sequence', (3, 37)),
            ('"""This is a docstring."""\n\nfrom collections.abc import Sequence\n', (4, 1)),
            *(
                (
                    (
                        '"""This is a docstring."""\n\n'
                        f"from collections.abc import Sequence\n{'\n' * count}"
                    ),
                    (5, 1),
                )
                for count in range(1, 5)
            ),
            (
                '"""\nThis is a docstring.\nwow!\n"""\n\nfrom collections.abc import Sequence',
                (6, 37),
            ),
            *(
                (
                    (
                        '"""\nThis is a docstring.\nwow!\n"""\n\n'
                        f"from collections.abc import Sequence\n{'\n' * count}"
                    ),
                    (8, 1),
                )
                for count in range(1, 5)
            ),
            *(
                (
                    (
                        '"""This is a docstring."""\n\n'
                        f"from collections.abc import Sequence{'\n' * count}x=3\n"
                    ),
                    (4, 1),
                )
                for count in range(1, 4)
            ),
            *(
                (
                    (
                        '"""This is a docstring."""\n\n'
                        f"from collections.abc import Sequence\n\n\n{'\n' * count}x=3\n"
                    ),
                    (5, 1),
                )
                for count in range(1, 4)
            ),
            *(
                (
                    (
                        '"""\nThis is a docstring.\nwow!\n"""\n\n'
                        f"from collections.abc import Sequence{'\n' * count}x=3\n"
                    ),
                    (7, 1),
                )
                for count in range(1, 4)
            ),
            *(
                (
                    (
                        '"""\nThis is a docstring.\nwow!\n"""\n\n'
                        f"from collections.abc import Sequence\n\n\n{'\n' * count}x=3\n"
                    ),
                    (8, 1),
                )
                for count in range(1, 3)
            ),
        ),
    )
    def test_missing_all_export(
        self, raw_test_ast: str, expected_error_position: tuple[int, int]
    ) -> None:
        """Ensure rule CAR001 is alerted for modules without __all__ exports."""
        assert self._get_message(*expected_error_position) in self._apply_carrot_plugin_to_ast(
            raw_test_ast
        )


class TestRuleCAR101(BaseTestCarrotPlugin):
    """Test suite for rule CAR101."""

    @pytest.mark.parametrize(
        "raw_test_ast",
        (
            "__all__ = ()",
            '"""This is a docstring."""\n__all__ = ()\n',
            (
                '"""This is a docstring."""\n'
                "from collections.abc import Sequence\n__all__: Sequence[str] = ()\n"
            ),
            'from collections.abc import Sequence\nx=3\n__all__: Sequence[str] = ("x",)\n',
        ),
    )
    def test_successful_all_export_provided(self, raw_test_ast: str) -> None:
        """Ensure rule CAR101 is not alerted for modules with __all__ exports."""
        assert all(
            "CAR101" not in problem
            for problem in self._apply_carrot_plugin_to_ast(raw_test_ast)
        )


class TestRuleCAR111(BaseTestCarrotPlugin):
    """Test suite for rule CAR111."""

    @classmethod
    def _get_message(cls, line_number: int, column_number: int) -> str:
        return (
            f"{line_number}:{column_number} CAR111 "
            "Preamble lines (imports, `__all__` declaration, module docstring, etc.) "
            "should be separated by a single newline"
        )

    @pytest.mark.parametrize(
        "raw_test_ast",
        (
            "",
            "  ",
            *("\n" * count for count in range(1, 6)),
            "  \n",
            (
                "#! /usr/bin/env python3\n"
                '"""This is a docstring."""\n\n'
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = ()\n\n"
                'print("hello")\n'
            ),
            (
                "#! /usr/bin/env python3\n\n"
                '"""This is a docstring."""\n\n'
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = ()\n\n"
                'print("hello")\n'
            ),
            (
                '"""This is a docstring."""\n\n'
                "from collections.abc import Sequence\n\n"
                "__all__: Sequence[str] = ()\n\n"
                'print("hello")\n'
            ),
            (
                '"""This is a docstring."""\n\n'
                "from collections.abc import Sequence\n\n"
                '__all__: Sequence[str] = ("foo",)\n\n'
                "def foo():\n    "
                'print("hello")\n'
            ),
            (
                "\n"
                '"""This is a docstring."""\n\n'
                "from collections.abc import Sequence\n\n"
                '__all__: Sequence[str] = ("foo",)\n\n'
                "def foo():\n    "
                'print("hello")\n'
            ),
            (
                "\n\n"
                '"""This is a docstring."""\n\n'
                "from collections.abc import Sequence\n\n"
                '__all__: Sequence[str] = ("foo",)\n\n'
                "def foo():\n    "
                'print("hello")\n'
            ),
            (
                '"""This is a docstring."""\n\n'
                "from collections.abc import Sequence\n\n"
                '__all__: Sequence[str] = ("foo",)\n\n'
                "import random\n\n"
                "def foo():\n    "
                'print(f"hello {random.random()}")\n'
            ),
            (
                "\n"
                '"""This is a docstring."""\n\n'
                "from collections.abc import Sequence\n\n"
                '__all__: Sequence[str] = ("foo",)\n\n'
                "import random\n\n"
                "def foo():\n    "
                'print(f"hello {random.random()}")\n'
            ),
            (
                '"""This is a docstring."""\n\n'
                "from collections.abc import Sequence\n\n"
                '__all__: Sequence[str] = ("foo",)\n\n'
                "import random\n"
            ),
            '"""This is a docstring."""\n\nimport random\n',
            '\n"""This is a docstring."""\n\nimport random\n',
            *(
                f'{"\n" * count_pre}"""This is a docstring."""{"\n" * count_post}'
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            *(
                f"{'\n' * count_pre}from collections.abc import Sequence{'\n' * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            *(
                f"{'\n' * count_pre}__all__: Sequence[str] = (){'\n' * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            *(
                f"{'\n' * count_pre}__all__ = (){'\n' * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            *(
                f"{'\n' * count_pre}x = 5{'\n' * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            *(
                f"{'\n' * count_pre}import random{'\n' * count_post}"
                for count_post in range(0, 5)
                for count_pre in range(0, 5)
            ),
            "import random\nx = random.random()\n",
            "import random\nx = random.random()\n\nx = 5\n",
            '"""This is a docstring."""\nx = 4\n\n\ny = 5\n',
        ),
    )
    def test_successful_single_newline_between_preamble(self, raw_test_ast: str) -> None:
        """Ensure rule CAR111 is alerted for incorrect lines between preamble blocks."""
        problems: AbstractSet[str] = self._apply_carrot_plugin_to_ast(raw_test_ast)
        assert not problems or any("CAR111" not in problem for problem in problems)

    @pytest.mark.parametrize(
        ("raw_test_ast", "expected_error_position"),
        (
            *(
                (
                    f"{'\n' * count}{line1}\n{line2}\n",
                    (2 + count, 1),
                    # NOTE: Test for missing single newline (first break)
                )
                for line1, line2 in itertools.combinations(
                    (
                        '"""This is a docstring."""',
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
                        f"{'\n' * count_pre}"
                        f'"""This is a docstring."""{"\n" * count_post}'
                        "from collections.abc import Sequence\n"
                    ),
                    (3 + count_pre, 1),
                    # NOTE: Test that always second newline is flagged when > 1 newlines (first break)
                )
                for count_post in range(3, 6)
                for count_pre in range(0, 4)
            ),
            *(
                (
                    (
                        f"{'\n' * count_pre}"
                        f'"""This is a docstring."""{"\n" * count_post1}'
                        f"from collections.abc import Sequence{'\n' * count_post2}"
                        "__all__: Sequence[str] = ()\n"
                    ),
                    (3 + count_pre, 1),
                    # NOTE: Test that always second newline is flagged when > 1 newlines (first break) and incorrect newlines below
                )
                for count_post1 in range(3, 6)
                for count_pre in range(0, 4)
                for count_post2 in range(1, 6)
                if count_post2 != 2
            ),
            *(
                (
                    (
                        f'{"\n" * count}"""This is a docstring."""\n\n'
                        "from collections.abc import Sequence\n"
                        "__all__: Sequence[str] = ()\n"
                    ),
                    (4 + count, 1),
                    # NOTE: Test for missing single newline (second break)
                )
                for count in range(0, 4)
            ),
            *(
                (
                    (
                        f'{"\n" * count_pre}"""This is a docstring."""\n\n'
                        f"from collections.abc import Sequence{'\n' * count_post}"
                        "__all__: Sequence[str] = ()\n"
                    ),
                    (5 + count_pre, 1),
                    # NOTE: Test that always second newline is flagged when > 1 newlines (second break)
                )
                for count_pre in range(0, 4)
                for count_post in range(3, 6)
            ),
            *(
                (
                    (
                        f"{'\n' * count_pre}"
                        f'"""This is a docstring."""{"\n" * count_post1}'
                        f"from collections.abc import Sequence{'\n' * count_post2}"
                        "__all__: Sequence[str] = ()\n"
                    ),
                    (3 + count_pre + count_post1, 1),
                    # NOTE: Test that always second newline is flagged when > 1 newlines (second break) and newlines above
                )
                for count_post1 in range(1, 6)
                for count_pre in range(0, 4)
                for count_post2 in range(3, 6)
                if count_post1 != 2
            ),
        ),
    )
    def test_no_multiple_newlines_between_preamble(
        self, raw_test_ast: str, expected_error_position: tuple[int, int]
    ) -> None:
        assert self._get_message(*expected_error_position) in self._apply_carrot_plugin_to_ast(
            raw_test_ast
        )


class TestRuleCAR610(BaseTestCarrotPlugin):
    """Test suite for rule CAR610."""

    @classmethod
    def _get_message(cls, line_number: int, column_number: int) -> str:
        return (
            f"{line_number}:{column_number} CAR610 "
            'Regex pattern string should use a raw string: `r"..."`'
        )

    @pytest.mark.parametrize(
        "raw_test_ast",
        (
            're.search(r"\\A\\w+[a-z]\\Z", content)',
            "re.search(rf\"\\A<(?:{\n'|'.join(url_schemes)})>\\Z\", content)",
            're.match(r"\\A\\w+[a-z]\\Z", content)',
            "re.match(rf\"\\A<(?:{\n'|'.join(url_schemes)})>\\Z\", content)",
            're.fullmatch(r"\\A\\w+[a-z]\\Z", content)',
            "re.fullmatch(rf\"\\A<(?:{\n'|'.join(url_schemes)})>\\Z\", content)",
        ),
    )
    def test_correctly_using_r_prefix(self, raw_test_ast: str) -> None:
        """Ensure rule CAR610 is not alerted for modules with an `rf` string prefix."""
        assert all(
            "CAR610" not in problem
            for problem in self._apply_carrot_plugin_to_ast(raw_test_ast)
        )

    @pytest.mark.parametrize(
        ("raw_test_ast", "expected_error_position"),
        (
            ('re.search("\\\\A\\\\w+[a-z]\\\\Z", content)', (1, 1)),
            ("re.search(f\"\\\\A<(?:{\n'|'.join(url_schemes)})>\\\\Z\", content)", (1, 1)),
            ('re.match("\\\\A\\\\w+[a-z]\\\\Z", content)', (1, 1)),
            ("re.match(f\"\\\\A<(?:{\n'|'.join(url_schemes)})>\\\\Z\", content)", (1, 1)),
            ('re.fullmatch("\\\\A\\\\w+[a-z]\\\\Z", content)', (1, 1)),
            ("re.fullmatch(f\"\\\\A<(?:{\n'|'.join(url_schemes)})>\\\\Z\", content)", (1, 1)),
        ),
    )
    def test_missing_prefix(
        self, raw_test_ast: str, expected_error_position: tuple[int, int]
    ) -> None:
        """Ensure rule CAR610 is not alerted for modules with an `rf` string prefix."""
        assert self._get_message(*expected_error_position) in self._apply_carrot_plugin_to_ast(
            raw_test_ast
        )
