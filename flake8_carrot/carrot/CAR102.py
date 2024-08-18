""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR102",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule


if TYPE_CHECKING:
    from flake8_carrot.carrot import CarrotPlugin


class RuleCAR102(CarrotRule, ast.NodeVisitor):
    """"""

    @override
    def __init__(self, plugin: "CarrotPlugin") -> None:
        self.all_found_count: int = 0

        super().__init__(plugin)

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR102 Multiple `__all__` exports found in a single module"

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:
        self.visit(tree)

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        ALL_EXPORT_FOUND: Final[bool] = any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        )
        if ALL_EXPORT_FOUND:
            if self.all_found_count > 0:
                self.problems.add_without_ctx((node.lineno, node.col_offset))

            self.all_found_count += 1

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        ALL_EXPORT_FOUND: Final[bool] = bool(
            isinstance(node.target, ast.Name)
            and node.target.id == "__all__"  # noqa: COM812
        )
        if ALL_EXPORT_FOUND:
            if self.all_found_count > 0:
                self.problems.add_without_ctx((node.lineno, node.col_offset))

            self.all_found_count += 1

        self.generic_visit(node)
