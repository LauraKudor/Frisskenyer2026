# ai.md – mesterséges intelligencia használata

## Eszköz és modell
- Claude (Anthropic), Claude Sonnet 5.5 modell
- Gemini, Gemini 3 modell

## Mire használtuk, és mekkora részben
- Grafikus felülethez, útmutatás egy új ötlet megvalósításához
- Tesztesetek generálása program működésének ellenőrzéséhez
- Debugging, errorok értelmezése

## Hogyan ellenőriztük és javítottuk
- Teszteltünk alaposan minden általa írt funkciót
- A grafikus felületen és a -q módban futtatott program naplóját összevetettük, a kettő egyezik.
- A kisebb hibákat manuálisan átírtuk, a nagyobbaknál megkértük, hogy változtasson

## 5 konkrét eset
1. **Platformválasztás:** a felületet először helyi weboldalként építettük, amit a program a böngészőben nyitott meg. Ezután átálltunk pywebview-ra, a belső logika és a felület HTML-je maradt. Így az interpreter Pythonban marad, a felület pedig a kiírásnak megfelel.
2. **Érték-blokkok:** az AI először egy legördülő listával oldotta meg a set jobb oldalát. Ezt valódi, sárga érték-blokkokra cseréltük (⟨simpleval⟩ mezők, 14 blokkforma, csak a set után ágyazható)
3. **Sebesség:** A felhasználó kiválaszthatja, hogy mekkora sebességgel fusson le a program, amit blokkokkal elkészített. Ötletünk implementálására használtuk az AI-t.
4. **Sok teszteset automatikusan:** Automatizálás elkészítése, hogy a csendes módban le tudjuk futtatni majd a 200 tesztesetet egyszerre
5. **GUI:** A frontend fejlesztés nem az erősségünk, ezért besegített ennek a felületnek a megvalósítására, megértésére és megtanulására
