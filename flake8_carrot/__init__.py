"""Custom opinionated linting rules to adhere Python code to CarrotManMatt's style guide."""

from collections.abc import Sequence

__all__: Sequence[str] = ("CarrotPlugin", "TeXBotPlugin")


from .plugins import CarrotPlugin, TeXBotPlugin
