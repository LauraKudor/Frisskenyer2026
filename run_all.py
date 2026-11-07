#!/usr/bin/env python3
"""Az összes input_*.txt lefuttatása csendes módban.

Használat:
    python run_all.py [bemeneti_mappa] [kimeneti_mappa]

Alapértelmezés: mindkettő az aktuális mappa. Az input_001.txt -> output_001.txt.
"""
import glob
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else "."
dst = sys.argv[2] if len(sys.argv) > 2 else src
os.makedirs(dst, exist_ok=True)

files = sorted(glob.glob(os.path.join(src, "input_*.txt")))
if not files:
    print("Nem találtam input_*.txt fájlt ebben a mappában:", os.path.abspath(src))
    sys.exit(1)

bad = 0
for f in files:
    name = os.path.basename(f).replace("input_", "output_", 1)
    r = subprocess.run([sys.executable, os.path.join(HERE, "robot.py"), "-q", f, os.path.join(dst, name)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        bad += 1
        print("HIBA:", os.path.basename(f), "-", (r.stderr.strip().splitlines() or ["?"])[-1])
print("%d fájl feldolgozva, %d hiba. Kimenet: %s" % (len(files), bad, os.path.abspath(dst)))
sys.exit(1 if bad else 0)
