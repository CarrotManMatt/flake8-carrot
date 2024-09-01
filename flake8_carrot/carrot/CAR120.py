""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR120",)


import ast
import re
from collections.abc import Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR120(CarrotRule):
    """"""

    TYPE_IGNORE_REGEX: Final[str] = r"(\s*)#(\s*)type(\s*):(\s*)ignore(?:(\s*)\[(\s*)[a-z_-]+(\s*)((?:,\s*[a-z_-]+\s*)*)(?:,(\s*))?])?"
    NOQA_REGEX: Final[str] = r"(\s*)#(\s*)noqa(?:(\s*):(\s*)[A-Z0-9]+((?:\s*,\s*[A-Z0-9]+)*)(?:\s*,)?)?"

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        replacement_message: object | None = ctx.get("replacement_message", None)
        if replacement_message is not None and not isinstance(replacement_message, str):
            raise TypeError

        return (
            "CAR120 "
            "Incorrect amount of whitespace in ignore comment"
            f"{f" ({replacement_message})" if replacement_message else ""}"
        )

    @classmethod
    def _get_single_type_ignore_error_locations(cls, line: str, offset: int = 0) -> dict[int, str]:
        match: re.Match[str] | None = re.search(f"{cls.TYPE_IGNORE_REGEX}\\Z", line)
        if match is None:
            return {}

        error_locations: dict[int, str] = {}

        if match.group(1) != "  ":
            error_locations[offset + match.span(1)[0]] = "Replace with 2 spaces"

        if match.group(2) != " ":
            error_locations[offset + match.span(2)[0]] = "Replace with a single space"

        if match.group(3) != "":
            error_locations[offset + match.span(3)[0]] = "Remove all spaces"

        if match.group(4) != " ":
            error_locations[offset + match.span(4)[0]] = "Replace with a single space"

        group_number: int
        for group_number in (5, 6, 7):
            group: str | None = match.group(group_number)
            if group is None or group == "":
                continue
            error_locations[offset + match.span(group_number)[0]] = "Remove all spaces"

        group8: str | None = match.group(8)
        if group8 is not None:
            GROUP8_MATCH_START: Final[int] = match.span(8)[0]

            group8_match: re.Match[str]
            for group8_match in re.finditer(r",(\s*)[a-z_-]+(\s*)", group8):
                if group8_match.group(1) != " ":
                    error_locations[offset + GROUP8_MATCH_START + group8_match.span(1)[0]] = "Replace with a single space"
                if group8_match.group(2) != "":
                    error_locations[offset + GROUP8_MATCH_START +  group8_match.span(2)[0]] = "Remove all spaces"

        trailing_comma_group: str | None = match.group(9)
        if trailing_comma_group is not None and trailing_comma_group != "":
            error_locations[offset + match.span(9)[0]] = "Remove all spaces"

        return error_locations

    @classmethod
    def _get_single_noqa_error_locations(cls, line: str, offset: int = 0) -> dict[int, str]:
        match: re.Match[str] | None = re.search(f"{cls.NOQA_REGEX}\\Z", line)
        if match is None:
            return {}

        error_locations: dict[int, str] = {}

        if match.group(1) != "  ":
            error_locations[offset + match.span(1)[0]] = "Replace with 2 spaces"

        if match.group(2) != " ":
            error_locations[offset + match.span(2)[0]] = "Replace with a single space"

        group3: str | None = match.group(3)
        if group3 is not None and group3 != "":
            error_locations[offset + match.span(3)[0]] = "Remove all spaces"

        group4: str | None = match.group(4)
        if group4 is not None and group4 != " ":
            error_locations[offset + match.span(4)[0]] = "Replace with a single space"

        group5: str | None = match.group(5)
        if group5 is not None:
            GROUP5_MATCH_START: Final[int] = match.span(5)[0]

            group5_match: re.Match[str]
            for group5_match in re.finditer(r"(\s*),(\s*)[A-Z0-9]+", group5):
                if group5_match.group(1) != "":
                    error_locations[offset + GROUP5_MATCH_START + group5_match.span(1)[0]] = "Remove all spaces"
                if group5_match.group(2) != " ":
                    error_locations[offset + GROUP5_MATCH_START +  group5_match.span(2)[0]] = "Replace with a single space"

        return error_locations

    @classmethod
    def _get_type_ignore_first_error_locations(cls, line: str) -> Mapping[int, str]:
        match: re.Match[str] | None = re.search(
            f"(?P<type_ignore>{cls.TYPE_IGNORE_REGEX})(?P<noqa>{cls.NOQA_REGEX})\\Z",
            line,
        )
        if match is None:
            return {}

        return (
            cls._get_single_type_ignore_error_locations(
                match.group("type_ignore"),
                offset=match.span("type_ignore")[0],
            )
            | cls._get_single_noqa_error_locations(
                match.group("noqa"),
                offset=match.span("noqa")[0],
            )
        )

    @classmethod
    def _get_noqa_first_error_locations(cls, line: str) -> Mapping[int, str]:
        match: re.Match[str] | None = re.search(
            f"(?P<noqa>{cls.NOQA_REGEX})(?P<type_ignore>{cls.TYPE_IGNORE_REGEX})\\Z",
            line,
        )
        if match is None:
            return {}

        return (
            cls._get_single_noqa_error_locations(
                match.group("noqa"),
                offset=match.span("noqa")[0],
            )
            | cls._get_single_type_ignore_error_locations(
                match.group("type_ignore"),
                offset=match.span("type_ignore")[0],
            )
        )

    @classmethod
    def _get_all_error_locations(cls, line: str) -> Mapping[int, str]:
        type_ignore_first_error_locations: Mapping[int, str] = cls._get_type_ignore_first_error_locations(line)
        if type_ignore_first_error_locations:
            return type_ignore_first_error_locations

        noqa_first_error_locations: Mapping[int, str] = cls._get_noqa_first_error_locations(line)
        if noqa_first_error_locations:
            return noqa_first_error_locations

        single_type_ignore_error_locations: Mapping[int, str] = cls._get_single_type_ignore_error_locations(line)
        if single_type_ignore_error_locations:
            return single_type_ignore_error_locations

        single_noqa_error_locations: Mapping[int, str] = cls._get_single_noqa_error_locations(line)
        if single_noqa_error_locations:
            return single_noqa_error_locations

        return {}

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        line_number: int
        line: str
        for line_number, line in enumerate(lines):
            match_location: int
            replacement_message: str
            for match_location, replacement_message in self._get_all_error_locations(line.rstrip()).items():
                self.problems[(line_number + 1, match_location)] = {
                    "replacement_message": replacement_message,
                }
