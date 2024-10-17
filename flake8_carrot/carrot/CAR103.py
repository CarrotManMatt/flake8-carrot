""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR103",)


import ast
from collections.abc import Iterable, Mapping
from tokenize import TokenInfo
from typing import override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR103(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "`__all__` export should be annotated as `Sequence[str]`"

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    @classmethod
    def _get_unannotated_all_from_assignment_targets(cls, targets: Iterable[ast.expr]) -> ast.Name | None:  # noqa: E501
        target: ast.expr
        for target in targets:
            match target:
                case ast.Name(id="__all__"):
                    # noinspection PyTypeChecker
                    return target

        return None

    @utils.generic_visit_before_return
    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        if self.plugin.first_all_export_line_numbers is None:
            return

        if node.lineno != self.plugin.first_all_export_line_numbers[0]:
            return

        all_assignment: ast.Name | None = self._get_unannotated_all_from_assignment_targets(
            node.targets,
        )
        if all_assignment is None:
            return

        self.problems.add_without_ctx(
            (
                all_assignment.lineno,
                (all_assignment.end_col_offset or all_assignment.col_offset),
            ),
        )

    @utils.generic_visit_before_return
    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if self.plugin.first_all_export_line_numbers is None:
            return

        if node.lineno != self.plugin.first_all_export_line_numbers[0]:
            return

        match node.target:
            case ast.Name(id="__all__"):
                pass
            case _:
                return

        match node.annotation:
            case ast.Subscript(value=ast.Name(id="Sequence"), slice=ast.Name(id="str")):
                return
            case ast.Constant(value="Sequence[str]"):
                return
            case ast.Name(id="Sequence") | ast.Constant(value="Sequence"):
                self.problems.add_without_ctx(
                    (
                        node.annotation.lineno,
                        (node.annotation.end_col_offset or node.annotation.col_offset) - 1,
                    ),
                )
            case _:
                self.problems.add_without_ctx(
                    (node.annotation.lineno, node.annotation.col_offset),
                )
