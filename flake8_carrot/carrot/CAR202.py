"""Linting rule to ensure `logging.Logger` variables contain the word 'logger'."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR202",)


class RuleCAR202(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure `logging.Logger` variables contain the word 'logger'."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "`logging.Logger` variable name should contain the word 'logger'"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @utils.generic_visit_before_return
    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        if "logger" in "".join(ast.unparse(target) for target in node.targets).lower():
            return

        match node.value:
            case ast.Call(
                func=(
                    ast.Name(id="getLogger")
                    | ast.Attribute(value=ast.Name(id="logging"), attr="getLogger")
                ),
            ):
                self.problems.add_without_ctx((node.lineno, node.col_offset))

    @utils.generic_visit_before_return
    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if "logger" in ast.unparse(node.target).lower():
            return

        match node.value:
            case ast.Call(
                func=(
                    ast.Name(id="getLogger")
                    | ast.Attribute(value=ast.Name(id="logging"), attr="getLogger")
                ),
            ):
                self.problems.add_without_ctx((node.target.lineno, node.target.col_offset))

        match node.annotation:
            case (
                ast.Constant(
                    value=(
                        "Logger" | "logging.Logger" | "FinalLogger]" | "Final[logging.Logger]"
                    ),
                )
                | ast.Name(id="Logger")
                | ast.Attribute(value=ast.Name(id="logging"), attr="Logger")
                | ast.Subscript(
                    value=ast.Name(id="Final"),
                    slice=(
                        ast.Name(id="Logger")
                        | ast.Attribute(value=ast.Name(id="logging"), attr="Logger")
                    ),
                )
            ):
                self.problems.add_without_ctx((node.target.lineno, node.target.col_offset))
