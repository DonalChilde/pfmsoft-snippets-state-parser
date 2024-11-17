from abc import ABC
from types import TracebackType
from typing import Any, Optional, Self, Sequence, Type

from pfmsoft.snippets.indexed_string.model import IndexedString

from pfmsoft.snippets.state_parser.model import ParseResult
from pfmsoft.snippets.state_parser.parse_exception import SingleParserFail


class ParseContextABC(ABC):
    def __init__(self) -> None:
        self.current_state = ""
        self.obj: dict[str, Any] = {}


class ParserABC(ABC):
    def __init__(self, state: str) -> None:
        super().__init__()
        self.state = state

    def parse(self, ctx: ParseContextABC, input: IndexedString) -> ParseResult:
        raise NotImplementedError

    def parse_fail(self, msg: str, input: IndexedString):
        raise SingleParserFail(
            msg=msg,
            parser_name=self.__class__.__name__,
            indexed_string=input,
        )


class ResultHandlerABC(ABC):
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
        raise NotImplementedError


class ParseSchemeABC(ABC):
    def __init__(
        self,
        beginning_state: str = "start",
    ) -> None:
        self.beginning_state = beginning_state

    def next_parsers(self, key: str) -> Sequence[ParserABC]:
        """Return a sequence of parsers based on a key.

        The key typically represents the current state of the parser, and the
        sequence of parsers are the expected matches for the next IndexedString.
        """
        raise NotImplementedError
