""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR003",)

import ast
from collections.abc import Iterable
from typing import Final, override

import astpretty
from classproperties import classproperty

from flake8_carrot.utils import BaseRule


class RuleCAR003(BaseRule):
    """"""

    @override
    def __init__(self) -> None:
        self.all_found_count: int = 0

        super().__init__()

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @override
    def ERROR_MESSAGE(cls) -> str:  # noqa: N805
        return "CAR003 `__all__` export should be annotated as `Sequence[str]`"

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        all_assignment_targets: Iterable[ast.Name] = (target for target in node.targets if isinstance(target, ast.Name) and target.id == "__all__")
        if all_assignment_targets:
            if self.all_found_count == 0:
                all_assignment: ast.Name = next(iter(all_assignment_targets))
                self.problems.add((all_assignment.lineno, all_assignment.end_col_offset - 1))

            self.all_found_count += 1

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        ALL_EXPORT_FOUND: Final[bool] = bool(
            isinstance(node.target, ast.Name)
            and node.target.id == "__all__"  # noqa: COM812
        )
        if ALL_EXPORT_FOUND:
            CORRECT_ANNOTATION: Final[bool] = bool(
                isinstance(node.annotation, ast.Subscript)
                and isinstance(node.annotation.value, ast.Name)
                and isinstance(node.annotation.slice, ast.Name)
                and node.annotation.value.id == "Sequence"
                and node.annotation.slice.id == "str"  # noqa: COM812
            )
            if self.all_found_count == 0 and not CORRECT_ANNOTATION:
                self.problems.add(
                    (
                        node.annotation.lineno,
                        (
                            node.annotation.end_col_offset - 1
                            if isinstance(node.annotation, ast.Name) and node.annotation.id == "Sequence"
                            else node.annotation.col_offset
                        ),
                    ),
                )

            self.all_found_count += 1

        self.generic_visit(node)
