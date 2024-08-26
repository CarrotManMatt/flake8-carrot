
""""""

from collections.abc import Sequence

__all__: Sequence[str] = (
    "CarrotPlugin",
    "RuleCAR101",
    "RuleCAR102",
    "RuleCAR103",
    "RuleCAR104",
    "RuleCAR105",
    "RuleCAR106",
    "RuleCAR107",
    "RuleCAR108",
    "RuleCAR201",
    "RuleCAR202",
    "RuleCAR301",
    "RuleCAR302",
    "RuleCAR303",
)


import ast
from tokenize import TokenInfo
from typing import AbstractSet, Final, override

from classproperties import classproperty

from flake8_carrot.utils import BasePlugin, CarrotRule

from .CAR101 import RuleCAR101
from .CAR102 import RuleCAR102
from .CAR103 import RuleCAR103
from .CAR104 import RuleCAR104
from .CAR105 import RuleCAR105
from .CAR106 import RuleCAR106
from .CAR107 import RuleCAR107
from .CAR108 import RuleCAR108
from .CAR201 import RuleCAR201
from .CAR202 import RuleCAR202
from .CAR301 import RuleCAR301
from .CAR302 import RuleCAR302
from .CAR303 import RuleCAR303


class CarrotPlugin(BasePlugin):
    """"""

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @override
    def name(cls) -> str:  # noqa: N805
        return cls._name(__name__)

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    @override
    def RULES(cls) -> frozenset[type[CarrotRule]]:  # type: ignore[override] # noqa: N805
        return frozenset(
            {
                RuleCAR101,
                RuleCAR102,
                RuleCAR103,
                RuleCAR104,
                RuleCAR105,
                RuleCAR106,
                RuleCAR107,
                RuleCAR108,
                RuleCAR201,
                RuleCAR202,
                RuleCAR301,
                RuleCAR302,
                RuleCAR303,
            },
        )

    @override
    def __init__(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        class ContextValuesFinder(ast.NodeVisitor):
            """"""

            @override
            def __init__(self) -> None:
                self.found_slash_command_group_names: set[str] = set()
                self.first_all_export_line_numbers: tuple[int, int] | None = None

            @classmethod
            def _node_is_slash_command_group_assignment(cls, node: ast.Assign | ast.AnnAssign) -> bool:
                return bool(
                    bool(
                        isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Name)
                        and node.value.func.id == "SlashCommandGroup"  # noqa: COM812
                    ) or bool(
                        isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Attribute)
                        and isinstance(node.value.func.value, ast.Name)
                        and node.value.func.value.id == "discord"
                        and node.value.func.attr == "SlashCommandGroup"  # noqa: COM812
                    ) or bool(
                        isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Attribute)
                        and isinstance(node.value.func.value, ast.Attribute)
                        and isinstance(node.value.func.value.value, ast.Name)
                        and node.value.func.value.value.id == "discord"
                        and node.value.func.value.attr == "commands"
                        and node.value.func.attr == "SlashCommandGroup"  # noqa: COM812
                    ) or bool(
                        isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Attribute)
                        and isinstance(node.value.func.value, ast.Attribute)
                        and isinstance(node.value.func.value.value, ast.Attribute)
                        and isinstance(node.value.func.value.value.value, ast.Name)
                        and node.value.func.value.value.value.id == "discord"
                        and node.value.func.value.value.attr == "commands"
                        and node.value.func.value.attr == "core"
                        and node.value.func.attr == "SlashCommandGroup"  # noqa: COM812
                    )  # noqa: COM812
                )

            @override
            def visit_Assign(self, node: ast.Assign) -> None:
                if self._node_is_slash_command_group_assignment(node):
                    target: ast.expr
                    for target in node.targets:
                        if not isinstance(target, ast.Name):
                            continue

                        self.found_slash_command_group_names.add(target.id)

                ALL_EXPORT_FOUND: Final[bool] = any(
                    isinstance(target, ast.Name) and target.id == "__all__"
                    for target in node.targets
                )
                if ALL_EXPORT_FOUND and self.first_all_export_line_numbers is None:
                    self.first_all_export_line_numbers = (
                        node.lineno,
                        node.end_lineno or node.lineno
                    )

                self.generic_visit(node)

            @override
            def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
                NODE_IS_SLASH_COMMAND_GROUP_ASSIGNMENT: Final[bool] = bool(
                    isinstance(node.target, ast.Name)
                    and self._node_is_slash_command_group_assignment(node)
                )
                if NODE_IS_SLASH_COMMAND_GROUP_ASSIGNMENT:
                    self.found_slash_command_group_names.add(node.target.id)  # type: ignore[union-attr]

                ALL_EXPORT_FOUND: Final[bool] = bool(
                    isinstance(node.target, ast.Name)
                    and node.target.id == "__all__"  # noqa: COM812
                )
                if ALL_EXPORT_FOUND and self.first_all_export_line_numbers is None:
                    self.first_all_export_line_numbers = (
                        node.lineno,
                        node.end_lineno or node.lineno#
                    )

                self.generic_visit(node)

        context_values_finder: ContextValuesFinder = ContextValuesFinder()
        context_values_finder.visit(tree)

        self._found_slash_command_group_names: AbstractSet[str] = (
            context_values_finder.found_slash_command_group_names
        )
        self._first_all_export_line_numbers: tuple[int, int] | None = (
            context_values_finder.first_all_export_line_numbers
        )
        self._true_start_line_number: int = self._find_true_start_line_number(tree)

        super().__init__(tree=tree, file_tokens=file_tokens, lines=lines)

    @property
    def found_slash_command_group_names(self) -> AbstractSet[str]:
        return self._found_slash_command_group_names

    @property
    def first_all_export_line_numbers(self) -> tuple[int, int] | None:
        return self._first_all_export_line_numbers

    @property
    def true_start_line_number(self) -> int:
        return self._true_start_line_number

    @classmethod
    def _find_true_start_line_number(cls, tree: ast.AST) -> int:
        if not isinstance(tree, ast.Module):
            raise TypeError("'tree' AST must be a module.")

        first_node: ast.stmt | None = next(iter(tree.body), None)
        if first_node is None:
            return 1

        return first_node.lineno
