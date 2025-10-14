"""Linting rule to enforce correct ordering of NOQA and `type: ignore` comments."""  # noqa: N999

import re
import tokenize
from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    import ast
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR122",)


class RuleCAR122(CarrotRule):
    """Linting rule to enforce correct ordering of NOQA and `type: ignore` comments."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "NOQA comment should be placed after `type: ignore` comment"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        file_token: TokenInfo
        for file_token in file_tokens:
            if file_token.type != tokenize.COMMENT:
                continue

            match: re.Match[str] | None = re.fullmatch(
                (
                    r"\A.*"
                    r"#\s*(?P<noqa>noqa)(?:\s*:\s*[A-Z0-9]+(?:\s*,\s*[A-Z0-9]+)*(?:\s*,)*)?"
                    r"\s*#\s*type\s*:\s*ignore(?:\s*\[\s*[a-z_-]+\s*(?:,\s*[a-z_-]+\s*)*(?:,\s*)*])?"
                    r"\Z"
                ),
                file_token.string.rstrip(),
            )
            if match is not None:
                self.problems.add_without_ctx(
                    (file_token.start[0], file_token.start[1] + match.span("noqa")[0]),
                )
                continue
