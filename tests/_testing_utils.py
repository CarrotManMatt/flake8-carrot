""""""

from collections.abc import Sequence

__all__: Sequence[str] = ("apply_plugin_to_ast",)

import ast
import tokenize
from collections.abc import Set
from io import StringIO

from flake8_carrot.utils import BasePlugin


def apply_plugin_to_ast(raw_testing_ast: str, plugin_class: type[BasePlugin]) -> Set[str]:
    """"""
    converted_lines: Sequence[str] = raw_testing_ast.split("\n")
    if not converted_lines[-1]:
        converted_lines = [f"{line}\n" for line in converted_lines[:-1]]
    else:
        converted_lines = (
            [f"{line}\n" for line in converted_lines[:-1]]
            + [converted_lines[-1]]
        )

    return {
        f"{line}:{column + 1} {message}"
        for line, column, message, _ in plugin_class(
            tree=ast.parse(raw_testing_ast),
            file_tokens=list(tokenize.generate_tokens(StringIO(raw_testing_ast).readline)),
            lines=converted_lines,
        ).run()
    }
