"""Linting rule to ensure only imports and the module docstring are above the export."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR105",)


class RuleCAR105(CarrotRule):
    """Linting rule to ensure only imports and the module docstring are above the export."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        line: object | None = ctx.get("line", None)
        if line is not None:
            if not isinstance(line, str):
                raise TypeError

            line = line.strip("\n\r\t `")

        return f"{
            f'`{line if len(line) < 30 else f"{line[:30]}..."}` is not'
            if line
            else "Only import statements & the module's docstring are"
        } allowed above `__all__` export"

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        if self.plugin.first_all_export_line_numbers is None or len(tree.body) < 2:
            return

        node: ast.stmt
        for node in tree.body:
            if node.lineno >= self.plugin.first_all_export_line_numbers[0]:
                return

            match node:
                case ast.Expr(value=ast.Constant(value=str())) if node == tree.body[0]:
                    continue
                case (
                    ast.ImportFrom()
                    | ast.Import()
                    | ast.If(test=ast.Name(id="TYPE_CHECKING"), orelse=[])
                    | ast.If(
                        test=ast.Compare(),
                        body=(ast.ImportFrom() | ast.Import(),),
                        orelse=(ast.ImportFrom() | ast.Import(),),
                    )
                ):
                    continue

            self.problems[(node.lineno, 0)] = {"line": ast.unparse(node).split("\n")[0]}
