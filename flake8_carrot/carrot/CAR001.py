""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR001",)

import ast
import enum
from collections.abc import Iterator
from enum import Enum
from typing import Final, override
from tokenize import TokenInfo

from classproperties import classproperty

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

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @override
    def ERROR_MESSAGE(cls) -> str:  # noqa: N805
        return (
            f"{cls.__name__.removeprefix("Rule")} "
            "Missing `__all__` export at the top of the module"
        )

    @classmethod
    def get_error_position(cls, tree: ast.AST, lines: Sequence[str]) -> tuple[int, int]:
        child_nodes: Iterator[ast.AST] = ast.iter_child_nodes(tree)
        print(repr(lines))

        try:
            first_child_node: ast.AST = next(child_nodes)
        except StopIteration:
            return 1, 0

        if isinstance(first_child_node, ast.Expr) and isinstance(first_child_node.value, ast.Constant):
            try:
                second_child_node: ast.AST = next(child_nodes)
            except StopIteration:
                if not lines[(first_child_node.end_lineno or first_child_node.lineno) - 1].endswith("\n"):
                    return (first_child_node.end_lineno or first_child_node.lineno), (first_child_node.end_col_offset or first_child_node.col_offset)

                return (first_child_node.end_lineno or first_child_node.lineno) + 1, 0

            if isinstance(second_child_node, ast.ImportFrom) and second_child_node.module == "collections.abc" and len(second_child_node.names) == 1 and second_child_node.names[0].name == "Sequence":
                try:
                    third_child_node: ast.AST = next(child_nodes)
                except StopIteration:
                    return (second_child_node.end_lineno or second_child_node.lineno), 0

                return (third_child_node.end_lineno or third_child_node.lineno), 0

            return (first_child_node.end_lineno or first_child_node.lineno), 0

        return 1, 0

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:
        if self.missing_all_export_flag is not self.MissingAllExportFlag.UNKNOWN:
            raise RuntimeError  # TODO: Message here

        super().run_check(tree=tree, file_tokens=file_tokens, lines=lines)

        if self.missing_all_export_flag is self.MissingAllExportFlag.UNKNOWN:
            error_line_number: int
            error_column_number: int
            error_line_number, error_column_number = self.get_error_position(tree, lines)

            self.problems.add((max(error_line_number, 1), max(error_column_number, 0)))

            # child_nodes: Sequence[ast.AST] = list(ast.iter_child_nodes(tree))
            #
            # best_line_number: int = 0
            #
            # if isinstance(child_nodes[0])
            #
            # node: ast.AST
            # index: int
            # for index, node in enumerate(ast.iter_child_nodes(tree)):
            #     print(node.end_lineno, index)
            #     FOUND_BETTER_IMPORT_LINE_NUMBER: bool = bool(
            #         isinstance(node, ast.ImportFrom)
            #         and node.module == "collections.abc"
            #         and ast.alias(name="Sequence", asname=None) in node.names
            #         and ((node.end_lineno or node.lineno) > best_line_number)  # noqa: COM812
            #     )
            #     if FOUND_BETTER_IMPORT_LINE_NUMBER:
            #         best_line_number = node.end_lineno or node.lineno
            #         continue
            #
            #     FOUND_BETTER_DOCSTRING_LINE_NUMBER: bool = bool(
            #         isinstance(node, ast.Expr)
            #         and isinstance(node.value, ast.Constant)
            #         and node.value.kind is None
            #         and ((node.end_lineno or node.lineno) > best_line_number)  # noqa: COM812
            #     )
            #     if FOUND_BETTER_DOCSTRING_LINE_NUMBER:
            #         best_line_number = node.end_lineno or node.lineno
            #         continue
            #
            #     break

    @override
    def visit_Module(self, node: ast.Module) -> None:
        if not node.body:
            self.problems.add((1, 0))
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
            and isinstance(node.target, ast.Name) and node.target.id == "__all__"  # noqa: COM812
        )
        if ALL_EXPORT_FOUND:
            self.missing_all_export_flag = self.MissingAllExportFlag.FOUND_ALL
            return

        self.generic_visit(node)
