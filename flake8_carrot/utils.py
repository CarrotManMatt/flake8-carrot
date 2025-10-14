"""Utility/base functions and classes used throughout this project."""

import abc
import ast
import functools
import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, final, override

from typed_classproperties import classproperty

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Generator, Iterable, Sequence
    from collections.abc import Set as AbstractSet
    from tokenize import TokenInfo
    from types import EllipsisType
    from typing import Final, Self

    from flake8_carrot.carrot import CarrotPlugin
    from flake8_carrot.tex_bot import TeXBotPlugin

__all__: Sequence[str] = (
    "ALL_PYCORD_FUNCTION_NAMES",
    "PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES",
    "PYCORD_EVENT_LISTENER_DECORATOR_NAMES",
    "PYCORD_OPTION_DECORATOR_NAMES",
    "PYCORD_SLASH_COMMAND_DECORATOR_NAMES",
    "PYCORD_TASK_DECORATOR_NAMES",
    "ASTNameID",
    "BasePlugin",
    "BaseRule",
    "CarrotRule",
    "ProblemsContainer",
    "TeXBotRule",
    "function_call_is_any_pycord_decorator",
    "function_call_is_pycord_context_command_decorator",
    "function_call_is_pycord_event_listener_decorator",
    "function_call_is_pycord_option_decorator",
    "function_call_is_pycord_slash_command_decorator",
    "function_call_is_pycord_task_decorator",
    "generic_visit_before_return",
)


if __name__ == "__main__":
    CANNOT_RUN_AS_SCRIPT_MESSAGE: Final[str] = "This module cannot be run as a script."
    raise RuntimeError(CANNOT_RUN_AS_SCRIPT_MESSAGE)


if TYPE_CHECKING:
    type ASTNameID = str | bytes | int | float | complex | EllipsisType | None

    type _ProblemsContainerKey = tuple[int, int]
    type _ProblemsContainerValue = Mapping[str, object]
    type _ProblemsContainerMapping = Mapping[_ProblemsContainerKey, _ProblemsContainerValue]
    type _ProblemsContainerIterable = Iterable[
        tuple[_ProblemsContainerKey, _ProblemsContainerValue]
    ]


PPRINT_MODULES: Final[AbstractSet[str]] = {"astpretty"}
PYCORD_SLASH_COMMAND_DECORATOR_NAMES: Final[AbstractSet[str]] = {
    "application_command",
    "command",
    "slash_command",
    "ApplicationCommand",
    "SlashCommand",
    "SlashCommandGroup",
}
PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES: Final[AbstractSet[str]] = {
    "user_command",
    "message_command",
    "UserCommand",
    "MessageCommand",
}
PYCORD_OPTION_DECORATOR_NAMES: Final[AbstractSet[str]] = {
    "option",
    "Option",
    "ThreadOption",
    "OptionChoice",
}
PYCORD_TASK_DECORATOR_NAMES: Final[AbstractSet[str]] = {"loop", "Loop", "SleepHandle"}
PYCORD_EVENT_LISTENER_DECORATOR_NAMES: Final[AbstractSet[str]] = {"listen", "listener"}
ALL_PYCORD_FUNCTION_NAMES: Final[AbstractSet[str]] = (
    PYCORD_SLASH_COMMAND_DECORATOR_NAMES
    | PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES
    | PYCORD_OPTION_DECORATOR_NAMES
    | PYCORD_TASK_DECORATOR_NAMES
    | PYCORD_EVENT_LISTENER_DECORATOR_NAMES
)


