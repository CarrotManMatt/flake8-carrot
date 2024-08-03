""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR106",)

import abc
import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, Literal, override

from flake8_carrot.utils import BaseRule


class RuleCAR106(BaseRule):
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
        def __init__(self, *, first_all_export_lineno: "RuleCAR106._BaseVisitPassFlag | int | None") -> None:  # noqa: E501
            if isinstance(first_all_export_lineno, RuleCAR106._BaseVisitPassFlag):
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
        def __init__(self, *, first_all_export_lineno: "RuleCAR106._BaseVisitPassFlag | int") -> None:  # noqa: E501
            if isinstance(first_all_export_lineno, RuleCAR106._BaseVisitPassFlag):
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
        self.visit_pass_flag: RuleCAR106._BaseVisitPassFlag = self.FirstVisitPassFlag(
            first_all_export_lineno=None,
        )

        super().__init__()

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
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        if self.visit_pass_flag:
            raise RuntimeError

        self.visit(tree)

        if not isinstance(self.visit_pass_flag, self.FirstVisitPassFlag):
            raise RuntimeError  # noqa: TRY004

        if self.visit_pass_flag:
            self.visit_pass_flag = self.SecondVisitPassFlag(
                first_all_export_lineno=self.visit_pass_flag,
            )

            self.visit(tree)

    @override
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        COLLECTIONS_IMPORT_FOUND: Final[bool] = bool(
            node.module in ("collections.abc", "typing")
            and isinstance(self.visit_pass_flag, self.SecondVisitPassFlag)
            and node.lineno < self.visit_pass_flag.first_all_export_lineno
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
