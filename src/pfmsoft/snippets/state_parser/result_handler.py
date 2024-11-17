from pathlib import Path
from types import TracebackType
from typing import Optional, Self, Type

from pfmsoft.snippets.state_parser.abc import ParseContextABC, ResultHandlerABC
from pfmsoft.snippets.state_parser.model import (
    ParseResult,
    parse_result_serializer,
    parsed_indexed_string_serializer,
)


class CollectResults(ResultHandlerABC):
    def __init__(self) -> None:
        self.results: list[ParseResult] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        pass

    def handle_result(
        self,
        ctx: ParseContextABC,
        parse_result: ParseResult,
    ) -> None:
        """
        Handle the result of a successful parse.

        Args:
            parse_result: The result of a successful parse.
        """
        self.results.append(parse_result)


class SaveParsedIndexedStringsToFile(ResultHandlerABC):
    """Do something with a parse result.

    Use as a context manager allows setup and trear down of assets if needed.
    """

    def __init__(
        self, path_out: Path, overwrite: bool = False, only_save_parsed: bool = False
    ) -> None:
        self.path_out = path_out
        self.results: list[ParseResult] = []
        self.overwrite = overwrite

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        serializer = parsed_indexed_string_serializer()
        serializer.save_iter_as_json(
            path_out=self.path_out,
            complex_obj=(x.parsed_indexed_string for x in self.results),
        )


class SaveResultsToFile(ResultHandlerABC):
    """Do something with a parse result.

    Use as a context manager allows setup and trear down of assets if needed.
    """

    def __init__(
        self, path_out: Path, overwrite: bool = False, only_save_parsed: bool = False
    ) -> None:
        self.path_out = path_out
        self.results: list[ParseResult] = []
        self.overwrite = overwrite
        self.only_save_parsed = only_save_parsed

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        serializer = parse_result_serializer()
        serializer.save_iter_as_json(path_out=self.path_out, complex_obj=self.results)

    def handle_result(
        self,
        ctx: ParseContextABC,
        parse_result: ParseResult,
    ) -> None:
        """
        Handle the result of a successful parse.

        Args:
            parse_result: The result of a successful parse.
        """
        self.results.append(parse_result)
