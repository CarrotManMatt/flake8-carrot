""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR501",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR501(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return (
            "CAR501 Use of dataclass found, declare class manually without \"magic\" instead"
        )

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    @utils.generic_visit_before_return
    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        decorator_node: ast.expr
        for decorator_node in node.decorator_list:
            decorator_name: str
            match decorator_node:
                case ast.Name(id=decorator_name) | ast.Call(func=ast.Name(id=decorator_name)):
                    if "dataclass" in decorator_name.lower():
                        self.problems.add_without_ctx(
                            (decorator_node.lineno, decorator_node.col_offset),
                        )
                        continue

            decorator_module: ast.expr
            match decorator_node:
                case (
                    ast.Attribute(value=decorator_module, attr=decorator_name)
                    | ast.Call(
                        func=ast.Attribute(value=decorator_module, attr=decorator_name),
                    )
                ):
                    if "dataclass" in (ast.unparse(decorator_module) + decorator_name).lower():
                        self.problems.add_without_ctx(
                            (decorator_node.lineno, decorator_node.col_offset),
                        )
                        continue
