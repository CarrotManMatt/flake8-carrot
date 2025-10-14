"""Linting rule to warn about passing `*args` or `**kwargs` as function arguments."""  # noqa: N999

import ast
from enum import Enum
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR151",)


class RuleCAR151(CarrotRule, ast.NodeVisitor):
    """Linting rule to warn about passing `*args` or `**kwargs` as function arguments."""

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

        return f"{
            invalid_argument_type.value
            if invalid_argument_type is not None
            else '`*args` or `**kwargs`'
        } passed to super-function call"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @utils.generic_visit_before_return
    @override
    def visit_Call(self, node: ast.Call) -> None:
        match node.func:
            case ast.Attribute(value=ast.Call(func=ast.Name(id="super"))):
                arg: ast.expr
                for arg in node.args:
                    if not isinstance(arg, ast.Starred):
                        continue

                    self.problems[(arg.lineno, arg.col_offset)] = {
                        "invalid_argument_type": self._InvalidArgumentType.STAR_ARGS,
                    }

                kwarg: ast.keyword
                for kwarg in node.keywords:
                    if kwarg.arg is not None:
                        continue

                    self.problems[(kwarg.lineno, kwarg.col_offset)] = {
                        "invalid_argument_type": self._InvalidArgumentType.STAR_STAR_KWARGS,
                    }

                return
