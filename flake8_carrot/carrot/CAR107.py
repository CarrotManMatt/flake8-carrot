""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR107",)

import ast
from collections.abc import Iterator, Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import BaseRule


class RuleCAR107(BaseRule):
    """"""

    @override
    def __init__(self) -> None:
        self.first_all_end_line_number: int | None = None

        super().__init__()

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR107 Double newline is required after `__all__` export"

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        if self.first_all_end_line_number is not None:
            raise RuntimeError

        self.visit(tree)

        if self.first_all_end_line_number is None:
            return

        first_all_end_line: str = lines[self.first_all_end_line_number - 1]  # type: ignore[unreachable]

        if not first_all_end_line.endswith("\n"):
            return

        remaining_lines: Iterator[str] = iter(lines[self.first_all_end_line_number:])

        try:
            first_line_after: str = next(remaining_lines)
        except StopIteration:
            return

        if first_line_after.strip("\n"):
            self.problems.add_without_ctx((self.first_all_end_line_number + 1, 0))
            return

        try:
            second_line_after: str = next(remaining_lines)
        except StopIteration:
            return

        if second_line_after.strip("\n"):
            self.problems.add_without_ctx((self.first_all_end_line_number + 2, 0))
            return

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
