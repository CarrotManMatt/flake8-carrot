"""
Linting rule to ensure the `__all__` export is a tuple.

Only applies to simple static `__all__` exports.
"""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR104",)


class RuleCAR104(CarrotRule, ast.NodeVisitor):
    """
    Linting rule to ensure the `__all__` export is a tuple.

    Only applies to simple static `__all__` exports.
    """

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "Simple `__all__` export should be of type `tuple`, not `list`"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @classmethod
    def _targets_contain_all(cls, targets: Iterable[ast.expr]) -> bool:
        target: ast.expr
        for target in targets:
            match target:
                case ast.Name(id="__all__"):
                    return True

        return False

    @utils.generic_visit_before_return
    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        if self.plugin.first_all_export_line_numbers is None:
            return

        if node.lineno != self.plugin.first_all_export_line_numbers[0]:
            return

        if not isinstance(node.value, ast.List):
            return

        if self._targets_contain_all(node.targets):
            self.problems.add_without_ctx((node.value.lineno, node.value.col_offset))

    @utils.generic_visit_before_return
    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if self.plugin.first_all_export_line_numbers is None:
            return

        if node.lineno != self.plugin.first_all_export_line_numbers[0]:
            return

        if not isinstance(node.value, ast.List):
            return

        match node.target:
            case ast.Name(id="__all__"):
                self.problems.add_without_ctx((node.value.lineno, node.value.col_offset))
