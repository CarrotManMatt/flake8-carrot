""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR105",)

import abc
import ast
from tokenize import TokenInfo
from typing import Final, Literal, override

from flake8_carrot.utils import BaseRule


class RuleCAR105(BaseRule):
    """"""

    class _BaseVisitPassFlag(abc.ABC):
        """"""

        def __bool__(self) -> bool:
            return self._get_true_value() is not None

        @abc.abstractmethod
        def _get_true_value(self) -> int | None:
            """"""

        @property
        @abc.abstractmethod
        def first_all_export_lineno(self) -> object:
            """"""

    class FirstVisitPassFlag(_BaseVisitPassFlag):
        """"""

        @override
        def __init__(self, *, first_all_export_lineno: "RuleCAR105._BaseVisitPassFlag | int | None") -> None:  # noqa: E501
            if isinstance(first_all_export_lineno, RuleCAR105._BaseVisitPassFlag):
                first_all_export_lineno = first_all_export_lineno._get_true_value()  # noqa: SLF001

            self._first_all_export_lineno: int | None = first_all_export_lineno

        @property
        @override
        def first_all_export_lineno(self) -> int | None:
            return self._first_all_export_lineno

        @override
        def _get_true_value(self) -> int | None:
            return self.first_all_export_lineno

    class SecondVisitPassFlag(_BaseVisitPassFlag):
        """"""

        @override
        def __init__(self, *, first_all_export_lineno: "RuleCAR105._BaseVisitPassFlag | int") -> None:  # noqa: E501
            if isinstance(first_all_export_lineno, RuleCAR105._BaseVisitPassFlag):
                raw_first_all_export_lineno: int | None = (
                    first_all_export_lineno._get_true_value()  # noqa: SLF001
                )
                if raw_first_all_export_lineno is None:
                    raise ValueError

                first_all_export_lineno = raw_first_all_export_lineno

            self._first_all_export_lineno: int = first_all_export_lineno

        @property
        @override
        def first_all_export_lineno(self) -> int:
            return self._first_all_export_lineno

        @override
        def __bool__(self) -> Literal[True]:
            if not super().__bool__():
                raise RuntimeError

            return True

        @override
        def _get_true_value(self) -> int | None:
            return self.first_all_export_lineno

    @override
    def __init__(self) -> None:
        self.visit_pass_flag: RuleCAR105._BaseVisitPassFlag = (
            self.FirstVisitPassFlag(first_all_export_lineno=None)
        )

        super().__init__()

    @classmethod
    @override
    def format_error_message(cls, ctx: dict[str, object]) -> str:
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
        if self.visit_pass_flag:
            raise RuntimeError

        self.visit(tree)

        if not isinstance(self.visit_pass_flag, self.FirstVisitPassFlag):
            raise RuntimeError  # noqa: TRY004

        self.visit_pass_flag = self.SecondVisitPassFlag(
            first_all_export_lineno=self.visit_pass_flag,
        )

        self.visit(tree)

    @override
    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, ast.Module):
            super().generic_visit(node)
            return

        EXPRESSION_BEFORE_ALL: Final[bool] = bool(
            hasattr(node, "lineno")
            and hasattr(node, "col_offset")
            and isinstance(self.visit_pass_flag, self.SecondVisitPassFlag)
            and node.lineno < self.visit_pass_flag.first_all_export_lineno
            and not bool(
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and node.lineno == 1  # noqa: COM812
            )
            and not bool(
                isinstance(node, ast.ImportFrom)
                and node.module in ("collections.abc", "typing")
                and any(name.name == "Sequence" for name in node.names)  # noqa: COM812
            )  # noqa: COM812
        )
        if EXPRESSION_BEFORE_ALL:
            line: str = ast.unparse(node).split("\n")[0]
            self.problems[(node.lineno, 0)] = {  # type: ignore[attr-defined]
                "line": f"`{line if len(line) < 30 else f"{line[:30]}..."}`",
            }

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        ALL_EXPORT_FOUND: Final[bool] = any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        )
        if ALL_EXPORT_FOUND and not self.visit_pass_flag:
            self.visit_pass_flag = self.FirstVisitPassFlag(first_all_export_lineno=node.lineno)

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        ALL_EXPORT_FOUND: Final[bool] = bool(
            isinstance(node.target, ast.Name)
            and node.target.id == "__all__"  # noqa: COM812
        )
        if ALL_EXPORT_FOUND and not self.visit_pass_flag:
            self.visit_pass_flag = self.FirstVisitPassFlag(first_all_export_lineno=node.lineno)

        self.generic_visit(node)
