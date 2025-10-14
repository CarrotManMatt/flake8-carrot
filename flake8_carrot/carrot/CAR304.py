"""Linting rule to ensure Pycord command and option names end with a full-stop."""  # noqa: N999

import ast
from enum import Enum
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR304",)


class RuleCAR304(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure Pycord command and option names end with a full-stop."""

    class _FunctionType(Enum):
        COMMAND = "command"
        OPTION = "option"

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        function_type: object | None = ctx.get("function_type", None)
        if function_type is not None and not isinstance(function_type, cls._FunctionType):
            raise TypeError

        return f"Pycord {
            function_type.value if function_type is not None else 'command/option'
        } description should end with a full-stop"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    def _check_single_argument(self, argument: ast.expr, function_type: _FunctionType) -> None:  # noqa: PLR0911, PLR0912
        if not isinstance(argument, ast.Constant):
            return

        if not argument.value or not isinstance(argument.value, str):
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
        if argument.value.endswith('"'):
            double_quote_count: int = argument.value.count('"')
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
            (argument.end_col_offset - 1) if argument.end_col_offset else argument.col_offset
        )
        self.problems[(argument.lineno, column_offset)] = {
            "function_type": function_type,
        }

    def _check_all_arguments(
        self, decorator_node: ast.Call, function_type: _FunctionType
    ) -> None:
        if len(decorator_node.args) >= 2:
            self._check_single_argument(decorator_node.args[1], function_type)

        keyword_argument: ast.keyword
        for keyword_argument in decorator_node.keywords:
            if keyword_argument.arg == "description":
                self._check_single_argument(keyword_argument.value, function_type)
                return

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
                if (
                    possible_slash_command_group_name
                    in self.plugin.found_slash_command_group_names
                    and possible_pycord_decorator_name
                    in (
                        utils.PYCORD_SLASH_COMMAND_DECORATOR_NAMES
                        | utils.PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES
                    )
                ):
                    self._check_all_arguments(decorator_node, self._FunctionType.COMMAND)
                    return

                if (
                    possible_slash_command_group_name
                    in self.plugin.found_slash_command_group_names
                    and possible_pycord_decorator_name in utils.PYCORD_OPTION_DECORATOR_NAMES
                ):
                    self._check_all_arguments(decorator_node, self._FunctionType.OPTION)
                    return

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        decorator_node: ast.expr
        for decorator_node in node.decorator_list:
            self._check_decorator(decorator_node)
