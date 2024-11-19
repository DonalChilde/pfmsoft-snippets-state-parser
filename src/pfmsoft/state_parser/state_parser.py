import logging
from typing import Iterable, Sequence

from pfmsoft.indexed_string.model import IndexedString
from pfmsoft.state_parser.abc import (
    ParseContextABC,
    ParseSchemeABC,
    ResultHandlerABC,
)
from pfmsoft.state_parser.model import ParseResult
from pfmsoft.state_parser.parse_exception import (
    ParseAllFail,
    ParseException,
    ParseJobFail,
    SingleParserFail,
)
from pfmsoft.state_parser.parsers import ParserABC


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ParseContext(ParseContextABC):
    def __init__(self) -> None:
        super().__init__()


class ParseScheme(ParseSchemeABC):
    def __init__(
        self,
        parser_lookup: dict[str, Sequence[ParserABC]],
        beginning_state: str = "start",
    ) -> None:
        super().__init__(beginning_state)
        self.parser_lookup = parser_lookup

    def next_parsers(self, key: str) -> Sequence[ParserABC]:
        """Return a sequence of parsers based on a key.

        The key typically represents the current state of the parser, and the
        sequence of parsers are the expected matches for the next IndexedString.
        """
        parsers = self.parser_lookup.get(key, None)
        if parsers is None:
            raise ParseJobFail(f"Failed to find parsers using key: {key}")
        return parsers


class StateParser:
    def __init__(
        self, parse_scheme: ParseSchemeABC, result_handler: ResultHandlerABC
    ) -> None:
        self.result_handler = result_handler
        self.parse_scheme = parse_scheme

    def parse(self, ctx: ParseContextABC, data: Iterable[IndexedString]) -> None:
        """
        Parse an iterable of indexed strings.

        Parses an iterable of indexed strings, eg. (idx=linenumber, txt=line).
        Uses `state` to predict the possible matches for the next indexed string.
        The beginning state is defined by the parse scheme, and each successful parse
        will return a new state. This new state will be used to get a list of possible
        parsers from the parse scheme, which will be checked in sequence until a match
        is found. If no valid matches are found, a `ParseException` will be raised,
        signaling a failure of the parse job. In other words, a match must be found for
        each `IndexedString`.

        Args:
            ctx: A container for custom in formation that is passed to parsers.
            data: An iterable of indexed strings to be parsed.

        Raises:
            error: Signals a failure of the overall parse job.
        """
        ctx.current_state = self.parse_scheme.beginning_state
        with self.result_handler as handler:
            for result in self._parse_indexed_strings(ctx=ctx, data=data):
                handler.handle_result(ctx=ctx, parse_result=result)

    def _parse_indexed_strings(
        self, ctx: ParseContextABC, data: Iterable[IndexedString]
    ) -> Iterable[ParseResult]:
        current_state = self.parse_scheme.beginning_state
        made_an_attempt: bool = False
        for indexed_string in data:
            made_an_attempt = True
            try:
                parse_result = self._parse_indexed_string(
                    indexed_string=indexed_string,
                    parsers=self.parse_scheme.next_parsers(key=current_state),
                    ctx=ctx,
                )
                current_state = parse_result.current_state
                yield parse_result
            except ParseAllFail as error:
                # All the provided parsers failed to match.
                logger.error("%s", error)
                raise error
            except ParseJobFail as error:
                # This is started from individual parser
                raise error
            except ParseException as error:
                # unexpected exception
                logger.error("%s", error)
                raise error
        if not made_an_attempt:
            failed_attempt = ParseJobFail(
                "No IndexedStrings provided to this parse attempt."
            )
            logger.error("%s", failed_attempt)
            raise failed_attempt

    def _parse_indexed_string(
        self,
        indexed_string: IndexedString,
        parsers: Sequence[ParserABC],
        ctx: ParseContextABC,
    ) -> ParseResult:
        """
        Parse an indexed string based on a list of possible parsers.

        The failure of an individual parser should raise a `ParseException`. This does not
        represent a failure of the parse job as a whole, unless none of the parsers
        successfully match.

        Args:
            indexed_string: An indexed string to parse.
            parsers: A sequence of parsers to try.
            ctx: A store for arbitrary information needed to parse.

        Raises:
            SingleParserFail: Signals the failure of a parser.
            ParseJobFail: Signals the failure of the parse job as a whole.
            ParseAllFail: Signals the failure of all parsers.

        Returns:
            The result of a successful parse.
        """
        for parser in parsers:
            try:
                parse_result = parser.parse(input=indexed_string, ctx=ctx)
                ctx.current_state = parse_result.current_state
                return parse_result
            except SingleParserFail as error:
                logger.debug(
                    "\n\tFAILED %r->%r\n\t%r\n\tCurrent State:%r",
                    error.parser_name,
                    error.indexed_string,
                    error,
                    ctx.current_state,
                )
            except ParseJobFail as error:
                logger.error(
                    "Parse Job failed %s Current State:%r", error, ctx.current_state
                )
                raise error
        raise ParseAllFail(
            f"No parser found for \n\tindexed_string={indexed_string!r}"
            f"\n\tTried {parsers!r}\n\tCurrent State:{ctx.current_state}",
            parser_names=[x.__class__.__name__ for x in parsers],
            indexed_string=indexed_string,
        )
