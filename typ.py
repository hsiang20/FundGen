from AST import *
from dataclasses import dataclass


@dataclass
class TypeError(Exception):
    msg: str

    def __init__(self, _msg: str):
        self.msg = _msg


class Type:
    pass


class Dim:
    pass


@dataclass
class ConcreteDim(Dim):
    """Concrete dimension (e.g. a number) for a matrix"""

    value: int

    def __eq__(self, other):
        return type(self) is type(other) and self.value == other.value


@dataclass
class MatrixType(Type):
    """Type for a matrix"""

    shape: (Dim, Dim)

    def __eq__(self, other):
        return type(self) is type(other) and self.shape == other.shape


@dataclass
class FunctionType(Type):
    """Type of a function"""

    params: [Type]
    ret: Type

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.params == other.params
            and self.ret == other.ret
        )


def type_expr(expr: Expr, bindings: ScopedDict, declarations: ScopedDict):
    """Types an expression. bindings is a dictionary mapping variable names
    to their type. declarations is a dictionary mapping function names
    to their types.

    Returns the type of the expression.
    Raises a TypeError if the types are incorrect.
    """

    # pass  # TODO (we have ~89 lines)
    match expr:
        case MatrixType(shape = shape):
            # return shape
            if shape == None:
                return None
            if type(shape[0]) == str:
                shape_0 = shape[0]
            else:
                shape_0 = shape[0].value
            if type(shape[1]) == str:
                shape_1 = shape[1]
            else:
                shape_1 = shape[1].value
            return (shape_0, shape_1)
        case Literal(value = value):
            return (1, 1)
        case Variable(name = name):
            try:
                return type_expr(bindings[name], bindings, declarations)
            except:
                raise ValueError(f"Undefined variable {name}")
        case MatrixLiteral(values = values):
            # print(values)
            matrix = np.array(values)
            return matrix.shape
        case BinaryExpr(left = left, right = right, op = op):
            match op:
                case BinOp.PLUS:
                    if (type_expr(left, bindings, declarations) != type_expr(right, bindings, declarations)):
                        raise TypeError(f"Type mismatch: ({left} + {right}")
                    return type_expr(left, bindings, declarations)
                case BinOp.MINUS:
                    if (type_expr(left, bindings, declarations) != type_expr(right, bindings, declarations)):
                        raise TypeError(f"Type mismatch: ({left} - {right}")
                    return type_expr(left, bindings, declarations)
                case BinOp.MUL:
                    left_type = type_expr(left, bindings, declarations)
                    right_type = type_expr(right, bindings, declarations)
                    # print(f"TYPE_EXPR: left = {left}, left_type = {left_type}")
                    # print(f"TYPE_EXPR: right = {right}, right_type = {right_type}")
                    if (left_type[1] != right_type[0]):
                        raise TypeError(f"Type mismatch: ({left}(with type {left_type}) * {right}(with type {right_type})")
                    return (left_type[0], right_type[1])
                case _:
                    raise ValueError(f"Unknown Op {op}")
        case FunctionCall(name=name, args=args):
            # print(f"TYPE_EXPR: FUNCTIONCALL args = {args}")
            arg_types = [type_expr(arg, bindings, declarations) for arg in args]
            if name == "print":
                # print(arg_values)
                return []
            if declarations.get(name) is not None:
                func = declarations.get(name)
                body = func.body
                params = func.params
                func_param_ty = [type_expr(param, bindings, declarations) for param in func.ty.params]
                func_ret_ty = type_expr(func.ty.ret, bindings, declarations)
                bindings.push_scope()
                # print("TYPE_EXPR: FunctionCall, params = ", params, "func_param_ty = ", func_param_ty, "arg_types = ", arg_types)
                assert len(params) == len(args), f"{name} has {len(params)} params but got {len(args)} args in {expr}"
                dict_tmp = {}
                for i in range(len(params)):
                    if (func_param_ty[i] == None):
                        continue
                    for j in range(2):
                        if type(func_param_ty[i][j]) == str:
                            if func_param_ty[i][j] not in dict_tmp:
                                dict_tmp[func_param_ty[i][j]] = arg_types[i][j]
                                # print(f"bindings[{func_param_ty[i][j]}] = {arg_types[i][j]}")
                            else:
                                if dict_tmp[func_param_ty[i][j]] != arg_types[i][j]:
                                    # print(f"bindings[{func_param_ty[i][j]}] = {bindings[func_param_ty[i][j]]} != {arg_types[i][j]}")
                                    raise TypeError(f"Function args type mismatch!")

                for i in range(len(args)):
                    # print(f"TYPE_EXPR: FUNCTIONCALL func_param_ty[i] = {func_param_ty[i]}")
                    if (func_param_ty[i] == None):
                        continue
                    if (arg_types[i][0] != func_param_ty[i][0] and type(func_param_ty[i][0]) != str):
                        raise TypeError(f"Wrong param type: should get {func_param_ty[i]} but got {arg_types[i]}")
                    if (arg_types[i][1] != func_param_ty[i][1] and type(func_param_ty[i][1]) != str):
                        raise TypeError(f"Wrong param type: should get {func_param_ty[i]} but got {arg_types[i]}")
                # arg_values = [interpret_expr(arg, bindings, declarations) for arg in args]
                for i in range(len(args)):
                    let_stmt = Let(params[i], arg_types[i])
                    type_stmt(let_stmt, bindings, declarations)
                return_value = type_block(body, bindings, declarations)
                # return_value = (type_expr(return_value[0], bindings, declarations), type_expr(return_value[1], bindings, declarations))
                if return_value == None:
                    return_value = (0, 0)
                if func_ret_ty != None:
                    if (return_value[0] != func_ret_ty[0] and type(func_ret_ty[0]) != str):
                        raise TypeError(f"Wrong return type: should get shape {func_ret_ty} but got {return_value}")
                    if (return_value[1] != func_ret_ty[1] and type(func_ret_ty[1]) != str):
                        raise TypeError(f"Wrong return type: should get shape {func_ret_ty} but got {return_value}")
                bindings.pop_scope()

                return return_value

                # print(f"TYPE_EXPR: return_value = {return_value}, func_ret_ty = {func_ret_ty}")
            else:
                raise ValueError(f"Undefined function {name}")
        case _:
            return expr


