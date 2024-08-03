""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR201",)

import ast
from typing import Final, override

from flake8_carrot.utils import BaseRule


class RuleCAR201(BaseRule):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: dict[str, object]) -> str:
        return (
            "CAR201 "
            "Assignment of `logging.Logger` object should be annotated as `Final[Logger]`"
        )

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        LOGGER_ASSIGNMENT_FOUND: Final[bool] = bool(
            isinstance(node.value, ast.Call)
            and (
                bool(
                    isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Name)
                    and node.value.func.value.id == "logging"
                    and node.value.func.attr == "getLogger"  # noqa: COM812
                )
                or bool(
                    isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "getLogger"  # noqa: COM812
                )  # noqa: COM812
            )
        )
        if LOGGER_ASSIGNMENT_FOUND:
            column_offset: int = node.col_offset

            if len(node.targets) == 1:
                no_targets_exception: StopIteration
                try:
                    variable_name: ast.Name = next(
                        iter(
                            target for target in node.targets if isinstance(target, ast.Name)
                        ),
                    )
                except StopIteration as no_targets_exception:
                    raise ValueError(
                        "No logger variable names found.",
                    ) from no_targets_exception

                column_offset = variable_name.end_col_offset or variable_name.col_offset

            self.problems.add_without_ctx((node.lineno, column_offset))

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        LOGGER_ASSIGNMENT_FOUND: Final[bool] = bool(
            isinstance(node.value, ast.Call)
            and (
                bool(
                    isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Name)
                    and node.value.func.value.id == "logging"
                    and node.value.func.attr == "getLogger"  # noqa: COM812
                )
                or bool(
                    isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "getLogger"  # noqa: COM812
                )
            )
            and not bool(
                isinstance(node.annotation, ast.Subscript)
                and isinstance(node.annotation.value, ast.Name)
                and isinstance(node.annotation.slice, ast.Name)
                and node.annotation.value.id == "Final"
                and node.annotation.slice.id == "Logger"  # noqa: COM812
            )  # noqa: COM812
        )
        if LOGGER_ASSIGNMENT_FOUND:
            self.problems.add_without_ctx(
                (node.annotation.lineno, node.annotation.col_offset),
            )

        self.generic_visit(node)
