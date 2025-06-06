from enum import Enum
from utils import ScopedDict
from dataclasses import dataclass
from helpers import *
from op import *



class BinOp(Enum):
    """Enum representing each arithmetic operator"""

    PLUS = 1
    MINUS = 2
    MUL = 3
    DIV = 4


class Statement:
    """Statement base class"""

    pass


class Expr(Statement):
    """Expression base class"""

    pass


@dataclass
class Block:
    """A "block" of code, which consists of a list of statements.

    This is always the root node of the AST.
    """

    stmts: list[Statement]

    def __eq__(self, other):
        return type(self) is type(other) and self.stmts == other.stmts


@dataclass
class BinaryExpr(Expr):
    """A binary expression, consisting of a left operand,
    right operand, and operator
    """

    left: Expr
    right: Expr
    op: BinOp

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.left == other.left
            and self.right == other.right
            and self.op == other.op
        )


@dataclass
class Let(Statement):
    """A let statement"""

    name: str
    value: Expr

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.name == other.name
            and self.value == other.value
        )


@dataclass
class Literal(Expr):
    """An integer literal, e.g. 5"""

    value: int

    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value


@dataclass
class Variable(Expr):
    """A variable"""

    name: str

    def __eq__(self, other):
        return type(self) is type(other) and self.name == other.name

@dataclass
class MatrixLiteral(Expr):
    """A matrix literal, e.g. [[1, 2], [3, 4]]"""

    values: list[list[Expr]]

    def __eq__(self, other):
        return type(self) is type(other) and self.values == other.values


@dataclass
class FunctionCall(Expr):
    """A function call"""

    name: str
    args: list[Expr]

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.name == other.name
            and self.args == other.args
        )


@dataclass
class FunctionDec(Statement):
    """A function declaration"""

    name: str
    params: list[str]
    body: Block
    ty: "FunctionType"

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.name == other.name
            and self.params == other.params
            and self.body == other.body
        )


@dataclass
class Show(Statement):
    """A show statement"""

    expr: Expr

    def __eq__(self, other):
        return type(self) is type(other) and self.expr == other.expr
    
@dataclass
class Stat(Statement):
    """A stat statement"""

    expr: Expr

    def __eq__(self, other):
        return type(self) is type(other) and self.expr == other.expr

@dataclass
class Select(Statement):
    """A select statement"""
    """num == 0 means can select any number"""
    num: int
    exprs: list[FunctionCall]

    def __eq__(self, other):
        return type(self) is type(other) and self.expr == other.expr

now_config = 0
best_config = 0
best_stat = None

