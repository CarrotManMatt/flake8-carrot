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
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    def _check_single_argument(self, argument: ast.expr, function_type: _FunctionType) -> None:
        if not isinstance(argument, ast.Constant):
            return

        INVALID_ARGUMENT_ENDING: Final[bool] = bool(
            not argument.value.endswith(".")
            and not bool(
                argument.value.endswith("!")
                or argument.value.endswith("?")
                or argument.value.endswith(";")
                or argument.value.endswith("%")
                or bool(
                    argument.value.endswith("]")
                    and "[" in argument.value  # noqa: COM812
                )
                or bool(
                    argument.value.endswith(")")
                    and "(" in argument.value  # noqa: COM812
                )
                or bool(
                    argument.value.endswith("}")
                    and "{" in argument.value  # noqa: COM812
                )
                or bool(
                    argument.value.endswith(">")
                    and "<" in argument.value  # noqa: COM812
                )
                or bool(
                    argument.value.endswith("\"")
                    and argument.value.count("\"") > 1
                    and argument.value.count("\"") % 2 == 0  # noqa: COM812
                )
                or bool(
                    argument.value.endswith("'")
                    and argument.value.count("'") > 1
                    and argument.value.count("'") % 2 == 0  # noqa: COM812
                )
                or bool(
                    argument.value.endswith("`")
                    and argument.value.count("`") > 1
                    and argument.value.count("`") % 2 == 0  # noqa: COM812
                )
                or bool(
                    argument.value.endswith("*")
                    and argument.value.count("*") > 1
                    and argument.value.count("*") % 2 == 0  # noqa: COM812
                )
                or bool(
                    argument.value.endswith("_")
                    and argument.value.count("_") > 1
                    and argument.value.count("_") % 2 == 0  # noqa: COM812
                )
                or bool(
                    argument.value.endswith("~")
                    and argument.value.count("~") > 1
                    and argument.value.count("~") % 2 == 0  # noqa: COM812
                )  # noqa: COM812
            )  # noqa: COM812
        )
        if INVALID_ARGUMENT_ENDING:
            # noinspection PyTypeChecker
            self.problems[(argument.lineno, (argument.end_col_offset - 1) if argument.end_col_offset else argument.col_offset)] = {  # noqa: E501
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

        FUNCTION_CALL_IS_PYCORD_COMMAND_FUNCTION: Final[bool] = bool(
            utils.function_call_is_pycord_slash_command_decorator(decorator_node)
            or utils.function_call_is_pycord_context_command_decorator(decorator_node)
            or bool(
                isinstance(decorator_node.func, ast.Attribute)
                and isinstance(decorator_node.func.value, ast.Name)
                and decorator_node.func.value.id in self.plugin.found_slash_command_group_names
                and decorator_node.func.attr in (
                    utils.PYCORD_SLASH_COMMAND_DECORATOR_NAMES
                    | utils.PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES
                )  # noqa: COM812
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
