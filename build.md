# build.md – fordítás és futtatás

## Platform
- Python **3.9 vagy újabb** (fejlesztve és tesztelve: Python 3.13, Linux).
- **Külső csomagok**: Python standard könyvtára (`http.server`, `json`, `re`) plus `pywebview` a beágyazott webes felülettel (embedded webview). `pywebview` telepítésre: `pip install pywebview`.
- A grafikus felület egy beágyazott webes nézetben jelenik meg (native webview, nem külön böngészőablak), amit a Python alkalmazás indít el. A weboldalt a program magától kiszolgálja a `127.0.0.1` címen. Internetkapcsolat nem kell. Kilépésnél a bezáró gomb és a webview lezárása is mukodik (a `/api/exit` végpont a webview-t is bezárja).

## Fordítás
Nincs fordítási lépés, a `robot.py` közvetlenül futtatható.
Opcionálisan önálló `robot.exe` is készíthető (Windows, PyInstaller):

```
pip install pyinstaller
pyinstaller --onefile --add-data "ui.html;." robot.py
```
(Linux/macOS-en az `--add-data` elválasztója `:`.) A kész `robot.exe` a `dist` mappában keletkezik, és ugyanúgy használható, mint a `python robot.py`.

## Futtatás
Grafikus IDE:

```
python robot.py input_001.txt output_001.txt
```
(Windows alatt a `robot.bat input_001.txt output_001.txt`, Linux/macOS-en a `./robot.sh input_001.txt output_001.txt` is megteszi.)

Csendes mód (felhasználói interakció nélkül, a napló kiírása után kilép):

```
python robot.py -q input_001.txt output_001.txt
```

Sok tesztfájl automatikus futtatása (Linux/macOS):

```
for f in input_*.txt; do python robot.py -q "$f" "${f/input_/output_}"; done
```
Windows (PowerShell):

```
Get-ChildItem input_*.txt | % { python robot.py -q $_.Name ($_.Name -replace '^input_','output_') }
```

## Tesztek
```
python run_tests.py
```
Az interpreter, a hibakódok, a naplóformátum és az 1000 soros limit regressziós tesztjei. A `tests/` mappában mintabemenetek vannak.

## Fájlok
| Fájl | Szerep |
|---|---|
| `robot.py` | indító, `-q` mód, a GUI helyi webszervere |
| `minescript.py` | bemenet-beolvasás, parser, interpreter, naplózás |
| `ui.html` | az IDE felülete: blokkszerkesztő, szöveges nézet, szimulátor, nyomkövetés, kézi vezérlés |
| `run_tests.py` | automata tesztek |
