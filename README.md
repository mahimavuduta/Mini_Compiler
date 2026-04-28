# 🛠️ Mini Compiler — 6 Phase Implementation

A complete mini compiler built in **Python** that processes a simplified programming language through all six standard compilation phases — from raw source code to assembly-level target code.

---

## 👥 Team
| Name | Roll Number |
|------|-------------|
| Roshini Yanamala | 160123733169 |
| Vuduta Mahima | 160123733177 |

**Guide:** Dr. G. Vanitha & Sasmitha Ma'am, Dept. of CSE  
**Institution:** Chaitanya Bharathi Institute of Technology (Autonomous), Hyderabad  
**Year:** 2025–2026

---

## 🚀 How to Run

```bash
python3 compiler.py
```

Type your program line by line and press **Enter on a blank line** to start compilation.  
Or type `demo` to instantly run the built-in sample program.

---

## 📋 Supported Syntax

```
int a = 5
int b = 10
int c = a + b * 2
if c > 15 :
    print ( c )
else :
    print ( a )
```

---

## ⚙️ Compilation Phases

### Phase 1 — Lexical Analysis
The lexer is the first phase of the compiler. It reads the source code character by character and groups them into meaningful units called **tokens**. Each token has a type (KEYWORD, IDENTIFIER, INTEGER, OPERATOR, etc.) and a value. It also builds a **Symbol Table** that tracks all identifiers (variable names) found in the program along with their data type and line number.

### Phase 2 — Syntax Analysis (Parsing)
The parser takes the token stream from Phase 1 and checks whether the tokens follow the **grammar rules** of the language. It builds an **Abstract Syntax Tree (AST)** — a tree structure that represents the hierarchical organisation of the program. Each node in the tree represents a construct such as a declaration, assignment, binary operation, or if-else statement.

### Phase 3 — Semantic Analysis
This phase checks the **meaning** of the program beyond just the grammar. It validates that variables are declared before use, that operations are performed on compatible types, and that there are no logical inconsistencies. An updated symbol table is produced with type information verified and confirmed.

### Phase 4 — Intermediate Code Generation (ICG)
The ICG phase translates the AST into **Three-Address Code (TAC)** — a simplified, machine-independent representation where each instruction has at most three operands. Temporary variables (t0, t1, t2...) are introduced to hold intermediate results. Control flow (if/else) is represented using conditional jumps and labels.

### Phase 5 — Optimised ICG
This phase applies **code optimisation techniques** to the TAC without changing the program's output:
- **Constant Folding** — Evaluates constant expressions at compile time (e.g., `4 + 6` → `10`)
- **Constant Propagation** — Replaces variables with their known constant values
- **Dead Code Elimination** — Removes temporary variables that are computed but never used

The result is fewer instructions and more efficient code.

### Phase 6 — Code Generation
The final phase translates the optimised TAC into **assembly-like target code** using registers (R1–R8). It performs register allocation (mapping variables to registers) and generates instructions like `MOV`, `ADD`, `SUB`, `MUL`, `CMP`, `JG`, `JMP`, `PRINT`, and `HLT`. This output closely resembles real machine-level assembly language.

---

## 🧮 Sample Output Summary

| Phase | Output |
|-------|--------|
| Lexical Analysis | 43 tokens, 5 identifiers in symbol table |
| Syntax Analysis | Full AST with nested binary operations |
| Semantic Analysis | All types validated — no errors |
| ICG | 17 Three-Address Code instructions |
| Optimised ICG | 16 instructions (constant fold: `4+6→10`) |
| Code Generation | 21 assembly instructions, 8 registers allocated |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3 |
| Parser | Recursive Descent |
| Optimisation | Constant Folding + Dead Code Elimination |
| Code Gen | Register-based assembly |
| Dependencies | None — pure Python stdlib only |

---

## 📄 License
Developed as a Project for academic purposes at CBIT (Autonomous), Hyderabad. Not for commercial use.
