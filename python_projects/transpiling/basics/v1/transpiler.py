import ast

class RustTranspiler(ast.NodeVisitor):
    def __init__(self):
        # Keep track of variables we've already declared
        self.declared_vars = set()

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            target = node.targets[0].id
        else:
            raise TypeError("Unsupported assignment target type")
            
        value_code = self.visit(node.value)
        if target not in self.declared_vars:
            self.declared_vars.add(target)
            # First time: declare it as mutable so we can update it later!
            return f"    let mut {target}: f64 = {value_code};\n"
        else:
            # Already exists: just reassign it directly without 'let mut'
            return f"    {target} = {value_code};\n"
    def visit_Name(self, node):
        return node.id

    def visit_Constant(self, node):
        return str(float(node.value))

    def visit_BinOp(self, node):
        left_code = self.visit(node.left)
        right_code = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            op_str = "+"
        elif isinstance(node.op, ast.Sub):
            op_str = "-"
        elif isinstance(node.op, ast.Mult):
            op_str = "*"
        elif isinstance(node.op, ast.Div):
            op_str = "/"
        else:
            raise NotImplementedError(f"Unsupported operator: {type(node.op)}")
        return f"({left_code} {op_str} {right_code})"
    def visit_Compare(self, node):
        left_code = self.visit(node.left)
        right_code = self.visit(node.comparators[0])  # grab the right side
        
        op = node.ops[0]
        if isinstance(op, ast.Gt):
            op_str = ">"
        elif isinstance(op, ast.Lt):
            op_str = "<"
        elif isinstance(op, ast.Eq):
            op_str = "=="
        elif isinstance(op, ast.NotEq):
            op_str = "!="
        elif isinstance(op, ast.GtE):
            op_str = ">="
        elif isinstance(op, ast.LtE):
            op_str = "<="
        else:
            raise NotImplementedError(f"Unsupported comparison operator: {type(op)}")
            
        return f"({left_code} {op_str} {right_code})"
    def visit_If(self, node):
        print(ast.dump(node.test))
        condition = self.visit(node.test)
        body_code = "".join([self.visit(stmt) for stmt in node.body])
        # 3. Stitch it into proper Rust syntax with curly braces
        return f"    if {condition} {{\n{body_code}    }}\n"
        

def main():
    try:
        with open("/home/busysofa/Documents/stupid lib/alpha/v1/transpiler prototyping and learning/input.py", "r") as f:
            tree = ast.parse(f.read())
        
        transpiler = RustTranspiler()
        rust_body = ""
        
        for node in tree.body:
                rust_body += transpiler.visit(node)
        rust_code = f"fn main() {{\n{rust_body}}}\n"
        
        with open("/home/busysofa/Documents/stupid lib/alpha/v1/transpiler prototyping and learning/src/main.rs", "w") as f:
            f.write(rust_code)
            
        print("[+] Success: input.py -> main.rs compiled cleanly.")
        
    except Exception as e:
        print(f"[-] CRITICAL EXCEPTION: {e}")

if __name__ == "__main__":
    main()