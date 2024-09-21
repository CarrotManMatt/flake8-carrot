""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR130",)


import ast
import re
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import override

from flake8_carrot.utils import CarrotRule, ProblemsContainer


class RuleCAR130(CarrotRule):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return (
            "CAR130 "
            "Incorrect ordering of raw & formatted string prefixes "
            "(use `fr\"...\"` not `rf\"...\"`)"
        )

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.problems = ProblemsContainer(
            (
                self.problems | {
                    (line_number, match.start()): {}
                    for line_number, line in enumerate(lines, start=1)
                    for match in re.finditer(r"rf\"", line)
                }
            ),
        )
