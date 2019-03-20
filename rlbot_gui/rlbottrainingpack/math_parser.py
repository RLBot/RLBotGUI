from ast import NodeVisitor, parse, Module, AST, Num, Call, Name, BinOp, List, NameConstant
from random import Random

from rlbot.utils.game_state_util import Vector3, Rotator
from rlbottraining.rng import SeededRandomNumberGenerator


class Parser(NodeVisitor):
    def __init__(self, rng: SeededRandomNumberGenerator):
        self.funcs = {
            x: getattr(rng, x)
            for x in dir(rng)
            if not (x.startswith("_") or x == "VERSION")
        }
        self.funcs.update({
            "Vector3": Vector3,
            "Rotator": Rotator
        })
        self.result = None
        super().__init__()

    def debug(self, node: AST):
        print(type(node))
        print({
            attrname: getattr(node, attrname)
            for attrname in dir(node)
            if not attrname.startswith("__")
        })

    def visit_Module(self, node: Module):
        if len(node.body) == 1:
            return self.visit(node.body[0])

        for child in node.body:
            self.visit(child)
        return self.result

    def visit_Call(self, node: Call):
        args = list(map(self.visit, node.args))
        return self.funcs[self.visit(node.func)](*args)

    def visit_Name(self, node: Name):
        return node.id

    def visit_NameConstant(self, node: NameConstant):
        return node.value

    def visit_Num(self, node: Num):
        return node.n

    def visit_List(self, node: List):
        return list(map(self.visit, node.elts))

    def visit_BinOp(self, node: BinOp):
        cls = type(node.op).__name__
        if cls == "Add":
            return self.visit(node.left) + self.visit(node.right)
        elif cls == "Sub":
            return self.visit(node.left) - self.visit(node.right)
        elif cls == "Div":
            return self.visit(node.left) / self.visit(node.right)
        elif cls == "Mult":
            return self.visit(node.left) * self.visit(node.right)
        else:
            raise Exception(f"BinOp '{cls}' not found!")

    def visit_UnaryOp(self, node: 'UnaryOp'):
        arg = self.visit(node.operand)
        cls = type(node.op).__name__
        if cls == "USub":
            return -arg
        raise Exception(f"UnaryOp '{cls}' not found!")

    def visit_Expr(self, node: 'Expr'):
        return self.visit(node.value)

    def generic_visit(self, node):
        self.debug(node)
        super().generic_visit(node)


def parse_statement(rng: SeededRandomNumberGenerator, string: str):
    return Parser(rng).visit(parse(string))


def parse_item(rng: SeededRandomNumberGenerator, item):
    if isinstance(item, list):
        return list(map(lambda x: parse_item(rng, x), item))
    if isinstance(item, str):
        try:
            res = parse_statement(rng, item)
            return res
        except Exception as exc:
            raise Exception(f"Unable to parse formula: '{item}'. "
                            "If you made this exercise, please check the code.") from exc
    return item


if __name__ == "__main__":
    def test_statement(statement, result):
        rng = SeededRandomNumberGenerator(Random(10))
        res = parse_statement(rng, statement)
        if isinstance(res, Vector3):
            assert (res.x == result.x and res.y == result.y and res.z == result.z)
        else:
            assert res == result, f"'{statement}' Failed: {res} != {result}"

    test_statement("-randint(10, 20)", -19)
    test_statement("10 - randint(5, 13)", 5)
    test_statement("10 + randint(6, 13)", 16)
    test_statement("10 * randint(5, 13)", 50)
    test_statement("6 / randint(1, 6)", 1.2)
    test_statement("choice([10, 5, 7])", 7)
    test_statement("choice([True, False, 0.1])", 0.1)
    test_statement("Vector3(10, 5, betavariate(0.1, 1))", Vector3(10, 5, 0.009623271562333275))

