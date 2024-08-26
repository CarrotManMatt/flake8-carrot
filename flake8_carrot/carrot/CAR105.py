""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR105",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import override

from flake8_carrot.utils import CarrotRule


class RuleCAR105(CarrotRule):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        line: object | None = ctx.get("line", None)
        if line is not None and not isinstance(line, str):
            raise TypeError

        return (
            "CAR105 "
            f"{
                f"{line} is not"
                if line
                else "Only `Sequence` import & module's docstring are"
            } allowed above `__all__` export"
        )

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        if not isinstance(tree, ast.Module):
            return

        node: ast.stmt
        for node in tree.body:
            EXPRESSION_BEFORE_ALL: bool = bool(
                hasattr(node, "lineno")
                and hasattr(node, "col_offset")
                and self.plugin.first_all_export_line_numbers is not None
                and node.lineno < self.plugin.first_all_export_line_numbers[0]
                and not bool(
                    isinstance(node, ast.Expr)
                    and isinstance(node.value, ast.Constant)
                    and node.lineno == self.plugin.true_start_line_number  # noqa: COM812
                )
                and not bool(
                    isinstance(node, ast.ImportFrom)
                    and node.module in ("collections.abc", "typing")
                    and any(name.name == "Sequence" for name in node.names)  # noqa: COM812
                )  # noqa: COM812
            )
            if EXPRESSION_BEFORE_ALL:
                line: str = ast.unparse(node).split("\n")[0]
                self.problems[(node.lineno, 0)] = {
                    "line": f"`{line if len(line) < 30 else f"{line[:30]}..."}`",
                }
