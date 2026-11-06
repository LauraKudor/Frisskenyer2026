from pathlib import Path
p = Path("C:/Users/ervin/Downloads/project/ui.html")
s = p.read_text(encoding="utf-8")
lines = s.split("\n")
for i, line in enumerate(lines):
    if "window.close();" in line and "bExit" not in line and i > 590 and i < 610:
        print(f"FOUND window.close at line {i+1}: {line.strip()}")
