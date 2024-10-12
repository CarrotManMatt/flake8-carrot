""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR304",)


import ast
from collections.abc import Mapping
from enum import Enum
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR304(CarrotRule, ast.NodeVisitor):
    """"""

    class _FunctionType(Enum):
        COMMAND = "command"
        OPTION = "option"

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        function_type: object | None = ctx.get("function_type", None)
        if function_type is not None and not isinstance(function_type, cls._FunctionType):
            raise TypeError

        return (
            "CAR304 "
            f"Pycord {
                function_type.value
                if function_type is not None
                else "command/option"
            } description should end with a full-stop"
        )

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    def _check_single_argument(self, argument: ast.expr, function_type: _FunctionType) -> None:  # noqa: C901, PLR0911, PLR0912
        if not isinstance(argument, ast.Constant) or not isinstance(argument.value, str):
            return

        if argument.value.endswith("."):
            return
        if argument.value.endswith("!"):
            return
        if argument.value.endswith("?"):
            return
        if argument.value.endswith(";"):
            return
        if argument.value.endswith("%"):
            return
        if argument.value.endswith("]") and "[" in argument.value:
            return
        if argument.value.endswith(")") and "(" in argument.value:
            return
        if argument.value.endswith("}") and "{" in argument.value:
            return
        if argument.value.endswith(">") and "<" in argument.value:
            return
        if argument.value.endswith("\""):
            double_quote_count: int = argument.value.count("\"")
            if double_quote_count > 1 and double_quote_count % 2 == 0:
                return
        if argument.value.endswith("'"):
            single_quote_count: int = argument.value.count("'")
            if single_quote_count > 1 and single_quote_count % 2 == 0:
                return
        if argument.value.endswith("`"):
            backtick_count: int = argument.value.count("`")
            if backtick_count > 1 and backtick_count % 2 == 0:
                return
        if argument.value.endswith("*"):
            asterisk_count: int = argument.value.count("*")
            if asterisk_count > 1 and asterisk_count % 2 == 0:
                return
        if argument.value.endswith("_"):
            underscore_count: int = argument.value.count("_")
            if underscore_count > 1 and underscore_count % 2 == 0:
                return
        if argument.value.endswith("~"):
            tilde_count: int = argument.value.count("~")
            if tilde_count > 1 and tilde_count % 2 == 0:
                return

        column_offset: int = (
            (argument.end_col_offset - 1)
            if argument.end_col_offset
            else argument.col_offset
        )
        self.problems[(argument.lineno, column_offset)] = {
            "function_type": function_type,
        }

    def _check_all_arguments(self, decorator_node: ast.Call, function_type: _FunctionType) -> None:  # noqa: E501
        if len(decorator_node.args) >= 2:
            positional_argument: ast.expr = decorator_node.args[1]
            self._check_single_argument(positional_argument, function_type)

        keyword_argument: ast.keyword
        for keyword_argument in decorator_node.keywords:
            if keyword_argument.arg == "description":
                self._check_single_argument(keyword_argument.value, function_type)
                return

    # noinspection DuplicatedCode
    def _check_decorator(self, decorator_node: ast.expr) -> None:
        if not isinstance(decorator_node, ast.Call):
            return

        if utils.function_call_is_pycord_slash_command_decorator(decorator_node):
            self._check_all_arguments(decorator_node, self._FunctionType.COMMAND)
            return

        if utils.function_call_is_pycord_context_command_decorator(decorator_node):
            self._check_all_arguments(decorator_node, self._FunctionType.COMMAND)
            return

        if utils.function_call_is_pycord_option_decorator(decorator_node):
            self._check_all_arguments(decorator_node, self._FunctionType.OPTION)
            return

        possible_slash_command_group_name: str
        possible_pycord_decorator_name: str
        match decorator_node.func:
            case ast.Attribute(
                value=ast.Name(id=possible_slash_command_group_name),
                attr=possible_pycord_decorator_name,
            ):
                COMMAND_FUNCTION: Final[bool] = bool(
                    possible_slash_command_group_name in self.plugin.found_slash_command_group_names  # noqa: E501
                    and possible_pycord_decorator_name in (
                        utils.PYCORD_SLASH_COMMAND_DECORATOR_NAMES
                        | utils.PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES
                    )  # noqa: COM812
                )
                if COMMAND_FUNCTION:
                    self._check_all_arguments(decorator_node, self._FunctionType.COMMAND)
                    return

                OPTION_FUNCTION: Final[bool] = bool(
                    possible_slash_command_group_name in self.plugin.found_slash_command_group_names  # noqa: E501
                    and possible_pycord_decorator_name in utils.PYCORD_OPTION_DECORATOR_NAMES  # noqa: COM812
                )
                if OPTION_FUNCTION:
                    self._check_all_arguments(decorator_node, self._FunctionType.OPTION)
                    return

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        decorator_node: ast.expr
        for decorator_node in node.decorator_list:
            self._check_decorator(decorator_node)
