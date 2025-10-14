"""Linting rule to warn about declaring `*args` or `**kwargs` as function parameters."""  # noqa: N999

import ast
from enum import Enum
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR150",)


class RuleCAR150(CarrotRule, ast.NodeVisitor):
    """Linting rule to warn about declaring `*args` or `**kwargs` as function parameters."""

    class _InvalidArgumentType(Enum):
        STAR_ARGS = "`*args`"
        STAR_STAR_KWARGS = "`**kwargs`"

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        invalid_argument_type: object | None = ctx.get("invalid_argument_type", None)
        if invalid_argument_type is not None and not isinstance(
            invalid_argument_type, cls._InvalidArgumentType
        ):
            raise TypeError

        return f"Use of {
            invalid_argument_type.value
            if invalid_argument_type is not None
            else '`*args` or `**kwargs`'
        } in function definition"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    def _check_args(self, args: ast.arguments) -> None:
        if args.vararg is not None:
            self.problems[(args.vararg.lineno, args.vararg.col_offset - 1)] = {
                "invalid_argument_type": self._InvalidArgumentType.STAR_ARGS,
            }

        if args.kwarg is not None:
            self.problems[(args.kwarg.lineno, args.kwarg.col_offset - 2)] = {
                "invalid_argument_type": self._InvalidArgumentType.STAR_STAR_KWARGS,
            }

    @utils.generic_visit_before_return
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_args(node.args)

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_args(node.args)
