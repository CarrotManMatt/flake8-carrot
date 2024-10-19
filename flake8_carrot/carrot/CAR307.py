""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR307",)


import ast
import re
from collections.abc import Mapping
from enum import Enum
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR307(CarrotRule, ast.NodeVisitor):
    """"""

    class _FunctionType(Enum):
        COMMAND = "slash-command"
        OPTION = "option"

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        function_type: object | None = ctx.get("context_command_type", None)
        if function_type is not None and not isinstance(function_type, RuleCAR307._FunctionType):
            raise TypeError

        incorrect_name: object | None = ctx.get("incorrect_name", None)
        if incorrect_name is not None and not isinstance(incorrect_name, str):
            raise TypeError

        invalid_character: object | None = ctx.get("invalid_character", None)
        if invalid_character is not None and not isinstance(invalid_character, str):
            raise TypeError

        if invalid_character is not None and len(invalid_character) != 1:
            MULTIPLE_INVALID_CHARACTERS_MESSAGE: Final[str] = (
                "Multiple invalid characters were given."
            )
            raise ValueError(MULTIPLE_INVALID_CHARACTERS_MESSAGE)

        if incorrect_name:
            incorrect_name = incorrect_name.strip().strip("'").strip()

        return (
            f"Invalid character: {
                f"'{invalid_character}'" if invalid_character is not None else ""
            }"
            f" found within Pycord {
                function_type.value
                if function_type is not None
                else "slash-command/option"
            } name"
            f"{f" '{incorrect_name}'" if incorrect_name else ""}"
        )

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    def _check_single_argument(self, argument: ast.expr, function_type: "RuleCAR307._FunctionType") -> None:  # noqa: E501
        if not isinstance(argument, ast.Constant):
            return

        if not argument.value or not isinstance(argument.value, str):
            return

        if function_type is self._FunctionType.COMMAND and argument.value.endswith((".", "_", " ")):
            COLUMN_OFFSET: Final[int] = (
                argument.end_col_offset - 1
                if argument.end_col_offset is not None
                else argument.col_offset + len(argument.value) - 1
            )
            self.problems[(argument.lineno, COLUMN_OFFSET)] = {
                "invalid_character": argument.value[-1],
                "function_type": function_type,
                "incorrect_name": argument.value,
            }

        for invalid_character in "`!¬£$€%^&*+=,<>?#~`":
            invalid_character_match: re.Match[str]
            for invalid_character_match in re.finditer(fr"\{invalid_character}", argument.value):
                self.problems[(argument.lineno, argument.col_offset + invalid_character_match.span()[0] + 1)] = {  # noqa: E501
                    "invalid_character": invalid_character,
                    "function_type": function_type,
                    "incorrect_name": argument.value,
                }

    def _check_all_arguments(self, decorator_node: ast.Call, function_type: _FunctionType) -> None:  # noqa: E501
        if decorator_node.args:
            self._check_single_argument(decorator_node.args[0], function_type)

        keyword_argument: ast.keyword
        for keyword_argument in decorator_node.keywords:
            if keyword_argument.arg == "name":
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
