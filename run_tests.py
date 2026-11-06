#!/usr/bin/env python3
"""Regressziós tesztek: python run_tests.py"""
import os
import subprocess
import sys
import tempfile

import minescript as ms

MAP = ["1 3", ">.@"]
failed = 0


def check(name, map_lines, prog, expected):
    global failed
    inp = "\n".join(map_lines) + "\n" + prog + ("\n" if prog else "")
    with tempfile.TemporaryDirectory() as d:
        fi, fo = os.path.join(d, "in.txt"), os.path.join(d, "out.txt")
        open(fi, "w", encoding="utf-8").write(inp)
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "robot.py"), "-q", fi, fo], check=True)
        got = open(fo, encoding="utf-8").read().split("\n")
    if got and got[-1] == "":
        got.pop()
    if isinstance(expected, str):
        expected = expected.split("\n")
    ok = got == expected
    print(("OK   " if ok else "FAIL ") + name)
    if not ok:
        failed += 1
        print("   várt:", expected[:12], "...", expected[-2:])
        print("   kapott:", got[:12], "...", got[-2:])


# --- a feladatkiírás naplópéldája
check("feladat-példa", ["3 15", "....@..........", ".#############.", ".......@...>..."],
      "set arany to isThere 2\nset count to 0\nturn by 0\nprint arany\nif false\n  print 1\nelse\n  set x to isThere 3\n  print 9",
      "1 isThere 2 false\n2\n3 turn by 0\n4 print false\n5\n7\n8 isThere 3 E_BAD_ARG\nEOR")
check("üres program", MAP, "", "EOR")

# --- futásidejű hibák
check("E_UNINITIALIZED op (nincs rövidzár)", MAP, "set x to true or c", "1 E_UNINITIALIZED\nEOR")
check("E_UNINITIALIZED print", MAP, "print q", "1 print E_UNINITIALIZED\nEOR")
check("E_UNINITIALIZED isThere", MAP, "set a to isThere q", "1 isThere E_UNINITIALIZED\nEOR")
check("E_TYPE_MISMATCH", MAP, "set a to 1\nset a to true", "1\n2 E_TYPE_MISMATCH\nEOR")
check("E_TYPE_MISMATCH isThere után (api + hiba)", MAP, "set a to 1\nset a to isThere 0", "1\n2 isThere 0 true E_TYPE_MISMATCH\nEOR")
check("E_BAD_OPERAND = típus", MAP, "set a to 1\nset b to a = true", "1\n2 E_BAD_OPERAND\nEOR")
check("E_BAD_OPERAND and int", MAP, "set a to 1\nset b to a and true", "1\n2 E_BAD_OPERAND\nEOR")
check("E_BAD_OPERAND not int", MAP, "set a to 1\nset b to not a", "1\n2 E_BAD_OPERAND\nEOR")
check("E_BAD_OPERAND + bool", MAP, "set b to 1 + true", "1 E_BAD_OPERAND\nEOR")
check("első operandus hibája előbb", MAP, "set b to true + c", "1 E_BAD_OPERAND\nEOR")
check("E_NON_BOOL_CONDITION", MAP, "set a to 3\nwhile a\n  print 1", "1\n2 E_NON_BOOL_CONDITION\nEOR")
check("E_BAD_ARG turn bool", MAP, "turn by true", "1 turn by true E_BAD_ARG\nEOR")
check("E_BAD_ARG isThere 3", MAP, "set a to isThere 3", "1 isThere 3 E_BAD_ARG\nEOR")
check("E_BAD_ARG negatív lépés", MAP, "set n to 0 - 1\nstep forward n", "1\n2 step forward -1 E_BAD_ARG\nEOR")
check("E_BEDROCK_HIT térkép széle", MAP, "step forward 5", "1 step forward 5 E_BEDROCK_HIT\nEOR")
check("E_NO_GOLD", MAP, "mine here", "1 mine here E_NO_GOLD\nEOR")

# --- működés
check("step + mine (arany a lépés közben megmarad)", MAP, "step forward 2\nmine here\nmine here",
      "1 step forward 2\n2 mine here\n3 mine here E_NO_GOLD\nEOR")
check("isThere térkép szélén = fal", ["1 1", ">"], "set a to isThere 1\nset b to isThere 0",
      "1 isThere 1 true\n2 isThere 0 false\nEOR")
check("turn by 1 majd isThere", ["2 2", ">.", "#."], "turn by 3\nset a to isThere 1\nturn by 4\nset b to isThere 0",
      "1 turn by 3\n2 isThere 1 true\n3 turn by 4\n4 isThere 0 false\nEOR")
check("else sor csak ha lefut", MAP, "if false\n  print 1\nelse\n  print 2", "1\n3\n4 print 2\nEOR")
check("if igaz ág, else kimarad", MAP, "if true\n  print 1\nelse\n  print 2\nprint 3", "1\n2 print 1\n5 print 3\nEOR")
check("while sor minden kiértékeléskor", MAP,
      "set i to 0\nset c to i < 2\nwhile c\n  set i to i + 1\n  set c to i < 2",
      "1\n2\n3\n4\n5\n3\n4\n5\n3\nEOR")
check("egyenlőség logikai", MAP, "set a to true = true\nprint a", "1\n2 print true\nEOR")

# --- futási limit
def loop(k):
    return ("set i to 0\nset c to i < %d\nwhile c\n  set i to i + 1\n  set c to i < %d\nprint i" % (k, k))


check("pontosan 1000 sor, normál vég (EOR)", MAP, loop(332),
      ["1", "2"] + ["3", "4", "5"] * 332 + ["3", "6 print 332", "EOR"])
check("1001. sor kezdeményezése: limit, nincs EOR", MAP, loop(333),
      ["1", "2"] + ["3", "4", "5"] * 332 + ["3", "4", ms.LIMIT_MSG])

# --- parser / nyelvtan
prog = "set count to 0\nwhile true\n  if true\n    if false\n      print 1\n    else\n      print 2\n"
assert "\n".join(ms.to_text(ms.parse_program(prog.rstrip("\n")))) == prog.rstrip("\n"), "szöveg-blokk körút"
print("OK   szöveg → AST → szöveg körút")
for w in ["while", "While", "ISTHERE", "9lives", "a b", ""]:
    assert not ms.is_ident(w), w
for w in ["arany", "count2", "X", "whileX"]:
    assert ms.is_ident(w), w
print("OK   azonosító-szabályok (kulcsszavak kis/nagybetűtől függetlenül tiltottak)")

print("\n%s" % ("MINDEN TESZT RENDBEN" if not failed else "%d TESZT HIBÁS" % failed))
sys.exit(1 if failed else 0)
