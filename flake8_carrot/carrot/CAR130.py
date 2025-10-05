""""""  # noqa: N999

import re
from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule, ProblemsContainer

if TYPE_CHECKING:
    import ast
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: "Sequence[str]" = ("RuleCAR130",)


class RuleCAR130(CarrotRule):
    """"""

    @classmethod
    @override
    def _format_error_message(cls, ctx: "Mapping[str, object]") -> str:
        return (
            "Incorrect ordering of raw & formatted string prefixes "
            '(use `fr"..."` not `rf"..."`)'
        )

    @override
    def run_check(
        self, tree: "ast.Module", file_tokens: "Sequence[TokenInfo]", lines: "Sequence[str]"
    ) -> None:
        self.problems = ProblemsContainer(
            (
                self.problems
                | {
                    (line_number, match.start()): {}
                    for line_number, line in enumerate(lines, start=1)
                    for match in re.finditer(r"rf\"", line)
                }
            ),
        )
