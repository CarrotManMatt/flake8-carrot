""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR110",)


import ast
from collections.abc import Iterator, Mapping
from tokenize import TokenInfo
from typing import override

from flake8_carrot.utils import CarrotRule


class RuleCAR110(CarrotRule):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR110 Double newline is required after `__all__` export"

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        if self.plugin.first_all_export_line_numbers is None:
            return

        if not lines[self.plugin.first_all_export_line_numbers[1] - 1].endswith("\n"):
            return

        remaining_lines: Iterator[str] = iter(
            lines[self.plugin.first_all_export_line_numbers[1]:],
        )

        first_line_after: str | None = next(remaining_lines, None)
        if first_line_after is None:
            return

        if first_line_after.strip("\n"):
            self.problems.add_without_ctx(
                (self.plugin.first_all_export_line_numbers[1] + 1, 0),
            )
            return

        second_line_after: str | None = next(remaining_lines, None)
        if second_line_after is None:
            return

        if second_line_after.strip("\n"):
            self.problems.add_without_ctx(
                (self.plugin.first_all_export_line_numbers[1] + 1, 0),
            )
            return

        third_line_after: str | None = next(remaining_lines, None)
        if third_line_after is None or third_line_after.strip("\n"):
            return

        self.problems.add_without_ctx(
            (self.plugin.first_all_export_line_numbers[1] + 3, 0),
        )
