# build.md – telepítés, fordítás és futtatás

## Platform
- Python **3.9 vagy újabb** (fejlesztve: Python 3.13).
- **Interpreter és `-q` mód**: csak a Python standard könyvtárát használja, nincs külső csomag.
- **Grafikus felület**: a `pywebview` csomag kell hozzá:

  ```
  pip install pywebview
  ```

  A felület HTML/CSS/JavaScript, de **a Python-alkalmazás saját ablakában, beágyazott webnézetben** jelenik meg. A program nem indít külön böngészőt. A weboldalt a program maga szolgálja ki a `127.0.0.1` címen, internetkapcsolat nem kell.
- A beágyazott webnézethez az operációs rendszer webmotorja kell:
  - Windows: Microsoft Edge WebView2 Runtime (a Windows 10/11 legtöbbször tartalmazza),
  - macOS: beépített WebKit,
  - Linux: GTK vagy Qt webes komponens (lásd a pywebview dokumentációját).

## Fordítás
Nincs fordítási lépés, a `robot.py` közvetlenül futtatható.

Opcionálisan önálló `robot.exe` is készíthető (Windows, PyInstaller):

```
pip install pyinstaller
pyinstaller --onefile --add-data "ui.html;." robot.py
```

(Linux/macOS-en az `--add-data` elválasztója `:`.) A kész `robot.exe` a `dist` mappában keletkezik, és ugyanúgy használható, mint a `python robot.py`.

## Futtatás

### Grafikus IDE

```
python robot.py input_001.txt output_001.txt
```

(Windows alatt a `robot.bat input_001.txt output_001.txt`, Linux/macOS-en a `./robot.sh input_001.txt output_001.txt` is megteszi.)

Az IDE saját ablakban nyílik meg. Kilépni a **Kilépés** gombbal vagy az ablak bezárásával lehet, mindkettő leállítja az alkalmazást. A naplófájl (`output_001.txt`) futás közben folyamatosan frissül.

### Csendes mód (felhasználói interakció nélkül)

```
python robot.py -q input_001.txt output_001.txt
```

Beolvassa a bemenetet, lefuttatja a programot, kiírja a naplófájlt, majd kilép. Ehhez a `pywebview` nem szükséges.

### Sok tesztfájl automatikus futtatása

A mellékelt `run_all.py` minden `input_*.txt` fájlt lefuttat csendes módban, és mellé írja az `output_*.txt` fájlokat:

```
python run_all.py <bemeneti_mappa> [<kimeneti_mappa>]
```

Kimeneti mappa nélkül az outputok a bemeneti mappába kerülnek. Parancssorból a `run_all.py` nélkül is megoldható:

Linux/macOS:

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

Az interpreter regressziós tesztjei: hibakódok, naplóformátum, `else` naplózása, az 1000 soros limit határesete és a szöveg–blokk átalakítás. A tesztek a `robot.py -q` módot hívják, ezért a `pywebview` nélkül is futnak. A `tests/` mappában mintabemenetek és a hozzájuk tartozó naplók vannak.

## Fájlok

| Fájl | Szerep |
|---|---|
| `robot.py` | indító, `-q` mód, a GUI helyi webszervere és a beágyazott ablak |
| `minescript.py` | bemenet-beolvasás, parser, interpreter, naplózás |
| `ui.html` | az IDE felülete: blokkszerkesztő érték-blokkokkal, szöveges nézet, szimulátor, nyomkövetés, kézi vezérlés |
| `run_tests.py` | automata regressziós tesztek |
| `run_all.py` | az összes `input_*.txt` lefuttatása csendes módban |
| `robot.bat`, `robot.sh` | indítóparancsok Windowsra, illetve Linux/macOS-re |