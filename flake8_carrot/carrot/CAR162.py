"""Linting rule class-property names should be in all caps."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR162",)


class RuleCAR162(CarrotRule, ast.NodeVisitor):
    """Linting rule class-property names should be in all caps."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        classproperty_name: object | None = ctx.get("classproperty_name", None)
        if classproperty_name is not None:
            if not isinstance(classproperty_name, str):
                raise TypeError

            classproperty_name = classproperty_name.strip("\n\r\t '")

        return f"Class-property name{
            f" '{classproperty_name}'" if classproperty_name else ''
        } should be in all caps{
            f": '{classproperty_name.upper()}'" if classproperty_name else ''
        }"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @classmethod
    def _has_classproperty_decorator(cls, decorators: Iterable[ast.expr]) -> bool:
        decorator_node: ast.expr
        for decorator_node in decorators:
            match decorator_node:
                case (
                    ast.Name(id="classproperty")
                    | ast.Name(id="cached_classproperty")
                    | ast.Attribute(value=ast.Name(id="classproperties"), attr="classproperty")
                    | ast.Attribute(
                        value=ast.Name(id="classproperties"), attr="cached_classproperty"
                    )
                    | ast.Call(
                        func=(
                            ast.Name(id="classproperty")
                            | ast.Name(id="cached_classproperty")
                            | ast.Attribute(
                                value=ast.Name(id="classproperties"), attr="classproperty"
                            )
                            | ast.Attribute(
                                value=ast.Name(id="classproperties"),
                                attr="cached_classproperty",
                            )
                        )
                    )
                ):
                    return True

        return False

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if not self._has_classproperty_decorator(node.decorator_list):
            return

        if not node.name.isupper():
            self.problems[(node.lineno, node.col_offset)] = {"classproperty_name": node.name}

    @utils.generic_visit_before_return
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
