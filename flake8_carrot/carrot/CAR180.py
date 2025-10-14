"""Linting rule to suggest replacing repeated boolean operators with `all()`/`any()`."""  # noqa: N999

import ast
from enum import Enum
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR180",)


class RuleCAR180(CarrotRule, ast.NodeVisitor):
    """Linting rule to suggest replacing repeated boolean operators with `all()`/`any()`."""

    class _OpType(Enum):
        OR = "or", "any(...)"
        AND = "and", "all(...)"

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        op_type: object | None = ctx.get("op_type", None)
        if op_type is not None and not isinstance(op_type, cls._OpType):
            raise TypeError

        return f"Replace repeated {
            f' `... {op_type.value[0]} ...`' if op_type is not None else 'boolean operator'
        } with {f' `{op_type.value[1]}`' if op_type is not None else 'call to `any()`/'}"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @utils.generic_visit_before_return
    @override
    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        if len(node.values) < 4:
            return

        match node.op:
            case ast.Or():
                self.problems[(node.lineno, node.col_offset)] = {"op_type": self._OpType.OR}
            case ast.And():
                self.problems[(node.lineno, node.col_offset)] = {"op_type": self._OpType.AND}
