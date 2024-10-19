""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR123",)


import ast
import re
import tokenize
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import override

from flake8_carrot.utils import CarrotRule


class RuleCAR123(CarrotRule):
    """"""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "Line comment should be placed before NOQA or `type: ignore` comment"

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        file_token: TokenInfo
        for file_token in file_tokens:
            if file_token.type != tokenize.COMMENT:
                continue

            match: re.Match[str] | None = re.fullmatch(
                r"\A.*(?:#\s+noqa[^#]*|#\s+type:\s*ignore[^#]*)+(?!#\s+noqa[^#]*|#\s+type:\s*ignore[^#]*)(#.+)\Z",
                file_token.string,
            )
            if match is not None:
                self.problems.add_without_ctx(
                    (file_token.start[0], file_token.start[1] + match.span(1)[0]),
                )
                continue
