from pfmsoft.snippets.indexed_string.model import IndexedString
from pfmsoft.snippets.state_parser.abc import ParseContextABC, ParserABC
from pfmsoft.snippets.state_parser.model import (
    ParsedIndexedString,
    ParseResult,
)


class Tokenize(ParserABC):
    def __init__(self, state: str) -> None:
        super().__init__(state)

    def parse(self, ctx: ParseContextABC, input: IndexedString) -> ParseResult:
        """
        only fails on whitespace
        """
        tokens = {"tokens": input.txt.split()}
        if not tokens["tokens"]:
            self.parse_fail(
                msg="No tokens found, is this whitespace only?", input=input
            )
        parsed = ParsedIndexedString(id=self.state, indexed_string=input, data=tokens)
        result = ParseResult(current_state=self.state, parsed_indexed_string=parsed)
        return result


class SkipWhiteSpace(ParserABC):
    def __init__(self, state: str = "whitespace") -> None:
        super().__init__(state)

    def parse(self, ctx: ParseContextABC, input: IndexedString) -> ParseResult:
        """
        This parser fails if the input txt is not all whitespace.

        The parse state is not advanced, the state passed back is the state
        from the parse context.
        """
        if input.txt.isspace():
            parsed = ParsedIndexedString(id=self.state, indexed_string=input, data={})
            result = ParseResult(
                current_state=ctx.current_state, parsed_indexed_string=parsed
            )
            return result
        elif not input.txt:
            parsed = ParsedIndexedString(id=self.state, indexed_string=input, data={})
            result = ParseResult(
                current_state=ctx.current_state, parsed_indexed_string=parsed
            )
            return result
        self.parse_fail(msg="This is not all whitespace", input=input)
        return result


class OnlyNumbers(ParserABC):
    def __init__(self, state: str = "numbers") -> None:
        super().__init__(state)

    def parse(self, ctx: ParseContextABC, input: IndexedString) -> ParseResult:
        tokens = input.txt.split()
        if not tokens:
            self.parse_fail(msg="This is all whitespace.", input=input)
        for item in tokens:
            if not item.isnumeric():
                self.parse_fail(msg="This is not all numbers.", input=input)
        parsed = ParsedIndexedString(
            id=self.state, indexed_string=input, data={"numbers": tokens}
        )
        result = ParseResult(current_state=self.state, parsed_indexed_string=parsed)
        return result


class OnlyAlphas(ParserABC):
    def __init__(self, state: str = "alphas") -> None:
        super().__init__(state)

    def parse(self, ctx: ParseContextABC, input: IndexedString) -> ParseResult:
        tokens = input.txt.split()
        if not tokens:
            self.parse_fail(msg="This is all whitespace.", input=input)
        for item in tokens:
            if not item.isalpha():
                self.parse_fail(msg="This is not all alphas.", input=input)
        parsed = ParsedIndexedString(
            id=self.state, indexed_string=input, data={"alphas": tokens}
        )
        result = ParseResult(current_state=self.state, parsed_indexed_string=parsed)
        return result


class KeyValue(ParserABC):
    def __init__(self, state: str) -> None:
        super().__init__(state)

    def parse(self, ctx: ParseContextABC, input: IndexedString) -> ParseResult:
        tokens = input.txt.split()
        key = ""
        data: list[dict[str, str]] = []
        for item in tokens:
            if key:
                data.append({"key": key, "value": item})
                key = ""
            if item.endswith(":"):
                key = item
        if not data:
            self.parse_fail(msg="No key value pairs found.", input=input)

        parsed = ParsedIndexedString(
            id=self.state, indexed_string=input, data={"keyvalues": data}
        )
        result = ParseResult(current_state=self.state, parsed_indexed_string=parsed)
        return result


class NumberOfTokens(ParserABC):
    def __init__(self, state: str, token_count: int) -> None:
        super().__init__(state)
        self.token_count = token_count

    def parse(self, ctx: ParseContextABC, input: IndexedString) -> ParseResult:
        tokens = input.txt.split()

        if not len(tokens) == self.token_count:
            self.parse_fail(msg="Number of tokens does not match.", input=input)

        parsed = ParsedIndexedString(
            id=self.state, indexed_string=input, data={"tokens": tokens}
        )
        result = ParseResult(current_state=self.state, parsed_indexed_string=parsed)
        return result
