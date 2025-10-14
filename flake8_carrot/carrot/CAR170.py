"""Linting rule to ensure union typesin `isintance()` calls are replaced by tuples."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR170",)


class RuleCAR170(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure union typesin `isintance()` calls are replaced by tuples."""

    @classmethod
    def _convert_expr_to_tuple(cls, expr: ast.expr) -> str:
        match expr:
            case ast.BinOp(op=ast.BitOr(), left=left, right=right):
                return (
                    f"{cls._convert_expr_to_tuple(left)}, {cls._convert_expr_to_tuple(right)}"
                )
            case ast.BinOp() | ast.BoolOp():
                return f"({ast.unparse(expr)})"
            case _:
                return ast.unparse(expr)

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        type_union: object | None = ctx.get("type_union", None)
        type_tuple: str = ""
        match type_union:
            case None:
                pass
            case ast.BinOp(op=ast.BitOr(), left=left, right=right):
                type_union = ast.unparse(type_union)
                type_tuple = f"({cls._convert_expr_to_tuple(left)}, {
                    cls._convert_expr_to_tuple(right)
                })"
            case _:
                raise TypeError

        return f"Replace type union{
            f' `{type_union if len(type_union) < 30 else f"{type_union[:30]}..."}`'
            if type_union
            else ''
        } with tuple{
            f' `{type_tuple if len(type_tuple) < 30 else f"{type_tuple[:30]}..."}`'
            if type_tuple
            else ''
        }"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @override
    def generic_visit(self, node: ast.AST) -> None:
        match node:
            case ast.Call(
                func=(
                    ast.Name(id="isinstance")
                    | ast.Name(id="issubclass")
                    | ast.Attribute(
                        value=ast.Name(id="builtins"), attr="isinstance" | "issubclass"
                    )
                ),
                args=[_, ast.BinOp(op=ast.BitOr()) as type_union],
            ):
                self.problems[(node.lineno, node.col_offset)] = {"type_union": type_union}

        super().generic_visit(node=node)
