"""Linting rule to ensure Pycord context command names are capitalised."""  # noqa: N999

import ast
from enum import Enum
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo
    from typing import Final, Self

__all__: Sequence[str] = ("RuleCAR305",)


class _ContextCommandType(Enum):
    MESSAGE = "message"
    USER = "user"

    @classmethod
    def format_value(cls, instance: Self | None) -> str:
        """Produce the formatted string value for this context-command type."""
        return f"{instance.value.strip('\n\r\t -')}-" if instance is not None else ""

    @classmethod
    def get_from_decorator_node(cls, decorator_node: ast.Call) -> _ContextCommandType:
        unparsed_decorator_node: str = ast.unparse(decorator_node).lower()

        if "message" in unparsed_decorator_node:
            return cls.MESSAGE

        if "user" in unparsed_decorator_node:
            return cls.USER

        NON_CONTEXT_COMMAND_MESSAGE: Final[str] = "Decorator node was not a context command."
        raise ValueError(NON_CONTEXT_COMMAND_MESSAGE)


class RuleCAR305(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure Pycord context command names are capitalised."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        context_command_type: object | None = ctx.get("context_command_type", None)
        if context_command_type is not None and not isinstance(
            context_command_type, _ContextCommandType
        ):
            raise TypeError

        return (
            f"Pycord {_ContextCommandType.format_value(context_command_type)}"
            "context command name should be capitalized"
        )

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    def _check_single_argument(
        self, argument: ast.expr, context_command_type: _ContextCommandType
    ) -> None:
        if not isinstance(argument, ast.Constant):
            return

        if not argument.value or not isinstance(argument.value, str):
            return

        if not argument.value[0].isupper():
            self.problems[(argument.lineno, argument.col_offset)] = {
                "context_command_type": context_command_type,
            }

    def _check_all_arguments(self, decorator_node: ast.Call) -> None:
        context_command_type: _ContextCommandType = (
            _ContextCommandType.get_from_decorator_node(decorator_node)
        )

        if decorator_node.args:
            self._check_single_argument(decorator_node.args[0], context_command_type)

        keyword_argument: ast.keyword
        for keyword_argument in decorator_node.keywords:
            if keyword_argument.arg == "name":
                self._check_single_argument(keyword_argument.value, context_command_type)
                return

    def _check_decorator(self, decorator_node: ast.expr) -> None:
        if not isinstance(decorator_node, ast.Call):
            return

        if utils.function_call_is_pycord_context_command_decorator(decorator_node):
            self._check_all_arguments(decorator_node)
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
                    in utils.PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES
                ):
                    self._check_all_arguments(decorator_node)
                    return

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        decorator_node: ast.expr
        for decorator_node in node.decorator_list:
            self._check_decorator(decorator_node)
