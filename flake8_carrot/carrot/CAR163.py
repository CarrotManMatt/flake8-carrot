"""Linting rule to warn when`__init__()` methods are not marked with `@override`."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR163",)


class RuleCAR163(CarrotRule, ast.NodeVisitor):
    """Linting rule to warn when`__init__()` methods are not marked with `@override`."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "`__init__()` method not marked with `@override`"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @classmethod
    def _has_override_decorator(cls, decorators: Iterable[ast.expr]) -> bool:
        decorator_node: ast.expr
        for decorator_node in decorators:
            match decorator_node:
                case (
                    ast.Name(id="override")
                    | ast.Attribute(value=ast.Name(id="typing"), attr="override")
                    | ast.Attribute(value=ast.Name(id="typing_extensions"), attr="override")
                    | ast.Call(
                        func=(
                            ast.Name(id="override")
                            | ast.Attribute(value=ast.Name(id="typing"), attr="override")
                            | ast.Attribute(
                                value=ast.Name(id="typing_extensions"), attr="override"
                            )
                        )
                    )
                ):
                    return True

        return False

    @utils.generic_visit_before_return
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name != "__init__":
            return

        if not self._has_override_decorator(node.decorator_list):
            self.problems.add_without_ctx((node.lineno, node.col_offset))
