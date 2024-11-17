from pathlib import Path
from typing import Sequence
import logging

from pfmsoft.snippets.indexed_string.index_strings import index_strings
from pfmsoft.snippets.state_parser import parsers
from pfmsoft.snippets.state_parser.abc import ParserABC
from pfmsoft.snippets.state_parser.model import parse_result_serializer
from pfmsoft.snippets.state_parser.result_handler import (
    SaveResultsToFile,
)
from pfmsoft.snippets.state_parser import (
    StateParser,
    ParseContext,
    ParseScheme,
)


logger = logging.getLogger(__name__)
DATA = """

There are five tokens here
one line



two: lines foo three: values bar bat
123 22323 3455
three lines of text
"""
scheme: dict[str, Sequence[ParserABC]] = {
    "start": [
        parsers.SkipWhiteSpace(),
        parsers.NumberOfTokens(state="three_tokens", token_count=3),
        parsers.NumberOfTokens(state="five_tokens", token_count=5),
    ],
    "three_tokens": [],
    "five_tokens": [
        parsers.SkipWhiteSpace(),
        parsers.NumberOfTokens(state="two_tokens", token_count=2),
    ],
    "two_tokens": [parsers.SkipWhiteSpace(), parsers.KeyValue(state="key_value")],
    "key_value": [
        parsers.NumberOfTokens(state="five_tokens", token_count=5),
        parsers.OnlyNumbers(state="only_numbers"),
    ],
    "only_numbers": [parsers.OnlyAlphas(state="only_alphas")],
    "only_alphas": [parsers.SkipWhiteSpace()],
}


def test_parse(test_output_dir: Path):
    path_out = (
        test_output_dir / "state_parser" / "parse_one" / "test_parse" / "results.json"
    )
    result_handler = SaveResultsToFile(path_out=path_out, overwrite=False)
    parse_scheme = ParseScheme(beginning_state="start", parser_lookup=scheme)
    parser = StateParser(parse_scheme=parse_scheme, result_handler=result_handler)
    string_factory = index_strings(strings=DATA.split("\n"), index_start=1)
    ctx = ParseContext()
    parser.parse(ctx=ctx, data=string_factory)
    print(f"{len(result_handler.results)}")
    assert len(result_handler.results) == 11


def test_serializer_parse_results(test_output_dir: Path):
    path_out = (
        test_output_dir
        / "state_parser"
        / "parse_one"
        / "test_serializer"
        / "results.json"
    )
    result_handler = SaveResultsToFile(path_out=path_out, overwrite=False)
    parse_scheme = ParseScheme(beginning_state="start", parser_lookup=scheme)
    parser = StateParser(parse_scheme=parse_scheme, result_handler=result_handler)
    string_factory = index_strings(strings=DATA.split("\n"), index_start=1)
    ctx = ParseContext()
    parser.parse(ctx=ctx, data=string_factory)
    result = result_handler.results
    print(f"{len(result_handler.results)}")
    assert len(result_handler.results) == 11
    serializer = parse_result_serializer()
    loaded_results = serializer.load_from_json_list(path_in=path_out)
    path_out_loaded = (
        test_output_dir / "state_parser" / "parse_one" / "results_loaded.json"
    )
    serializer.save_iter_as_json(path_out=path_out_loaded, complex_obj=loaded_results)
    logger.info(f"       results:{result!r}")
    logger.info(f"loaded_results:{loaded_results!r}")
    assert loaded_results.__repr__() == result.__repr__()
