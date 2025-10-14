import ast
import tokenize
from io import StringIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from collections.abc import Set as AbstractSet

    from flake8_carrot.utils import BasePlugin

__all__: Sequence[str] = ("apply_plugin_to_ast",)


def apply_plugin_to_ast(
    raw_testing_ast: str, plugin_class: type[BasePlugin]
) -> AbstractSet[str]:
    """Retrieve all the warnings from applying all of a plugin's rules to an AST."""
    converted_lines: Sequence[str] = raw_testing_ast.split("\n")
    if not converted_lines[-1]:
        converted_lines = [f"{line}\n" for line in converted_lines[:-1]]
    else:
        converted_lines = [f"{line}\n" for line in converted_lines[:-1]] + [
            converted_lines[-1]
        ]

    return {
        f"{line}:{column + 1} {message}"
        for line, column, message, _ in plugin_class(
            tree=ast.parse(raw_testing_ast),
            file_tokens=list(tokenize.generate_tokens(StringIO(raw_testing_ast).readline)),
            lines=converted_lines,
        ).run()
    }
