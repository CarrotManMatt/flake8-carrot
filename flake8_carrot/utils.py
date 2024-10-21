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
import functools
import re
from collections.abc import Callable, Generator, Iterable, Mapping, Collection
from collections.abc import Set as AbstractSet
from tokenize import TokenInfo
from typing import TYPE_CHECKING, Final, final, override

from classproperties import classproperty

if __name__ == "__main__":
    CANNOT_RUN_AS_SCRIPT_MESSAGE: Final[str] = "This module cannot be run as a script."
    raise RuntimeError(CANNOT_RUN_AS_SCRIPT_MESSAGE)

if TYPE_CHECKING:
    from flake8_carrot.carrot import CarrotPlugin
    from flake8_carrot.tex_bot import TeXBotPlugin

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


class ProblemsContainer(dict[_ProblemsContainerKey, _ProblemsContainerValue]):
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


class BaseRule[T_plugin: BasePlugin](abc.ABC):
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
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str: ...

    @classmethod
    @final
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        """"""
        return (
            f"{cls.__name__.lower().removeprefix("rule").upper()} "
            f"{cls._format_error_message(ctx)}"
        )


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


def _function_call_is_pycord_function_from_commands_module(node: ast.Call, decorator_names: Collection[str]) -> bool:  # noqa: E501
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
    """"""
    return _function_call_is_pycord_function_from_commands_module(
        node,
        PYCORD_SLASH_COMMAND_DECORATOR_NAMES,
    )

def function_call_is_pycord_context_command_decorator(node: ast.Call) -> bool:
    """"""
    return _function_call_is_pycord_function_from_commands_module(
        node,
        PYCORD_CONTEXT_COMMAND_DECORATOR_NAMES,
    )

def function_call_is_pycord_option_decorator(node: ast.Call) -> bool:
    """"""
    return _function_call_is_pycord_function_from_commands_module(
        node,
        PYCORD_OPTION_DECORATOR_NAMES,
    )

def function_call_is_pycord_task_decorator(node: ast.Call) -> bool:
    """"""
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
    """"""
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
    """"""
    return any(
        (
            function_call_is_pycord_slash_command_decorator(node),
            function_call_is_pycord_context_command_decorator(node),
            function_call_is_pycord_option_decorator(node),
            function_call_is_pycord_task_decorator(node),
            function_call_is_pycord_event_listener_decorator(node),
        ),
    )

def generic_visit_before_return[T_Visitor: ast.NodeVisitor, T_Node: ast.AST](func: Callable[[T_Visitor, T_Node], None]) -> Callable[[T_Visitor, T_Node], None]:  # noqa: E501
    """"""
    @functools.wraps(func)
    def wrapper(self: T_Visitor, node: T_Node) -> None:
        func(self, node)
        self.generic_visit(node)

    return wrapper
