"""Linting rule to warn about uses of string functions that have will have no effect."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR141",)


class RuleCAR141(CarrotRule, ast.NodeVisitor):
    """Linting rule to warn about uses of string functions that have will have no effect."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "String function seems to have no effect"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    def _check_for_string_function(self, statements: Iterable[ast.stmt]) -> None:
        statement: ast.stmt
        for statement in statements:
            match statement:
                case ast.Expr(
                    value=ast.Call(func=ast.Attribute(value=ast.Constant(value=str()))),
                ):
                    self.problems.add_without_ctx((statement.lineno, statement.col_offset))
                    continue
                case _:
                    continue

    @utils.generic_visit_before_return
    @override
    def visit_Module(self, node: ast.Module) -> None:
        self._check_for_string_function(node.body)

    @utils.generic_visit_before_return
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_for_string_function(node.body)

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_for_string_function(node.body)

    @utils.generic_visit_before_return
    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check_for_string_function(node.body)

    @utils.generic_visit_before_return
    @override
    def visit_For(self, node: ast.For) -> None:
        self._check_for_string_function(node.body)
        self._check_for_string_function(node.orelse)

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._check_for_string_function(node.body)
        self._check_for_string_function(node.orelse)

    @utils.generic_visit_before_return
    @override
    def visit_While(self, node: ast.While) -> None:
        self._check_for_string_function(node.body)
        self._check_for_string_function(node.orelse)

    @utils.generic_visit_before_return
    @override
    def visit_If(self, node: ast.If) -> None:
        self._check_for_string_function(node.body)
        self._check_for_string_function(node.orelse)

    @utils.generic_visit_before_return
    @override
    def visit_With(self, node: ast.With) -> None:
        self._check_for_string_function(node.body)

    @utils.generic_visit_before_return
    @override
    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self._check_for_string_function(node.body)

    @utils.generic_visit_before_return
    @override
    def visit_Try(self, node: ast.Try) -> None:
        self._check_for_string_function(node.body)
        self._check_for_string_function(node.orelse)
        self._check_for_string_function(node.finalbody)

    @utils.generic_visit_before_return
    @override
    def visit_TryStar(self, node: ast.TryStar) -> None:
        self._check_for_string_function(node.body)
        self._check_for_string_function(node.orelse)
        self._check_for_string_function(node.finalbody)

    @utils.generic_visit_before_return
    @override
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._check_for_string_function(node.body)

    @utils.generic_visit_before_return
    @override
    def visit_Match(self, node: ast.Match) -> None:
        case: ast.match_case
        for case in node.cases:
            self._check_for_string_function(case.body)
