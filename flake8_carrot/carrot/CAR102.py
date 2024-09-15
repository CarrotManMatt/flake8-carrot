""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR102",)


import ast
from collections.abc import Iterable, Mapping
from tokenize import TokenInfo
from typing import override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR102(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR102 Multiple `__all__` exports found in a single module"

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    @classmethod
    def _get_all_assignment(cls, targets: Iterable[ast.expr]) -> ast.Name | None:
        target: ast.expr
        for target in targets:
            match target:
                case ast.Name(id="__all__"):
                    # noinspection PyTypeChecker
                    return target
                case ast.Tuple():
                    # noinspection PyUnresolvedReferences
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
