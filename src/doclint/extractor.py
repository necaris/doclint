import os
from pathlib import Path
from collections.abc import Generator
from typing import NamedTuple, cast

import tree_sitter
import tree_sitter_python

# Set up a constant for the Python language instance exposed by Tree-Sitter
# Creates a `PY_LANGUAGE` module-level variable
PY_LANGUAGE = tree_sitter.Language(tree_sitter_python.language())
PY_PARSER = tree_sitter.Parser(PY_LANGUAGE)

"""Construct a query from our custom file."""
PY_QUERY = tree_sitter.Query(
    PY_LANGUAGE,
    (Path(__file__).parent.parent / "queries" / "python.scm").read_text(),
)


class DocumentedExpression(NamedTuple):
    doc: bytes
    expression: bytes
    context: bytes | None = None


def definitions_from_file(
    path: os.PathLike[str],
) -> Generator[DocumentedExpression, None, None]:
    with open(path, "rb") as f:
        tree = PY_PARSER.parse(f.read())
    for _, mtch in PY_QUERY.matches(tree.root_node):
        doc = b"\n".join(cast(bytes, n.text) for n in mtch["doc"])
        definition = cast(bytes, mtch["definition"][0].text)
        yield DocumentedExpression(doc, definition)
