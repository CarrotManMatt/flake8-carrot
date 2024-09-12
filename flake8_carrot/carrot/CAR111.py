""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR111",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import override

from flake8_carrot.utils import CarrotRule


class RuleCAR111(CarrotRule):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return (
            "CAR111 "
            "Preamble lines (imports, `__all__` declaration, module docstring, etc.) "
            "should be seperated by a single newline"
        )

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        if not lines or len(lines) < 3:
            return

        first_line: str = lines[0]
