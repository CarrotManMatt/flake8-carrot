""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR303",)


import ast
import re
from collections.abc import Mapping
from enum import Enum
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR303(CarrotRule, ast.NodeVisitor):
    """"""

    class _FunctionType(Enum):
        COMMAND = "command"
        OPTION = "option"

    class _InvalidArgumentReason(Enum):
        REQUIRES_HYPHENATION = "should be hyphenated"
        REQUIRES_LOWERCASING = "should be lowercased"
        REQUIRES_BOTH = "should be both hyphenated and lowercased"


    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        function_type: object | None = ctx.get("function_type", None)
        if function_type is not None and not isinstance(function_type, cls._FunctionType):
            raise TypeError

        incorrect_name: object | None = ctx.get("incorrect_name", None)
        if incorrect_name is not None and not isinstance(incorrect_name, str):
            raise TypeError

        invalid_argument_reason: object | None = ctx.get("invalid_argument_reason", None)
        if invalid_argument_reason is not None and not isinstance(invalid_argument_reason, cls._InvalidArgumentReason):
            raise TypeError

        hyphenated_name: str | None = (
            incorrect_name.strip("").replace(
                ".",
                "-",
            ).replace(
                " ",
                "-",
            ).replace(
                "_",
                "-",
            ).lower()
            if incorrect_name is not None
            else incorrect_name
        )

        return (
            "CAR303 "
            f"Pycord {
                function_type.value
                if function_type is not None
                else "command/option"
            } name"
            f"{f" '{incorrect_name}'" if incorrect_name else ""} "
            f"{
                invalid_argument_reason.value
                if invalid_argument_reason is not None
                else "should be hyphenated and/or lowercased"
            } "
            f"{f": '{hyphenated_name}'" if hyphenated_name else ""}"
        )

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:
        self.visit(tree)

    def _check_single_argument(self, argument: ast.expr, function_type: _FunctionType) -> bool:
        if not isinstance(argument, ast.Constant):
            return False

        ARGUMENT_NEEDS_HYPHENATION: Final[bool] = bool(
            "." in argument.value
            or " " in argument.value
            or "_" in argument.value
        )
        ARGUMENT_NEEDS_LOWERCASING: Final[bool] = bool(
            re.search(r"[A-Z]", argument.value)
        )
        if not ARGUMENT_NEEDS_HYPHENATION and not ARGUMENT_NEEDS_LOWERCASING:
            return False

        # noinspection PyTypeChecker
        self.problems[(argument.lineno, argument.col_offset + 1)] = {  # noqa: E501
            "function_type": function_type,
            "incorrect_name": argument.value,
            "invalid_argument_reason": (
                self._InvalidArgumentReason.REQUIRES_BOTH
                if ARGUMENT_NEEDS_HYPHENATION and ARGUMENT_NEEDS_LOWERCASING
                else (
                    self._InvalidArgumentReason.REQUIRES_HYPHENATION
                    if ARGUMENT_NEEDS_HYPHENATION
                    else self._InvalidArgumentReason.REQUIRES_LOWERCASING
                )
            ),
        }

        return True

    def _check_all_arguments(self, decorator_node: ast.Call, function_type: _FunctionType) -> None:
        if decorator_node.args:
            positional_argument: ast.expr = decorator_node.args[0]
            self._check_single_argument(positional_argument, function_type)

        keyword_argument: ast.keyword
        for keyword_argument in decorator_node.keywords:
            if keyword_argument.arg == "name" and self._check_single_argument(keyword_argument.value, function_type):
                return

    def _check_decorator(self, decorator_node: ast.expr) -> None:
        if not isinstance(decorator_node, ast.Call):
            return

        FUNCTION_CALL_IS_PYCORD_COMMAND_FUNCTION: Final[bool] = bool(
            utils.function_call_is_pycord_command_decorator(decorator_node)
            or bool(
                isinstance(decorator_node.func, ast.Attribute)
                and isinstance(decorator_node.func.value, ast.Name)
                and decorator_node.func.value.id in self.plugin.found_slash_command_group_names
                and decorator_node.func.attr in utils.PYCORD_COMMAND_DECORATOR_NAMES  # noqa: COM812
            )  # noqa: COM812
        )
        if FUNCTION_CALL_IS_PYCORD_COMMAND_FUNCTION:
            self._check_all_arguments(decorator_node, self._FunctionType.COMMAND)

        FUNCTION_CALL_IS_PYCORD_OPTION_FUNCTION: Final[bool] = bool(
            utils.function_call_is_pycord_option_decorator(decorator_node)
            or bool(
                isinstance(decorator_node.func, ast.Attribute)
                and isinstance(decorator_node.func.value, ast.Name)
                and decorator_node.func.value.id in self.plugin.found_slash_command_group_names
                and decorator_node.func.attr in utils.PYCORD_OPTION_DECORATOR_NAMES  # noqa: COM812
            )  # noqa: COM812
        )
        if FUNCTION_CALL_IS_PYCORD_OPTION_FUNCTION:
            self._check_all_arguments(decorator_node, self._FunctionType.OPTION)

    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        decorator_node: ast.expr
        for decorator_node in node.decorator_list:
            self._check_decorator(decorator_node)

        self.generic_visit(node)
