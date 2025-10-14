"""Linting rule to warn on the unnecessary use of string strip functions."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR140",)


class RuleCAR140(CarrotRule, ast.NodeVisitor):
    """Linting rule to warn on the unnecessary use of string strip functions."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "Unnecessary use of string strip function"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @utils.generic_visit_before_return
    @override
    def visit_Compare(self, node: ast.Compare) -> None:
        string_object: ast.expr
        fallback_column_number: int
        match node:
            case ast.Compare(
                ops=[ast.In()],
                comparators=[
                    ast.Call(
                        func=ast.Attribute(
                            attr=("strip" | "lstrip" | "rstrip"),
                            value=string_object,
                        ),
                        col_offset=fallback_column_number,
                    ),
                ],
            ):
                self.problems.add_without_ctx(
                    (
                        string_object.end_lineno or string_object.lineno,
                        (
                            string_object.end_col_offset + 1
                            if string_object.end_col_offset is not None
                            else fallback_column_number
                        ),
                    ),
                )
                return

            case _:
                return
