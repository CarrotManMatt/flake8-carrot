""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR102",)


import ast
from collections.abc import Iterable, Mapping
from tokenize import TokenInfo
from typing import Final, override

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
                    return cls._get_all_assignment(target.elts)
                case _:
                    continue

        return None

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        all_assignment: ast.Name | None = self._get_all_assignment(node.targets)

        IS_FIRST_ALL_EXPORT: Final[bool] = bool(
            all_assignment is not None
            and self.plugin.first_all_export_line_numbers is not None
            and all_assignment.lineno != self.plugin.first_all_export_line_numbers[0]  # noqa: COM812
        )
        if IS_FIRST_ALL_EXPORT:
            self.problems.add_without_ctx(
                (
                    all_assignment.lineno,  # type: ignore[union-attr]
                    all_assignment.col_offset,  # type: ignore[union-attr]
                ),
            )

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        MULTIPLE_ALL_EXPORTS_FOUND: Final[bool] = bool(
            isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
            and self.plugin.first_all_export_line_numbers is not None
            and node.lineno != self.plugin.first_all_export_line_numbers[0]  # noqa: COM812
        )
        if MULTIPLE_ALL_EXPORTS_FOUND:
            self.problems.add_without_ctx((node.lineno, node.col_offset))
