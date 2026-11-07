"""MineScript"""
import re

KEYWORDS = {
    "and", "by", "else", "false", "forward", "here", "if", "isthere",
    "mine", "not", "or", "print", "set", "step", "to", "true", "turn", "while",
}
LIMIT = 1000
LIMIT_MSG = "INSTRUCTION_COUNT_LIMIT_EXCEEDED"

# 0 = kelet, 1 = észak, 2 = nyugat, 3 = dél (balra fordulás: +1)
DIRS = [(1, 0), (0, -1), (-1, 0), (0, 1)]
DIR_CHARS = {">": 0, "^": 1, "<": 2, "v": 3}
DIR_TO_CHAR = {0: ">", 1: "^", 2: "<", 3: "v"}

ARITH = {"+", "-", "*"}
COMPARE = {"<", "<=", ">", ">="}
EQUALITY = {"=", "<>"}
LOGIC = {"and", "or"}


def is_keyword(s):
    return s in KEYWORDS


def is_ident(s):
    return re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", s) is not None and not is_keyword(s)


# ---------------------------------------------------------------- bemenet

def read_input(path):
    """-> (rows, cols, grid(list[str]), program_text)"""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    rows, cols = [int(x) for x in lines[0].split()]
    grid = [lines[1 + i] if 1 + i < len(lines) else "" for i in range(rows)]
    grid = [g.ljust(cols, "#")[:cols] for g in grid]
    prog = lines[1 + rows:]
    while prog and prog[-1].strip() == "":
        prog.pop()
    return rows, cols, grid, "\n".join(l.rstrip() for l in prog)


# ---------------------------------------------------------------- parser

def _tokens(line):
    indent = len(line) - len(line.lstrip(" "))
    return indent, line.split()


def _parse_expr(t):
    if len(t) == 1:
        return {"k": "val", "a": t[0]}
    if len(t) == 2:
        if t[0] == "isThere":
            return {"k": "isThere", "a": t[1]}
        return {"k": "not", "a": t[1]}
    return {"k": "bin", "op": t[1], "a": t[0], "b": t[2]}


def parse_program(text):
    """Szöveges forráskód -> AST (sorszámokkal)."""
    L = [_tokens(l) for l in text.split("\n")] if text != "" else []
    n = len(L)

    def body(i, hdr_indent):
        j = i
        while j < n and not L[j][1]:
            j += 1
        if j < n and L[j][0] > hdr_indent:
            return block(j, L[j][0])
        return [], i

    def block(i, ind):
        nodes = []
        while i < n:
            indent, t = L[i]
            if not t:
                i += 1
                continue
            if indent < ind:
                break
            line = i + 1
            c = t[0]
            if c == "step":
                nodes.append({"t": "step", "a": t[2], "line": line}); i += 1
            elif c == "turn":
                nodes.append({"t": "turn", "a": t[2], "line": line}); i += 1
            elif c == "mine":
                nodes.append({"t": "mine", "line": line}); i += 1
            elif c == "print":
                nodes.append({"t": "print", "a": t[1], "line": line}); i += 1
            elif c == "set":
                nodes.append({"t": "set", "name": t[1], "expr": _parse_expr(t[3:]), "line": line}); i += 1
            elif c == "while":
                b, i = body(i + 1, indent)
                nodes.append({"t": "while", "a": t[1], "body": b, "line": line})
            elif c == "if":
                b, i = body(i + 1, indent)
                j = i
                while j < n and not L[j][1]:
                    j += 1
                if j < n and L[j][0] == indent and L[j][1][0] == "else":
                    eb, i = body(j + 1, indent)
                    nodes.append({"t": "ifelse", "a": t[1], "body": b, "ebody": eb,
                                  "line": line, "eline": j + 1})
                else:
                    nodes.append({"t": "if", "a": t[1], "body": b, "line": line})
            else:  # eltévedt else stb - bemenet mindig helyes, átlépjük
                i += 1
        return nodes, i

    nodes, _ = block(0, 0) if n else ([], 0)
    return nodes


def expr_text(e):
    if e["k"] == "val":
        return e["a"]
    if e["k"] == "bin":
        return "%s %s %s" % (e["a"], e["op"], e["b"])
    if e["k"] == "not":
        return "not " + e["a"]
    return "isThere " + e["a"]


