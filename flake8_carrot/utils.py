""""""

from collections.abc import Iterator, Sequence

__all__: Sequence[str] = ("BasePlugin", "BaseRule")

import abc
import ast
import importlib.metadata
from collections.abc import Generator
from typing import Final, override
from tokenize import TokenInfo

from classproperties import classproperty

if __name__ == "__main__":
    CANNOT_RUN_AS_SCRIPT_MESSAGE: Final[str] = "This module cannot be run as a script."
    raise RuntimeError(CANNOT_RUN_AS_SCRIPT_MESSAGE)


class BasePlugin(abc.ABC):
    """"""

    version = importlib.metadata.version(__name__.split(".")[0])

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @abc.abstractmethod
    def name(cls) -> str:  # noqa: N805
        """The name of this flake8 plugin."""  # noqa: D401

    @classmethod
    def _name(cls, name: str) -> str:
        return f"flake8_{name.split(".")[-1]}"

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @abc.abstractmethod
    def RULES(cls) -> frozenset[type["BaseRule"]]:  # noqa: N802,N805
        """"""

    def __init__(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:
        """"""
        self._tree: ast.AST = tree
        self._file_tokens: Sequence[TokenInfo] = file_tokens
        self._lines: Sequence[str] = lines

    def run(self) -> Generator[tuple[int, int, str, type["BasePlugin"]], None, None]:
        """"""
        RuleClass: type[BaseRule]
        for RuleClass in self.RULES:
            rule: BaseRule = RuleClass()
            rule.run_check(tree=self._tree, file_tokens=self._file_tokens, lines=self._lines)

            line_number: int
            column_number: int
            for line_number, column_number in rule.problems:
                yield line_number, column_number, rule.ERROR_MESSAGE, type(self)


class BaseRule(ast.NodeVisitor, abc.ABC):
    """"""

    @override
    def __init__(self) -> None:
        self.problems: set[tuple[int, int]] = set()

        super().__init__()

    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:
        """"""
        self.visit(tree)

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @abc.abstractmethod
    def ERROR_MESSAGE(cls) -> str:  # noqa: N802, N805
        """"""
