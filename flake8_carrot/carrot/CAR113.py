""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR113",)


import ast
from ast import NodeVisitor
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR113(CarrotRule, NodeVisitor):
    """"""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "Comprehension `in` term should be on the same line as the `for` term"

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    @utils.generic_visit_before_return
    @override
    def visit_comprehension(self, node: ast.comprehension) -> None:
        ITER_LINENO: Final[int] = node.iter.lineno

        if (node.target.end_lineno or node.target.lineno) != ITER_LINENO:
            self.problems.add_without_ctx((ITER_LINENO, node.iter.col_offset - 3))
