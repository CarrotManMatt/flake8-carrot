""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR104",)


import ast
from collections.abc import Iterable, Mapping
from tokenize import TokenInfo
from typing import override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR104(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR104 Simple `__all__` export should be of type `tuple`, not `list`"

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
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
