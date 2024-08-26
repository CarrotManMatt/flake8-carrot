""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR301",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot import utils
from flake8_carrot.utils import (
    CarrotRule,
)


class RuleCAR301(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
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
                f"{function_name[:35]}..."
                if len(function_name) > 35
                else function_name
            )

        return (
            "CAR301 "
            f"Pycord function{f" `{function_name}()`" if function_name else ""} "
            "should not be called with positional argument"
            f"{f" `{positional_argument}`" if positional_argument else "s"} "
            "(use named keyword arguments instead)"
        )

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    @override
    def visit_Call(self, node: ast.Call) -> None:
        FUNCTION_CALL_IS_PYCORD_FUNCTION: Final[bool] = bool(
            utils.function_call_is_pycord_command_decorator(node)
            or utils.function_call_is_pycord_task_decorator(node)
            or utils.function_call_is_pycord_event_listener_decorator(node)
            or bool(
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in self.plugin.found_slash_command_group_names
                and node.func.attr in utils.PYCORD_COMMAND_DECORATOR_NAMES | utils.PYCORD_OPTION_DECORATOR_NAMES  # noqa: E501, COM812
            )  # noqa: COM812
        )
        if FUNCTION_CALL_IS_PYCORD_FUNCTION:
            positional_argument: ast.expr
            for positional_argument in node.args:
                # noinspection PyTypeChecker
                self.problems[(positional_argument.lineno, positional_argument.col_offset)] = {
                    "positional_argument": ast.unparse(positional_argument),
                    "function_name": ast.unparse(node.func),
                }

        self.generic_visit(node)
