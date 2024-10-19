""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR303",)


import ast
import re
from collections.abc import Mapping
from enum import Enum
from tokenize import TokenInfo
from typing import Final, Literal, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR303(CarrotRule, ast.NodeVisitor):
    """"""

    class _FunctionType(Enum):
        COMMAND = "slash-command"
        OPTION = "option"

    class _InvalidArgumentReason(Enum):
        REQUIRES_HYPHENATION = "should be hyphenated"
        REQUIRES_LOWERCASING = "should be lowercased"
        REQUIRES_BOTH = "should be both hyphenated and lowercased"

        @classmethod
        def from_bools(cls, *, requires_hyphenation: bool, requires_lowercasing: bool) -> "RuleCAR303._InvalidArgumentReason | Literal[False]":  # noqa: E501
            """"""
            if requires_hyphenation and requires_lowercasing:
                return cls.REQUIRES_BOTH

            if requires_hyphenation:
                return cls.REQUIRES_HYPHENATION

            if requires_lowercasing:
                return cls.REQUIRES_LOWERCASING

            return False

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        function_type: object | None = ctx.get("function_type", None)
        if function_type is not None and not isinstance(function_type, cls._FunctionType):
            raise TypeError

        incorrect_name: object | None = ctx.get("incorrect_name", None)
        if incorrect_name is not None and not isinstance(incorrect_name, str):
            raise TypeError

        invalid_argument_reason: object | None = ctx.get("invalid_argument_reason", None)
        INVALID_ARGUMENT_REASON_IS_INVALID_TYPE: Final[bool] = bool(
            invalid_argument_reason is not None
            and not isinstance(invalid_argument_reason, cls._InvalidArgumentReason)  # noqa: COM812
        )
        if INVALID_ARGUMENT_REASON_IS_INVALID_TYPE:
            raise TypeError

        if incorrect_name:
            incorrect_name = incorrect_name.strip().strip("'").strip()

        corrected_name: str | None = (
            f"{
                incorrect_name[:-1].replace(
                    ".",
                    "-",
                ).replace(
                    " ",
                    "-",
                ).replace(
                    "_",
                    "-",
                )
            }{incorrect_name[-1]}"
            if (
                incorrect_name is not None
                and (
                    invalid_argument_reason is cls._InvalidArgumentReason.REQUIRES_HYPHENATION
                    or invalid_argument_reason is cls._InvalidArgumentReason.REQUIRES_BOTH
                )
            )
            else incorrect_name
        )

        corrected_name = (
            corrected_name.lower()
            if corrected_name is not None
            else corrected_name
        )

        return (
            f"Pycord {
                function_type.value
                if function_type is not None
                else "slash-command/option"
            } name"
            f"{f" '{incorrect_name}'" if incorrect_name else ""} "
            f"{
                invalid_argument_reason.value  # type: ignore[attr-defined]
                if invalid_argument_reason is not None
                else "should be hyphenated and/or lowercased"
            } "
            f"{f": '{corrected_name}'" if corrected_name else ""}"
        )

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    def _check_single_argument(self, argument: ast.expr, function_type: _FunctionType) -> None:
        if not isinstance(argument, ast.Constant):
            return

        if not argument.value or not isinstance(argument.value, str):
            return

        reason: RuleCAR303._InvalidArgumentReason | Literal[False] = (
            self._InvalidArgumentReason.from_bools(
                requires_hyphenation=(
                    "." in argument.value[:-1]
                    or " " in argument.value[:-1]
                    or "_" in argument.value[:-1]
                ),
                requires_lowercasing=bool(re.search(r"[A-Z]", argument.value)),
            )
        )
        if reason is False:
            return

        # noinspection PyTypeChecker
        self.problems[(argument.lineno, argument.col_offset + 1)] = {
            "function_type": function_type,
            "incorrect_name": argument.value,
            "invalid_argument_reason": reason,
        }

    def _check_all_arguments(self, decorator_node: ast.Call, function_type: _FunctionType) -> None:  # noqa: E501
        if decorator_node.args:
            self._check_single_argument(decorator_node.args[0], function_type)

        keyword_argument: ast.keyword
        for keyword_argument in decorator_node.keywords:
            if keyword_argument.arg == "name":
                self._check_single_argument(keyword_argument.value, function_type)
                return

    def _check_decorator(self, decorator_node: ast.expr) -> None:
        if not isinstance(decorator_node, ast.Call):
            return

        if utils.function_call_is_pycord_slash_command_decorator(decorator_node):
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
                    and possible_pycord_decorator_name in utils.PYCORD_SLASH_COMMAND_DECORATOR_NAMES  # noqa: E501, COM812
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
