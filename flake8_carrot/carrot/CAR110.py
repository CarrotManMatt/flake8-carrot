"""Linting rule to ensure a double newline is present after the `__all__` export."""  # noqa: N999

from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    import ast
    from collections.abc import Iterator, Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR110",)


class RuleCAR110(CarrotRule):
    """Linting rule to ensure a double newline is present after the `__all__` export."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "Double newline is required after `__all__` export"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        if self.plugin.first_all_export_line_numbers is None:
            return

        if not lines[self.plugin.first_all_export_line_numbers[1] - 1].endswith("\n"):
            return

        remaining_lines: Iterator[str] = iter(
            lines[self.plugin.first_all_export_line_numbers[1] :],
        )

        first_line_after: str | None = next(remaining_lines, None)
        if first_line_after is None:
            return

        if first_line_after.strip("\n\r"):
            self.problems.add_without_ctx(
                (self.plugin.first_all_export_line_numbers[1] + 1, 0),
            )
            return

        second_line_after: str | None = next(remaining_lines, None)
        if second_line_after is None:
            return

        if second_line_after.strip("\n\r"):
            self.problems.add_without_ctx(
                (self.plugin.first_all_export_line_numbers[1] + 1, 0),
            )
            return

        third_line_after: str | None = next(remaining_lines, None)
        if third_line_after is None or third_line_after.strip("\n\r"):
            return

        self.problems.add_without_ctx(
            (self.plugin.first_all_export_line_numbers[1] + 3, 0),
        )
