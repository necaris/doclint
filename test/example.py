"""
This is an example file with a module-level docstring. The docstring in this instance may span multiple lines, but this should not be relevant to tree-sitter's parsing.
"""

# This is an example of a documented module-level constant, whose documentation
# spans multiple lines.
MAGIC = object()

"""This is a module-level constant with a string as documentation."""
MAGIC_TOO = id(MAGIC) + id("too")


def add(a: int | float, b: int | float) -> int | float:
    """Adds numbers A and B."""
    return a + b


def do_complicated_thing():
    """Perform a complicated action."""

    # TODO: Perhaps we should also consider block comments above an expression
    # statement -- such as this one -- to be documenting the expression?
    foo = (bar() + baz()) ** quux()
    return foo / 2.364


class Magic:
    """Look at this class documentation string!"""

    # This is a comment documenting an attribute.
    attrib: int = 0

    def __init__(self, value: int | float):
        """
        A method's documentation string should be treated differently from a
        function's doc string, because evaluating its appropriateness should
        include the context of the whole surrounding class.
        """
        self.attrib = int(value)

    def __str__(self):
        # A block comment here should also be considered documentation for the
        # method, shouldn't it?
        return f"{self.__class__.__name__}({self.attrib})"
