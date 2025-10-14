"""Linting rules under the "CAR" category."""

import ast
from typing import TYPE_CHECKING, override

from typed_classproperties import classproperty

from flake8_carrot import utils
from flake8_carrot.utils import BasePlugin, CarrotRule

from .CAR101 import RuleCAR101
from .CAR102 import RuleCAR102
from .CAR103 import RuleCAR103
from .CAR104 import RuleCAR104
from .CAR105 import RuleCAR105
from .CAR110 import RuleCAR110
from .CAR111 import RuleCAR111
from .CAR120 import RuleCAR120
from .CAR121 import RuleCAR121
from .CAR122 import RuleCAR122
from .CAR123 import RuleCAR123
from .CAR124 import RuleCAR124
from .CAR140 import RuleCAR140
from .CAR141 import RuleCAR141
from .CAR150 import RuleCAR150
from .CAR151 import RuleCAR151
from .CAR160 import RuleCAR160
from .CAR161 import RuleCAR161
from .CAR162 import RuleCAR162
from .CAR163 import RuleCAR163
from .CAR170 import RuleCAR170
from .CAR180 import RuleCAR180
from .CAR201 import RuleCAR201
from .CAR202 import RuleCAR202
from .CAR301 import RuleCAR301
from .CAR302 import RuleCAR302
from .CAR303 import RuleCAR303
from .CAR304 import RuleCAR304
from .CAR305 import RuleCAR305
from .CAR401 import RuleCAR401
from .CAR501 import RuleCAR501
from .CAR601 import RuleCAR601
from .CAR602 import RuleCAR602
from .CAR610 import RuleCAR610

if TYPE_CHECKING:
    from collections.abc import Collection, Sequence
    from collections.abc import Set as AbstractSet
    from tokenize import TokenInfo

__all__: Sequence[str] = (
    "CarrotPlugin",
    "CarrotRule",
    "RuleCAR101",
    "RuleCAR102",
    "RuleCAR103",
    "RuleCAR104",
    "RuleCAR105",
    "RuleCAR110",
    "RuleCAR111",
    "RuleCAR120",
    "RuleCAR121",
    "RuleCAR122",
    "RuleCAR123",
    "RuleCAR124",
    "RuleCAR140",
    "RuleCAR141",
    "RuleCAR150",
    "RuleCAR151",
    "RuleCAR160",
    "RuleCAR161",
    "RuleCAR162",
    "RuleCAR163",
    "RuleCAR170",
    "RuleCAR180",
    "RuleCAR201",
    "RuleCAR202",
    "RuleCAR301",
    "RuleCAR302",
    "RuleCAR303",
    "RuleCAR304",
    "RuleCAR305",
    "RuleCAR401",
    "RuleCAR501",
    "RuleCAR601",
    "RuleCAR602",
    "RuleCAR610",
)


class _ContextValuesFinder(ast.NodeVisitor):
    @override
    def __init__(self) -> None:
        self.found_slash_command_group_names: set[str] = set()
        self.first_all_export_line_numbers: tuple[int, int] | None = None
        self.pprint_imported_for_debugging: bool = False

        # TODO: Implement finding  # noqa: FIX002
        self.found_loggers: set[ast.Assign | ast.AnnAssign] = set()

    @classmethod
    def _node_is_slash_command_group_assignment(cls, node: ast.Assign | ast.AnnAssign) -> bool:
        match node.value:
            case ast.Call(
                func=(
                    ast.Name(id="SlashCommandGroup")
                    | ast.Attribute(
                        value=(
                            ast.Name(id="discord")
                            | ast.Attribute(
                                value=ast.Name(id="discord"),
                                attr="commands",
                            )
                            | ast.Attribute(
                                value=ast.Attribute(
                                    value=ast.Name(id="discord"),
                                    attr="commands",
                                ),
                                attr="core",
                            )
                        ),
                        attr="SlashCommandGroup",
                    )
                ),
            ):
                return True

            case _:
                return False

    @utils.generic_visit_before_return
    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        if self._node_is_slash_command_group_assignment(node):
            target: ast.expr
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    continue

                self.found_slash_command_group_names.add(target.id)

        if self.first_all_export_line_numbers is None:
            for target in node.targets:
                match target:
                    case ast.Name(id="__all__"):
                        self.first_all_export_line_numbers = (
                            node.lineno,
                            node.end_lineno or node.lineno,
                        )
                        break

        # TODO: Find loggers using rule 201  # noqa: FIX002

    @utils.generic_visit_before_return
    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name) and self._node_is_slash_command_group_assignment(
            node
        ):
            self.found_slash_command_group_names.add(node.target.id)

        match node.target:
            case ast.Name(id="__all__") if self.first_all_export_line_numbers is None:
                self.first_all_export_line_numbers = (
                    node.lineno,
                    (node.end_lineno or node.lineno),
                )

    @utils.generic_visit_before_return
    @override
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module in utils.PPRINT_MODULES:
            import_alias: ast.alias
            for import_alias in node.names:
                if "print" in import_alias.name:
                    self.pprint_imported_for_debugging = True
                    break


class CarrotPlugin(BasePlugin):
    """Plugin class holding all "TXB" rules to be run on some code provided by Flake8."""

    @classproperty
    @override
    def RULES(cls) -> Collection[type[CarrotRule]]:
        return {
            RuleCAR101,
            RuleCAR102,
            RuleCAR103,
            RuleCAR104,
            RuleCAR105,
            RuleCAR110,
            RuleCAR111,
            RuleCAR120,
            RuleCAR121,
            RuleCAR122,
            RuleCAR123,
            RuleCAR124,
            RuleCAR140,
            RuleCAR141,
            RuleCAR150,
            RuleCAR151,
            RuleCAR160,
            RuleCAR161,
            RuleCAR162,
            RuleCAR163,
            RuleCAR170,
            RuleCAR180,
            RuleCAR201,
            RuleCAR202,
            RuleCAR301,
            RuleCAR302,
            RuleCAR303,
            RuleCAR304,
            RuleCAR305,
            RuleCAR401,
            RuleCAR501,
            RuleCAR601,
            RuleCAR602,
            RuleCAR610,
        }

    @override
    def __init__(
        self,
        tree: ast.AST,
        file_tokens: "Sequence[TokenInfo]",  # noqa: UP037
        lines: "Sequence[str]",  # noqa: UP037
    ) -> None:
        context_values_finder: _ContextValuesFinder = _ContextValuesFinder()
        context_values_finder.visit(tree)

        self._found_slash_command_group_names: AbstractSet[str] = (
            context_values_finder.found_slash_command_group_names
        )
        self._first_all_export_line_numbers: tuple[int, int] | None = (
            context_values_finder.first_all_export_line_numbers
        )
        self._pprint_imported_for_debugging: bool = (
            context_values_finder.pprint_imported_for_debugging
        )
        self._found_loggers: AbstractSet[ast.Assign | ast.AnnAssign] = (
            context_values_finder.found_loggers
        )

        super().__init__(tree=tree, file_tokens=file_tokens, lines=lines)

    @property
    def found_slash_command_group_names(self) -> AbstractSet[str]:  # noqa: D102
        return self._found_slash_command_group_names

    @property
    def first_all_export_line_numbers(self) -> tuple[int, int] | None:  # noqa: D102
        return self._first_all_export_line_numbers

    @property
    def pprint_imported_for_debugging(self) -> bool:  # noqa: D102
        return self._pprint_imported_for_debugging

    @property
    def found_loggers(self) -> AbstractSet[ast.Assign | ast.AnnAssign]:  # noqa: D102
        return self._found_loggers
