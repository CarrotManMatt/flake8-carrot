"""Linting rule to ensure ignore comments have the correct amount of whitespace."""  # noqa: N999

import re
import tokenize
from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule, ProblemsContainer

if TYPE_CHECKING:
    import ast
    from collections.abc import Mapping, Sequence
    from tokenize import TokenInfo
    from typing import Final

__all__: Sequence[str] = ("RuleCAR120",)


class RuleCAR120(CarrotRule):
    """Linting rule to ensure ignore comments have the correct amount of whitespace."""

    TYPE_IGNORE_REGEX: Final[str] = (
        r"\s*#(\s*)type(\s*):(\s*)ignore(?:(\s*)\[(\s*)"
        r"[a-z_-]+(\s*)((?:,\s*[a-z_-]+\s*)*)(?:,(\s*))*])?"
    )
    NOQA_REGEX: Final[str] = (
        r"\s*#(\s*)noqa(?:(\s*):(\s*)[A-Z0-9]+"
        r"((?:\s*,\s*[A-Z0-9]+)*)(?:\s*,)*)?"
    )

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        replacement_message: object | None = ctx.get("replacement_message", None)
        if replacement_message is not None:
            if not isinstance(replacement_message, str):
                raise TypeError

            replacement_message = replacement_message.strip("\n\r\t '")

        return f"Incorrect amount of whitespace in ignore comment{
            f' ({replacement_message})' if replacement_message else ''
        }"

    @classmethod
    def _get_single_type_ignore_error_locations(
        cls, line: str, offset: int = 0
    ) -> dict[int, str]:
        match: re.Match[str] | None = re.search(rf"{cls.TYPE_IGNORE_REGEX}\Z", line)
        if match is None:
            return {}

        error_locations: dict[int, str] = {}

        if match.group(1) != " ":
            error_locations[offset + match.span(1)[0]] = "Replace with a single space"

        if match.group(2) != "":
            error_locations[offset + match.span(2)[0]] = "Remove all spaces"

        if match.group(3) != " ":
            error_locations[offset + match.span(3)[0]] = "Replace with a single space"

        group_number: int
        for group_number in (4, 5, 6):
            group: str | None = match.group(group_number)
            if group is None or group == "":
                continue
            error_locations[offset + match.span(group_number)[0]] = "Remove all spaces"

        group7: str | None = match.group(7)
        if group7 is not None:
            GROUP7_MATCH_START: Final[int] = match.span(7)[0]

            group7_match: re.Match[str]
            for group7_match in re.finditer(r",(\s*)[a-z_-]+(\s*)", group7):
                if group7_match.group(1) != " ":
                    error_locations[offset + GROUP7_MATCH_START + group7_match.span(1)[0]] = (
                        "Replace with a single space"
                    )
                if group7_match.group(2) != "":
                    error_locations[offset + GROUP7_MATCH_START + group7_match.span(2)[0]] = (
                        "Remove all spaces"
                    )

        trailing_comma_group: str | None = match.group(8)
        if trailing_comma_group is not None and trailing_comma_group != "":
            error_locations[offset + match.span(8)[0]] = "Remove all spaces"

        return error_locations

    @classmethod
    def _get_single_noqa_error_locations(cls, line: str, offset: int = 0) -> dict[int, str]:
        match: re.Match[str] | None = re.search(rf"{cls.NOQA_REGEX}\Z", line)
        if match is None:
            return {}

        error_locations: dict[int, str] = {}

        if match.group(1) != " ":
            error_locations[offset + match.span(1)[0]] = "Replace with a single space"

        group2: str | None = match.group(2)
        if group2 is not None and group2 != "":
            error_locations[offset + match.span(2)[0]] = "Remove all spaces"

        group3: str | None = match.group(3)
        if group3 is not None and group3 != " ":
            error_locations[offset + match.span(3)[0]] = "Replace with a single space"

        group4: str | None = match.group(4)
        if group4 is not None:
            GROUP4_MATCH_START: Final[int] = match.span(4)[0]

            group4_match: re.Match[str]
            for group4_match in re.finditer(r"(\s*),(\s*)[A-Z0-9]+", group4):
                if group4_match.group(1) != "":
                    error_locations[offset + GROUP4_MATCH_START + group4_match.span(1)[0]] = (
                        "Remove all spaces"
                    )
                if group4_match.group(2) != " ":
                    error_locations[offset + GROUP4_MATCH_START + group4_match.span(2)[0]] = (
                        "Replace with a single space"
                    )

        return error_locations

    @classmethod
    def _get_type_ignore_first_error_locations(cls, line: str) -> Mapping[int, str]:
        match: re.Match[str] | None = re.search(
            rf"(?P<type_ignore>{cls.TYPE_IGNORE_REGEX})(?P<noqa>{cls.NOQA_REGEX})\Z",
            line,
        )
        if match is None:
            return {}

        return cls._get_single_type_ignore_error_locations(
            match.group("type_ignore"),
            offset=match.span("type_ignore")[0],
        ) | cls._get_single_noqa_error_locations(
            match.group("noqa"),
            offset=match.span("noqa")[0],
        )

    @classmethod
    def _get_noqa_first_error_locations(cls, line: str) -> Mapping[int, str]:
        match: re.Match[str] | None = re.search(
            rf"(?P<noqa>{cls.NOQA_REGEX})(?P<type_ignore>{cls.TYPE_IGNORE_REGEX})\Z",
            line,
        )
        if match is None:
            return {}

        return cls._get_single_noqa_error_locations(
            match.group("noqa"),
            offset=match.span("noqa")[0],
        ) | cls._get_single_type_ignore_error_locations(
            match.group("type_ignore"),
            offset=match.span("type_ignore")[0],
        )

    @classmethod
    def _get_all_error_locations(cls, line: str) -> Mapping[int, str]:
        type_ignore_first_error_locations: Mapping[int, str] = (
            cls._get_type_ignore_first_error_locations(line)
        )
        if type_ignore_first_error_locations:
            return type_ignore_first_error_locations

        noqa_first_error_locations: Mapping[int, str] = cls._get_noqa_first_error_locations(
            line
        )
        if noqa_first_error_locations:
            return noqa_first_error_locations

        single_type_ignore_error_locations: Mapping[int, str] = (
            cls._get_single_type_ignore_error_locations(line)
        )
        if single_type_ignore_error_locations:
            return single_type_ignore_error_locations

        single_noqa_error_locations: Mapping[int, str] = cls._get_single_noqa_error_locations(
            line
        )
        if single_noqa_error_locations:
            return single_noqa_error_locations

        return {}

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.problems = ProblemsContainer(
            (
                self.problems
                | {
                    (file_token.start[0], file_token.start[1] + match_location): {
                        "replacement_message": replacement_message,
                    }
                    for file_token in file_tokens
                    for match_location, replacement_message in self._get_all_error_locations(
                        file_token.string.rstrip(),
                    ).items()
                    if file_token.type == tokenize.COMMENT
                }
            ),
        )
