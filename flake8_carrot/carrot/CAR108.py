""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR108",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR108(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        export_object_name: object | None = ctx.get("export_object_name", None)
        if export_object_name is not None and not isinstance(export_object_name, str):
            raise TypeError

        correct_index: object | None = ctx.get("correct_index", None)
        if correct_index is not None and not isinstance(correct_index, int):
            raise TypeError

        if export_object_name is None:
            return "CAR108 `__all__` export should be in alphabetical order"

        return (
            "CAR108 "
            f"Object `{export_object_name}` "
            "within `__all__` export should be in alphabetical order"
            f"{f" (correct index: {correct_index})" if correct_index is not None else ""}"
        )

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    def _check_for_non_alphabetical_all_export_values(self, values: ast.List | ast.Tuple) -> None:  # noqa: E501
        sorted_values: list[ast.Constant] = sorted(
            (value for value in values.elts if isinstance(value, ast.Constant)),
            key=lambda value: value.value,
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

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        FIRST_ALL_EXPORT_FOUND: Final[bool] = bool(
            any(
                isinstance(target, ast.Name) and target.id == "__all__"
                for target in node.targets
            )
            and isinstance(node.value, ast.List | ast.Tuple)
            and self.plugin.first_all_export_line_numbers is not None
            and node.lineno == self.plugin.first_all_export_line_numbers[0]  # noqa: COM812
        )
        if FIRST_ALL_EXPORT_FOUND:
            self._check_for_non_alphabetical_all_export_values(node.value)  # type: ignore[arg-type]

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        FIRST_ALL_EXPORT_FOUND: Final[bool] = bool(
            isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
            and isinstance(node.value, ast.List | ast.Tuple)
            and self.plugin.first_all_export_line_numbers is not None
            and node.lineno == self.plugin.first_all_export_line_numbers[0]  # noqa: COM812
        )
        if FIRST_ALL_EXPORT_FOUND:
            self._check_for_non_alphabetical_all_export_values(node.value)  # type: ignore[arg-type]

        self.generic_visit(node)
