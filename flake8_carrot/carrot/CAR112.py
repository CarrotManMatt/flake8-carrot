""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR112",)


import ast
from ast import NodeVisitor
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR112(CarrotRule, NodeVisitor):
    """"""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        definition_type: object | None = ctx.get("definition_type", None)
        if definition_type is not None and not isinstance(definition_type, str):
            raise TypeError

        return (
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
    def _check_function_is_multiline(cls, start_line_number: int, returns: ast.expr | None, args: ast.arguments, type_params: Sequence[ast.type_param]) -> bool:  # noqa: E501
        if returns is not None:
            return start_line_number != (returns.end_lineno or returns.lineno)

        ALL_ARGS: Sequence[ast.arg] = [
            *args.posonlyargs,
            *args.args,
            *([args.vararg] if args.vararg is not None else []),
            *args.kwonlyargs,
            *([args.kwarg] if args.kwarg is not None else []),
        ]
        if ALL_ARGS:
            return start_line_number != (ALL_ARGS[-1].end_lineno or ALL_ARGS[-1].lineno)

        if type_params:
            return start_line_number != (type_params[-1].end_lineno or type_params[-1].lineno)

        return False

    @classmethod
    def _check_class_is_multiline(cls, start_line_number: int, keywords: Sequence[ast.keyword], bases: Sequence[ast.expr], type_params: Sequence[ast.type_param]) -> bool:  # noqa: E501
        if keywords:
            return start_line_number != (keywords[-1].end_lineno or keywords[-1].lineno)

        if bases:
            return start_line_number != (bases[-1].end_lineno or bases[-1].lineno)

        if type_params:
            return start_line_number != (type_params[-1].end_lineno or type_params[-1].lineno)

        return False

    @classmethod
    def _check_for_loop_is_multiline(cls, start_line_number: int, for_iter: ast.expr) -> bool:
        return start_line_number != (for_iter.end_lineno or for_iter.lineno)

    @classmethod
    def _check_while_loop_is_multiline(cls, start_line_number: int, test: ast.expr) -> bool:
        return start_line_number != (test.end_lineno or test.lineno)

    @classmethod
    def _check_if_statement_is_multiline(cls, start_line_number: int, test: ast.expr) -> bool:
        return start_line_number != (test.end_lineno or test.lineno)

    @utils.generic_visit_before_return
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        FUNCTION_IS_MULTILINE: Final[bool] = self._check_function_is_multiline(
            node.lineno,
            node.returns,
            node.args,
            node.type_params,
        )
        if FUNCTION_IS_MULTILINE:
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "function",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        FUNCTION_IS_MULTILINE: Final[bool] = self._check_function_is_multiline(
            node.lineno,
            node.returns,
            node.args,
            node.type_params,
        )
        if FUNCTION_IS_MULTILINE:
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "function",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        CLASS_IS_MULTILINE: Final[bool] = self._check_class_is_multiline(
            node.lineno,
            node.keywords,
            node.bases,
            node.type_params
        )
        if CLASS_IS_MULTILINE:
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "class",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_For(self, node: ast.For) -> None:
        if self._check_for_loop_is_multiline(node.lineno, node.iter):
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "for-loop",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        if self._check_for_loop_is_multiline(node.lineno, node.iter):
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "for-loop",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_While(self, node: ast.While) -> None:
        if self._check_while_loop_is_multiline(node.lineno, node.test):
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "while-loop",
            }
            return

    @utils.generic_visit_before_return
    @override
    def visit_If(self, node: ast.If) -> None:
        if self._check_if_statement_is_multiline(node.lineno, node.test):
            self.problems[(node.lineno, node.col_offset)] = {
                "definition_type": "if-check",
            }
            return
