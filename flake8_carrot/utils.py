""""""

from collections.abc import Sequence

__all__: Sequence[str] = ("check_not_run_as_script",)


from typing import Final


def check_not_run_as_script(module_name: str) -> None:
    """"""
    if module_name == "__main__":
        CANNOT_RUN_AS_SCRIPT_MESSAGE: Final[str] = "This module cannot be run as a script."
        raise RuntimeError(CANNOT_RUN_AS_SCRIPT_MESSAGE)
