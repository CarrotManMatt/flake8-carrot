"""Linting rule to ensure all uses of `astpretty.pprint` are removed."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR401",)


class RuleCAR401(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure all uses of `astpretty.pprint` are removed."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "`astpretty.pprint` found"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    @utils.generic_visit_before_return
    @override
    def visit_Call(self, node: ast.Call) -> None:
        function_name: str
        line_number: int
        column_number: int
        match node.func:
            case ast.Name(id=function_name, lineno=line_number, col_offset=column_number):
                if not self.plugin.pprint_imported_for_debugging:
                    return

                if "print" in function_name.lower():
                    self.problems.add_without_ctx((line_number, column_number))
                    return

                return

        module_name: str
        match node.func:
            case ast.Attribute(
                value=ast.Name(id=module_name),
                attr=function_name,
                lineno=line_number,
                col_offset=column_number,
            ):
                if module_name in utils.PPRINT_MODULES and "print" in function_name.lower():
                    self.problems.add_without_ctx((line_number, column_number))
                    return

                return
