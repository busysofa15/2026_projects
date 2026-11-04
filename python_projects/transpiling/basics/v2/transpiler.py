import ast
import traceback
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
        elif isinstance(node.op,ast.Mod):
            op_str = "%"
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
        condition = self.visit(node.test)
        body_code = "".join([self.visit(stmt) for stmt in node.body])
        # 3. Stitch it into proper Rust syntax with curly braces
        rust_code =  f"    if {condition} {{\n{body_code}    }}\n"
        if node.orelse:
        # Check if the orelse is an 'elif' (i.e., a single If statement)
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                # Recursively call visit for the elif branch!
                elif_code = self.visit(node.orelse[0])
                rust_code += f" else {elif_code.strip()}"
            else:
                # Regular 'else' block
                else_body = "".join([self.visit(stmt) for stmt in node.orelse])
                rust_code += f" else {{\n{else_body}    }}"
            
        return rust_code + "\n"
    def visit_Name(self, node):
        return node.id
    def visit_For(self, node):
        if isinstance(node.target, ast.Name):
            target_name = node.target.id
        else:
            raise NotImplementedError("Only simple variable names are supported in for loops.")

        if (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Name)
            and node.iter.func.id == "range"
        ):
            args = node.iter.args
            if len(args) == 1:
                stop = args[0].value
                iter_expr = f"0..{stop}"
            elif len(args) == 2:
                start = args[0].value
                stop = args[1].value
                iter_expr = f"{start}..{stop}"
            else:
                raise NotImplementedError("3-argument range() not supported here.")
        else:
            raise NotImplementedError("Only range() iterables are supported.")

        body_code = "".join([self.visit(stmt) for stmt in node.body])
        return f"    for {target_name} in {iter_expr} {{\n{body_code}    }}\n"
    def visit_While(self, node):
        try:
            condition = self.visit(node.test)
            body_code = "".join([self.visit(stmt) for stmt in node.body])
            rust_code =  f"    while {condition} {{\n{body_code}    }}\n"
            return rust_code
        except Exception as e:
            print(f"only simple comparison based while loops are available {e}")   
    def visit_FunctionDef(self, node):
        func_name = node.name
        params = [f"{arg.arg}: f64" for arg in node.args.args]
        params_code = ", ".join(params)
        has_return = any(isinstance(stmt, ast.Return) for stmt in node.body)
        return_type = " -> f64" if has_return else ""
        body_parts = []
        for stmt in node.body:
            res = self.visit(stmt)
            if res is None:
                raise TypeError(f"Bro, your statement '{ast.dump(stmt)}' returned None! Fix its visitor method immediately.")
            body_parts.append(res)
        body_code = "".join(body_parts)
        return f"fn {func_name}({params_code}){return_type} {{\n{body_code}}}\n"
    def visit_Return(self, node):
        if node.value is not None:
            val_code = self.visit(node.value)
            return f"    return {val_code};\n"
        else:
            return f"    return;\n"
    def visit_Expr(self, node):
        val = self.visit(node.value)
        return f"    {val};\n"
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        else:
            raise NotImplementedError("Only direct function calls are supported.")
        args_code = ", ".join([self.visit(arg) for arg in node.args])
        return f"{func_name}({args_code})"
    #def visit_MatchClass(self, node):
        
    def visit_ClassDef(self, node):
        class_name = node.name
        fields = set()
        methods_code = ""

        for body_item in node.body:
            # 1. Extract fields from __init__ assignments (e.g., self.volume = ...)
            if isinstance(body_item, ast.FunctionDef) and body_item.name == "__init__":
                for stmt in body_item.body:
                    if isinstance(stmt, ast.Assign) and isinstance(stmt.targets[0], ast.Attribute):
                        target_attr = stmt.targets[0]
                        if isinstance(target_attr.value, ast.Name) and target_attr.value.id == "self":
                            fields.add(target_attr.attr)
            
            # 2. Transpile other methods into the impl block
            elif isinstance(body_item, ast.FunctionDef):
                # Temporarily alter function translation for methods
                method_name = body_item.name
                params = []
                for arg in body_item.args.args:
                    if arg.arg == "self":
                        params.append("&mut self")
                    else:
                        params.append(f"{arg.arg}: f64")
                
                params_code = ", ".join(params)
                body_parts = []
                for stmt in body_item.body:
                    body_parts.append(self.visit(stmt))
                body_code = "".join(body_parts)
                
                methods_code += f"    pub fn {method_name}({params_code}) {{\n{body_code    }}}\n\n"

        # Build Rust Struct fields
        fields_code = "\n".join([f"    pub {f}: f64," for f in fields])
        rust_struct = f"pub struct {class_name} {{\n{fields_code}\n}}\n\n"
        rust_impl = f"impl {class_name} {{\n{methods_code}}}\n"

        return rust_struct + rust_impl
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
        traceback.print_exc()

if __name__ == "__main__":
    main()