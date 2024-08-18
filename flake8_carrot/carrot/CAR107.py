""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR107",)


import ast
from collections.abc import Iterator, Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR107(CarrotRule):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR107 Double newline is required after `__all__` export"

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        SKIP_FILE: Final[bool] = bool(
            self.plugin.first_all_export_line_numbers is None
            or not lines[self.plugin.first_all_export_line_numbers[1] - 1].endswith("\n")
        )
        if SKIP_FILE:
            return

        remaining_lines: Iterator[str] = iter(lines[self.plugin.first_all_export_line_numbers[1]:])  # type: ignore[index]

        first_line_after: str | None = next(remaining_lines, None)
        if first_line_after is None:
            return

        if first_line_after.strip("\n"):
            self.problems.add_without_ctx((self.plugin.first_all_export_line_numbers[1] + 1, 0))  # type: ignore[index]
            return

        second_line_after: str | None = next(remaining_lines, None)
        if second_line_after is None:
            return

        if second_line_after.strip("\n"):
            self.problems.add_without_ctx((self.plugin.first_all_export_line_numbers[1] + 1, 0))  # type: ignore[index]
            return
