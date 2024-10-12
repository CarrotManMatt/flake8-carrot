""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR112",)


import ast
from ast import NodeVisitor
from collections.abc import Iterable, Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR112(CarrotRule, NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        definition_type: object | None = ctx.get("definition_type", None)
        if definition_type is not None and not isinstance(definition_type, str):
            raise TypeError

        return (
            "CAR112 "
            f"{
                f"{definition_type.strip().capitalize()} definition"
                if definition_type is not None
                else "Function/class/for-loop/if-check/while-loop definitions"
            } "
            "should not spread over multiple lines"
        )

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    @classmethod
    def _check_bodied_ast(cls, start_line_number: int, end_line_number: int | None, body_parts: Iterable[Sequence[ast.stmt]]) -> bool:  # noqa: E501
        body: Sequence[ast.stmt]
        for body in body_parts:
            if len(body) == 0:
                continue

            first_decorator_line_number: int
            match body[0]:
                case (
                    ast.FunctionDef(
                        decorator_list=[ast.expr(lineno=first_decorator_line_number), *_],
                    )
                    | ast.AsyncFunctionDef(
                        decorator_list=[ast.expr(lineno=first_decorator_line_number), *_],
                    )
                ):
                    return first_decorator_line_number - 1 != start_line_number

                case _:
                    return body[0].lineno - 1 != start_line_number

        if end_line_number is None:
            return False

        return end_line_number != start_line_number

    @utils.generic_visit_before_return
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        FUNCTION_IS_MULTILINE: Final[bool] = self._check_bodied_ast(
            node.lineno,
            node.end_lineno,
            (node.body,),
        )
        if FUNCTION_IS_MULTILINE:
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "function",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        FUNCTION_IS_MULTILINE: Final[bool] = self._check_bodied_ast(
            node.lineno,
            node.end_lineno,
            (node.body,),
        )
        if FUNCTION_IS_MULTILINE:
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "function",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        CLASS_IS_MULTILINE: Final[bool] = self._check_bodied_ast(
            node.lineno,
            node.end_lineno,
            (node.body,),
        )
        if CLASS_IS_MULTILINE:
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "class",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_For(self, node: ast.For) -> None:
        FOR_IS_MULTILINE: Final[bool] = self._check_bodied_ast(
            node.lineno,
            node.end_lineno,
            (node.body, node.orelse),
        )
        if FOR_IS_MULTILINE:
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "for-loop",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        FOR_IS_MULTILINE: Final[bool] = self._check_bodied_ast(
            node.lineno,
            node.end_lineno,
            (node.body, node.orelse),
        )
        if FOR_IS_MULTILINE:
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "for-loop",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_While(self, node: ast.While) -> None:
        WHILE_IS_MULTILINE: Final[bool] = self._check_bodied_ast(
            node.lineno,
            node.end_lineno,
            (node.body, node.orelse),
        )
        if WHILE_IS_MULTILINE:
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "while-loop",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_If(self, node: ast.If) -> None:
        IF_IS_MULTILINE: Final[bool] = self._check_bodied_ast(
            node.lineno,
            node.end_lineno,
            (node.body, node.orelse),
        )
        if IF_IS_MULTILINE:
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "if-check",
            }
            return
