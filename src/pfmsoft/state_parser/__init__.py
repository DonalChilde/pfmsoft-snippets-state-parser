"""Top-level package for pfmsoft_state_parser."""

from pfmsoft.state_parser.state_parser import (
    StateParser,
    ParseContext,
    ParseScheme,
)
from pfmsoft.state_parser import parsers
from pfmsoft.state_parser import result_handler
from pfmsoft.state_parser import model

__author__ = "Chad Lowe"
__email__ = "pfmsoft.dev@gmail.com"
# The short X.Y.Z version.
__version__ = "0.0.0"
# The full version, including alpha/beta/rc tags.
__release__ = __version__

__all__ = [
    "StateParser",
    "ParseContext",
    "ParseScheme",
    "parsers",
    "result_handler",
    "model",
]
