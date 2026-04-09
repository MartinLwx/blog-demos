import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY_LANGUAGE = Language(tspython.language())

code = """def sum(x: int, y: int) -> int:
    return x + y


sum(1, 2)
"""

parser = Parser(PY_LANGUAGE)
tree = parser.parse(bytes(code, encoding="utf8"))

query = Query(
    PY_LANGUAGE,
    """(typed_parameter
         (identifier)@name
         type: (type (identifier)@val))""",
)
captures = QueryCursor(query).captures(tree.root_node)
for arg_name, arg_type in zip(captures["name"], captures["val"]):
    print(f"{str(arg_name.text)}: {str(arg_type.text)}")
