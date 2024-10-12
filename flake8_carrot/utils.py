""""""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "ALL_PYCORD_FUNCTION_NAMES",
    "BasePlugin",
    "BaseRule",
    "CarrotRule",
    "PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES",
    "PYCORD_EVENT_LISTENER_DECORATOR_NAMES",
    "PYCORD_OPTION_DECORATOR_NAMES",
    "PYCORD_SLASH_COMMAND_DECORATOR_NAMES",
    "PYCORD_TASK_DECORATOR_NAMES",
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


import abc
import ast
import enum
import functools
import re
from collections.abc import Callable, Generator, Iterable, Mapping
from collections.abc import Set as AbstractSet
from enum import Enum
from tokenize import TokenInfo
from typing import TYPE_CHECKING, Final, Generic, TypeAlias, TypeVar, override

from classproperties import classproperty

if __name__ == "__main__":
    CANNOT_RUN_AS_SCRIPT_MESSAGE: Final[str] = "This module cannot be run as a script."
    raise RuntimeError(CANNOT_RUN_AS_SCRIPT_MESSAGE)

if TYPE_CHECKING:
    from flake8_carrot.carrot import CarrotPlugin
    from flake8_carrot.tex_bot import TeXBotPlugin

T_plugin = TypeVar("T_plugin", bound="BasePlugin")
T_Visitor = TypeVar("T_Visitor", bound=ast.NodeVisitor)
T_Node = TypeVar("T_Node", bound=ast.AST)
_ProblemsContainerKey: TypeAlias = tuple[int, int]
_ProblemsContainerValue: TypeAlias = Mapping[str, object]
_ProblemsContainerMapping: TypeAlias = Mapping[_ProblemsContainerKey, _ProblemsContainerValue]
_ProblemsContainerDict: TypeAlias = dict[_ProblemsContainerKey, _ProblemsContainerValue]
_ProblemsContainerIterable: TypeAlias = Iterable[
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
    """"""

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @abc.abstractmethod
    def RULES(cls) -> frozenset[type["BaseRule[BasePlugin]"]]:  # noqa: N802, N805
        """"""

    def __init__(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        """"""
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

    def run(self) -> Generator[tuple[int, int, str, type["BasePlugin"]], None, None]:
        """"""
        RuleClass: type[BaseRule[BasePlugin]]
        for RuleClass in self.RULES:
            rule: BaseRule[BasePlugin] = RuleClass(plugin=self)
            rule.run_check(tree=self._tree, file_tokens=self._file_tokens, lines=self._lines)

            line_number: int
            column_number: int
            ctx: Mapping[str, object]
            for (line_number, column_number), ctx in rule.problems.items():
                yield line_number, column_number, rule.format_error_message(ctx), type(self)


class ProblemsContainer(_ProblemsContainerDict):
    """"""

    @classmethod
    def clean_key(cls, key: _ProblemsContainerKey | str) -> _ProblemsContainerKey:
        """"""
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

    # noinspection PyOverrides
    @override
    def __init__(self, mapping: _ProblemsContainerMapping | _ProblemsContainerIterable | None = None, /, **kwargs: _ProblemsContainerValue) -> None:  # noqa: E501, CAR150
        if mapping is None:
            mapping = {}
        elif isinstance(mapping, Mapping):
            mapping = {self.clean_key(key): value for key, value in mapping.items()}
        elif isinstance(mapping, Iterable) and not isinstance(mapping, Mapping):
            mapping = {self.clean_key(key): value for key, value in mapping}

        if kwargs:
            mapping = {
                **{self.clean_key(key): value for key, value in kwargs.items()},
                **mapping,
            }

        super().__init__(mapping)

    # noinspection PyOverrides
    @override
    def __setitem__(self, key: _ProblemsContainerKey, value: _ProblemsContainerValue, /) -> None:  # noqa: E501
        super().__setitem__(self.clean_key(key), value)

    def add_without_ctx(self, problem_location: _ProblemsContainerKey) -> None:
        """"""
        self[problem_location] = {}


class BaseRule(abc.ABC, Generic[T_plugin]):
    """"""

    @override
    def __init__(self, plugin: T_plugin) -> None:
        self.plugin: T_plugin = plugin
        self.problems: ProblemsContainer = ProblemsContainer()

        super().__init__()

    @abc.abstractmethod
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        """"""

    @classmethod
    @abc.abstractmethod
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        """"""


class CarrotRule(BaseRule["CarrotPlugin"], abc.ABC):
    """"""

    @override
    def __init__(self, plugin: "CarrotPlugin") -> None:
        super().__init__(plugin)


class TeXBotRule(BaseRule["TeXBotPlugin"], abc.ABC):
    """"""

    @override
    def __init__(self, plugin: "TeXBotPlugin") -> None:
        super().__init__(plugin)


class _PycordCommandsModuleLookFor(Enum):
    SLASH_COMMAND_DECORATORS = enum.auto()
    CONTEXT_COMMAND_DECORATORS = enum.auto()
    OPTION_DECORATORS = enum.auto()


def _function_call_is_pycord_function_from_commands_module(node: ast.Call, pycord_commands_module_look_for: _PycordCommandsModuleLookFor) -> bool:  # noqa: E501
    NAMES: Final[AbstractSet[str] | None] = (
        PYCORD_SLASH_COMMAND_DECORATOR_NAMES
        if pycord_commands_module_look_for is _PycordCommandsModuleLookFor.SLASH_COMMAND_DECORATORS  # noqa: E501
        else (
            PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES
            if pycord_commands_module_look_for is _PycordCommandsModuleLookFor.CONTEXT_COMMAND_DECORATORS  # noqa: E501
            else (
                PYCORD_OPTION_DECORATOR_NAMES
                if pycord_commands_module_look_for is _PycordCommandsModuleLookFor.OPTION_DECORATORS  # noqa: E501
                else None
            )
        )
    )

    if NAMES is None:
        raise RuntimeError

    return bool(  # TODO: Convert to match case
        (isinstance(node.func, ast.Name) and node.func.id in NAMES)
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "discord"
            and node.func.attr in NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "discord"
            and node.func.value.attr == "commands"
            and node.func.attr in NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Attribute)
            and isinstance(node.func.value.value.value, ast.Name)
            and node.func.value.value.value.id == "discord"
            and node.func.value.value.attr == "commands"
            and node.func.value.attr in ("core", "options")
            and node.func.attr in NAMES  # noqa: COM812
        )  # noqa: COM812
    )

