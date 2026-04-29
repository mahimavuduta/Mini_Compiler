"""
╔══════════════════════════════════════════════════════════════╗
║          MINI COMPILER — 6 PHASE IMPLEMENTATION              ║
║          Language: Python-like arithmetic + control flow     ║
╚══════════════════════════════════════════════════════════════╝

HOW TO RUN:
    python3 compiler.py

Phases:
  1. Lexical Analysis     → Tokens + Symbol Table
  2. Syntax Analysis      → Abstract Syntax Tree (AST)
  3. Semantic Analysis    → Type Checking + Scope Validation
  4. Intermediate Code    → Three-Address Code (TAC)
  5. Optimised ICG        → Constant Folding + Dead Code Elimination
  6. Code Generation      → Assembly-like Target Code
"""

import re

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SAMPLE INPUT PROGRAM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SOURCE_CODE = """
int a = 5
int b = 10
int c = a + b * 2
int d = c - a
int e = 4 + 6
if c > 15 :
    print ( c )
else :
    print ( d )
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DISPLAY HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

W = 65

def banner(phase_num, title):
    print("\n" + "═" * W)
    print(f"  ◆  PHASE {phase_num}:  {title}")
    print("═" * W)

def section_title(title):
    print(f"\n  ▸ {title}")
    print("  " + "─" * (W - 4))

def table(headers, rows, col_widths):
    top = "  ┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    mid = "  ├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    bot = "  └" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

    def row_str(cols):
        r = "  │"
        for col, w in zip(cols, col_widths):
            r += f" {str(col):<{w}} │"
        return r

    print(top)
    print(row_str(headers))
    print(mid)
    for r in rows:
        print(row_str(r))
    print(bot)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PHASE 1 — LEXICAL ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEYWORDS   = {'int', 'float', 'if', 'else', 'while', 'print', 'return'}
TOKEN_SPEC = [
    ('FLOAT',      r'\d+\.\d+'),
    ('INTEGER',    r'\d+'),
    ('COMPARATOR', r'>=|<=|==|!=|>|<'),
    ('OPERATOR',   r'[+\-*/=%]'),
    ('DELIMITER',  r'[():,;{}]'),
    ('COLON',      r':'),
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),
    ('NEWLINE',    r'\n'),
    ('SKIP',       r'[ \t]+'),
    ('COMMENT',    r'#.*'),
]

def phase1_lexer(source):
    banner(1, "LEXICAL ANALYSIS")
    tokens = []
    symbol_table = {}
    line_num = 1
    master = '|'.join(f'(?P<{n}>{p})' for n, p in TOKEN_SPEC)

    for m in re.finditer(master, source):
        kind  = m.lastgroup
        value = m.group()
        if kind in ('SKIP', 'COMMENT'):
            continue
        if kind == 'NEWLINE':
            line_num += 1
            continue
        if kind == 'IDENTIFIER' and value in KEYWORDS:
            kind = 'KEYWORD'
        if kind == 'DELIMITER' and value == ':':
            kind = 'COLON'
        tokens.append((kind, value, line_num))
        if kind == 'IDENTIFIER' and value not in symbol_table:
            symbol_table[value] = {'type': 'unknown', 'value': None, 'line': line_num}

    # ── Post-process: fill type & value from declaration pattern ─
    for i in range(len(tokens) - 2):
        if (tokens[i][0] == 'KEYWORD' and tokens[i][1] in ('int', 'float') and
            tokens[i+1][0] == 'IDENTIFIER' and
            tokens[i+2][0] == 'OPERATOR' and tokens[i+2][1] == '='):
            name  = tokens[i+1][1]
            dtype = tokens[i][1]
            if name in symbol_table:
                symbol_table[name]['type'] = dtype
                # If next token after = is a direct number, fill value
                if i+3 < len(tokens) and tokens[i+3][0] in ('INTEGER', 'FLOAT'):
                    val = int(tokens[i+3][1]) if tokens[i+3][0] == 'INTEGER' else float(tokens[i+3][1])
                    symbol_table[name]['value'] = val
                else:
                    symbol_table[name]['value'] = 'expression'

    # ── Token Table ──────────────────────────────────────────────
    section_title("TOKEN TABLE")
    rows = [(i+1, t[0], t[1], t[2]) for i, t in enumerate(tokens)]
    table(["#", "TOKEN TYPE", "VALUE", "LINE"],
          rows, [4, 14, 12, 6])

    # ── Symbol Table ─────────────────────────────────────────────
    section_title("SYMBOL TABLE (Identifiers)")
    if symbol_table:
        sym_rows = [(name, info['type'], str(info['value']), info['line'])
                    for name, info in symbol_table.items()]
        table(["NAME", "TYPE", "VALUE", "LINE"],
              sym_rows, [10, 10, 10, 6])
    else:
        print("  (no identifiers found)")

    print(f"\n  ✔  Total tokens : {len(tokens)}")
    print(f"  ✔  Identifiers  : {len(symbol_table)}")
    return tokens, symbol_table


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PHASE 2 — SYNTAX ANALYSIS  (AST)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ASTNode:
    def __init__(self, node_type, **kwargs):
        self.type = node_type
        self.__dict__.update(kwargs)

    def __repr__(self):
        attrs = {k: v for k, v in self.__dict__.items() if k != 'type'}
        return f"{self.type}({attrs})"

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens]
        self.pos    = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type=None, expected_val=None):
        tok = self.tokens[self.pos]
        if expected_type and tok[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type} got {tok[0]}('{tok[1]}') at line {tok[2]}")
        if expected_val and tok[1] != expected_val:
            raise SyntaxError(f"Expected '{expected_val}' got '{tok[1]}' at line {tok[2]}")
        self.pos += 1
        return tok

    def parse_program(self):
        stmts = []
        while self.pos < len(self.tokens):
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        return ASTNode('Program', body=stmts)

    def parse_statement(self):
        tok = self.peek()
        if tok is None:
            return None
        if tok[0] == 'KEYWORD' and tok[1] in ('int', 'float'):
            return self.parse_declaration()
        if tok[0] == 'KEYWORD' and tok[1] == 'if':
            return self.parse_if()
        if tok[0] == 'KEYWORD' and tok[1] == 'print':
            return self.parse_print()
        if tok[0] == 'IDENTIFIER':
            return self.parse_assignment()
        self.pos += 1
        return None

    def parse_declaration(self):
        dtype = self.consume('KEYWORD')[1]
        name  = self.consume('IDENTIFIER')[1]
        self.consume('OPERATOR', '=')
        expr  = self.parse_expr()
        return ASTNode('Declaration', dtype=dtype, name=name, value=expr)

    def parse_assignment(self):
        name = self.consume('IDENTIFIER')[1]
        self.consume('OPERATOR', '=')
        expr = self.parse_expr()
        return ASTNode('Assignment', name=name, value=expr)

    def parse_print(self):
        self.consume('KEYWORD', 'print')
        self.consume('DELIMITER', '(')
        expr = self.parse_expr()
        self.consume('DELIMITER', ')')
        return ASTNode('Print', value=expr)

    def parse_if(self):
        self.consume('KEYWORD', 'if')
        cond = self.parse_condition()
        self.consume('COLON')
        then_branch = [self.parse_statement()]
        else_branch = []
        if self.peek() and self.peek()[0] == 'KEYWORD' and self.peek()[1] == 'else':
            self.consume('KEYWORD', 'else')
            self.consume('COLON')
            else_branch = [self.parse_statement()]
        return ASTNode('If', condition=cond, then_branch=then_branch, else_branch=else_branch)

    def parse_condition(self):
        left = self.parse_expr()
        op   = self.consume('COMPARATOR')[1]
        right = self.parse_expr()
        return ASTNode('Condition', op=op, left=left, right=right)

    def parse_expr(self):
        left = self.parse_term()
        while self.peek() and self.peek()[0] == 'OPERATOR' and self.peek()[1] in ('+', '-'):
            op    = self.consume('OPERATOR')[1]
            right = self.parse_term()
            left  = ASTNode('BinaryOp', op=op, left=left, right=right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.peek() and self.peek()[0] == 'OPERATOR' and self.peek()[1] in ('*', '/'):
            op    = self.consume('OPERATOR')[1]
            right = self.parse_factor()
            left  = ASTNode('BinaryOp', op=op, left=left, right=right)
        return left

    def parse_factor(self):
        tok = self.peek()
        if tok[0] == 'INTEGER':
            self.pos += 1
            return ASTNode('Number', value=int(tok[1]))
        if tok[0] == 'FLOAT':
            self.pos += 1
            return ASTNode('Number', value=float(tok[1]))
        if tok[0] == 'IDENTIFIER':
            self.pos += 1
            return ASTNode('Identifier', name=tok[1])
        if tok[0] == 'DELIMITER' and tok[1] == '(':
            self.consume('DELIMITER', '(')
            expr = self.parse_expr()
            self.consume('DELIMITER', ')')
            return expr
        raise SyntaxError(f"Unexpected token: {tok}")


def print_ast(node, indent=0):
    pad = "    " * indent
    if node is None:
        return
    if node.type == 'Program':
        print(f"{pad}Program")
        for stmt in node.body:
            print_ast(stmt, indent + 1)
    elif node.type == 'Declaration':
        print(f"{pad}├─ Declaration [{node.dtype}]  {node.name} =")
        print_ast(node.value, indent + 2)
    elif node.type == 'Assignment':
        print(f"{pad}├─ Assignment  {node.name} =")
        print_ast(node.value, indent + 2)
    elif node.type == 'BinaryOp':
        print(f"{pad}├─ BinaryOp  [{node.op}]")
        print_ast(node.left,  indent + 2)
        print_ast(node.right, indent + 2)
    elif node.type == 'Number':
        print(f"{pad}├─ Number  {node.value}")
    elif node.type == 'Identifier':
        print(f"{pad}├─ Identifier  {node.name}")
    elif node.type == 'Condition':
        print(f"{pad}├─ Condition  [{node.op}]")
        print_ast(node.left,  indent + 2)
        print_ast(node.right, indent + 2)
    elif node.type == 'If':
        print(f"{pad}├─ If")
        print(f"{pad}│  ├─ Condition:")
        print_ast(node.condition, indent + 3)
        print(f"{pad}│  ├─ Then:")
        for s in node.then_branch:
            print_ast(s, indent + 3)
        if node.else_branch:
            print(f"{pad}│  └─ Else:")
            for s in node.else_branch:
                print_ast(s, indent + 3)
    elif node.type == 'Print':
        print(f"{pad}├─ Print")
        print_ast(node.value, indent + 2)


def phase2_parser(tokens):
    banner(2, "SYNTAX ANALYSIS — ABSTRACT SYNTAX TREE")
    parser = Parser(tokens)
    ast    = parser.parse_program()
    section_title("ABSTRACT SYNTAX TREE")
    print()
    print_ast(ast, 1)
    print(f"\n  ✔  AST nodes built successfully")
    return ast


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PHASE 3 — SEMANTIC ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def phase3_semantic(ast):
    banner(3, "SEMANTIC ANALYSIS")
    symbol_table = {}
    errors   = []
    warnings = []

    def eval_type(node):
        if node.type == 'Number':
            return 'float' if isinstance(node.value, float) else 'int'
        if node.type == 'Identifier':
            if node.name not in symbol_table:
                errors.append(f"  ✘  Undeclared variable '{node.name}'")
                return 'unknown'
            return symbol_table[node.name]['type']
        if node.type == 'BinaryOp':
            lt = eval_type(node.left)
            rt = eval_type(node.right)
            if lt == 'float' or rt == 'float':
                return 'float'
            return 'int'
        return 'unknown'

    def analyse(node):
        if node is None:
            return
        if node.type == 'Program':
            for s in node.body:
                analyse(s)
        elif node.type == 'Declaration':
            t = eval_type(node.value)
            symbol_table[node.name] = {'type': node.dtype, 'inferred': t, 'line': '—'}
            if node.dtype != t and t != 'unknown':
                warnings.append(f"  ⚠  Type mismatch: '{node.name}' declared {node.dtype} but assigned {t}")
        elif node.type == 'Assignment':
            if node.name not in symbol_table:
                errors.append(f"  ✘  Assignment to undeclared variable '{node.name}'")
            else:
                eval_type(node.value)
        elif node.type == 'If':
            eval_type(node.condition.left)
            eval_type(node.condition.right)
            for s in node.then_branch: analyse(s)
            for s in node.else_branch: analyse(s)
        elif node.type == 'Print':
            eval_type(node.value)

    analyse(ast)

    # ── Symbol Table ─────────────────────────────────────────────
    section_title("UPDATED SYMBOL TABLE")
    sym_rows = [(name, info['type'], info['inferred']) for name, info in symbol_table.items()]
    table(["VARIABLE", "DECLARED TYPE", "INFERRED TYPE"], sym_rows, [12, 15, 14])

    # ── Errors & Warnings ────────────────────────────────────────
    section_title("SEMANTIC CHECKS")
    if errors:
        for e in errors:
            print(f"  {e}")
    else:
        print("  ✔  No semantic errors found")
    if warnings:
        for w in warnings:
            print(f"  {w}")
    else:
        print("  ✔  No type warnings")

    return symbol_table


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PHASE 4 — INTERMEDIATE CODE GENERATION (Three-Address Code)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ICGGenerator:
    def __init__(self):
        self.code    = []
        self.temp_no = 0
        self.label_no= 0

    def new_temp(self):
        t = f"t{self.temp_no}"
        self.temp_no += 1
        return t

    def new_label(self):
        l = f"L{self.label_no}"
        self.label_no += 1
        return l

    def emit(self, instr):
        self.code.append(instr)

    def gen_expr(self, node):
        if node.type == 'Number':
            return str(node.value)
        if node.type == 'Identifier':
            return node.name
        if node.type == 'BinaryOp':
            l = self.gen_expr(node.left)
            r = self.gen_expr(node.right)
            t = self.new_temp()
            self.emit(f"{t} = {l} {node.op} {r}")
            return t

    def gen(self, node):
        if node.type == 'Program':
            for s in node.body:
                self.gen(s)
        elif node.type == 'Declaration':
            t = self.gen_expr(node.value)
            self.emit(f"{node.name} = {t}")
        elif node.type == 'Assignment':
            t = self.gen_expr(node.value)
            self.emit(f"{node.name} = {t}")
        elif node.type == 'Print':
            t = self.gen_expr(node.value)
            self.emit(f"print {t}")
        elif node.type == 'If':
            l_true  = self.new_label()
            l_false = self.new_label()
            l_end   = self.new_label()
            lv = self.gen_expr(node.condition.left)
            rv = self.gen_expr(node.condition.right)
            self.emit(f"if {lv} {node.condition.op} {rv} goto {l_true}")
            self.emit(f"goto {l_false}")
            self.emit(f"{l_true}:")
            for s in node.then_branch:
                self.gen(s)
            self.emit(f"goto {l_end}")
            self.emit(f"{l_false}:")
            for s in node.else_branch:
                self.gen(s)
            self.emit(f"{l_end}:")


def phase4_icg(ast):
    banner(4, "INTERMEDIATE CODE GENERATION (Three-Address Code)")
    gen = ICGGenerator()
    gen.gen(ast)

    section_title("THREE-ADDRESS CODE")
    for i, line in enumerate(gen.code, 1):
        prefix = "  " if line.endswith(':') else "  "
        label  = f"  {i:<4}"
        print(f"{label}│  {line}")

    print(f"\n  ✔  {len(gen.code)} TAC instructions generated")
    return gen.code


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PHASE 5 — OPTIMISED ICG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def is_number(s):
    try:
        float(s)
        return True
    except:
        return False

def const_val(s):
    try:
        v = float(s)
        return int(v) if v == int(v) else v
    except:
        return None

def phase5_optimizer(tac):
    banner(5, "OPTIMISED INTERMEDIATE CODE GENERATION")
    const_map = {}   # var → constant value
    used_vars = set()
    optimized = []
    changes   = []

    # ── Pass 1: Constant Folding + Propagation ───────────────────
    section_title("PASS 1 — Constant Folding & Propagation")
    for instr in tac:
        # x = a OP b
        m = re.match(r'(\w+)\s*=\s*(\S+)\s*([+\-*/])\s*(\S+)', instr)
        if m:
            dest, a, op, b = m.groups()
            a_val = const_map.get(a, const_val(a))
            b_val = const_map.get(b, const_val(b))
            if a_val is not None and b_val is not None:
                try:
                    result = eval(f"{a_val} {op} {b_val}")
                    result = int(result) if result == int(result) else result
                    new_instr = f"{dest} = {result}"
                    changes.append(f"  ✔  Constant fold: [{instr}]  →  [{new_instr}]")
                    const_map[dest] = result
                    optimized.append(new_instr)
                    continue
                except:
                    pass
            # Propagation: replace known constants
            a_rep = str(a_val) if a_val is not None and a != str(a_val) else a
            b_rep = str(b_val) if b_val is not None and b != str(b_val) else b
            new_instr = f"{dest} = {a_rep} {op} {b_rep}"
            if new_instr != instr:
                changes.append(f"  ✔  Const propagate: [{instr}]  →  [{new_instr}]")
            if is_number(a_rep) and is_number(b_rep):
                result = eval(f"{a_rep} {op} {b_rep}")
                result = int(result) if result == int(result) else result
                const_map[dest] = result
                new_instr = f"{dest} = {result}"
            # simple assignment x = const
            m2 = re.match(r'(\w+)\s*=\s*(\S+)$', new_instr)
            if m2:
                d, v = m2.groups()
                if is_number(v):
                    const_map[d] = const_val(v)
            optimized.append(new_instr)
            continue

        # simple x = y
        m2 = re.match(r'(\w+)\s*=\s*(\S+)$', instr)
        if m2:
            dest, src = m2.groups()
            if src in const_map:
                new_instr = f"{dest} = {const_map[src]}"
                const_map[dest] = const_map[src]
                if new_instr != instr:
                    changes.append(f"  ✔  Const propagate: [{instr}]  →  [{new_instr}]")
                optimized.append(new_instr)
                continue

        optimized.append(instr)

    if changes:
        for c in changes:
            print(c)
    else:
        print("  (no constant folding opportunities)")

    # ── Pass 2: Dead Code Elimination ───────────────────────────
    section_title("PASS 2 — Dead Code Elimination")
    # Find all used variables
    for instr in optimized:
        tokens = re.findall(r'\b([a-zA-Z_]\w*)\b', instr)
        for t in tokens:
            if not (instr.startswith(t + ' =') or instr.endswith(':')):
                used_vars.add(t)

    final    = []
    removed  = []
    for instr in optimized:
        m = re.match(r'(t\d+)\s*=', instr)
        if m and m.group(1) not in used_vars:
            removed.append(f"  ✔  Dead code removed: [{instr}]")
        else:
            final.append(instr)

    if removed:
        for r in removed:
            print(r)
    else:
        print("  (no dead code found)")

    # ── Optimised TAC ────────────────────────────────────────────
    section_title("OPTIMISED THREE-ADDRESS CODE")
    for i, line in enumerate(final, 1):
        print(f"  {i:<4}│  {line}")

    print(f"\n  ✔  Before optimisation : {len(tac)} instructions")
    print(f"  ✔  After optimisation  : {len(final)} instructions")
    print(f"  ✔  Instructions saved  : {len(tac) - len(final)}")
    return final


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PHASE 6 — CODE GENERATION (Assembly-like Target Code)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def phase6_codegen(opt_tac):
    banner(6, "CODE GENERATION — TARGET ASSEMBLY CODE")
    reg_pool    = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8']
    reg_map     = {}   # var/temp → register
    reg_idx     = 0
    target_code = []

    def get_reg(var):
        nonlocal reg_idx
        if var in reg_map:
            return reg_map[var]
        reg = reg_pool[reg_idx % len(reg_pool)]
        reg_idx += 1
        reg_map[var] = reg
        return reg

    OP_MAP = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}

    for instr in opt_tac:
        # x = a OP b
        m = re.match(r'(\w+)\s*=\s*(\S+)\s*([+\-*/])\s*(\S+)', instr)
        if m:
            dest, a, op, b = m.groups()
            rd = get_reg(dest)
            ra = get_reg(a) if not is_number(a) else a
            rb = get_reg(b) if not is_number(b) else b
            asm_op = OP_MAP.get(op, op)
            if not is_number(a):
                target_code.append(f"MOV {rd}, {ra}")
            else:
                target_code.append(f"MOV {rd}, {a}")
            target_code.append(f"{asm_op} {rd}, {rb if not is_number(b) else b}")
            continue

        # x = const/var
        m2 = re.match(r'(\w+)\s*=\s*(\S+)$', instr)
        if m2:
            dest, src = m2.groups()
            rd = get_reg(dest)
            rs = get_reg(src) if not is_number(src) else src
            target_code.append(f"MOV {rd}, {rs}")
            continue

        # print x
        m3 = re.match(r'print\s+(\S+)', instr)
        if m3:
            var = m3.group(1)
            rv  = get_reg(var) if not is_number(var) else var
            target_code.append(f"PRINT {rv}")
            continue

        # if x OP y goto L
        m4 = re.match(r'if\s+(\S+)\s*(>=|<=|==|!=|>|<)\s*(\S+)\s+goto\s+(\S+)', instr)
        if m4:
            a, op, b, label = m4.groups()
            ra = get_reg(a) if not is_number(a) else a
            rb = get_reg(b) if not is_number(b) else b
            cmp_op = {'>' :'JG', '<' :'JL', '>=' :'JGE', '<=' :'JLE', '==' :'JE', '!=' :'JNE'}
            target_code.append(f"CMP {ra}, {rb}")
            target_code.append(f"{cmp_op[op]} {label}")
            continue

        # goto L
        m5 = re.match(r'goto\s+(\S+)', instr)
        if m5:
            target_code.append(f"JMP {m5.group(1)}")
            continue

        # Label:
        if re.match(r'L\d+:', instr):
            target_code.append(f"\n{instr}")
            continue

        target_code.append(f"; {instr}")

    target_code.append("HLT")

    # ── Register Allocation Table ────────────────────────────────
    section_title("REGISTER ALLOCATION")
    if reg_map:
        table(["VARIABLE / TEMP", "REGISTER"],
              list(reg_map.items()), [16, 10])

    # ── Assembly Code ─────────────────────────────────────────────
    section_title("GENERATED ASSEMBLY CODE")
    for i, line in enumerate(target_code, 1):
        if line.startswith('\n'):
            print()
            print(f"  {i:<4}│  {line.strip()}")
        else:
            print(f"  {i:<4}│  {line}")

    print(f"\n  ✔  {len(target_code)} assembly instructions generated")
    return target_code


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN — RUN ALL PHASES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_source_code():
    print("\n" + "█" * W)
    print("█" + " " * (W-2) + "█")
    print("█" + "   MINI COMPILER — 6 PHASE DEMONSTRATION".center(W-2) + "█")
    print("█" + " " * (W-2) + "█")
    print("█" * W)

    print("""
  SUPPORTED SYNTAX:
  ─────────────────────────────────────────────────────────────
  │  Variable declaration :  int a = 5
  │  Arithmetic           :  int c = a + b * 2
  │  If / Else            :  if c > 10 :
  │                              print ( c )
  │                          else :
  │                              print ( a )
  │  Print statement      :  print ( a )
  ─────────────────────────────────────────────────────────────
  Type your program below.
  Press ENTER on an empty line when done.
  (or type 'demo' to use the built-in sample program)
  ─────────────────────────────────────────────────────────────
