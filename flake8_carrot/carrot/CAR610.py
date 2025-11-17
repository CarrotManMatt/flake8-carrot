"""Linting rule to ensure regex patterns use raw strings."""  # noqa: N999

import ast
import re
import tokenize
from io import StringIO
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Mapping, Sequence
    from tokenize import TokenInfo
    from typing import Final

    from flake8_carrot.carrot import CarrotPlugin

__all__: Sequence[str] = ("RuleCAR610",)


class RuleCAR610(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure regex patterns use raw strings."""

    @override
    def __init__(self, plugin: CarrotPlugin) -> None:
        self.source: str | None = None

        super().__init__(plugin)

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return 'Regex pattern string should use a raw string: `r"..."`'

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.source = "".join(lines)
        self.visit(tree)

    def _check_node_for_incorrect_string_type(
        self, argument: ast.Constant | ast.JoinedStr
    ) -> None:
        TOKENS: Final[Iterable[TokenInfo]] = tokenize.generate_tokens(
            StringIO(
                (
                    ast.get_source_segment(self.source, argument)
                    if self.source is not None
                    else ast.unparse(argument)
                ),
            ).readline,
        )

        token: TokenInfo
        for token in TOKENS:
            if (
                (isinstance(argument, ast.Constant) and token.type == tokenize.STRING)
                or token.type == tokenize.FSTRING_START
            ) and not re.search(r"\A(?:rf?|fr)[\"']", token.string):
                self.problems.add_without_ctx(
                    (argument.lineno - 1 + token.start[0], token.start[1]),
                )

    @utils.generic_visit_before_return
    @override
    def visit_Call(self, node: ast.Call) -> None:
        RE_FUNCTION_NAMES: Final[Collection[str]] = (
            "search",
            "match",
            "fullmatch",
            "findall",
            "finditer",
            "compile",
            "split",
            "sub",
            "subn",
        )

        function_name: str
        argument: ast.Constant | ast.JoinedStr
        match node:
            case ast.Call(
                func=(
                    ast.Attribute(value=ast.Name(id="re"), attr=function_name)
                    | ast.Name(id=function_name)
                ),
                args=[(ast.Constant(value=str()) | ast.JoinedStr()) as argument, *_],
            ):
                if function_name not in RE_FUNCTION_NAMES:
                    return

                self._check_node_for_incorrect_string_type(argument)
                return
