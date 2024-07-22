""""""

import ast
from collections.abc import Sequence

__all__: Sequence[str] = ("apply_plugin_to_ast",)

from collections.abc import Set

from flake8_carrot.plugins.base import BasePlugin


def apply_plugin_to_ast(raw_testing_ast: str, plugin_class: type[BasePlugin]) -> Set[str]:
    """"""
    return {
        f"{line}:{column} {message}"
        for line, column, message, _ in plugin_class(ast.parse(raw_testing_ast)).run()
    }
