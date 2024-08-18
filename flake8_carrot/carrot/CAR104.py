""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR104",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR104(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR104 Simple `__all__` export should be of type `tuple`, not `list`"

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:
        self.visit(tree)

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        FIRST_ALL_EXPORT_FOUND: Final[bool] = bool(
            any(
                isinstance(target, ast.Name) and target.id == "__all__"
                for target in node.targets
            )
            and isinstance(node.value, ast.List)
            and self.plugin.first_all_export_line_numbers is not None
            and node.lineno == self.plugin.first_all_export_line_numbers[0]
        )
        if FIRST_ALL_EXPORT_FOUND:
            self.problems.add_without_ctx((node.value.lineno, node.value.col_offset))

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        FIRST_ALL_EXPORT_FOUND: Final[bool] = bool(
            isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
            and isinstance(node.value, ast.List)
            and self.plugin.first_all_export_line_numbers is not None
            and node.lineno == self.plugin.first_all_export_line_numbers[0]  # noqa: COM812
        )
        if FIRST_ALL_EXPORT_FOUND:
            self.problems.add_without_ctx((node.value.lineno, node.value.col_offset))  # type: ignore[union-attr]

        self.generic_visit(node)
