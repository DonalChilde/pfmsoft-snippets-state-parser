####################################################
#                                                  #
#  src/snippets/indexed_string/state_parser/parse_exception.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-02-05T05:59:31-07:00            #
# Last Modified: 2023-04-22T15:59:58.363420+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Sequence

from pfmsoft.snippets.indexed_string.model import IndexedString


class ParseException(Exception):
    """Use this exception to signal a failed parse."""


class SingleParserFail(ParseException):
    """Use this exception to signal single parser failed."""

    def __init__(
        self,
        msg: str,
        parser_name: str,
        indexed_string: IndexedString,
        *args: object,
    ) -> None:
        super().__init__(msg, *args)
        self.parser_name = parser_name
        self.indexed_string = indexed_string


class ParseJobFail(ParseException):
    """Use this exception to signal whole parse job failed."""

    def __init__(self, msg: str, *args: object) -> None:
        super().__init__(msg, *args)


class ParseAllFail(ParseJobFail):
    """Use this exception to signal all parsers failed, job failed."""

    def __init__(
        self,
        msg: str,
        parser_names: Sequence[str],
        indexed_string: IndexedString,
        *args: object,
    ) -> None:
        super().__init__(msg, *args)
        self.parsers = parser_names
        self.indexed_string = indexed_string


class ParseValidationError(ParseException):
    # TODO not sure of the place for this, validation more likely to take place
    #   outside parser.
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
