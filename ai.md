# ai.md – mesterséges intelligencia használata

> A csapat saját szavaival érdemes átfogalmazni / kiegészíteni: ez a vázlat azt írja le, ami a fejlesztés során ténylegesen történt.

## Eszköz és modell
- Claude (Anthropic), Claude Sonnet 5.5 modell, a claude.ai chat felületen, fájl- és shell-eszközökkel.

## Mire használtuk, és mekkora részben
- A feladatkiírás (PDF) értelmezése, a nyelvtan és a szemantikai szabályok összegyűjtése.
- A teljes forráskód megírása: `minescript.py` (parser, interpreter, napló), `robot.py` (CLI, helyi szerver), `ui.html` (IDE), `run_tests.py`.
- A programkód nagyjából **egésze** AI segítségével készült; a csapat feladata a felülvizsgálat, a futtatás és a hibák visszajelzése volt.

## Hogyan ellenőriztük és javítottuk
- A feladatkiírás naplópéldáját szó szerint teszttel rögzítettük (`run_tests.py`), és az összes teszt lefut (`python run_tests.py`).
- Minden hibakódhoz, az `else`-naplózáshoz, a térkép széléhez és az 1000 soros limit határesetéhez (pontosan 1000 sor / 1001. sor) külön tesztet írtunk.
- A GUI-t valódi (headless) Chrome-ban, a videó forgatókönyvének lépései szerint próbáltuk végig (blokkok beszúrása, futtatás, nyomkövetés, kézi vezérlés, 8.1–8.4 ideiglenes módosítások), és képernyőképeken ellenőriztük.
- A GUI-ban futtatott program naplóját összevetettük a `-q` móddal kapott naplóval (bájtra azonos).

## 5 konkrét eset
1. **Platformválasztás:** a környezetben nem volt Tkinter, ezért az IDE grafikus felületét helyi weboldalra építettük (a Python-szerver csak a futtatást és a naplófájlt kezeli). Ez sikeres döntés volt, mert a blokkszerkesztő így egyszerűen megvalósítható.
2. **Félreérthető kiírás:** a `step forward n` falba ütközésénél a szöveg alapján a robot a fal elé lép, majd `E_BEDROCK_HIT` hiba keletkezik; ezt feltételezésként kezeltük, és a versenybizottsággal érdemes tisztázni.
3. **AI hibája a tesztekben:** az AI először `while i < 2` alakú teszteket írt, ami a nyelvtan szerint érvénytelen (a feltétel csak egy `simpleval`); a tesztek hibáját a futtatás azonnal jelezte, és `set c to i < 2` + `while c` alakra javítottuk.
4. **Naplószinkron:** gyors futásnál a lépésenkénti naplóírás lemaradt a futástól; a kéréseket összevontuk, hogy mindig a legfrissebb állapot kerüljön a fájlba. Ezt a headless böngészős teszt fedte fel.
5. **Vizuális hiba:** a képernyőképen az if-else blokk fejléce „ifelse”-t írt „if” helyett; ezt a screenshot-ellenőrzés találta meg, és javítottuk.