class BasePlugin(abc.ABC):
    """Base plugin class to hold a selection of linting rules."""

    @classproperty
    @abc.abstractmethod
    def RULES(cls) -> Collection[type[BaseRule[Self]]]:  # noqa: D102, N802
        pass

    @override
    def __init__(
        self,
        tree: ast.AST,
        file_tokens: "Sequence[TokenInfo]",  # noqa: UP037
        lines: "Sequence[str]",  # noqa: UP037
    ) -> None:
        if isinstance(tree, ast.Module):
            pass
        elif isinstance(tree, ast.Interactive):
            tree = ast.Module(body=tree.body, type_ignores=[])
        elif isinstance(tree, ast.Expression):
            tree = ast.Module(body=[ast.Expr(tree.body)], type_ignores=[])
        else:
            CANNOT_RUN_WITH_NON_MODULE_MESSAGE: Final[str] = (
                "Cannot run flake8-carrot plugin with tree that is not an 'ast.Module'."
            )
            raise TypeError(CANNOT_RUN_WITH_NON_MODULE_MESSAGE)

        self._tree: ast.Module = tree
        self._file_tokens: Sequence[TokenInfo] = file_tokens
        self._lines: Sequence[str] = lines

    def run(self) -> Generator[tuple[int, int, str, type[Self]]]:
        """Perform complete linting over the stored Flake8 code context."""
        RuleClass: type[BaseRule[Self]]
        for RuleClass in self.RULES:
            rule: BaseRule[Self] = RuleClass(plugin=self)
            rule.run_check(tree=self._tree, file_tokens=self._file_tokens, lines=self._lines)

            line_number: int
            column_number: int
            ctx: Mapping[str, object]
            for (line_number, column_number), ctx in rule.problems.items():
                yield line_number, column_number, rule.format_error_message(ctx), type(self)


class ProblemsContainer(dict["_ProblemsContainerKey", "_ProblemsContainerValue"]):
    """Collection of problem locations mapped to error message contexts."""

    @classmethod
    def clean_key(cls, key: _ProblemsContainerKey | str) -> _ProblemsContainerKey:
        """Ensure the given problem location matches the required format."""
        if isinstance(key, str):
            match: re.Match[str] | None = re.fullmatch(
                r"\A(?P<line_number>\d+),(?P<column_number>\d+)\Z",
                key,
            )
            if match is None:
                INVALID_PROBLEM_LOCATION_MESSAGE: Final[str] = (
                    f"Invalid problem location: `{key}`."
                )
                raise ValueError(INVALID_PROBLEM_LOCATION_MESSAGE)

            key = (int(match.group("line_number")), int(match.group("column_number")))

        if key[0] < 1 or key[1] < 0:
            NEGATIVE_PROBLEM_LOCATION_MESSAGE: Final[str] = (
                "Problem locations cannot be negative."
            )
            raise ValueError(NEGATIVE_PROBLEM_LOCATION_MESSAGE)

        return key

    @override
    def __init__(
        self,
        mapping: _ProblemsContainerMapping | _ProblemsContainerIterable | None = None,
        /,
        **kwargs: _ProblemsContainerValue,  # noqa: CAR150
    ) -> None:
        mapping = (
            {}
            if mapping is None
            else {
                self.clean_key(key): value
                for key, value in (
                    mapping.items() if isinstance(mapping, Mapping) else mapping
                )
            }
        )

        if kwargs:
            mapping.update({self.clean_key(key): value for key, value in kwargs.items()})

        super().__init__(mapping)

    @override
    def __setitem__(
        self, key: _ProblemsContainerKey, value: _ProblemsContainerValue, /
    ) -> None:
        super().__setitem__(self.clean_key(key), value)

    def add_without_ctx(self, problem_location: _ProblemsContainerKey) -> None:
        """Add a problem at the given location without a context."""
        self[problem_location] = {}


class BaseRule[T_plugin: BasePlugin](abc.ABC):
    """Base rule class defining common plugin-based functionality."""

    @override
    def __init__(self, plugin: T_plugin) -> None:
        self.plugin: T_plugin = plugin
        self.problems: ProblemsContainer = ProblemsContainer()

        super().__init__()

    @abc.abstractmethod
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        """Update the problems-dict from those arising from the given code."""

    @classmethod
    @abc.abstractmethod
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        pass

    @classmethod
    @final
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        """Retrieve the formatted error message for this rule with the given context."""
        return (
            f"{cls.__name__.lower().removeprefix('rule').upper()} "
            f"{cls._format_error_message(ctx)}"
        )


class CarrotRule(BaseRule["CarrotPlugin"], abc.ABC):
    """Base rule class for all "CAR" lint rules."""

    @override
    def __init__(self, plugin: CarrotPlugin) -> None:
        super().__init__(plugin)


class TeXBotRule(BaseRule["TeXBotPlugin"], abc.ABC):
    """Base rule class for all "TXB" lint rules."""

    @override
    def __init__(self, plugin: TeXBotPlugin) -> None:
        super().__init__(plugin)


