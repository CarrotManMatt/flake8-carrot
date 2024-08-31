""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR120",)


import ast
import re
from collections.abc import Set as AbstractSet
from collections.abc import Iterable, Mapping
from tokenize import TokenInfo
from typing import Final, override

from flake8_carrot.utils import CarrotRule


class RuleCAR120(CarrotRule):
    """"""

    TYPE_IGNORE_REGEX: Final[str] = r"(\s*)#(\s*)type(\s*):(\s*)ignore(?:(\s*)\[(\s*)[a-z_-]+(\s*)((?:,\s*[a-z_-]+\s*)*)])?"
    NOQA_REGEX: Final[str] = r"(\s*)#(\s*)noqa(?:(\s*):(\s*)[A-Z0-9]+((?:\s*,\s*[A-Z0-9]+)*))?"

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        return "CAR120 Incorrect amount of whitespace in ignore comment"

    @classmethod
    def _get_single_type_ignore_error_locations(cls, match: re.Match[str]) -> AbstractSet[int]:
        # noinspection DuplicatedCode
        error_locations: set[int] = set()

        if match.group(1) != "  ":
            error_locations.add(match.span(1)[0])

        if match.group(2) != " ":
            error_locations.add(match.span(2)[0])

        if match.group(3) != "":
            error_locations.add(match.span(3)[0])

        if match.group(4) != " ":
            error_locations.add(match.span(4)[0])

        group_number: int
        for group_number in (5, 6, 7):
            group: str | None = match.group(group_number)
            if group is None or group == "":
                continue
            error_locations.add(match.span(group_number)[0])

        group8: str | None = match.group(8)
        if group8 is not None:
            GROUP8_MATCH_START: Final[int] = match.span(8)[0]

            group8_match: re.Match[str]
            for group8_match in re.finditer(r",(\s*)[a-z_-]+(\s*)", group8):
                if group8_match.group(1) != " ":
                    error_locations.add(GROUP8_MATCH_START + group8_match.span(1)[0])
                if group8_match.group(2) != "":
                    error_locations.add(GROUP8_MATCH_START +  group8_match.span(2)[0])

        return error_locations

    @classmethod
    def _get_single_noqa_error_locations(cls, match: re.Match[str]) -> AbstractSet[int]:
        # noinspection DuplicatedCode
        error_locations: set[int] = set()

        if match.group(1) != "  ":
            error_locations.add(match.span(1)[0])

        if match.group(2) != " ":
            error_locations.add(match.span(2)[0])

        group3: str | None = match.group(3)
        if group3 is not None and group3 != "":
            error_locations.add(match.span(3)[0])

        group4: str | None = match.group(4)
        if group4 is not None and group4 != " ":
            error_locations.add(match.span(4)[0])

        group5: str | None = match.group(5)
        if group5 is not None:
            GROUP5_MATCH_START: Final[int] = match.span(5)[0]

            group5_match: re.Match[str]
            for group5_match in re.finditer(r"(\s*),(\s*)[A-Z0-9]+", group5):
                if group5_match.group(1) != "":
                    error_locations.add(GROUP5_MATCH_START + group5_match.span(1)[0])
                if group5_match.group(2) != " ":
                    error_locations.add(GROUP5_MATCH_START +  group5_match.span(2)[0])

        return error_locations

    @classmethod
    def _get_type_ignore_first_error_locations(cls, line: str) -> AbstractSet[int]:
        error_locations: set[int] = set()

        match: re.Match[str] | None = re.search(
            f"{cls.TYPE_IGNORE_REGEX}{cls.NOQA_REGEX}\\Z",
            line,
        )
        if match is None:
            return error_locations

        error_locations = error_locations | cls._get_single_type_ignore_error_locations(match)

        if match.group(9) != "  ":
            error_locations.add(match.span(9)[0])

        if match.group(10) != " ":
            error_locations.add(match.span(10)[0])

        group11: str | None = match.group(11)
        if group11 is not None and group11 != "":
            error_locations.add(match.span(11)[0])

        group12: str | None = match.group(12)
        if group12 is not None and group12 != " ":
            error_locations.add(match.span(12)[0])

        group13: str | None = match.group(13)
        if group13 is not None:
            GROUP13_MATCH_START: Final[int] = match.span(13)[0]

            group13_match: re.Match[str]
            for group13_match in re.finditer(r"(\s*),(\s*)[A-Z0-9]+", group13):
                if group13_match.group(1) != "":
                    error_locations.add(GROUP13_MATCH_START + group13_match.span(1)[0])
                if group13_match.group(2) != " ":
                    error_locations.add(GROUP13_MATCH_START +  group13_match.span(2)[0])

        return error_locations

    @classmethod
    def _get_noqa_first_error_locations(cls, line: str) -> AbstractSet[int]:
        # noinspection DuplicatedCode
        error_locations: set[int] = set()

        match: re.Match[str] | None = re.search(
            f"{cls.NOQA_REGEX}{cls.TYPE_IGNORE_REGEX}\\Z",
            line,
        )
        if match is None:
            return error_locations

        error_locations = error_locations | cls._get_single_noqa_error_locations(match)

        if match.group(6) != "  ":
            error_locations.add(match.span(6)[0])

        if match.group(7) != " ":
            error_locations.add(match.span(7)[0])

        if match.group(8) != "":
            error_locations.add(match.span(8)[0])

        if match.group(9) != " ":
            error_locations.add(match.span(9)[0])

        group_number: int
        for group_number in (10, 11, 12):
            group: str | None = match.group(group_number)
            if group is None or group == "":
                continue
            error_locations.add(match.span(group_number)[0])

        group13: str | None = match.group(13)
        if group13 is not None:
            GROUP13_MATCH_START: Final[int] = match.span(13)[0]

            group13_match: re.Match[str]
            for group13_match in re.finditer(r",(\s*)[a-z_-]+(\s*)", group13):
                if group13_match.group(1) != " ":
                    error_locations.add(GROUP13_MATCH_START + group13_match.span(1)[0])
                if group13_match.group(2) != "":
                    error_locations.add(GROUP13_MATCH_START +  group13_match.span(2)[0])

        return error_locations

    @classmethod
    def _get_all_error_locations(cls, line: str) -> Iterable[int]:
        single_type_ignore_match: re.Match[str] | None = re.search(
            f"{cls.TYPE_IGNORE_REGEX}\\Z",
            line,
        )
        single_noqa_match: re.Match[str] | None = re.search(
            f"{cls.NOQA_REGEX}\\Z",
            line,
        )

        return (
            (
                cls._get_single_type_ignore_error_locations(single_type_ignore_match)
                if single_type_ignore_match is not None
                else set()
            )
            | (
                cls._get_single_noqa_error_locations(single_noqa_match)
                if single_noqa_match is not None
                else set()
            )
            | cls._get_type_ignore_first_error_locations(line)
            | cls._get_noqa_first_error_locations(line)
        )

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        line_number: int
        line: str
        for line_number, line in enumerate(lines):
            match_location: int
            for match_location in self._get_all_error_locations(line.rstrip()):
                self.problems.add_without_ctx((line_number + 1, match_location))
