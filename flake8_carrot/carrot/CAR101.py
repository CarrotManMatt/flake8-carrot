"""Linting rule to ensure the `__all__` export is not missing from a module."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR101",)


class RuleCAR101(CarrotRule):
    """Linting rule to ensure the `__all__` export is not missing from a module."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "Missing `__all__` export at the top of the module"

    @classmethod
    def get_error_position(
        cls, tree_body: Sequence[ast.stmt], lines: Sequence[str]
    ) -> tuple[int, int]:  # NOTE: I'm sorry to whoever has to work out what is going on here
        """Retrieve the correct error position for this rule based on the problematic AST."""
        if not tree_body:
            return 1, 0

        first_child_node: ast.stmt = tree_body[0]
        first_child_end_lineno: int = first_child_node.end_lineno or first_child_node.lineno

        match first_child_node:
            case ast.Expr(value=ast.Constant()):
                pass
            case _:
                return 1, 0

        if len(tree_body) < 2:
            if not lines[first_child_end_lineno - 1].endswith("\n"):
                return (
                    first_child_end_lineno,
                    (first_child_node.end_col_offset or first_child_node.col_offset),
                )

            return (
                min(
                    first_child_end_lineno + 2,
                    len(lines[first_child_end_lineno:]) + first_child_end_lineno + 1,
                ),
                0,
            )

        second_child_node: ast.stmt = tree_body[1]
        second_child_end_lineno: int = second_child_node.end_lineno or second_child_node.lineno

        match second_child_node:
            case ast.ImportFrom(module="collections.abc", names=[ast.alias(name="Sequence")]):
                pass
            case _:
                if len(lines[first_child_end_lineno : second_child_end_lineno - 1]) in (1, 2):
                    return first_child_end_lineno + 1, 0

                return (
                    min(
                        first_child_end_lineno + 2,
                        (
                            len(lines[first_child_end_lineno : second_child_end_lineno - 1])
                            + first_child_end_lineno
                            + 1
                        ),
                    ),
                    0,
                )

        if len(tree_body) < 3:
            if not lines[second_child_end_lineno - 1].endswith("\n"):
                return (
                    second_child_end_lineno,
                    second_child_node.end_col_offset or second_child_node.col_offset,
                )

            return (
                min(
                    second_child_end_lineno + 2,
                    len(lines[second_child_end_lineno:]) + second_child_end_lineno + 1,
                ),
                0,
            )

        third_child_node: ast.stmt = tree_body[2]
        third_child_end_lineno: int = third_child_node.end_lineno or third_child_node.lineno

        if len(lines[second_child_end_lineno : third_child_end_lineno - 1]) in (1, 2):
            return second_child_end_lineno + 1, 0

        return (
            min(
                second_child_end_lineno + 2,
                (
                    len(lines[second_child_end_lineno : third_child_end_lineno - 1])
                    + second_child_end_lineno
                    + 1
                ),
            ),
            0,
        )

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        if self.plugin.first_all_export_line_numbers is not None:
            return

        error_line_number: int
        error_column_number: int
        error_line_number, error_column_number = self.get_error_position(tree.body, lines)

        self.problems.add_without_ctx(
            (max(error_line_number, 1), max(error_column_number, 0)),
        )
