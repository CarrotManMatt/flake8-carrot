""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR122",)


import ast
import re
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR122(CarrotRule):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR122 NOQA comment should be placed after `type: ignore` comment"

    @classmethod
    def _check_noqa_first(cls, line: str) -> int | None:
        match: re.Match[str] | None = re.search(
            (
                r"\s*#\s*(?P<noqa>noqa)(?:\s*:\s*[A-Z0-9]+(?:\s*,\s*[A-Z0-9]+)*(?:\s*,)*)?"
                r"\s*#\s*type\s*:\s*ignore(?:\s*\[\s*[a-z_-]+\s*(?:,\s*[a-z_-]+\s*)*(?:,\s*)*])?"
                r"\Z"
            ),
            line,
        )
        if match is None:
            return None

        return match.span("noqa")[0]

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        line_number: int
        line: str
        for line_number, line in enumerate(lines, start=1):
            found_error: int | None = self._check_noqa_first(line.rstrip())

            if found_error is None:
                continue

            self.problems.add_without_ctx((line_number, found_error))
