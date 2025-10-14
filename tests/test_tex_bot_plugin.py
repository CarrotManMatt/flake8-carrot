"""Test suite to check the functionality of all TXB plugin rules."""

from typing import TYPE_CHECKING

from flake8_carrot import TeXBotPlugin
from tests._testing_utils import apply_plugin_to_ast

if TYPE_CHECKING:
    from collections.abc import Sequence
    from collections.abc import Set as AbstractSet

__all__: Sequence[str] = ()


def _apply_tex_bot_plugin_to_ast(raw_testing_ast: str) -> AbstractSet[str]:
    return apply_plugin_to_ast(raw_testing_ast, TeXBotPlugin)