def _function_call_is_pycord_function_from_commands_module(
    node: ast.Call, decorator_names: Collection[str]
) -> bool:
    function_name: str
    match node.func:
        case (
            ast.Name(id=function_name)
            | ast.Attribute(
                value=(
                    ast.Name(id="discord")
                    | ast.Attribute(
                        value=ast.Name(id="discord"),
                        attr="commands",
                    )
                    | ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="discord"),
                            attr="commands",
                        ),
                        attr=("core" | "options"),
                    )
                ),
                attr=function_name,
            )
        ):
            return function_name in decorator_names

        case _:
            return False


def function_call_is_pycord_slash_command_decorator(node: ast.Call) -> bool:
    """Check if the given call AST node is calling the pycord slash-command decorator."""
    return _function_call_is_pycord_function_from_commands_module(
        node,
        PYCORD_SLASH_COMMAND_DECORATOR_NAMES,
    )


def function_call_is_pycord_context_command_decorator(node: ast.Call) -> bool:
    """Check if the given call AST node is calling the pycord context-command decorator."""
    return _function_call_is_pycord_function_from_commands_module(
        node,
        PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES,
    )


def function_call_is_pycord_option_decorator(node: ast.Call) -> bool:
    """Check if the given call AST node is calling the pycord command option decorator."""
    return _function_call_is_pycord_function_from_commands_module(
        node,
        PYCORD_OPTION_DECORATOR_NAMES,
    )


def function_call_is_pycord_task_decorator(node: ast.Call) -> bool:
    """Check if the given function call AST node is calling the pycord task decorator."""
    function_name: str
    match node.func:
        case (
            ast.Name(id=function_name)
            | ast.Attribute(
                value=(
                    ast.Attribute(
                        value=(
                            ast.Name(id="discord")
                            | ast.Attribute(value=ast.Name(id="discord"), attr="ext")
                        ),
                        attr="tasks",
                    )
                ),
                attr=function_name,
            )
        ):
            return function_name in PYCORD_TASK_DECORATOR_NAMES

    module_name: str
    match node.func:
        case ast.Attribute(
            value=ast.Name(id=module_name),
            attr=function_name,
        ):
            if function_name not in PYCORD_TASK_DECORATOR_NAMES:
                return False

            if "bot" in module_name.lower() or "client" in module_name.lower():
                return True

            return module_name in ("discord", "tasks")

    return False


def function_call_is_pycord_event_listener_decorator(node: ast.Call) -> bool:
    """Check if the given call AST node is calling a pycord event listener decorator."""
    function_name: str
    match node.func:
        case (
            ast.Name(id=function_name)
            | ast.Attribute(
                value=ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id="discord"),
                        attr="ext",
                    ),
                    attr="commands",
                ),
                attr=function_name,
            )
        ):
            return function_name in PYCORD_EVENT_LISTENER_DECORATOR_NAMES

    module_name: str
    match node.func:
        case ast.Attribute(value=ast.Name(id=module_name), attr=function_name):
            if function_name not in PYCORD_EVENT_LISTENER_DECORATOR_NAMES:
                return False

            if any(value in module_name.lower() for value in ("bot", "client", "cog")):
                return True

            return module_name in ("discord", "commands")

        case ast.Attribute(
            value=ast.Attribute(value=ast.Name(id="discord"), attr=module_name),
            attr=function_name,
        ):
            if function_name not in PYCORD_EVENT_LISTENER_DECORATOR_NAMES:
                return False

            if any(value in module_name.lower() for value in ("bot", "client", "cog")):
                return True

            return module_name == "commands"

    return False


def function_call_is_any_pycord_decorator(node: ast.Call) -> bool:
    """Check if the given function call AST node is calling a pycord decorator."""
    return any(
        (
            function_call_is_pycord_slash_command_decorator(node),
            function_call_is_pycord_context_command_decorator(node),
            function_call_is_pycord_option_decorator(node),
            function_call_is_pycord_task_decorator(node),
            function_call_is_pycord_event_listener_decorator(node),
        ),
    )


def generic_visit_before_return[T_Visitor: ast.NodeVisitor, T_Node: ast.AST](
    func: Callable[[T_Visitor, T_Node], None],
) -> Callable[[T_Visitor, T_Node], None]:
    """Ensure a NodeVisitor overriden method calls generic_visit() before returning."""

    @functools.wraps(func)
    def wrapper(self: T_Visitor, node: T_Node) -> None:
        func(self, node)
        self.generic_visit(node)

    return wrapper