def type_stmt(stmt: Statement, bindings: ScopedDict, declarations: ScopedDict):
    """Type checks a statement. bindings is a dictionary mapping variable names
    to their type. declarations is a dictionary mapping function names
    to their types.

    Raises TypeError if the types are incorrect.
    """
    # pass  # TODO (we have ~32 lines)
    match stmt:
        case Let(name = name, value = value):
            bindings[name] = value
        case FunctionDec(name = name, params = params, body = body, ty = ty):
            if name == "print":
                # print(arg_values)
                raise ValueError("Redefining function print!")
            if declarations.get(name) is None:
                # print(f"TYPE_STMT: FunctionDec ty = {ty}")
                func_ret_ty = type_expr(ty.ret, bindings, declarations)
                # print(f"TYPE_STMT: FunctionDec func_ret_ty = {func_ret_ty}")
                if func_ret_ty == None:
                    declarations[name] = stmt
                    return
                for i in range(len(params)):
                    # print(ty.params[i].shape)
                    if (ty.params[i].shape == None):
                        declarations[name] = stmt
                        return
                bindings.push_scope()
                for i in range(len(params)):
                    let_stmt = Let(params[i], ty.params[i])
                    type_stmt(let_stmt, bindings, declarations)
                return_value = type_block(body, bindings, declarations)
                # return_value = (type_expr(return_value[0], bindings, declarations), type_expr(return_value[1], bindings, declarations))
                if return_value == None:
                    return_value = (0, 0)
                
                if (return_value != func_ret_ty):
                    raise TypeError(f"Wrong return type: should get shape {func_ret_ty} but got {return_value}")
                bindings.pop_scope()

                # print(f"TYPE_STMT: return_value = {return_value}, func_ret_ty = {func_ret_ty}")
            else:
                raise ValueError(f"Redefining function {name}!")
            declarations[name] = stmt
        case Return(expr = expr):
            return type_expr(expr, bindings, declarations)
        case FunctionCall(name = name, args = args):
            type_expr(stmt, bindings, declarations)


def type_block(block: Block, bindings: ScopedDict, declarations: ScopedDict):
    """Type checks a block. bindings is a dictionary mapping variable names
    to their type. declarations is a dictionary mapping function names
    to their types.

    Raises TypeError if the types are incorrect.
    """

    for statement in block.stmts:
        match statement:
            case Return(expr = expr):
                return type_expr(expr, bindings, declarations)
        type_stmt(statement, bindings, declarations)
