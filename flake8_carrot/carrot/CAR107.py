""""""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from tokenize import TokenInfo

__all__: "Sequence[str]" = ("RuleCAR107",)


class RuleCAR107(
    CarrotRule, ast.NodeVisitor
):  # NOTE: This rule can be removed once RUF022 is no longer in preview
    """"""

    @classmethod
    @override
    def _format_error_message(cls, ctx: "Mapping[str, object]") -> str:
        export_object_name: object | None = ctx.get("export_object_name", None)
        if export_object_name is not None and not isinstance(export_object_name, str):
            raise TypeError

        if export_object_name is None:
            return "`__all__` export should be in alphabetical order"

        correct_index: object | None = ctx.get("correct_index", None)
        if correct_index is not None and not isinstance(correct_index, int):
            raise TypeError

        export_object_name = export_object_name.strip().strip("`").strip()

        return (
            f"Object `{export_object_name}` "
            "within `__all__` export should be in alphabetical order"
            f"{f' (correct index: {correct_index})' if correct_index is not None else ''}"
        )

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: "Sequence[TokenInfo]", lines: "Sequence[str]"
    ) -> None:
        self.visit(tree)

    @classmethod
    def _targets_contain_all(cls, targets: "Iterable[ast.expr]") -> bool:
        target: ast.expr
        for target in targets:
            match target:
                case ast.Name(id="__all__"):
                    return True

        return False

    def _check_for_non_alphabetical_all_export_values(
        self, values: ast.List | ast.Tuple
    ) -> None:
        sorted_values: list[ast.Constant] = sorted(
            (value for value in values.elts if isinstance(value, ast.Constant)),
            key=lambda value: str(value.value),
        )

        index: int
        value: ast.expr
        for index, value in enumerate(values.elts):
            if not isinstance(value, ast.Constant):
                continue

            correct_index: int = sorted_values.index(value)

            if index != correct_index:
                self.problems[(value.lineno, value.col_offset)] = {
                    "export_object_name": value.value,
                    "correct_index": correct_index,
                }

    @utils.generic_visit_before_return
    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        if self.plugin.first_all_export_line_numbers is None:
            return

        if node.lineno != self.plugin.first_all_export_line_numbers[0]:
            return

        if not isinstance(node.value, ast.List | ast.Tuple):
            return

        if self._targets_contain_all(node.targets):
            self._check_for_non_alphabetical_all_export_values(node.value)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if self.plugin.first_all_export_line_numbers is None:
            return

        if node.lineno != self.plugin.first_all_export_line_numbers[0]:
            return

        if not isinstance(node.value, ast.List | ast.Tuple):
            return

        match node.target:
            case ast.Name(id="__all__"):
                self._check_for_non_alphabetical_all_export_values(node.value)
