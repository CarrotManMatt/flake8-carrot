""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR301",)

import abc
import ast
from collections.abc import Mapping
from collections.abc import Set as AbstractSet
from tokenize import TokenInfo
from typing import Final, override, Literal

from flake8_carrot.utils import BaseRule


class RuleCAR301(BaseRule):
    """"""

    PYCORD_COMMAND_NAMES: AbstractSet[str] = frozenset(
        {
            "application_command",
            "command",
            "slash_command",
            "user_command",
            "message_command",
            "ApplicationCommand",
            "SlashCommand",
            "SlashCommandGroup",
            "UserCommand",
            "MessageCommand",
            "option",
            "Option",
            "ThreadOption",
            "OptionChoice",
        },
    )

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
    """"""

    class _BaseVisitPassFlag(abc.ABC):
        """"""

        def __bool__(self) -> bool:
            return self._get_true_value() is not None

        @abc.abstractmethod
        def _get_true_value(self) -> AbstractSet[str] | None:
            """"""

        @property
        @abc.abstractmethod
        def slash_command_group_names(self) -> object:
            """"""

        @override
        def __repr__(self) -> str:
            return f"{self.__class__.__name__}({self.slash_command_group_names!r})"

    class FirstVisitPassFlag(_BaseVisitPassFlag):
        """"""

        @override
        def __init__(self, *, slash_command_group_names: "RuleCAR106._BaseVisitPassFlag | set[str] | None") -> None:  # noqa: E501
            if isinstance(slash_command_group_names, RuleCAR301._BaseVisitPassFlag):
                raw_slash_command_group_names: AbstractSet[str] | None = (
                    slash_command_group_names._get_true_value()  # noqa: SLF001
                )

                slash_command_group_names = (
                    raw_slash_command_group_names
                    if bool(
                        raw_slash_command_group_names is None
                        or isinstance(raw_slash_command_group_names, set)  # noqa: COM812
                    )
                    else set(raw_slash_command_group_names)
                )

            self._slash_command_group_names: set[str] | None = slash_command_group_names

        @property
        @override
        def slash_command_group_names(self) -> AbstractSet[str] | None:
            return self._slash_command_group_names

        def add_slash_command_group_name(self, slash_command_group_name: str) -> None:
            if self._slash_command_group_names is None:
                self._slash_command_group_names = {slash_command_group_name}
            else:
                self._slash_command_group_names.add(slash_command_group_name)

        @override
        def _get_true_value(self) -> set[str] | None:
            return self.slash_command_group_names

    class SecondVisitPassFlag(_BaseVisitPassFlag):
        """"""

        @override
        def __init__(self, *, slash_command_group_names: "RuleCAR301._BaseVisitPassFlag | AbstractSet[str]") -> None:  # noqa: E501
            if isinstance(slash_command_group_names, RuleCAR301._BaseVisitPassFlag):
                raw_slash_command_group_names: AbstractSet[str] | None = (
                    slash_command_group_names._get_true_value()  # noqa: SLF001
                )
                if raw_slash_command_group_names is None:
                    raise ValueError

                slash_command_group_names = raw_slash_command_group_names

            self._slash_command_group_names: AbstractSet[str] = slash_command_group_names

        @property
        @override
        def slash_command_group_names(self) -> AbstractSet[str]:
            return self._slash_command_group_names

        @override
        def __bool__(self) -> Literal[True]:
            if not super().__bool__():
                raise RuntimeError

            return True

        @override
        def _get_true_value(self) -> AbstractSet[str] | None:
            return self.slash_command_group_names

    @override
    def __init__(self) -> None:
        self.visit_pass_flag: RuleCAR301._BaseVisitPassFlag = self.FirstVisitPassFlag(
            slash_command_group_names=None,
        )

        super().__init__()

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        if self.visit_pass_flag:
            raise RuntimeError

        self.visit(tree)

        if not isinstance(self.visit_pass_flag, self.FirstVisitPassFlag):
            raise RuntimeError  # noqa: TRY004

        if self.visit_pass_flag:
            self.visit_pass_flag = self.SecondVisitPassFlag(
                slash_command_group_names=self.visit_pass_flag,
            )

            self.visit(tree)

    @override
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(self.visit_pass_flag, self.FirstVisitPassFlag):
            PYCORD_CALL_FOUND: Final[bool] = bool(
                bool(
                    isinstance(node.func, ast.Name)
                    and node.func.id in self.PYCORD_COMMAND_NAMES  # noqa: COM812
                )
                or bool(
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "discord"
                    and node.func.attr in self.PYCORD_COMMAND_NAMES  # noqa: COM812
                )
                or bool(
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Attribute)
                    and isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "discord"
                    and node.func.value.attr == "commands"
                    and node.func.attr in self.PYCORD_COMMAND_NAMES  # noqa: COM812
                )
                or bool(
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Attribute)
                    and isinstance(node.func.value.value, ast.Attribute)
                    and isinstance(node.func.value.value.value, ast.Name)
                    and node.func.value.value.value.id == "discord"
                    and node.func.value.value.attr == "commands"
                    and node.func.value.attr in ("core", "options")
                    and node.func.attr in self.PYCORD_COMMAND_NAMES  # noqa: COM812
                )  # noqa: COM812
            )
            if PYCORD_CALL_FOUND:
                positional_argument: ast.expr
                for positional_argument in node.args:
                    # noinspection PyTypeChecker
                    self.problems[(positional_argument.lineno, positional_argument.col_offset)] = {
                        "positional_argument": ast.unparse(positional_argument),
                        "function_name": ast.unparse(node.func),
                    }

        elif isinstance(self.visit_pass_flag, self.SecondVisitPassFlag):
            SLASH_GROUP_CALL_FOUND: Final[bool] = bool(
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in self.visit_pass_flag.slash_command_group_names
                and node.func.attr in self.PYCORD_COMMAND_NAMES  # noqa: COM812
            )
            if SLASH_GROUP_CALL_FOUND:
                positional_argument: ast.expr
                for positional_argument in node.args:
                    # noinspection PyTypeChecker
                    self.problems[(positional_argument.lineno, positional_argument.col_offset)] = {
                        "positional_argument": ast.unparse(positional_argument),
                        "function_name": ast.unparse(node.func),
                    }

        self.generic_visit(node)

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        if isinstance(self.visit_pass_flag, self.FirstVisitPassFlag):
            SLASH_COMMAND_GROUP_FOUND: Final[bool] = bool(
                bool(
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "SlashCommandGroup"
                )
                or bool(
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Name)
                    and node.value.func.value.id == "discord"
                    and node.value.func.attr == "SlashCommandGroup"
                )
                or bool(
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Attribute)
                    and isinstance(node.value.func.value.value, ast.Name)
                    and node.value.func.value.value.id == "discord"
                    and node.value.func.value.id == "commands"
                    and node.value.func.attr == "SlashCommandGroup"
                )
                or bool(
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Attribute)
                    and isinstance(node.value.func.value.value, ast.Attribute)
                    and isinstance(node.value.func.value.value.value, ast.Name)
                    and node.value.func.value.value.value.id == "discord"
                    and node.value.func.value.value.id == "commands"
                    and node.value.func.value.id == "core"
                    and node.value.func.attr == "SlashCommandGroup"
                )
            )
            if SLASH_COMMAND_GROUP_FOUND:
                target: ast.expr
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.visit_pass_flag.add_slash_command_group_name(target.id)

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(self.visit_pass_flag, self.FirstVisitPassFlag):
            SLASH_COMMAND_GROUP_FOUND: Final[bool] = bool(
                bool(
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "SlashCommandGroup"
                )
                or bool(
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Name)
                    and node.value.func.value.id == "discord"
                    and node.value.func.attr == "SlashCommandGroup"
                )
                or bool(
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Attribute)
                    and isinstance(node.value.func.value.value, ast.Name)
                    and node.value.func.value.value.id == "discord"
                    and node.value.func.value.attr == "commands"
                    and node.value.func.attr == "SlashCommandGroup"
                )
                or bool(
                    isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Attribute)
                    and isinstance(node.value.func.value.value, ast.Attribute)
                    and isinstance(node.value.func.value.value.value, ast.Name)
                    and node.value.func.value.value.value.id == "discord"
                    and node.value.func.value.value.attr == "commands"
                    and node.value.func.value.attr == "core"
                    and node.value.func.attr == "SlashCommandGroup"
                )
                or bool(
                    isinstance(node.annotation, ast.Name)
                    and node.annotation.id == "SlashCommandGroup"
                )
                or bool(
                    isinstance(node.annotation, ast.Attribute)
                    and isinstance(node.annotation.value, ast.Name)
                    and node.annotation.value.id == "discord"
                    and node.annotation.attr == "SlashCommandGroup"
                )
                or bool(
                    isinstance(node.annotation, ast.Attribute)
                    and isinstance(node.annotation.value, ast.Attribute)
                    and isinstance(node.annotation.value.value, ast.Name)
                    and node.annotation.value.value.id == "discord"
                    and node.annotation.value.attr == "commands"
                    and node.annotation.attr == "SlashCommandGroup"
                )
                or bool(
                    isinstance(node.annotation, ast.Attribute)
                    and isinstance(node.annotation.value, ast.Attribute)
                    and isinstance(node.annotation.value.value, ast.Attribute)
                    and isinstance(node.annotation.value.value.value, ast.Name)
                    and node.annotation.value.value.value.id == "discord"
                    and node.annotation.value.value.attr == "commands"
                    and node.annotation.value.attr == "core"
                    and node.annotation.attr == "SlashCommandGroup"
                )
            )
            if SLASH_COMMAND_GROUP_FOUND:
                self.visit_pass_flag.add_slash_command_group_name(node.target.id)

        self.generic_visit(node)