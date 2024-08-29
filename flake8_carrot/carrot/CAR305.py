""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR305",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR305(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        function_name: object | None = ctx.get("function_name", None)
        if function_name is not None and not isinstance(function_name, str):
            raise TypeError

        return (
            "CAR305 "
            f"Return annotation of autocomplete function '{function_name}' "
            "should be `Set[discord.OptionChoice] | Set[str]`"
        )

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    def _check_function(self, node: ast.AsyncFunctionDef) -> None:
        ALL_ARGS: Sequence[ast.arg] = (
            node.args.posonlyargs
            + node.args.args
            + node.args.kwonlyargs
        )

        FUNCTION_HAS_INCORRECT_STRUCTURE: Final[bool] = bool(
            len(ALL_ARGS) == 0
            or ALL_ARGS[0].arg in ("self", "cls")
            or not (len(node.args.kw_defaults) + len(node.args.defaults) >= len(ALL_ARGS) - 1)
            or any(
                isinstance(decorator, ast.Name) and decorator.id == "classmethod"
                for decorator in node.decorator_list
            )  # noqa: COM812
        )
        # noinspection PyUnresolvedReferences
        FUNCTION_IS_AUTOCOMPLETE_GETTER: Final[bool] = bool(
            "autocomplete" in node.name.lower()
            or node.name.lower().startswith("get_")
            or ALL_ARGS[0].arg == "ctx"
            or "context" in ALL_ARGS[0].arg
            or bool(
                isinstance(ALL_ARGS[0].annotation, ast.Name)
                and "context" in ALL_ARGS[0].annotation.id.lower()  # noqa: COM812
            )
            or bool(
                isinstance(ALL_ARGS[0].annotation, ast.Constant)
                and "context" in ALL_ARGS[0].annotation.value.lower()  # noqa: COM812
            )
            or "autocomplete callable" in (ast.get_docstring(node) or "").lower()  # noqa: COM812
        )
        if FUNCTION_HAS_INCORRECT_STRUCTURE or not FUNCTION_IS_AUTOCOMPLETE_GETTER:
            return

        if node.returns is None:
            self.problems[(node.end_lineno or node.lineno, (node.end_col_offset - 1) if node.end_col_offset else node.col_offset)] = {  # noqa: E501
                "function_name": node.name,
            }

        FUNCTION_HAS_CORRECT_RETURN_ANNOTATION: Final[bool] = bool(
            bool(
                isinstance(node.returns, ast.Constant)
                and node.returns.value == "Set[discord.OptionChoice] | Set[str]"  # noqa: COM812
            )
            or bool(
                isinstance(node.returns, ast.BinOp)
                and isinstance(node.returns.op, ast.BitOr)
                and isinstance(node.returns.left, ast.Subscript)
                and isinstance(node.returns.right, ast.Subscript)
                and isinstance(node.returns.left.value, ast.Name)
                and isinstance(node.returns.left.slice, ast.Attribute)
                and isinstance(node.returns.right.value, ast.Name)
                and isinstance(node.returns.right.slice, ast.Name)
                and isinstance(node.returns.left.slice.value, ast.Name)
                and node.returns.left.value.id == "Set"
                and node.returns.left.slice.value.id == "discord"
                and node.returns.left.slice.attr == "OptionChoice"
                and node.returns.right.value.id == "Set"
                and node.returns.right.slice.id == "str"  # noqa: COM812
            )  # noqa: COM812
        )
        if not FUNCTION_HAS_CORRECT_RETURN_ANNOTATION:
            self.problems[(node.returns.lineno, node.returns.col_offset)] = {  # type: ignore[union-attr]
                "function_name": node.name,
            }

    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)

        self.generic_visit(node)
