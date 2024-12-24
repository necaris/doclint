import pathlib
from doclint.extractor import definitions_from_file


def test_queries_work():
    example_file = pathlib.Path(__file__).parent / "example.py"
    defs = list(definitions_from_file(example_file))
    assert defs is None
