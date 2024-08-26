""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR202",)


import ast
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR202(CarrotRule, ast.NodeVisitor):
    """"""

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return (
            "CAR202 "
            "`logging.Logger` variable name should contain the word 'logger'"
        )

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        self.visit(tree)

    @override
    def visit_Assign(self, node: ast.Assign) -> None:
        LOGGER_ASSIGNMENT_FOUND: Final[bool] = bool(
            isinstance(node.value, ast.Call)
            and (
                bool(
                    isinstance(node.value.func, ast.Attribute)
                    and isinstance(node.value.func.value, ast.Name)
                    and node.value.func.value.id == "logging"
                    and node.value.func.attr == "getLogger"  # noqa: COM812
                )
                or bool(
                    isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "getLogger"  # noqa: COM812
                )
            )  # noqa: COM812
        )
        if LOGGER_ASSIGNMENT_FOUND:
            targets: list[ast.Name] = [
                target for target in node.targets if isinstance(target, ast.Name)
            ]
            if len(targets) == 1 and "logger" not in targets[0].id:
                self.problems.add_without_ctx((targets[0].lineno, targets[0].col_offset))

        self.generic_visit(node)

    @override
    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        LOGGER_ASSIGNMENT_FOUND: Final[bool] = bool(
            bool(
                isinstance(node.target, ast.Name)
                and bool(
                    isinstance(node.value, ast.Call)
                    and (
                        bool(
                            isinstance(node.value.func, ast.Attribute)
                            and isinstance(node.value.func.value, ast.Name)
                            and node.value.func.value.id == "logging"
                            and node.value.func.attr == "getLogger"  # noqa: COM812
                        )
                        or bool(
                            isinstance(node.value.func, ast.Name)
                            and node.value.func.id == "getLogger"  # noqa: COM812
                        )
                    )  # noqa: COM812
                )  # noqa: COM812
            )
            or bool(
                isinstance(node.annotation, ast.Name)
                and node.annotation.id == "Logger"  # noqa: COM812
            )
            or bool(
                isinstance(node.annotation, ast.Attribute)
                and isinstance(node.annotation.value, ast.Name)
                and node.annotation.value.id == "logging"
                and node.annotation.attr == "Logger"  # noqa: COM812
            )
            or bool(
                isinstance(node.annotation, ast.Subscript)
                and isinstance(node.annotation.value, ast.Name)
                and isinstance(node.annotation.slice, ast.Name)
                and node.annotation.value.id == "Final"
                and node.annotation.slice.id == "Logger"  # noqa: COM812
            )
            or bool(
                isinstance(node.annotation, ast.Subscript)
                and isinstance(node.annotation.value, ast.Name)
                and isinstance(node.annotation.slice, ast.Attribute)
                and isinstance(node.annotation.slice.value, ast.Name)
                and node.annotation.value.id == "Final"
                and node.annotation.slice.value.id == "logging"
                and node.annotation.slice.attr == "Logger"  # noqa: COM812
            )  # noqa: COM812
        )
        if LOGGER_ASSIGNMENT_FOUND and self._logger_in_assignment_target(node.target):
            self.problems.add_without_ctx((node.target.lineno, node.target.col_offset))

        self.generic_visit(node)

    @classmethod
    def _logger_in_assignment_target(cls, target: ast.expr | str) -> bool:
        match target:
            case str():
                return "logger" in target.lower()

            case ast.Name():
                # noinspection PyUnresolvedReferences
                return cls._logger_in_assignment_target(target.id)

            case ast.Constant():
                return cls._logger_in_assignment_target(target.value)

            case ast.Attribute():
                # noinspection PyUnresolvedReferences
                ATTRIBUTE_CONTAINS_LOGGER: Final[bool] = cls._logger_in_assignment_target(
                    target.attr,
                )
                if ATTRIBUTE_CONTAINS_LOGGER:
                    return ATTRIBUTE_CONTAINS_LOGGER

                return cls._logger_in_assignment_target(target.value)

            case ast.Subscript():
                SUBSCRIPT_CONTAINS_LOGGER: Final[bool] = cls._logger_in_assignment_target(
                    target.value,
                )
                if SUBSCRIPT_CONTAINS_LOGGER:
                    return SUBSCRIPT_CONTAINS_LOGGER

                # noinspection PyUnresolvedReferences
                if isinstance(target.slice, ast.expr):
                    # noinspection PyUnresolvedReferences
                    return cls._logger_in_assignment_target(target.slice)

                raise NotImplementedError  # TODO

            case _:
                UNABLE_TO_IDENTIFY_LOGGER_MESSAGE: Final[str] = (
                    "Not able to identify the word `logger` "
                    f"within ast node 'ast.{type(target).__name__}'."
                )
                raise TypeError(UNABLE_TO_IDENTIFY_LOGGER_MESSAGE)
