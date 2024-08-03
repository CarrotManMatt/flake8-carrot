""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR302",)


import ast
from collections.abc import Mapping
from typing import Final, override

from flake8_carrot import utils
from flake8_carrot.utils import BaseRule


class RuleCAR302(BaseRule):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return (
            "CAR302 "
            "Pycord cog subclass name should end with either 'CommandCog' or 'CommandsCog', "
            "if that cog contains command(s)"
        )

    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        FOUND_MISLABELLED_COG_SUBCLASS: Final[bool] = bool(
            not node.name.endswith("CommandCog")
            and not node.name.endswith("CommandsCog")  # TODO: Make name identification smarter (based on one or multiple commands)
            and bool(
                "cog" in node.name.lower()
                or any(
                    "cog" in base.id.lower()
                    for base in node.bases
                    if isinstance(base, ast.Name)
                )
                or any(
                    "cog" in base.attr.lower()
                    for base in node.bases
                    if isinstance(base, ast.Attribute)
                )  # noqa: COM812
            )  # noqa: COM812
        )
        if FOUND_MISLABELLED_COG_SUBCLASS:
            COG_SUBCLASS_IS_COMMAND_COG: Final[bool] = any(
                bool(
                    isinstance(decorator_node, ast.Call)
                    and utils.function_call_is_pycord_function_call(decorator_node)
                )
                for class_inner_node in ast.walk(node)
                if isinstance(class_inner_node, ast.AsyncFunctionDef)
                for decorator_node in class_inner_node.decorator_list
            )  # TODO: Identify subclass is command cog from function arguments or slash command group decorators
            if COG_SUBCLASS_IS_COMMAND_COG:
                self.problems.add_without_ctx((node.lineno, node.col_offset + 6))

        self.generic_visit(node)