def to_text(nodes, depth=0):
    out = []
    pad = "  " * depth
    for n in nodes:
        t = n["t"]
        if t == "step":
            out.append(pad + "step forward " + n["a"])
        elif t == "turn":
            out.append(pad + "turn by " + n["a"])
        elif t == "mine":
            out.append(pad + "mine here")
        elif t == "print":
            out.append(pad + "print " + n["a"])
        elif t == "set":
            out.append(pad + "set %s to %s" % (n["name"], expr_text(n["expr"])))
        elif t in ("if", "ifelse", "while"):
            out.append(pad + ("while " if t == "while" else "if ") + n["a"])
            out += to_text(n["body"], depth + 1)
            if t == "ifelse":
                out.append(pad + "else")
                out += to_text(n["ebody"], depth + 1)
    return out


# ---------------------------------------------------------------- futtatás

class Err(Exception):
    def __init__(self, code):
        self.code = code


class Halt(Exception):
    pass


def vtype(v):
    return "bool" if isinstance(v, bool) else "int"


def vstr(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


class Run:
    def __init__(self, rows, cols, grid):
        self.rows, self.cols = rows, cols
        self.g = []
        self.x = self.y = self.d = 0
        for y, row in enumerate(grid):
            r = []
            for x, ch in enumerate(row):
                if ch in DIR_CHARS:
                    self.x, self.y, self.d = x, y, DIR_CHARS[ch]
                    ch = "."
                r.append(ch)
            self.g.append(r)
        self.disc = [[False] * cols for _ in range(rows)]
        self.disc[self.y][self.x] = True
        self.mined = 0
        self.vars = {}
        self.entries = []
        self.texts = []
        self.end = "EOR"
        self.state0 = self.snapshot()

    # --- állapot
    def snapshot(self):
        return {
            "x": self.x, "y": self.y, "d": self.d,
            "g": ["".join(r) for r in self.g],
            "v": ["".join("1" if c else "0" for c in r) for r in self.disc],
            "m": self.mined,
        }

    def inside(self, x, y):
        return 0 <= x < self.cols and 0 <= y < self.rows

    def front(self):
        dx, dy = DIRS[self.d]
        return self.x + dx, self.y + dy

    def front_kind(self):
        fx, fy = self.front()
        if not self.inside(fx, fy):
            return 1
        c = self.g[fy][fx]
        return 1 if c == "#" else 2 if c == "@" else 0

    # --- változó / érték olvasás
    def read(self, tok):
        if tok == "true":
            return True
        if tok == "false":
            return False
        if re.fullmatch(r"[0-9]+", tok):
            return int(tok)
        if tok in self.vars:
            return self.vars[tok]
        raise Err("E_UNINITIALIZED")

    # --- egy sor feldolgozásának kezdete / vége
    def begin(self):
        if len(self.entries) >= LIMIT:
            self.end = "LIMIT"
            raise Halt()
        return {"api": None, "out": None, "err": None}

    def commit(self, line, e):
        parts = [str(line)]
        if e["api"]:
            name, param, ret = e["api"]
            parts.append(name)
            if param is not None:
                parts.append(param)
            if ret is not None:
                parts.append(ret)
        if e["err"]:
            parts.append(e["err"])
        text = " ".join(parts)
        self.texts.append(text)
        self.entries.append({
            "line": line, "text": text, "err": e["err"], "out": e["out"],
            "st": self.snapshot(),
            "vars": [[k, vtype(v), vstr(v)] for k, v in self.vars.items()],
        })
        if e["err"]:
            raise Halt()

    # --- API
    def api_isthere(self, e, tok):
        try:
            w = self.read(tok)
        except Err as x:
            e["api"] = ("isThere", None, None)
            raise x
        if vtype(w) != "int" or w not in (0, 1, 2):
            e["api"] = ("isThere", vstr(w), None)
            raise Err("E_BAD_ARG")
        fx, fy = self.front()
        if self.inside(fx, fy):
            self.disc[fy][fx] = True
        res = self.front_kind() == w
        e["api"] = ("isThere", str(w), vstr(res))
        return res

    def nonneg_param(self, e, name, tok):
        try:
            v = self.read(tok)
        except Err as x:
            e["api"] = (name, None, None)
            raise x
        e["api"] = (name, vstr(v), None)
        if vtype(v) != "int" or v < 0:
            raise Err("E_BAD_ARG")
        return v

    # --- kifejezés
    def eval_calc(self, e, ex):
        k = ex["k"]
        if k == "val":
            return self.read(ex["a"])
        if k == "isThere":
            return self.api_isthere(e, ex["a"])
        if k == "not":
            v = self.read(ex["a"])
            if vtype(v) != "bool":
                raise Err("E_BAD_OPERAND")
            return not v
        op = ex["op"]
        a = self.read(ex["a"])
        if op in ARITH or op in COMPARE:
            if vtype(a) != "int":
                raise Err("E_BAD_OPERAND")
        elif op in LOGIC:
            if vtype(a) != "bool":
                raise Err("E_BAD_OPERAND")
        b = self.read(ex["b"])
        if op in EQUALITY:
            if vtype(a) != vtype(b):
                raise Err("E_BAD_OPERAND")
            return (a == b) if op == "=" else (a != b)
        if op in LOGIC:
            if vtype(b) != "bool":
                raise Err("E_BAD_OPERAND")
            return (a and b) if op == "and" else (a or b)
        if vtype(b) != "int":
            raise Err("E_BAD_OPERAND")
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "<":
            return a < b
        if op == "<=":
            return a <= b
        if op == ">":
            return a > b
        return a >= b

    def cond(self, tok):
        v = self.read(tok)
        if vtype(v) != "bool":
            raise Err("E_NON_BOOL_CONDITION")
        return v

    # --- végrehajtás
    def exec_block(self, nodes):
        for n in nodes:
            self.exec_node(n)

    def exec_node(self, n):
        t = n["t"]
        e = self.begin()
        try:
            if t == "set":
                val = self.eval_calc(e, n["expr"])
                name = n["name"]
                if name in self.vars and vtype(self.vars[name]) != vtype(val):
                    raise Err("E_TYPE_MISMATCH")
                self.vars[name] = val
            elif t == "step":
                cnt = self.nonneg_param(e, "step forward", n["a"])
                dx, dy = DIRS[self.d]
                for _ in range(cnt):
                    nx, ny = self.x + dx, self.y + dy
                    if not self.inside(nx, ny) or self.g[ny][nx] == "#":
                        raise Err("E_BEDROCK_HIT")
                    self.x, self.y = nx, ny
                    self.disc[ny][nx] = True
            elif t == "turn":
                cnt = self.nonneg_param(e, "turn by", n["a"])
                self.d = (self.d + cnt) % 4
            elif t == "mine":
                e["api"] = ("mine here", None, None)
                if self.g[self.y][self.x] != "@":
                    raise Err("E_NO_GOLD")
                self.g[self.y][self.x] = "."
                self.mined += 1
            elif t == "print":
                try:
                    v = self.read(n["a"])
                except Err as x:
                    e["api"] = ("print", None, None)
                    raise x
                e["api"] = ("print", vstr(v), None)
                e["out"] = vstr(v)
            elif t in ("if", "ifelse"):
                c = self.cond(n["a"])
                self.commit(n["line"], e)
                if c:
                    self.exec_block(n["body"])
                elif t == "ifelse":
                    e2 = self.begin()
                    self.commit(n["eline"], e2)
                    self.exec_block(n["ebody"])
                return
            elif t == "while":
                while True:
                    c = self.cond(n["a"])
                    self.commit(n["line"], e)
                    if not c:
                        return
                    self.exec_block(n["body"])
                    e = self.begin()
        except Err as x:
            e["err"] = x.code
        self.commit(n["line"], e)

    def go(self, nodes):
        try:
            self.exec_block(nodes)
        except Halt:
            pass

    def final_line(self):
        return LIMIT_MSG if self.end == "LIMIT" else "EOR"

    def log_lines(self, n=None):
        if n is None or n >= len(self.texts):
            return self.texts + [self.final_line()]
        return self.texts[:max(0, n)]

    def log_text(self, n=None):
        return "\n".join(self.log_lines(n)) + "\n"


def execute(rows, cols, grid, prog_text):
    r = Run(rows, cols, grid)
    r.go(parse_program(prog_text))
    return r


def write_log(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
