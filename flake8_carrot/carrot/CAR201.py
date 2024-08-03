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
        targets: list[ast.Name] = [
            target for target in node.targets if isinstance(target, ast.Name)
        ]

        LOGGER_ASSIGNMENT_FOUND: Final[bool] = bool(
            bool(
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
                )  # noqa: COM812
            )
            or len(targets) == 1 and "logger" in targets[0].id
        )
        if LOGGER_ASSIGNMENT_FOUND:
            self.problems.add_without_ctx(
                (
                    node.lineno,
                    (
                        (targets[0].end_col_offset or targets[0].col_offset)
                        if len(targets) == 1
                        else node.col_offset
                    ),
                ),
            )

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        LOGGER_ASSIGNMENT_FOUND: Final[bool] = bool(
            bool(
                bool(
                    bool(
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
                        )  # noqa: COM812
                    )
                    or bool(
                        isinstance(node.target, ast.Name)
                        and "logger" in node.target.id  # noqa: COM812
                    )  # noqa: COM812
                )
                and not bool(
                    isinstance(node.annotation, ast.Subscript)
                    and isinstance(node.annotation.value, ast.Name)
                    and isinstance(node.annotation.slice, ast.Name)
                    and node.annotation.value.id == "Final"
                    and node.annotation.slice.id == "Logger"  # noqa: COM812
                )  # noqa: COM812
            )
            or bool(
                isinstance(node.annotation, ast.Name)
                and node.annotation.id == "Logger"  # noqa: COM812
            )
            or bool(
                isinstance(node.annotation, ast.Attribute)
                and isinstance(node.annotation.value, ast.Name)
                and node.annotation.value.id == "logging"
                and node.annotation.attr == "Logger"  # noqa: COM812
            )
            or bool(
                isinstance(node.annotation, ast.Subscript)
                and isinstance(node.annotation.value, ast.Name)
                and isinstance(node.annotation.slice, ast.Attribute)
                and isinstance(node.annotation.slice.value, ast.Name)
                and node.annotation.value.id == "Final"
                and node.annotation.slice.value.id == "logging"
                and node.annotation.slice.attr == "Logger"  # noqa: COM812
            )  # noqa: COM812
        )
        if LOGGER_ASSIGNMENT_FOUND:
            self.problems.add_without_ctx(
                (node.annotation.lineno, node.annotation.col_offset),
            )

        self.generic_visit(node)
