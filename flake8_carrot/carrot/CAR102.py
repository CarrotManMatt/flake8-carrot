"""Linting rule to ensure only a singular `__all__` export is present."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR102",)


class RuleCAR102(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure only a singular `__all__` export is present."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "Multiple `__all__` exports found in a single module"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @classmethod
    def _get_all_assignment(cls, targets: Iterable[ast.expr]) -> ast.Name | None:
        target: ast.expr
        for target in targets:
            match target:
                case ast.Name(id="__all__"):
                    return target
                case ast.Tuple():
                    return cls._get_all_assignment(target.elts)

        return None

    @utils.generic_visit_before_return
    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        if self.plugin.first_all_export_line_numbers is None:
            return

        all_assignment: ast.Name | None = self._get_all_assignment(node.targets)
        if all_assignment is None:
            return

        if all_assignment.lineno == self.plugin.first_all_export_line_numbers[0]:
            return

        self.problems.add_without_ctx((all_assignment.lineno, all_assignment.col_offset))

    @utils.generic_visit_before_return
    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if self.plugin.first_all_export_line_numbers is None:
            return

        if node.lineno == self.plugin.first_all_export_line_numbers[0]:
            return

        match node.target:
            case ast.Name(id="__all__"):
                self.problems.add_without_ctx((node.lineno, node.col_offset))
