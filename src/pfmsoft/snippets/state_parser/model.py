from dataclasses import dataclass, field
from typing import Any, TypedDict

from pfmsoft.snippets.indexed_string.model import IndexedString, IndexedStringTD


class ParsedIndexedStringTD(TypedDict):
    id: str
    indexed_string: IndexedStringTD
    data: dict[str, Any]


class ParseResultTD(TypedDict):
    current_state: str
    parsed_indexed_string: ParsedIndexedStringTD


@dataclass
class ParsedIndexedString:
    id: str
    indexed_string: IndexedString
    data: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_simple(simple_obj: ParsedIndexedStringTD) -> "ParsedIndexedString":
        result = ParsedIndexedString(
            id=simple_obj["id"],
            indexed_string=IndexedString(**simple_obj["indexed_string"]),
            data=simple_obj["data"],
        )
        return result


@dataclass
class ParseResult:
    current_state: str
    parsed_indexed_string: ParsedIndexedString

    @staticmethod
    def from_simple(simple_obj: ParseResultTD) -> "ParseResult":
        result = ParseResult(
            current_state=simple_obj["current_state"],
            parsed_indexed_string=ParsedIndexedString.from_simple(
                simple_obj["parsed_indexed_string"]
            ),
        )
        return result
