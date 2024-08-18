""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR106",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR106(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        imported_class: object | None = ctx.get("imported_class", None)
        if imported_class is not None and not isinstance(imported_class, str):
            raise TypeError

        return (
            "CAR106 "
            f"{
                f"Importing `{imported_class}`, from `collections.abc`, is not"
                if imported_class
                else "Only `Sequence` import, from `collections.abc`, is"
            } allowed above `__all__` export"
        )

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:
        self.visit(tree)

    @override
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        COLLECTIONS_IMPORT_FOUND: Final[bool] = bool(
            node.module in ("collections.abc", "typing")
            and self.plugin.first_all_export_line_numbers is not None
            and node.lineno < self.plugin.first_all_export_line_numbers[0]
            and any(alias.name == "Sequence" for alias in node.names)  # noqa: COM812
        )
        if COLLECTIONS_IMPORT_FOUND:
            alias: ast.alias
            for alias in node.names:
                if alias.name == "Sequence":
                    continue

                self.problems[(alias.lineno, alias.col_offset)] = {
                    "imported_class": alias.name,
                }

        self.generic_visit(node)
