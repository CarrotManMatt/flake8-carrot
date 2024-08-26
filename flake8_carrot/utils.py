""""""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "BasePlugin",
    "BaseRule",
    "CarrotRule",
    "PYCORD_COMMAND_DECORATOR_NAMES",
    "PYCORD_EVENT_LISTENER_DECORATOR_NAMES",
    "PYCORD_OPTION_DECORATOR_NAMES",
    "PYCORD_TASK_DECORATOR_NAMES",
    "ProblemsContainer",
    "TeXBotRule",
    "function_call_is_pycord_command_decorator",
    "function_call_is_pycord_event_listener_decorator",
    "function_call_is_pycord_option_decorator",
    "function_call_is_pycord_task_decorator",
)


import abc
import ast
from collections.abc import Generator, Mapping
from collections.abc import Set as AbstractSet
from tokenize import TokenInfo
from typing import Final, TYPE_CHECKING, override, Generic, TypeVar

from classproperties import classproperty

if __name__ == "__main__":
    CANNOT_RUN_AS_SCRIPT_MESSAGE: Final[str] = "This module cannot be run as a script."
    raise RuntimeError(CANNOT_RUN_AS_SCRIPT_MESSAGE)

if TYPE_CHECKING:
    from flake8_carrot.carrot import CarrotPlugin
    from flake8_carrot.tex_bot import TeXBotPlugin

T_plugin = TypeVar("T_plugin", bound="BasePlugin")


PYCORD_COMMAND_DECORATOR_NAMES: Final[AbstractSet[str]] = frozenset(
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
    },
)
PYCORD_OPTION_DECORATOR_NAMES: Final[AbstractSet[str]] = frozenset(
    {
        "option",
        "Option",
        "ThreadOption",
        "OptionChoice",
    }
)
PYCORD_TASK_DECORATOR_NAMES: Final[AbstractSet[str]] = frozenset(
    {"loop", "Loop", "SleepHandle"},
)
PYCORD_EVENT_LISTENER_DECORATOR_NAMES: Final[AbstractSet[str]] = frozenset(
    {"listen", "listener"},
)


class BasePlugin(abc.ABC):
    """"""

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @abc.abstractmethod
    def RULES(cls) -> frozenset[type["BaseRule[BasePlugin]"]]:  # noqa: N802,N805
        """"""

    def __init__(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        """"""
        self._tree: ast.AST = tree
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


class ProblemsContainer(dict[tuple[int, int], Mapping[str, object]]):
    """"""

    def add_without_ctx(self, problem_location: tuple[int, int]) -> None:
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
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: ARG002, E501
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


def function_call_is_pycord_command_decorator(node: ast.Call) -> bool:
    """"""
    return bool(
        bool(
            isinstance(node.func, ast.Name)
            and node.func.id in PYCORD_COMMAND_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "discord"
            and node.func.attr in PYCORD_COMMAND_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "discord"
            and node.func.value.attr == "commands"
            and node.func.attr in PYCORD_COMMAND_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Attribute)
            and isinstance(node.func.value.value.value, ast.Name)
            and node.func.value.value.value.id == "discord"
            and node.func.value.value.attr == "commands"
            and node.func.value.attr in ("core", "options")
            and node.func.attr in PYCORD_COMMAND_DECORATOR_NAMES  # noqa: COM812
        )  # noqa: COM812
    )


def function_call_is_pycord_option_decorator(node: ast.Call) -> bool:
    """"""
    return bool(
        bool(
            isinstance(node.func, ast.Name)
            and node.func.id in PYCORD_OPTION_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "discord"
            and node.func.attr in PYCORD_OPTION_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "discord"
            and node.func.value.attr == "commands"
            and node.func.attr in PYCORD_OPTION_DECORATOR_NAMES  # noqa: COM812
        )
        or bool(
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and isinstance(node.func.value.value, ast.Attribute)
            and isinstance(node.func.value.value.value, ast.Name)
            and node.func.value.value.value.id == "discord"
            and node.func.value.value.attr == "commands"
            and node.func.value.attr in ("core", "options")
            and node.func.attr in PYCORD_OPTION_DECORATOR_NAMES  # noqa: COM812
        )  # noqa: COM812
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
