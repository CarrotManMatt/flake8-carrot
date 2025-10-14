"""
Linting rule to ensure `re.fullmatch()` is used over `re.search()`.

Only applicable when the regex pattern uses beginning and ending line anchors.
"""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR602",)


class RuleCAR602(CarrotRule, ast.NodeVisitor):
    """
    Linting rule to ensure `re.fullmatch()` is used over `re.search()`.

    Only applicable when the regex pattern uses beginning and ending line anchors.
    """

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return (
            "Use `re.fullmatch()` over `re.search()` "
            "when using beginning & ending line anchors"
        )

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @classmethod
    def _look_for_single_re_multiline(cls, arg: ast.expr) -> bool:
        match arg:
            case ast.Attribute(value=ast.Name(id="re"), attr="MULTILINE"):
                return True

        left: ast.expr
        right: ast.expr
        match arg:
            case ast.BinOp(op=ast.BitOr(), left=left, right=right):
                return cls._look_for_single_re_multiline(
                    left
                ) or cls._look_for_single_re_multiline(right)

        return False

    @utils.generic_visit_before_return
    @override
    def visit_Call(self, node: ast.Call) -> None:
        regex: str
        remaining_args: Iterable[ast.expr]
        match node:
            case ast.Call(
                func=(
                    ast.Attribute(value=ast.Name(id="re"), attr="search")
                    | ast.Name(id="search")
                ),
                args=[ast.Constant(value=str(regex)), *remaining_args],
            ):
                if regex.startswith(r"\A") and regex.endswith(r"\Z"):
                    self.problems.add_without_ctx((node.func.lineno, node.func.col_offset))
                    return

                if (
                    any(self._look_for_single_re_multiline(arg) for arg in remaining_args)
                    and regex.startswith(r"^")
                    and regex.endswith(r"$")
                ):
                    self.problems.add_without_ctx((node.func.lineno, node.func.col_offset))
                    return

                return
