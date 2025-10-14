"""Linting rule to ensure linting comments do not have an incorrect number of commas."""  # noqa: N999

import re
import tokenize
from collections.abc import Mapping
from enum import Enum
from typing import TYPE_CHECKING, override

from flake8_carrot.utils import CarrotRule, ProblemsContainer

if TYPE_CHECKING:
    import ast
    from collections.abc import Sequence
    from tokenize import TokenInfo

__all__: Sequence[str] = ("RuleCAR121",)


type _ErrorLocationContext = tuple[_IgnoreCommentType, bool]
type _ErrorLocationsMapping = Mapping[int, _ErrorLocationContext]
type _ErrorLocationsDict = dict[int, _ErrorLocationContext]


class _IgnoreCommentType(Enum):
    TYPE_IGNORE = (
        r"\s*#\s*type\s*:\s*ignore\s*\[\s*[a-z_-]+\s*(?:,\s*[a-z_-]+\s*)*((?:,\s*)+)\s*]",
        "`type: ignore`",
    )
    NOQA = (r"\s*#\s*noqa\s*:\s*[A-Z0-9]+(?:\s*,\s*[A-Z0-9]+)*\s*((?:,\s*)+)", "NOQA")


class RuleCAR121(CarrotRule):
    """Linting rule to ensure linting comments do not have an incorrect number of commas."""

    @classmethod
    @override
    def _format_error_message(cls, ctx: Mapping[str, object]) -> str:
        ignore_comment_type: object | None = ctx.get("ignore_comment_type", None)
        if ignore_comment_type is not None and not isinstance(
            ignore_comment_type, _IgnoreCommentType
        ):
            raise TypeError

        multiple_commas: object | None = ctx.get("multiple_commas", None)
        if multiple_commas is not None and not isinstance(multiple_commas, bool):
            raise TypeError

        return (
            f"{ignore_comment_type.value[1] if ignore_comment_type is not None else 'Ignore'} "
            f"comment should not have {
                'trailing comma(s)'
                if multiple_commas is None
                else ('trailing commas' if multiple_commas else 'a trailing comma')
            }"
        )

    @classmethod
    def _get_single_error_locations(
        cls, ignore_comment_type: _IgnoreCommentType, line: str, offset: int = 0
    ) -> _ErrorLocationsDict:
        match: re.Match[str] | None = re.search(rf"{ignore_comment_type.value[0]}\Z", line)
        if match is None:
            return {}

        error_locations: _ErrorLocationsDict = {}

        match match.group(1).count(","):
            case 0:
                raise ValueError
            case 1:
                error_locations[offset + match.span(1)[0]] = ignore_comment_type, False
            case _:
                error_locations[offset + match.span(1)[0]] = ignore_comment_type, True

        return error_locations

    @classmethod
    def _get_type_ignore_first_error_locations(cls, line: str) -> _ErrorLocationsMapping:
        match: re.Match[str] | None = re.search(
            (
                rf"(?P<type_ignore>{
                    _IgnoreCommentType.TYPE_IGNORE.value[0].replace(
                        r'((?:,\s*)+)',
                        r'(?:,\s*)*',
                    )
                })"
                rf"(?P<noqa>{
                    _IgnoreCommentType.NOQA.value[0].replace(
                        r'((?:,\s*)+)',
                        r'(?:,\s*)*',
                    )
                })"
                r"\Z"
            ),
            line,
        )
        if match is None:
            return {}

        return cls._get_single_error_locations(
            _IgnoreCommentType.TYPE_IGNORE,
            match.group("type_ignore"),
            offset=match.span("type_ignore")[0],
        ) | cls._get_single_error_locations(
            _IgnoreCommentType.NOQA,
            match.group("noqa"),
            offset=match.span("noqa")[0],
        )

    @classmethod
    def _get_noqa_first_error_locations(cls, line: str) -> _ErrorLocationsMapping:
        match: re.Match[str] | None = re.search(
            (
                rf"(?P<noqa>{
                    _IgnoreCommentType.NOQA.value[0].replace(
                        r'((?:,\s*)+)',
                        r'(?:,\s*)*',
                    )
                })"
                rf"(?P<type_ignore>{
                    _IgnoreCommentType.TYPE_IGNORE.value[0].replace(
                        r'((?:,\s*)+)',
                        r'(?:,\s*)*',
                    )
                })"
                r"\Z"
            ),
            line,
        )
        if match is None:
            return {}

        return cls._get_single_error_locations(
            _IgnoreCommentType.NOQA,
            match.group("noqa"),
            offset=match.span("noqa")[0],
        ) | cls._get_single_error_locations(
            _IgnoreCommentType.TYPE_IGNORE,
            match.group("type_ignore"),
            offset=match.span("type_ignore")[0],
        )

    @classmethod
    def _get_all_error_locations(cls, line: str) -> _ErrorLocationsMapping:
        type_ignore_first_error_locations: _ErrorLocationsMapping = (
            cls._get_type_ignore_first_error_locations(line)
        )
        if type_ignore_first_error_locations:
            return type_ignore_first_error_locations

        noqa_first_error_locations: _ErrorLocationsMapping = (
            cls._get_noqa_first_error_locations(line)
        )
        if noqa_first_error_locations:
            return noqa_first_error_locations

        single_type_ignore_error_locations: _ErrorLocationsMapping = (
            cls._get_single_error_locations(
                _IgnoreCommentType.TYPE_IGNORE,
                line,
            )
        )
        if single_type_ignore_error_locations:
            return single_type_ignore_error_locations

        single_noqa_error_locations: _ErrorLocationsMapping = cls._get_single_error_locations(
            _IgnoreCommentType.NOQA,
            line,
        )
        if single_noqa_error_locations:
            return single_noqa_error_locations

        return {}

    @override
    def run_check(
        self, tree: ast.Module, file_tokens: Sequence[TokenInfo], lines: Sequence[str]
    ) -> None:
        self.problems = ProblemsContainer(
            self.problems
            | {
                (file_token.start[0], file_token.start[1] + match_location): {
                    "ignore_comment_type": ignore_comment_type,
                    "multiple_commas": multiple_commas,
                }
                for file_token in file_tokens
                for match_location, (
                    ignore_comment_type,
                    multiple_commas,
                ) in self._get_all_error_locations(
                    file_token.string.rstrip(),
                ).items()
                if file_token.type == tokenize.COMMENT
            },
        )
