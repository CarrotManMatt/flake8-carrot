"""Linting rule to ensure assignment of `logging.Logger` objects are annotated as final."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR201",)


class RuleCAR201(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure assignment of `logging.Logger` objects are annotated as final."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "Assignment of `logging.Logger` object should be annotated as `Final[Logger]`"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    def _add_unannotated_problem(self, node: ast.Assign) -> None:
        self.problems.add_without_ctx(
            (
                (
                    node.targets[-1].end_lineno or node.targets[-1].lineno
                    if len(node.targets) > 0
                    else node.lineno
                ),
                (
                    node.targets[-1].end_col_offset or node.targets[-1].col_offset
                    if len(node.targets) > 0
                    else node.col_offset
                ),
            ),
        )

    @classmethod
    def _check_slice_elements(cls, slice_elements: Sequence[ast.expr]) -> bool:
        slice_element: ast.expr
        for slice_element in slice_elements:
            variable_name: str
            match slice_element:
                case ast.Name(id=variable_name):
                    if "logger" in variable_name.lower():
                        return True
                case ast.Constant(value=str(variable_name)):
                    if "logger" in variable_name.lower():
                        return True

        return False

    @classmethod
    def _match_single_target(cls, target: ast.Name | ast.expr) -> bool:
        variable_name: str
        match target:
            case ast.Subscript(value=ast.Name(id=variable_name)):
                if "loggers" in variable_name.lower():
                    return True

        slice_elements: Sequence[ast.expr]
        match target:
            case ast.Name(id=variable_name) if "logger" in variable_name.lower():
                return True

            case ast.Subscript(slice=ast.Name(id=variable_name)) if (
                "logger" in variable_name.lower()
            ):
                return True

            case ast.Subscript(slice=ast.Constant(value=str(variable_name))) if (
                "logger" in variable_name.lower()
            ):
                return True

            case ast.Subscript(slice=ast.Tuple(elts=slice_elements)) if (
                cls._check_slice_elements(slice_elements)
            ):
                return True

            case _:
                return False

    @utils.generic_visit_before_return
    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        match node.value:
            case (
                ast.Call(func=ast.Attribute(value=ast.Name(id="logging"), attr="getLogger"))
                | ast.Call(func=ast.Name(id="getLogger"))
            ):
                self._add_unannotated_problem(node)
                return

        target: ast.expr
        for target in node.targets:
            if self._match_single_target(target):
                self._add_unannotated_problem(node)
                return

    @utils.generic_visit_before_return
    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        match node.annotation:
            case (
                ast.Constant(value="Final[Logger]")
                | ast.Subscript(value=ast.Name(id="Final"), slice=ast.Name(id="Logger"))
            ):
                return

            case (
                ast.Constant(value=("Logger" | "logging.Logger" | "Final[logging.Logger]"))
                | ast.Name(id="Logger")
                | ast.Attribute(value=ast.Name(id="logging"), attr="Logger")
                | ast.Subscript(
                    value=ast.Name(id="Final"),
                    slice=ast.Attribute(value=ast.Name(id="logging"), attr="Logger"),
                )
            ):
                self.problems.add_without_ctx(
                    (node.annotation.lineno, node.annotation.col_offset),
                )
                return

        if self._match_single_target(node.target):
            self.problems.add_without_ctx(
                (node.annotation.lineno, node.annotation.col_offset),
            )
            return

        match node.value:
            case ast.Call(
                func=(
                    ast.Name(id="getLogger")
                    | ast.Attribute(value=ast.Name(id="logging"), attr="getLogger")
                ),
            ):
                self.problems.add_without_ctx(
                    (node.annotation.lineno, node.annotation.col_offset),
                )
                return

    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return

    @override
    def visit_For(self, node: ast.For) -> None:
        return
