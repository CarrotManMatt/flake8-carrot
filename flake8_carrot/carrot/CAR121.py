""""""  # noqa: N999

from collections.abc import Sequence

__all__: Sequence[str] = ("RuleCAR121",)


import ast
import re
from collections.abc import Mapping
from enum import Enum
from tokenize import TokenInfo
from typing import override

from flake8_carrot.utils import CarrotRule


class RuleCAR121(CarrotRule):
    """"""

    class _IgnoreCommentType(Enum):
        TYPE_IGNORE = (r"\s*#\s*type\s*:\s*ignore\s*\[\s*[a-z_-]+\s*(?:,\s*[a-z_-]+\s*)*(,)\s*]", "`type: ignore`")
        NOQA = (r"\s*#\s*noqa\s*:\s*[A-Z0-9]+(?:\s*,\s*[A-Z0-9]+)*\s*(,)", "NOQA")

    @classmethod
    @override
    def format_error_message(cls, ctx: Mapping[str, object]) -> str:
        ignore_comment_type: object | None = ctx.get("ignore_comment_type", None)
        if ignore_comment_type is not None and not isinstance(ignore_comment_type, cls._IgnoreCommentType):
            raise TypeError

        return f"CAR121 {ignore_comment_type.value[1] if ignore_comment_type is not None else "Ignore"} comment should not have trailing comma"

    @classmethod
    def _get_single_error_locations(cls, ignore_comment_type: _IgnoreCommentType, line: str, offset: int = 0) -> dict[int, _IgnoreCommentType]:
        match: re.Match[str] | None = re.search(f"{ignore_comment_type.value}\\Z", line)
        if match is None:
            return {}

        error_locations: dict[int, RuleCAR121._IgnoreCommentType] = {}

        if match.group(1) == ",":
            error_locations[offset + match.span(1)[0]] = ignore_comment_type

        return error_locations

    @classmethod
    def _get_type_ignore_first_error_locations(cls, line: str) -> Mapping[int, _IgnoreCommentType]:
        match: re.Match[str] | None = re.search(
            f"(?P<type_ignore>{cls._IgnoreCommentType.TYPE_IGNORE.value[0]})(?P<noqa>{cls._IgnoreCommentType.NOQA.value[0]})\\Z",
            line,
        )
        if match is None:
            return {}

        return (
            cls._get_single_error_locations(
                cls._IgnoreCommentType.TYPE_IGNORE,
                match.group("type_ignore"),
                offset=match.span("type_ignore")[0],
            )
            | cls._get_single_error_locations(
                cls._IgnoreCommentType.NOQA,
                match.group("noqa"),
                offset=match.span("noqa")[0],
            )
        )

    @classmethod
    def _get_noqa_first_error_locations(cls, line: str) -> Mapping[int, _IgnoreCommentType]:
        match: re.Match[str] | None = re.search(
            f"(?P<noqa>{cls._IgnoreCommentType.NOQA.value[0]})(?P<type_ignore>{cls._IgnoreCommentType.TYPE_IGNORE.value[0]})\\Z",
            line,
        )
        if match is None:
            return {}

        return (
            cls._get_single_error_locations(
                cls._IgnoreCommentType.NOQA,
                match.group("noqa"),
                offset=match.span("noqa")[0],
            )
            | cls._get_single_error_locations(
                cls._IgnoreCommentType.TYPE_IGNORE,
                match.group("type_ignore"),
                offset=match.span("type_ignore")[0],
            )
        )

    @classmethod
    def _get_all_error_locations(cls, line: str) -> Mapping[int, _IgnoreCommentType]:  # TODO: Not working
        type_ignore_first_error_locations: Mapping[int, RuleCAR121._IgnoreCommentType] = cls._get_type_ignore_first_error_locations(line)
        if type_ignore_first_error_locations:
            return type_ignore_first_error_locations

        noqa_first_error_locations: Mapping[int, RuleCAR121._IgnoreCommentType] = cls._get_noqa_first_error_locations(line)
        if noqa_first_error_locations:
            return noqa_first_error_locations

        single_type_ignore_error_locations: Mapping[int, RuleCAR121._IgnoreCommentType] = cls._get_single_error_locations(
            cls._IgnoreCommentType.TYPE_IGNORE,
            line,
        )
        if single_type_ignore_error_locations:
            return single_type_ignore_error_locations

        single_noqa_error_locations: Mapping[int, RuleCAR121._IgnoreCommentType] = cls._get_single_error_locations(
            cls._IgnoreCommentType.NOQA,
            line,
        )
        if single_noqa_error_locations:
            return single_noqa_error_locations

        return {}

    @override
    def run_check(self, tree: ast.AST, file_tokens: Sequence[TokenInfo], lines: Sequence[str]) -> None:  # noqa: E501
        line_number: int
        line: str
        for line_number, line in enumerate(lines):
            match_location: int
            ignore_comment_type: RuleCAR121._IgnoreCommentType
            for match_location, ignore_comment_type in self._get_all_error_locations(line.rstrip()).items():
                self.problems[(line_number + 1, match_location)] = {"ignore_comment_type": ignore_comment_type}
