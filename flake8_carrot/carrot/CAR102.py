""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR002",)

import ast
from typing import Final, override

from flake8_carrot.utils import BaseRule


class RuleCAR002(BaseRule):
    """"""

    @override
    def __init__(self) -> None:
        self.all_found_count: int = 0

        super().__init__()

    @classmethod
    @override
    def format_error_message(cls, ctx: dict[str, object]) -> str:
        return "CAR002 Multiple `__all__` exports found in a single module"

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
