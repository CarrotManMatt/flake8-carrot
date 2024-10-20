""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR601",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR601(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "Prefer to use `re.fullmatch()` over `re.match()`"

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    @utils.generic_visit_before_return
    @override
    def visit_Call(self, node: ast.Call) -> None:
        match node:
            case ast.Call(
                func=(
                    ast.Attribute(value=ast.Name(id="re"), attr="match")
                    | ast.Name(id="match")
                ),
                args=[ast.Constant(value=str()), *_],
            ):
                self.problems.add_without_ctx((node.func.lineno, node.func.col_offset))
                return

        first_argument: str
        match node:
            case ast.Call(
                func=(
                    ast.Attribute(value=ast.Name(id="re"), attr="match")
                    | ast.Name(id="match")
                ),
                args=[ast.Name(id=first_argument), *_],
            ):
                if first_argument.isupper():
                    self.problems.add_without_ctx((node.func.lineno, node.func.col_offset))
                    return
