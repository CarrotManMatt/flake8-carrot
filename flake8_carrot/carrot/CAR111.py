"""Linting rule to ensure preamble lines are separated by only single newlines."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR111",)


class RuleCAR111(CarrotRule):
    """Linting rule to ensure preamble lines are separated by only single newlines."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return (
            "Preamble lines (imports, `__all__` declaration, module docstring, etc.) "
            "should be separated by a single newline"
        )

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        if len(lines) <= 1 or len(tree.body) < 2:
            return

        match tree.body[0]:
            case (
                ast.Expr(value=ast.Constant(value=str()))
                | ast.ImportFrom(module="collections", names=[ast.alias(name="abc.Sequence")])
                | ast.ImportFrom(module="collections", names=[ast.alias(name="abc.Iterable")])
                | ast.ImportFrom(module="collections.abc", names=[ast.alias(name="Sequence")])
                | ast.ImportFrom(module="collections.abc", names=[ast.alias(name="Iterable")])
                | ast.ImportFrom(module="typing", names=[ast.alias(name="Sequence")])
                | ast.ImportFrom(module="typing", names=[ast.alias(name="Iterable")])
                | ast.Import(names=[ast.alias(name="collections")])
                | ast.Import(names=[ast.alias(name="collections.abc")])
                | ast.Import(names=[ast.alias(name="collections.abc.Sequence")])
                | ast.Import(names=[ast.alias(name="collections.abc.Iterable")])
            ):
                pass
            case _:
                return

        match tree.body[1]:
            case (
                ast.ImportFrom(
                    module="collections",
                    names=[ast.alias(name="abc.Sequence"), *_],
                )
                | ast.ImportFrom(
                    module="collections",
                    names=[ast.alias(name="abc.Iterable"), *_],
                )
                | ast.ImportFrom(
                    module="collections.abc",
                    names=[ast.alias(name="Sequence"), *_],
                )
                | ast.ImportFrom(
                    module="collections.abc",
                    names=[ast.alias(name="Iterable"), *_],
                )
                | ast.ImportFrom(module="typing", names=[ast.alias(name="Sequence"), *_])
                | ast.ImportFrom(module="typing", names=[ast.alias(name="Iterable"), *_])
                | ast.Import(names=[ast.alias(name="collections")])
                | ast.Import(names=[ast.alias(name="collections.abc")])
                | ast.Import(names=[ast.alias(name="collections.abc.Sequence")])
                | ast.Import(names=[ast.alias(name="collections.abc.Iterable")])
                | ast.AnnAssign(target=ast.Name(id="__all__"))
                | ast.Assign(targets=[ast.Name(id="__all__"), *_])
            ):
                pass
            case _:
                return

        first_line_end_index: int = (tree.body[0].end_lineno or tree.body[0].lineno) - 1

        if lines[first_line_end_index + 1].strip():
            self.problems.add_without_ctx((first_line_end_index + 1 + 1, 0))
        elif (
            len(lines[first_line_end_index:]) >= 4
            and not lines[first_line_end_index + 2].strip()
        ):
            self.problems.add_without_ctx((first_line_end_index + 2 + 1, 0))

        if not len(tree.body) >= 3:
            return

        match tree.body[2]:
            case (
                ast.AnnAssign(target=ast.Name(id="__all__"))
                | ast.Assign(targets=[ast.Name(id="__all__"), *_])
            ):
                pass
            case _:
                return

        second_line_end_index: int = (tree.body[1].end_lineno or tree.body[1].lineno) - 1

        if lines[second_line_end_index + 1].strip():
            self.problems.add_without_ctx((second_line_end_index + 1 + 1, 0))
        elif (
            len(lines[second_line_end_index:]) >= 4
            and not lines[second_line_end_index + 2].strip()
        ):
            self.problems.add_without_ctx((second_line_end_index + 2 + 1, 0))
