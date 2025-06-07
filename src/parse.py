from parsimonious.nodes import NodeVisitor
from parsimonious.nodes import Node
from parsimonious.grammar import Grammar
from pathlib import Path
from AST import *
import sys


class MatrixVisitor(NodeVisitor):
    """Visitor for the parse tree"""

    pass  # TODO (we have ~159 lines)

    def visit_program(self, node, visited_children):
        # (statement / emptyline)*
        return Block(list([v[0] for v in visited_children if v[0] is not None]))

    def visit_statement(self, node, visited_children):
        # (function / return_stmt) semicolon
        return visited_children[0][0]
    
    def visit_function(self, node, visited_children):
        # name leftparam param_list? rightparam
        name = visited_children[0]
        args = visited_children[2][0]
        return FunctionCall(name, args)
    
    def visit_param_list(self, node, visited_children):
        # (expr comma)* expr
        if len(visited_children[0]) == 0:
            return {visited_children[1][0]: visited_children[1][1]}
        exprs = []
        for [expr, comma] in visited_children[0]:
            exprs.append(expr)
        
        exprs.append(visited_children[1])
        exprs_dict = {}
        for name, data in exprs:
            exprs_dict[name] = data
        return exprs_dict
    
    def visit_expr(self, node, visited_children):
        # name equal (name / literal / string)
        return (visited_children[0], visited_children[2][0])

    def visit_show_stmt(self, node, visited_children):
        # show name
        return Show(visited_children[1])
    
    def visit_stat_stmt(self, node, visited_children):
        # stat name
        return Stat(visited_children[1])
    
    def visit_select_stmt(self, node, visited_children):
        # select leftparam (literal / name) rightparam leftbrace (function semicolon)* rightbrace
        _, _, literals, _, _, funcs, func, _ = visited_children
        if len(literals) > 0:
            num = literals[0]
        else:
            num = 0
        exprs = []
        if len(funcs) > 0:
            for f, comma in funcs:
                exprs.append(f)
        exprs.append(func)
        return Select(num=num, exprs=exprs)

    def visit_name(self, node, visited_children):
        # ~r"[a-zA-Z][-\w]*"
        return node.children[0].text

    def visit_literal(self, node, visited_children):
        # ~r"[0-9]+" ws
        value = int(node.text)
        return value
    
    def visit_string(self, node, visited_children):
        # ~r'"[^"]*"' ws
        s = node.children[0].text
        return s[1:-1]
    
    def visit_comment(self, node, visited_children):
        return None

    def generic_visit(self, node, visited_children):
        """The generic visit method. Returns the node if it has no children,
        otherwise it returns the children.
        Feel free to modify this as you like.
        """
        return visited_children


def parse(file_name: str):
    grammar = Grammar(Path(f"{src_path}/grammar.peg").read_text())
    tree = grammar.parse(Path(file_name).read_text())

    # print("parsing", file_name)
    visitor = MatrixVisitor()
    ast = visitor.visit(tree)
    return ast


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: parse.py [file]")
        exit(1)

    grammar = Grammar(Path("grammar.peg").read_text())
    tree = grammar.parse(Path(sys.argv[1]).read_text())
    # print(tree)
    visitor = MatrixVisitor()
    ast = visitor.visit(tree)
    print(ast)
    