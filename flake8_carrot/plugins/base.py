"""Abstract base classes for flake8 plugins."""

from collections.abc import Sequence

__all__: Sequence[str] = ("BasePlugin",)


import abc
import ast
import importlib.metadata
from collections.abc import Generator

from classproperties import classproperty

from flake8_carrot import utils

utils.check_not_run_as_script(__name__)


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

    def __init__(self, tree: ast.AST) -> None:
        """"""
        self._tree: ast.AST = tree

    @abc.abstractmethod
    def run(self) -> Generator[tuple[int, int, str, type["BasePlugin"]], None, None]:
        """"""
