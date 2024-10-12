""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR305",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule


class RuleCAR305(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        function_name: object | None = ctx.get("function_name", None)
        if function_name is not None and not isinstance(function_name, str):
            raise TypeError

        if function_name:
            function_name = function_name.strip().strip("'").strip()

        return (
            "CAR305 "
            "Return annotation of autocomplete function "
            f"{f"'{function_name}' " if function_name else ""}"
            "should be `AbstractSet[discord.OptionChoice] | AbstractSet[str]`"
        )

    @override
    def run_check(self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    @classmethod
    def _function_is_autocomplete_getter(cls, node: ast.AsyncFunctionDef) -> bool:
        ALL_ARGS: Final[Sequence[ast.arg]] = (
            node.args.posonlyargs
            + node.args.args
            + node.args.kwonlyargs
        )

        if "autocomplete" in node.name.lower():
            return True
        if node.name.lower().startswith("get_"):
            return True
        if ALL_ARGS[0].arg == "ctx":
            return True
        if "context" in ALL_ARGS[0].arg:
            return True

        annotation_value: str
        match ALL_ARGS[0].annotation:
            case ast.Name(id=annotation_value) | ast.Constant(value=annotation_value):
                if "context" in annotation_value.lower():
                    return True

        docstring: str | None = ast.get_docstring(node)
        return docstring is not None and "autocomplete callable" in docstring.lower()

    def _check_function(self, node: ast.AsyncFunctionDef) -> None:
        ALL_ARGS: Final[Sequence[ast.arg]] = (
            node.args.posonlyargs
            + node.args.args
            + node.args.kwonlyargs
        )

        if node.name.startswith("_"):
            return
        if len(ALL_ARGS) == 0:
            return
        if ALL_ARGS[0].arg in ("self", "cls"):
            return
        if len(node.args.kw_defaults) + len(node.args.defaults) < len(ALL_ARGS) - 1:
            return

        FUNCTION_IS_CLASSMETHOD: Final[bool] = any(
            isinstance(decorator, ast.Name) and decorator.id == "classmethod"
            for decorator in node.decorator_list
        )
        if FUNCTION_IS_CLASSMETHOD:
            return

        return_value: str
        match node.returns:
            case ast.Constant(value=return_value) | ast.Name(id=return_value):
                if return_value in ("str", "int", "bool", "None"):
                    return

        if not self._function_is_autocomplete_getter(node):
            return

        if node.returns is None:
            column_offset: int = (
                (node.end_col_offset - 1) if node.end_col_offset else node.col_offset
            )
            self.problems[(node.end_lineno or node.lineno), column_offset] = {
                "function_name": node.name,
            }
            return

        match node.returns:
            case (
                ast.Constant(value="AbstractSet[discord.OptionChoice] | AbstractSet[str]")
                | ast.BinOp(
                    op=ast.BitOr,
                    left=ast.Subscript(
                        value=ast.Name(id="AbstractSet"),
                        slice=ast.Attribute(
                            value=ast.Name(id="discord"),
                            attr="OptionChoice",
                        ),
                    ),
                    right=ast.Subscript(
                        value=ast.Name(id="AbstractSet"),
                        slice=ast.Name(id="str"),
                    ),
                )
            ):
                return

        self.problems[(node.returns.lineno, node.returns.col_offset)] = {
            "function_name": node.name,
        }

    @utils.generic_visit_before_return
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