""")

    lines = []
    while True:
        try:
            line = input("  >>> ")
        except EOFError:
            break
        if line.strip().lower() == 'demo':
            return SOURCE_CODE
        if line.strip() == '' and lines:
            break
        lines.append(line)

    if not lines:
        print("  No input given. Using demo program.\n")
        return SOURCE_CODE

    return '\n'.join(lines)


def main():
    source = get_source_code()

    print("\n  SOURCE PROGRAM:")
    print("  " + "─" * (W - 4))
    for line in source.strip().split('\n'):
        print(f"  │  {line}")
    print("  " + "─" * (W - 4))

    try:
        tokens, sym  = phase1_lexer(source)
        ast          = phase2_parser(tokens)
        symbol_table = phase3_semantic(ast)
        tac          = phase4_icg(ast)
        opt_tac      = phase5_optimizer(tac)
        asm          = phase6_codegen(opt_tac)
    except SyntaxError as e:
        print(f"\n  ✘  Syntax Error: {e}")
        print("  Please check your program and try again.\n")
        return
    except Exception as e:
        print(f"\n  ✘  Error: {e}")
        return

    print("\n" + "═" * W)
    print("  ✅  COMPILATION COMPLETE — All 6 phases executed")
    print("═" * W + "\n")


if __name__ == '__main__':
    main()
