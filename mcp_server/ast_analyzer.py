"""
Module Phân tích Cây Cú pháp Trừu tượng (AST Analyzer) cho mã nguồn Python.
- Kiểm tra tính hợp lệ cú pháp mà không cần chạy mã
- Phát hiện cấu trúc vòng lặp (For, While)
- Phát hiện đệ quy (hàm gọi lại chính nó)
- Phát hiện biến tích lũy (Accumulator: +=, *=, .append())
- Nhận xét sư phạm tĩnh hỗ trợ AI Tutor
"""
import ast


class ASTInspector(ast.NodeVisitor):
    def __init__(self):
        self.for_count = 0
        self.while_count = 0
        self.has_return = False
        self.defined_functions = []
        self.accumulator_patterns = []
        self.function_calls = {}  # {func_name: [called_funcs]}
        self.current_function = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        func_info = {
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "lineno": node.lineno
        }
        self.defined_functions.append(func_info)
        
        prev_func = self.current_function
        self.current_function = node.name
        self.function_calls[node.name] = []
        
        self.generic_visit(node)
        self.current_function = prev_func

    def visit_For(self, node: ast.For):
        self.for_count += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        self.while_count += 1
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return):
        self.has_return = True
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        # Biến tích lũy dạng a += x hoặc a *= x
        target_name = node.target.id if isinstance(node.target, ast.Name) else "unknown"
        op_name = type(node.op).__name__
        self.accumulator_patterns.append(f"{target_name} ({op_name})")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        called_name = None
        if isinstance(node.func, ast.Name):
            called_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            called_name = node.func.attr
            if node.func.attr in ("append", "extend"):
                target = node.func.value.id if isinstance(node.func.value, ast.Name) else "list"
                self.accumulator_patterns.append(f"{target}.{node.func.attr}()")
                
        if self.current_function and called_name:
            self.function_calls[self.current_function].append(called_name)
            
        self.generic_visit(node)


def analyze_code_ast(code: str) -> dict:
    """
    Phân tích AST tĩnh mã nguồn Python.
    Trả về dict chi tiết đặc trưng cấu trúc cú pháp.
    """
    if not code or not code.strip():
        return {
            "valid": False,
            "syntax_error": "Mã nguồn trống.",
            "structural_summary": "Không có mã nguồn để phân tích."
        }

    try:
        tree = ast.parse(code)
    except SyntaxError as se:
        return {
            "valid": False,
            "syntax_error": {
                "message": se.msg,
                "lineno": se.lineno,
                "offset": se.offset,
                "text": se.text.strip() if se.text else ""
            },
            "structural_summary": f"Mã nguồn có lỗi cú pháp tại dòng {se.lineno}: {se.msg}"
        }

    inspector = ASTInspector()
    inspector.visit(tree)

    # Kiểm tra đệ quy: có hàm nào gọi chính nó trong thân hàm
    has_recursion = False
    recursive_functions = []
    for func_name, calls in inspector.function_calls.items():
        if func_name in calls:
            has_recursion = True
            recursive_functions.append(func_name)

    total_loops = inspector.for_count + inspector.while_count
    has_loops = total_loops > 0
    has_accumulator = len(inspector.accumulator_patterns) > 0

    # Tạo tóm tắt cấu trúc sư phạm bằng tiếng Việt
    observations = []
    if inspector.for_count > 0:
        observations.append(f"Sử dụng {inspector.for_count} vòng lặp for")
    if inspector.while_count > 0:
        observations.append(f"Sử dụng {inspector.while_count} vòng lặp while")
    if total_loops == 0:
        observations.append("Không sử dụng vòng lặp nào")

    if has_accumulator:
        patterns_str = ", ".join(list(set(inspector.accumulator_patterns))[:3])
        observations.append(f"Có biến tích lũy ({patterns_str})")
    else:
        observations.append("Không phát hiện biến tích lũy rõ ràng")

    if has_recursion:
        observations.append(f"Có cấu trúc đệ quy ở hàm: {', '.join(recursive_functions)}")

    if inspector.defined_functions:
        fn_names = [f["name"] for f in inspector.defined_functions]
        observations.append(f"Đã định nghĩa các hàm: {', '.join(fn_names)}")
    else:
        observations.append("Mã nguồn dạng script tuần tự (không định nghĩa hàm riêng)")

    line_count = len([line for line in code.splitlines() if line.strip() and not line.strip().startswith("#")])

    return {
        "valid": True,
        "syntax_error": None,
        "line_count": line_count,
        "has_loops": has_loops,
        "loop_details": {
            "for_count": inspector.for_count,
            "while_count": inspector.while_count,
            "total": total_loops
        },
        "has_recursion": has_recursion,
        "recursive_functions": recursive_functions,
        "has_accumulator": has_accumulator,
        "accumulator_patterns": list(set(inspector.accumulator_patterns)),
        "has_return": inspector.has_return,
        "defined_functions": inspector.defined_functions,
        "observations": observations,
        "structural_summary": "; ".join(observations) + f" (Tổng {line_count} dòng code thực tế)."
    }
