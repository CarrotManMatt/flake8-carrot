"""Linting rule to ensure cog subclass names end with "Command(s)"."""  # noqa: N999

import ast
from typing import TYPE_CHECKING, override

from flake8_carrot import utils
from flake8_carrot.utils import CarrotRule

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from tokenize import TokenInfo
    from typing import Final

__all__: Sequence[str] = ("RuleCAR302",)


class RuleCAR302(CarrotRule, ast.NodeVisitor):
    """Linting rule to ensure cog subclass names end with "Command(s)"."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        needs_to_be_plural: object | None = ctx.get("needs_to_be_plural", None)
        if needs_to_be_plural is not None and not isinstance(needs_to_be_plural, bool):
            raise TypeError

        return (
            "Pycord cog subclass name should end with "
            f"{
                f"'Command{'s' if needs_to_be_plural else ''}Cog'"
                if needs_to_be_plural is not None
                else "'CommandCog' or 'CommandsCog'"
            }, "
            f"if that cog contains {
                f'{"multiple commands" if needs_to_be_plural else "a single command"}'
                if needs_to_be_plural is not None
                else 'command(s)'
            }"
        )

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.visit(tree)

    def _function_is_command(self, node: ast.AsyncFunctionDef) -> bool:
        if node.name.startswith("_") or node.name.startswith("autocomplete_"):
            return False

        if node.returns is not None and not (
            isinstance(node.returns, ast.Constant) and node.returns.value is None
        ):
            return False

        has_slash_command_decorator: bool = False

        decorator_node: ast.expr
        for decorator_node in node.decorator_list:
            if not isinstance(decorator_node, ast.Call):
                continue

            if utils.function_call_is_pycord_task_decorator(decorator_node):
                return False

            if utils.function_call_is_pycord_event_listener_decorator(decorator_node):
                return False

            if utils.function_call_is_pycord_slash_command_decorator(decorator_node):
                has_slash_command_decorator = True
                continue

            if utils.function_call_is_pycord_context_command_decorator(decorator_node):
                has_slash_command_decorator = True
                continue

            possible_slash_command_group_name: str
            match decorator_node.func:
                case ast.Attribute(
                    value=ast.Name(id=possible_slash_command_group_name),
                    attr="command",
                ):
                    if (
                        possible_slash_command_group_name
                        in self.plugin.found_slash_command_group_names
                    ):
                        has_slash_command_decorator = True
                        continue

        if has_slash_command_decorator:
            return has_slash_command_decorator

        second_argument: ast.arg
        match node.args:
            case ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self"), second_argument, *_],
            ):
                if second_argument.arg == "ctx":
                    return True

                if "context" in second_argument.arg.lower():
                    return True

                second_argument_annotation: utils.ASTNameID
                match second_argument.annotation:
                    case (
                        ast.Name(id=second_argument_annotation)
                        | ast.Constant(value=second_argument_annotation)
                    ):
                        if "context" in str(second_argument_annotation).lower():
                            return True

        return False

    @classmethod
    def _is_class_a_cog_subclass(
        cls, class_name: str, class_bases: Iterable[ast.expr]
    ) -> bool:
        if "cog" in class_name:
            return True

        base: ast.expr
        for base in class_bases:
            if isinstance(base, ast.Attribute) and "cog" in base.attr.lower():
                return True

            if isinstance(base, ast.Name) and "cog" in base.id.lower():
                return True

        return False

    @classmethod
    def _is_cog_class_mislabelled(
        cls, class_name: str, number_of_commands_in_class: int
    ) -> bool:
        if "base" in class_name.lower():
            return False

        if number_of_commands_in_class == 1 and not class_name.endswith("CommandCog"):
            return True

        return number_of_commands_in_class > 1 and not class_name.endswith("CommandsCog")

    @utils.generic_visit_before_return
    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if not self._is_class_a_cog_subclass(node.name, node.bases):
            return

        number_of_commands_in_class: int = sum(
            (
                1
                for class_inner_node in node.body
                if (
                    isinstance(class_inner_node, ast.AsyncFunctionDef)
                    and self._function_is_command(class_inner_node)
                )
            ),
        )

        if number_of_commands_in_class < 0:
            NEGATIVE_COMMAND_FUNCTIONS_FOUND_MESSAGE: Final[str] = (
                "Found less than 0 command functions within cog class."
            )
            raise ValueError(NEGATIVE_COMMAND_FUNCTIONS_FOUND_MESSAGE)

        if number_of_commands_in_class == 0:
            return

        if self._is_cog_class_mislabelled(node.name, number_of_commands_in_class):
            self.problems[(node.lineno, node.col_offset + 6)] = {
                "needs_to_be_plural": number_of_commands_in_class > 1,
            }
