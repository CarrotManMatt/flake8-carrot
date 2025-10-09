""""""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR301",)


class RuleCAR301(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        positional_argument: object | None = ctx.get("positional_argument", None)
        if positional_argument is not None:
            if not isinstance(positional_argument, str):
                raise TypeError

            positional_argument = (
                f"{positional_argument[:35]}..."
                if len(positional_argument) > 35
                else positional_argument
            )

        function_name: object | None = ctx.get("function_name", None)
        if function_name is not None:
            if not isinstance(function_name, str):
                raise TypeError

            function_name = (
                f"{function_name[:35]}..." if len(function_name) > 35 else function_name
            )

        return (
            f"Pycord function{f' `{function_name}()`' if function_name else ''} "
            "should not be called with positional argument"
            f"{f' `{positional_argument}`' if positional_argument else 's'} "
            "(use named keyword arguments instead)"
        )

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    def _check_for_positional_arguments(self, node: ast.Call) -> None:
        positional_argument: ast.expr
        for positional_argument in node.args:
            self.problems[(positional_argument.lineno, positional_argument.col_offset)] = {
                "positional_argument": ast.unparse(positional_argument),
                "function_name": ast.unparse(node.func),
            }

    @utils.generic_visit_before_return
    @override
    def visit_Call(self, node: ast.Call) -> None:
        if utils.function_call_is_any_pycord_decorator(node):
            self._check_for_positional_arguments(node)
            return

        possible_slash_command_group_name: str
        possible_pycord_function_name: str
        match node.func:
            case ast.Attribute(
                value=ast.Name(id=possible_slash_command_group_name),
                attr=possible_pycord_function_name,
            ):
                if (
                    possible_slash_command_group_name
                    in self.plugin.found_slash_command_group_names
                    and possible_pycord_function_name in utils.ALL_PYCORD_FUNCTION_NAMES
                ):
                    self._check_for_positional_arguments(node)
                    return
