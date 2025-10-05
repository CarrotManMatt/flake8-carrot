""""""  # noqa: N999

import ast
import tokenize
from ast import NodeVisitor
from io import StringIO
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping, Sequence
    from tokenize import TokenInfo
    from typing import Final

    from flake8_carrot.carrot import CarrotPlugin

__all__: "Sequence[str]" = ("RuleCAR112",)


class RuleCAR112(CarrotRule, NodeVisitor):
    """"""

    @override
    def __init__(self, plugin: "CarrotPlugin") -> None:
        self.source: str | None = None

        super().__init__(plugin)

    @classmethod
    @override
    def _format_error_message(cls, ctx: "Mapping[str, object]") -> str:
        definition_type: object | None = ctx.get("definition_type", None)
        if definition_type is not None and not isinstance(definition_type, str):
            raise TypeError

        return (
            f"{
                f'{definition_type.strip().capitalize()} definition'
                if definition_type is not None
                else 'Function/class/for-loop/if-check/while-loop definitions'
            } "
            "should not spread over multiple lines"
        )

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: "Sequence[TokenInfo]", lines: "Sequence[str]"
    ) -> None:
        self.source = "".join(lines)
        self.visit(tree)

    def _check_ast_is_multiline(
        self,
        node: ast.FunctionDef
        | ast.AsyncFunctionDef
        | ast.ClassDef
        | ast.While
        | ast.For
        | ast.AsyncFor
        | ast.If,
    ) -> tuple[int, int] | None:
        CHECK_VALUES: Final[Collection[str]] = ("def", "class", "if", "while", "for")

        TOKENS: Final[Sequence[TokenInfo]] = list(
            tokenize.generate_tokens(
                StringIO(
                    (
                        ast.get_source_segment(self.source, node)
                        if self.source is not None
                        else ast.unparse(node)
                    ),
                ).readline,
            ),
        )

        token: TokenInfo
        token_index: int
        for token_index, token in enumerate(TOKENS):
            if token.type == tokenize.NAME and token.string in CHECK_VALUES:
                return (
                    self._get_first_token_from_next_line(TOKENS[token_index:]).start
                    if self._check_for_multiline_colon(token.start[0], TOKENS[token_index:])
                    else None
                )

        return None

    @classmethod
    def _check_for_multiline_colon(
        cls, correct_line: int, tokens: "Sequence[TokenInfo]"
    ) -> bool:
        token: TokenInfo
        for token in tokens:
            if token.exact_type != tokenize.COLON:
                continue

            return token.end[0] != correct_line

        NO_COLON_FOUND_MESSAGE: Final[str] = (
            "Invalid code provided; no ending stament colon found."
        )
        raise RuntimeError(NO_COLON_FOUND_MESSAGE)

    @classmethod
    def _get_first_token_from_next_line(cls, tokens: "Sequence[TokenInfo]") -> "TokenInfo":
        FIRST_LINE: Final[int] = tokens[0].start[0]

        token: TokenInfo
        for token in tokens:
            if token.start[0] == FIRST_LINE:
                continue

            return token

        TOKENS_WERE_SINGLE_LINE_MESSAGE: Final[str] = "Provided tokens were not multiline."
        raise RuntimeError(TOKENS_WERE_SINGLE_LINE_MESSAGE)

    @utils.generic_visit_before_return
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        PROBLEM: Final[tuple[int, int] | None] = self._check_ast_is_multiline(node)
        if PROBLEM is None:
            return

        self.problems[(node.lineno + PROBLEM[0] - 1, PROBLEM[1])] = {
            "definition_type": "function",
        }

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        PROBLEM: Final[tuple[int, int] | None] = self._check_ast_is_multiline(node)
        if PROBLEM is None:
            return

        self.problems[(node.lineno + PROBLEM[0] - 1, PROBLEM[1])] = {
            "definition_type": "function",
        }

    @utils.generic_visit_before_return
    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        PROBLEM: Final[tuple[int, int] | None] = self._check_ast_is_multiline(node)
        if PROBLEM is None:
            return

        self.problems[(node.lineno + PROBLEM[0] - 1, PROBLEM[1])] = {
            "definition_type": "class",
        }

    @utils.generic_visit_before_return
    @override
    def visit_For(self, node: ast.For) -> None:
        PROBLEM: Final[tuple[int, int] | None] = self._check_ast_is_multiline(node)
        if PROBLEM is None:
            return

        self.problems[(node.lineno + PROBLEM[0] - 1, PROBLEM[1])] = {
            "definition_type": "for-loop",
        }

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        PROBLEM: Final[tuple[int, int] | None] = self._check_ast_is_multiline(node)
        if PROBLEM is None:
            return

        self.problems[(node.lineno + PROBLEM[0] - 1, PROBLEM[1])] = {
            "definition_type": "for-loop",
        }

    @utils.generic_visit_before_return
    @override
    def visit_While(self, node: ast.While) -> None:
        PROBLEM: Final[tuple[int, int] | None] = self._check_ast_is_multiline(node)
        if PROBLEM is None:
            return

        self.problems[(node.lineno + PROBLEM[0] - 1, PROBLEM[1])] = {
            "definition_type": "while-loop",
        }

    @utils.generic_visit_before_return
    @override
    def visit_If(self, node: ast.If) -> None:
        PROBLEM: Final[tuple[int, int] | None] = self._check_ast_is_multiline(node)
        if PROBLEM is None:
            return

        self.problems[(node.lineno + PROBLEM[0] - 1, PROBLEM[1])] = {
            "definition_type": "if-check",
        }