def function_call_is_pycord_slash_command_decorator(node: ast.Call) -> bool:
    """"""
    return _function_call_is_pycord_function_from_commands_module(
        node,
        _PycordCommandsModuleLookFor.SLASH_COMMAND_DECORATORS,
    )

def function_call_is_pycord_context_command_decorator(node: ast.Call) -> bool:
    """"""
    return _function_call_is_pycord_function_from_commands_module(
        node,
        _PycordCommandsModuleLookFor.CONTEXT_COMMAND_DECORATORS,
    )

def function_call_is_pycord_option_decorator(node: ast.Call) -> bool:
    """"""
    return _function_call_is_pycord_function_from_commands_module(
        node,
        _PycordCommandsModuleLookFor.OPTION_DECORATORS,
    )

def function_call_is_pycord_task_decorator(node: ast.Call) -> bool:
    """"""
    return bool(
        bool(
            isinstance(node.func, ast.Name)
            and node.func.id in PYCORD_TASK_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and bool(
                node.func.value.id in ("discord", "tasks")
                or "bot" in node.func.value.id.lower()
                or "client" in node.func.value.id.lower()  # noqa: COM812
            )
            and node.func.attr in PYCORD_TASK_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "discord"
            and node.func.value.attr == "tasks"
            and node.func.attr in PYCORD_TASK_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Attribute)
            and isinstance(node.func.value.value.value, ast.Name)
            and node.func.value.value.value.id == "discord"
            and node.func.value.value.attr == "ext"
            and node.func.value.attr == "tasks"
            and node.func.attr in PYCORD_TASK_DECORATOR_NAMES  # noqa: COM812
        )  # noqa: COM812
    )

def function_call_is_pycord_event_listener_decorator(node: ast.Call) -> bool:
    """"""
    return bool(
        bool(
            isinstance(node.func, ast.Name)
            and node.func.id in PYCORD_EVENT_LISTENER_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and bool(
                node.func.value.id in ("discord", "commands")
                or "bot" in node.func.value.id.lower()
                or "client" in node.func.value.id.lower()
                or "cog" in node.func.value.id.lower()  # noqa: COM812
            )
            and node.func.attr in PYCORD_EVENT_LISTENER_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "discord"
            and bool(
                node.func.value.attr == "commands"
                or "bot" in node.func.value.attr.lower()
                or "client" in node.func.value.attr.lower()
                or "cog" in node.func.value.attr.lower()  # noqa: COM812
            )
            and node.func.attr in PYCORD_EVENT_LISTENER_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Attribute)
            and isinstance(node.func.value.value.value, ast.Name)
            and node.func.value.value.value.id == "discord"
            and node.func.value.value.attr == "ext"
            and node.func.value.attr == "commands"
            and node.func.attr in PYCORD_EVENT_LISTENER_DECORATOR_NAMES  # noqa: COM812
        )  # noqa: COM812
    )

def function_call_is_any_pycord_decorator(node: ast.Call) -> bool:
    """"""
    return bool(
        function_call_is_pycord_slash_command_decorator(node)
        or function_call_is_pycord_context_command_decorator(node)
        or function_call_is_pycord_option_decorator(node)
        or function_call_is_pycord_task_decorator(node)
        or function_call_is_pycord_event_listener_decorator(node)  # noqa: COM812
    )

def generic_visit_before_return(func: Callable[[T_Visitor, T_Node], None]) -> Callable[[T_Visitor, T_Node], None]:  # noqa: E501
    """"""
    @functools.wraps(func)
    def wrapper(self: T_Visitor, node: T_Node) -> None:
        func(self, node)
        self.generic_visit(node)

    return wrapper
