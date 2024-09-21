""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR105",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import override

from mypy.fastparse import Constant

from flake8_carrot.utils import CarrotRule


class RuleCAR105(CarrotRule):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        line: object | None = ctx.get("line", None)
        if line is not None and not isinstance(line, str):
            raise TypeError

        if line:
            line = line.strip().strip("`").strip()
            # noinspection PyTypeChecker
            line = f"`{
                line if len(line) < 30 else f"{line[:30]}..."
            }`"

        return (
            "CAR105 "
            f"{
                f"{line} is not"
                if line
                else "Only `Sequence` import & module's docstring are"
            } allowed above `__all__` export"
        )

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        if self.plugin.first_all_export_line_numbers is None or len(tree.body) < 2:
            return

        node: ast.stmt
        for node in tree.body:
            if node.lineno >= self.plugin.first_all_export_line_numbers[0]:
                return

            if node == tree.body[0]:
                match node:
                    case ast.Expr(value=Constant()):
                        continue

            match node:
                case ast.ImportFrom(module="collections.abc" | "typing"):
                    # noinspection PyUnresolvedReferences
                    if any(name.name == "Sequence" for name in node.names):
                        continue

            self.problems[(node.lineno, 0)] = {"line": ast.unparse(node).split("\n")[0]}
