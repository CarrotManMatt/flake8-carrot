""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR100",)

import ast
from collections.abc import Iterator
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import BaseRule


class RuleCAR100(BaseRule):
    """"""

    @override
    def __init__(self) -> None:
        self.first_all_end_line_number: int | None = None

        super().__init__()

    @classmethod
    @override
    def format_error_message(cls, ctx: dict[str, object]) -> str:
        return "CAR100 Assignment of `logging.Logger` object should be marked as `Final`"

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        ALL_EXPORT_FOUND: Final[bool] = any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets  # noqa: COM812
        )
        if ALL_EXPORT_FOUND and self.first_all_end_line_number is None:
            self.first_all_end_line_number = node.end_lineno or node.lineno

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        ALL_EXPORT_FOUND: Final[bool] = bool(
            isinstance(node.target, ast.Name)
            and node.target.id == "__all__"  # noqa: COM812
        )
        if ALL_EXPORT_FOUND and self.first_all_end_line_number is None:
            self.first_all_end_line_number = node.end_lineno or node.lineno

        self.generic_visit(node)
