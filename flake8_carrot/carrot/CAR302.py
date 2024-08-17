""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR302",)


import abc
import ast
from collections.abc import Mapping
from collections.abc import Set as AbstractSet
from tokenize import TokenInfo
from typing import Final, Literal, override

from flake8_carrot import utils
from flake8_carrot.utils import BaseRule


class RuleCAR302(BaseRule):
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
        def __init__(self, *, slash_command_group_names: "RuleCAR302._BaseVisitPassFlag | set[str] | None") -> None:  # noqa: E501
            if isinstance(slash_command_group_names, RuleCAR302._BaseVisitPassFlag):
                raw_slash_command_group_names: AbstractSet[str] | None = (
                    slash_command_group_names._get_true_value()  # noqa: SLF001
                )

                slash_command_group_names = (
                    raw_slash_command_group_names
                    if raw_slash_command_group_names is None or isinstance(
                        raw_slash_command_group_names,
                        set,
                    )
                    else set(raw_slash_command_group_names)
                )

            self._slash_command_group_names: set[str] | None = slash_command_group_names

        @property
        @override
        def slash_command_group_names(self) -> AbstractSet[str] | None:
            return self._slash_command_group_names

        def add_slash_command_group_name(self, slash_command_group_name: str) -> None:
            """"""
            if self._slash_command_group_names is None:
                self._slash_command_group_names = {slash_command_group_name}
            else:
                self._slash_command_group_names.add(slash_command_group_name)

        @override
        def _get_true_value(self) -> AbstractSet[str] | None:
            return self.slash_command_group_names

    class SecondVisitPassFlag(_BaseVisitPassFlag):
        """"""

        @override
        def __init__(self, *, slash_command_group_names: "RuleCAR302._BaseVisitPassFlag | AbstractSet[str]") -> None:  # noqa: E501
            if isinstance(slash_command_group_names, RuleCAR302._BaseVisitPassFlag):
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
        self.visit_pass_flag: RuleCAR302._BaseVisitPassFlag = self.FirstVisitPassFlag(
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
            self.problems.clear()
            self.visit_pass_flag = self.SecondVisitPassFlag(
                slash_command_group_names=self.visit_pass_flag,
            )

            self.visit(tree)

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        needs_to_be_plural: object | None = ctx.get("needs_to_be_plural", None)
        if needs_to_be_plural is not None and not isinstance(needs_to_be_plural, bool):
            raise TypeError

        return (
            "CAR302 "
            "Pycord cog subclass name should end with "
            f"{
                f"'Command{"s" if needs_to_be_plural else ""}Cog'"
                if needs_to_be_plural is not None
                else "'CommandCog' or 'CommandsCog'"
            }, "
            f"if that cog contains {
                f"{"multiple commands" if needs_to_be_plural else "a single command"}"
                if needs_to_be_plural is not None
                else "command(s)"
            }"
        )

    def function_is_command(self, node: ast.AsyncFunctionDef) -> bool:
        """"""
        FUNCTION_HAS_WRONG_SIGNATURE: Final[bool] = bool(
            node.name.startswith("_")
            or node.name.startswith("autocomplete_")
            or bool(
                node.returns is not None
                and not bool(
                    isinstance(node.returns, ast.Constant)
                    and node.returns.value is None  # noqa: COM812
                )  # noqa: COM812
            )  # noqa: COM812
        )
        if FUNCTION_HAS_WRONG_SIGNATURE:
            return False

        function_is_command: bool = False

        decorator_node: ast.expr
        for decorator_node in node.decorator_list:
            if not isinstance(decorator_node, ast.Call):
                continue

            DECORATOR_IS_NOT_COMMAND: bool = bool(
                utils.function_call_is_pycord_task_decorator(decorator_node)
                or utils.function_call_is_pycord_event_listener_decorator(decorator_node)  # noqa: COM812
            )
            if DECORATOR_IS_NOT_COMMAND:
                return False

            DECORATOR_IS_COMMAND: bool = bool(
                utils.function_call_is_pycord_command_decorator(decorator_node)
                or bool(
                    isinstance(
                        self.visit_pass_flag.slash_command_group_names,
                        self.SecondVisitPassFlag,
                    )
                    and isinstance(decorator_node.func, ast.Attribute)
                    and isinstance(decorator_node.func.value, ast.Name)
                    and decorator_node.func.value.id in self.visit_pass_flag.slash_command_group_names  # type: ignore[operator] # noqa: E501
                    and decorator_node.func.attr == "command"  # noqa: COM812
                )  # noqa: COM812
            )

            if DECORATOR_IS_COMMAND:
                function_is_command = True

        if function_is_command:
            return function_is_command

        # noinspection PyUnresolvedReferences
        return bool(
            not node.args.posonlyargs
            and len(node.args.args) >= 2
            and node.args.args[0].arg == "self"
            and bool(
                node.args.args[1].arg == "ctx"
                or "context" in node.args.args[1].arg
                or bool(
                    isinstance(node.args.args[1].annotation, ast.Name)
                    and "context" in node.args.args[1].annotation.id.lower()  # noqa: COM812
                )  # noqa: COM812
            )  # noqa: COM812
        )

    def get_number_of_commands_in_class(self, node: ast.ClassDef) -> int:
        """"""
        commands_count: int = 0

        class_inner_node: ast.AST
        for class_inner_node in ast.walk(node):
            NODE_IS_WRONG_TYPE: bool = bool(
                not isinstance(class_inner_node, ast.AsyncFunctionDef)
                or not self.function_is_command(class_inner_node)  # noqa: COM812
            )
            if NODE_IS_WRONG_TYPE:
                continue

            commands_count += 1

        return commands_count

    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        FOUND_COG_SUBCLASS: Final[bool] = bool(
            "cog" in node.name.lower()
            or any(
                "cog" in base.id.lower()
                    for base in node.bases
                    if isinstance(base, ast.Name)
            )
            or any(
                "cog" in base.attr.lower()
                    for base in node.bases
                    if isinstance(base, ast.Attribute)
            )  # noqa: COM812
        )
        if FOUND_COG_SUBCLASS:
            number_of_commands_in_class: int = self.get_number_of_commands_in_class(node)
            if number_of_commands_in_class < 0:
                NEGATIVE_COMMAND_FUNCTIONS_FOUND_MESSAGE: Final[str] = (
                    "Found less than 0 command functions within cog class."
                )
                raise ValueError(NEGATIVE_COMMAND_FUNCTIONS_FOUND_MESSAGE)

            if number_of_commands_in_class == 0:
                return

            is_multiple_commands_cog_subclass: bool = number_of_commands_in_class > 1

            COG_SUBCLASS_IS_MISLABELLED: Final[bool] = bool(
                bool(
                    not is_multiple_commands_cog_subclass
                    and not node.name.endswith("CommandCog")  # noqa: COM812
                )
                or bool(
                    is_multiple_commands_cog_subclass
                    and not node.name.endswith("CommandsCog")  # noqa: COM812
                )  # noqa: COM812
            )
            if COG_SUBCLASS_IS_MISLABELLED:
                self.problems[(node.lineno, node.col_offset + 6)] = {
                    "needs_to_be_plural": is_multiple_commands_cog_subclass,
                }

        self.generic_visit(node)



    @classmethod
    def _node_is_slash_command_group_assignment(cls, node: ast.Assign | ast.AnnAssign) -> bool:
        return bool(
            bool(
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "SlashCommandGroup"  # noqa: COM812
            )
            or bool(
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and isinstance(node.value.func.value, ast.Name)
                and node.value.func.value.id == "discord"
                and node.value.func.attr == "SlashCommandGroup"  # noqa: COM812
            )
            or bool(
                isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and isinstance(node.value.func.value, ast.Attribute)
                and isinstance(node.value.func.value.value, ast.Name)
                and node.value.func.value.value.id == "discord"
                and node.value.func.value.attr == "commands"
                and node.value.func.attr == "SlashCommandGroup"  # noqa: COM812
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
                and node.value.func.attr == "SlashCommandGroup"  # noqa: COM812
            )  # noqa: COM812
        )

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        if isinstance(self.visit_pass_flag, self.FirstVisitPassFlag):
            SLASH_COMMAND_GROUP_FOUND: Final[bool] = (  # NOTE: `if` statements should not be combined because the `_node_id_slash_command_group_assignment()` function is expensive to run
                self._node_is_slash_command_group_assignment(node)
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
            SLASH_COMMAND_GROUP_FOUND: Final[bool] = (  # NOTE: `if` statements should not be combined because the `_node_id_slash_command_group_assignment()` function is expensive to run
                self._node_is_slash_command_group_assignment(node)
            )
            if isinstance(node.target, ast.Name) and SLASH_COMMAND_GROUP_FOUND:
                self.visit_pass_flag.add_slash_command_group_name(node.target.id)

        self.generic_visit(node)
