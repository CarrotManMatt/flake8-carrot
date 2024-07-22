""""""

from collections.abc import Sequence

__all__: Sequence[str] = ()

from collections.abc import Set

from flake8_carrot import TeXBotPlugin
from tests._testing_utils import apply_plugin_to_ast


def _apply_tex_bot_plugin_to_ast(raw_testing_ast: str) -> Set[str]:
    """"""
    return apply_plugin_to_ast(raw_testing_ast, TeXBotPlugin)
