"""Linting rule to ensure classes are not defined inside functions."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR160",)


class RuleCAR160(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure classes are not defined inside functions."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        function_name: object | None = ctx.get("function_name", None)
        if function_name is not None:
            if not isinstance(function_name, str):
                raise TypeError

            function_name = function_name.strip("\n\r\t '()")

        class_name: object | None = ctx.get("class_name", None)
        if class_name is not None:
            if not isinstance(class_name, str):
                raise TypeError

            class_name = class_name.strip("\n\r\t '")

        is_function_async: object | None = ctx.get("is_function_async", None)
        if class_name is not None and not isinstance(is_function_async, bool):
            raise TypeError

        return f"Class{
            f" '{class_name if len(class_name) < 30 else f'{class_name[:30]}...'}'"
            if class_name
            else ''
        } defined inside {'async ' if is_function_async else ''}function{
            f" '{function_name if len(function_name) < 30 else f'{function_name[:30]}...'}()'"
            if function_name
            else ''
        }"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        inner_node: ast.AST
        for inner_node in ast.walk(node):
            if isinstance(inner_node, ast.ClassDef):
                self.problems[(inner_node.lineno, inner_node.col_offset)] = {
                    "function_name": node.name,
                    "class_name": inner_node.name,
                    "is_function_async": isinstance(node, ast.AsyncFunctionDef),
                }

    # NOTE: Don't descend into visitor children
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)

    # NOTE: Don't descend into visitor children
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
