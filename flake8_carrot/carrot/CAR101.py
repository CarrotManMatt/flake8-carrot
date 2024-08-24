""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR101",)


import ast
from collections.abc import Iterator, Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR101(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR101 Missing `__all__` export at the top of the module"

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
        if self.plugin.first_all_export_line_numbers is None:
            error_line_number: int
            error_column_number: int
            error_line_number, error_column_number = self.get_error_position(tree, lines)

            self.problems.add_without_ctx(
                (max(error_line_number, 1), max(error_column_number, 0)),
            )
