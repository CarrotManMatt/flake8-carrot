""""""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: "Sequence[str]" = ("RuleCAR105",)


class RuleCAR105(CarrotRule):
    """"""

    @classmethod
    @override
    def _format_error_message(cls, ctx: "Mapping[str, object]") -> str:
        line: object | None = ctx.get("line", None)
        if line is not None and not isinstance(line, str):
            raise TypeError

        if line:
            line = line.strip().strip("`").strip()
            line = f"`{line if len(line) < 30 else f'{line[:30]}...'}`"

        return f"{
            f'{line} is not' if line else "Only `Sequence` import & module's docstring are"
        } allowed above `__all__` export"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: "Sequence[TokenInfo]", lines: "Sequence[str]"
    ) -> None:
        if self.plugin.first_all_export_line_numbers is None or len(tree.body) < 2:
            return

        node: ast.stmt
        for node in tree.body:
            if node.lineno >= self.plugin.first_all_export_line_numbers[0]:
                return

            if node == tree.body[0]:
                match node:
                    case ast.Expr(value=ast.Constant()):
                        continue

            match node:
                case ast.ImportFrom(module="collections.abc" | "typing"):
                    if any(name.name == "Sequence" for name in node.names):
                        continue

            self.problems[(node.lineno, 0)] = {"line": ast.unparse(node).split("\n")[0]}
