"""Custom opinionated linting rules to adhere Python code to CarrotManMatt's style guide."""

from typing import TYPE_CHECKING

from .carrot import CarrotPlugin
from .tex_bot import TeXBotPlugin

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__: Sequence[str] = ("CarrotPlugin", "TeXBotPlugin")
