""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR103",)

import ast
from typing import Final, override

from flake8_carrot.utils import BaseRule


class RuleCAR103(BaseRule):
    """"""

    @override
    def __init__(self) -> None:
        self.all_found_count: int = 0

        super().__init__()

    @classmethod
    @override
    def format_error_message(cls, ctx: dict[str, object]) -> str:
        return "CAR103 `__all__` export should be annotated as `Sequence[str]`"

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        all_assignment: ast.Name | None = next(
            (
                target
                for target in node.targets
                if isinstance(target, ast.Name) and target.id == "__all__"
            ),
            None,
        )
        if all_assignment is not None:
            if self.all_found_count == 0:
                self.problems.add_without_ctx(
                    (
                        all_assignment.lineno,
                        (all_assignment.end_col_offset or all_assignment.col_offset) - 1,
                    ),
                )

            self.all_found_count += 1

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        ALL_EXPORT_FOUND: Final[bool] = bool(
            isinstance(node.target, ast.Name)
            and node.target.id == "__all__"  # noqa: COM812
        )
        if ALL_EXPORT_FOUND:
            CORRECT_ANNOTATION: Final[bool] = bool(
                isinstance(node.annotation, ast.Subscript)
                and isinstance(node.annotation.value, ast.Name)
                and isinstance(node.annotation.slice, ast.Name)
                and node.annotation.value.id == "Sequence"
                and node.annotation.slice.id == "str"  # noqa: COM812
            )
            if self.all_found_count == 0 and not CORRECT_ANNOTATION:
                self.problems.add_without_ctx(
                    (
                        node.annotation.lineno,
                        (
                            (node.annotation.end_col_offset or node.annotation.col_offset) - 1
                            if isinstance(node.annotation, ast.Name) and node.annotation.id == "Sequence"
                            else node.annotation.col_offset
                        ),
                    ),
                )

            self.all_found_count += 1

        self.generic_visit(node)
