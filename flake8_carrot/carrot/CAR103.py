""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR103",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR103(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR103 `__all__` export should be annotated as `Sequence[str]`"

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        all_assignment: ast.Name | None = next(
            (
                target
                for target in node.targets
                if isinstance(target, ast.Name) and target.id == "__all__"
            ),
            None,
        )
        IS_FIRST_ALL_EXPORT: Final[bool] = bool(
            all_assignment is not None
            and self.plugin.first_all_export_line_numbers is not None
            and node.lineno == self.plugin.first_all_export_line_numbers[0]  # noqa: COM812
        )
        if IS_FIRST_ALL_EXPORT:
            self.problems.add_without_ctx(
                (
                    all_assignment.lineno,  # type: ignore[union-attr]
                    (all_assignment.end_col_offset or all_assignment.col_offset),  # type: ignore[union-attr]
                ),
            )

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        INCORRECTLY_ANNOTATED_ALL_EXPORT_FOUND: Final[bool] = bool(
            isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
            and self.plugin.first_all_export_line_numbers is not None
            and node.lineno == self.plugin.first_all_export_line_numbers[0]
            and not bool(
                isinstance(node.annotation, ast.Subscript)
                and isinstance(node.annotation.value, ast.Name)
                and isinstance(node.annotation.slice, ast.Name)
                and node.annotation.value.id == "Sequence"
                and node.annotation.slice.id == "str"  # noqa: COM812
            )  # noqa: COM812
        )
        if INCORRECTLY_ANNOTATED_ALL_EXPORT_FOUND:
            self.problems.add_without_ctx(
                (
                    node.annotation.lineno,
                    (
                        (node.annotation.end_col_offset or node.annotation.col_offset) - 1
                        if bool(
                            isinstance(node.annotation, ast.Name)
                            and node.annotation.id == "Sequence"  # noqa: COM812
                        )
                        else node.annotation.col_offset
                    ),
                ),
            )

        self.generic_visit(node)