def interpret_expr(expr: Expr, bindings: ScopedDict, declarations: ScopedDict):
    global now_config
    global best_config
    global best_stat
    match expr:
        case FunctionCall(name=name, args=args):
            if name == "load":
                args_check(args, ["data"])
                assert("data" in args)
                data = load(args["data"])
                bindings[args["data"]] = data
                bindings["_tmp"] = data
                return
            if name == "tsmean":
                args_check(args, ["out", "in", "days"])
                data_in = find_data_in(args, bindings)
                out = tsmean(data_in, args["days"])
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out
            if name == "add":
                args_check(args, ["out", "in1", "in2"])
                data_in1 = find_data_in(args, bindings, name="in1")
                data_in2 = find_data_in(args, bindings, name="in2")
                out = add(data_in1, data_in2)
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out
            if name == "sub":
                args_check(args, ["out", "in1", "in2"])
                data_in1 = find_data_in(args, bindings, name="in1")
                data_in2 = find_data_in(args, bindings, name="in2")
                out = sub(data_in1, data_in2)
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out
            if name == "mul":
                args_check(args, ["out", "in1", "in2"])
                data_in1 = find_data_in(args, bindings, name="in1")
                data_in2 = find_data_in(args, bindings, name="in2")
                out = mul(data_in1, data_in2)
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out
            if name == "div":
                args_check(args, ["out", "in1", "in2"])
                data_in1 = find_data_in(args, bindings, name="in1")
                data_in2 = find_data_in(args, bindings, name="in2")
                out = div(data_in1, data_in2)
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out
            if name == "flip":
                args_check(args, ["out", "in"])
                data_in = find_data_in(args, bindings)
                out = flip(data_in)
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out
            if name == "normalize":
                args_check(args, ["out", "in"])
                data_in = find_data_in(args, bindings)
                out = normalize(data_in)
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out
            if name == "demean":
                args_check(args, ["out", "in"])
                data_in = find_data_in(args, bindings)
                out = demean(data_in)
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out
            if name == "rank":
                args_check(args, ["out", "in"])
                data_in = find_data_in(args, bindings)
                out = rank(data_in)
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out
            if name == "tsrank":
                args_check(args, ["out", "in", "days"])
                data_in = find_data_in(args, bindings)
                out = tsrank(data_in, args["days"])
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out
            if name == "tscorr":
                args_check(args, ["out", "in1", "in2", "days"])
                data_in1 = find_data_in(args, bindings, name="in1")
                data_in2 = find_data_in(args, bindings, name="in2")
                out = tscorr(data_in1, data_in2, args["days"])
                bindings[args["out"]] = out
                bindings["_tmp"] = out
                return out

            if name == "nanto0":
                assert("out" in args)
                assert("in" in args)
                nanto0()
                return

            arg_values = [interpret_expr(arg, bindings, declarations) for arg in args]
            if name == "print":
                print(*arg_values)
                return []
            if declarations.get(name) is not None:
                func = declarations.get(name)
                body = func.body
                params = func.params
                ty = func.ty
                bindings.push_scope()
                # print("in functionCall, params =", params)
                for i in range(len(args)):
                    let_stmt = Let(params[i], arg_values[i])
                    interpret_stmt(let_stmt, bindings, declarations)
                return_value = interpret_block(body, bindings, declarations)
                bindings.pop_scope()
                return return_value
            else:
                raise ValueError(f"Undefined function {name}")
        case Show(expr = expr):
            cumulative_return = draw_profit(bindings[expr])
        case Stat(expr = expr):
            sharpe, annual_returns_rate = show_stat(bindings[expr])
            # print(bindings[expr])
            if best_stat == None:
                best_config = now_config
                best_stat = {"Sharpe": sharpe, "Annual Returns Rate": annual_returns_rate}
                save_to_cache(bindings[expr], bindings[expr].index, "cache/portfolio.npz")
            else:
                if sharpe > best_stat["Sharpe"]:
                    best_config = now_config
                    best_stat = {"Sharpe": sharpe, "Annual Returns Rate": annual_returns_rate}
                    save_to_cache(bindings[expr], bindings[expr].index, "cache/portfolio.npz")


def interpret_stmt(stmt: Statement, bindings: ScopedDict, declarations: ScopedDict):
    match stmt:
        case Show(expr = expr):
            return interpret_expr(stmt, bindings, declarations)
        case Stat(expr = expr):
            return interpret_expr(stmt, bindings, declarations)
        case FunctionCall(name = name, args = args):
            interpret_expr(stmt, bindings, declarations)
            

def interpret_block(block: Block, bindings: ScopedDict, declarations: ScopedDict):
    global now_config
    global best_config
    global best_stat
    num_of_iteration = 1
    all_block = [[]]
    for stmt in block.stmts:
        if type(stmt).__name__ == 'Select':
            if (stmt.num != 0):
                all_block, num_of_iteration = repeat_block_n(all_block, num_of_iteration, stmt)
            else: 
                # stmt.num == 0, can choose any subset of functions
                all_block, num_of_iteration = repeat_block_all(all_block, num_of_iteration, stmt)
        else:
            for i in range(len(all_block)):
                all_block[i].append(stmt)

    print(f"Cases to run:{num_of_iteration}")

    for i in range(num_of_iteration):
        for stmt in all_block[i]:
            interpret_stmt(stmt, bindings, declarations)
        now_config += 1
    # print(f"Best Config:")
    # print_config(all_block[best_config])
    # print()
    # print(f"Best State:")
    print_stat(best_stat)
    print()
    # Draw and save image
    cached_data, cached_dates = load_from_cache("cache/portfolio.npz")
    portfolio = pd.DataFrame(cached_data, index=cached_dates)
    save_profit(portfolio)
    with open("portfolio/portfolio.txt", "w") as f:
        for s in all_block[best_config]:
            f.write(str(s))
            f.write("\n")
    return []
