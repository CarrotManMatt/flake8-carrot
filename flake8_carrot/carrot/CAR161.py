"""Linting rule to ensure the body of abstract methods only contains the docstring."""  # noqa: N999

import ast
import builtins
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR161",)


class RuleCAR161(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure the body of abstract methods only contains the docstring."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        abstract_method_name: object | None = ctx.get("abstract_method_name", None)
        if abstract_method_name is not None:
            if not isinstance(abstract_method_name, str):
                raise TypeError

            abstract_method_name = abstract_method_name.strip("\n\r\t '()")

        return f"Body of abstract method{
            f" '{
                abstract_method_name
                if len(abstract_method_name) < 30
                else f'{abstract_method_name[:30]}...'
            }()'"
            if abstract_method_name
            else ''
        } should only contain the docstring{
            ' or `pass`'
            if abstract_method_name and abstract_method_name.startswith('_')
            else ''
        } "

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @classmethod
    def _has_abstractmethod_decorator(cls, decorators: Iterable[ast.expr]) -> bool:
        decorator_node: ast.expr
        for decorator_node in decorators:
            match decorator_node:
                case (
                    ast.Name(id="abstractmethod")
                    | ast.Attribute(value=ast.Name(id="abc"), attr="abstractmethod")
                    | ast.Call(
                        func=(
                            ast.Name(id="abstractmethod")
                            | ast.Attribute(value=ast.Name(id="abc"), attr="abstractmethod")
                        )
                    )
                ):
                    return True

        return False

    @classmethod
    def _has_property_decorator(cls, decorators: Iterable[ast.expr]) -> bool:
        decorator_node: ast.expr
        for decorator_node in decorators:
            match decorator_node:
                case (
                    ast.Name(id="property")
                    | ast.Name("cached_property")
                    | ast.Name(id="classproperty")
                    | ast.Name(id="cached_classproperty")
                    | ast.Attribute(value=ast.Name(id="classproperties"), attr="classproperty")
                    | ast.Attribute(
                        value=ast.Name(id="classproperties"), attr="cached_classproperty"
                    )
                    | ast.Call(
                        func=(
                            ast.Name(id="property")
                            | ast.Name("cached_property")
                            | ast.Name(id="classproperty")
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

    @classmethod
    def _has_overload_decorator(cls, decorators: Iterable[ast.expr]) -> bool:
        decorator_node: ast.expr
        for decorator_node in decorators:
            match decorator_node:
                case (
                    ast.Name(id="overload")
                    | ast.Attribute(value=ast.Name(id="typing"), attr="overload")
                    | ast.Attribute(value=ast.Name(id="typing_extensions"), attr="overload")
                    | ast.Call(
                        func=(
                            ast.Name(id="overload")
                            | ast.Attribute(value=ast.Name(id="typing"), attr="overload")
                            | ast.Attribute(
                                value=ast.Name(id="typing_extensions"), attr="overload"
                            )
                        )
                    )
                ):
                    return True

        return False

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if not self._has_abstractmethod_decorator(node.decorator_list):
            return

        body_node: ast.stmt
        for body_node in node.body:
            match body_node:
                case ast.Expr(value=ast.Constant(value=str())):
                    continue
                case ast.Pass() if node.name.strip().startswith(
                    "_"
                ) or self._has_property_decorator(node.decorator_list):
                    continue
                case ast.Expr(value=ast.Constant(value=builtins.Ellipsis)) if (
                    self._has_overload_decorator(node.decorator_list)
                ):
                    continue
                case _:
                    self.problems[(body_node.lineno, body_node.col_offset)] = {
                        "abstract_method_name": node.name
                    }

    @utils.generic_visit_before_return
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
