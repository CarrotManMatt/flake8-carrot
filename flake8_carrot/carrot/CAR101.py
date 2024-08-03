""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR001",)

import ast
import enum
from collections.abc import Iterator
from enum import Enum
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import BaseRule


class RuleCAR001(BaseRule):
    """"""

    class MissingAllExportFlag(Enum):
        """"""

        UNKNOWN = enum.auto()
        FOUND_ALL = enum.auto()
        BODY_WAS_EMPTY = enum.auto()

    @override
    def __init__(self) -> None:
        self.missing_all_export_flag: RuleCAR001.MissingAllExportFlag = (
            self.MissingAllExportFlag.UNKNOWN
        )

        super().__init__()

    @classmethod
    @override
    def format_error_message(cls, ctx: dict[str, object]) -> str:
        return "CAR001 Missing `__all__` export at the top of the module"

    @classmethod
    def get_error_position(cls, tree: ast.AST, lines: Sequence[str]) -> tuple[int, int]:  # NOTE: I'm sorry to whoever has to work out what is going on here
        """"""
        child_nodes: Iterator[ast.AST] = ast.iter_child_nodes(tree)

        try:
            first_child_node: ast.AST = next(child_nodes)
        except StopIteration:
            return 1, 0

        first_child_end_lineno: object = (
            getattr(
                first_child_node,
                "end_lineno",
                None,
            ) or getattr(  # noqa: B009
                first_child_node,
                "lineno",
            )
        )
        if not isinstance(first_child_end_lineno, int):
            raise TypeError

        FIRST_CHILD_NODE_IS_DOCSTRING: Final[bool] = bool(
            isinstance(first_child_node, ast.Expr)
            and isinstance(first_child_node.value, ast.Constant)  # noqa: COM812
        )

        if FIRST_CHILD_NODE_IS_DOCSTRING:
            try:
                second_child_node: ast.AST = next(child_nodes)
            except StopIteration:
                if not lines[first_child_end_lineno - 1].endswith("\n"):
                    return (
                        first_child_end_lineno,
                        (first_child_node.end_col_offset or first_child_node.col_offset),  # type: ignore[attr-defined]
                    )

                return (
                    min(
                        first_child_end_lineno + 2,
                        len(lines[first_child_end_lineno:]) + first_child_end_lineno + 1,
                    ),
                    0,
                )

            second_child_end_lineno: object = (
                getattr(
                    second_child_node,
                    "end_lineno",
                    None,
                ) or getattr(  # noqa: B009
                    second_child_node,
                    "lineno",
                )
            )
            if not isinstance(second_child_end_lineno, int):
                raise TypeError

            SECOND_CHILD_NODE_IS_SEQUENCE_IMPORT: Final[bool] = bool(
                isinstance(second_child_node, ast.ImportFrom)
                and second_child_node.module == "collections.abc"
                and len(second_child_node.names) == 1
                and second_child_node.names[0].name == "Sequence"  # noqa: COM812
            )
            if SECOND_CHILD_NODE_IS_SEQUENCE_IMPORT:
                try:
                    third_child_node: ast.AST = next(child_nodes)
                except StopIteration:
                    if not lines[second_child_end_lineno - 1].endswith("\n"):
                        return (
                            second_child_end_lineno,
                            (
                                second_child_node.end_col_offset  # type: ignore[attr-defined]
                                or second_child_node.col_offset  # type: ignore[attr-defined]
                            ),
                        )

                    return (
                         min(
                             second_child_end_lineno + 2,
                             (
                                 len(lines[second_child_end_lineno:])
                                 + second_child_end_lineno + 1
                             ),
                         ),
                         0,
                    )

                third_child_end_lineno: object = (
                    getattr(
                        third_child_node,
                        "end_lineno",
                        None,
                    ) or getattr(  # noqa: B009
                        third_child_node,
                        "lineno",
                    )
                )
                if not isinstance(third_child_end_lineno, int):
                    raise TypeError

                if len(lines[second_child_end_lineno:third_child_end_lineno - 1]) in (1, 2):
                    return second_child_end_lineno + 1, 0

                return (
                    min(
                        second_child_end_lineno + 2,
                        (
                            len(lines[second_child_end_lineno:third_child_end_lineno - 1])
                            + second_child_end_lineno + 1
                        ),
                    ),
                    0,
                )

            if len(lines[first_child_end_lineno:second_child_end_lineno - 1]) in (1, 2):
                return first_child_end_lineno + 1, 0

            return (
                min(
                    first_child_end_lineno + 2,
                    (
                        len(lines[first_child_end_lineno:second_child_end_lineno - 1])
                        + first_child_end_lineno + 1
                    ),
                ),
                0,
            )

        return 1, 0

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        if self.missing_all_export_flag is not self.MissingAllExportFlag.UNKNOWN:
            raise RuntimeError

        super().run_check(tree=tree, file_tokens=file_tokens, lines=lines)

        if self.missing_all_export_flag is self.MissingAllExportFlag.UNKNOWN:
            error_line_number: int
            error_column_number: int
            error_line_number, error_column_number = self.get_error_position(tree, lines)

            self.problems.add_without_ctx(
                (max(error_line_number, 1), max(error_column_number, 0)),
            )

    @override
    def visit_Module(self, node: ast.Module) -> None:
        if not node.body:
            self.problems.add_without_ctx((1, 0))
            self.missing_all_export_flag = self.MissingAllExportFlag.BODY_WAS_EMPTY
            return

        self.generic_visit(node)

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        ALL_EXPORT_FOUND: Final[bool] = bool(
            self.missing_all_export_flag is self.MissingAllExportFlag.UNKNOWN
            and any(
                isinstance(target, ast.Name) and target.id == "__all__"
                for target in node.targets
            )  # noqa: COM812
        )
        if ALL_EXPORT_FOUND:
            self.missing_all_export_flag = self.MissingAllExportFlag.FOUND_ALL
            return

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        ALL_EXPORT_FOUND: Final[bool] = bool(
            self.missing_all_export_flag is self.MissingAllExportFlag.UNKNOWN
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"  # noqa: COM812
        )
        if ALL_EXPORT_FOUND:
            self.missing_all_export_flag = self.MissingAllExportFlag.FOUND_ALL
            return

        self.generic_visit(node)
