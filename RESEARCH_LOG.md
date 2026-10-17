# Kutatási és fejlesztési napló

Ez a napló a később összeállítandó szakdolgozat háttéranyaga. A kutatás és fejlesztés fontos döntéseit, forrásait, kísérleteit, eredményeit és korlátait őrzi meg. Nem kész dolgozatszöveg.

## 2026-09-19 – A munkamenet rögzítése

- Mérföldkő: előkészítés, a négy mérföldkő megkezdése előtt.
- Felhasználói döntés: először a négy mérföldkő kutatási és fejlesztési munkáját végezzük el, a szakdolgozat dokumentumát csak utána állítjuk össze.
- A kutatás és fejlesztés során minden, a dolgozat szempontjából fontos információt folyamatosan rögzíteni kell.
- Aktuális állapot: a követelmények, témaadatok és a munkamenet rögzítve az `AGENTS.md` fájlban. Kutatás, fejlesztés és tesztelés még nem kezdődött el; a felhasználó kifejezetten kérte, hogy még ne fejlesszünk.
- Forrás: a felhasználó jelen beszélgetésben megadott utasítása.

## 2026-09-19 – M1 engedélyezése és felhasználói válaszok

- Mérföldkő: 1.
- A korábbi várakozást felülírja a felhasználó engedélye: az első mérföldkő kutatási és környezet-előkészítési munkája elkezdhető.
- A felhasználó elfogadta a helyi Python-alapú, fizetős szolgáltatás nélküli előkészítést; nincs technológiai megkötés vagy megadott meglévő kód.
- A vizsgálati célpont még nincs eldöntve. A forráskód-elemzés egyelőre a témakiíráshoz igazodó telepítési próba, nem végleges termékirány.
- A saját modell tanításának követelményét a felhasználó még nem egyeztette a témavezetővel.
- Szakdolgozati jelentőség: a rendszer tényleges AI-hozzájárulását és az arról tehető állításokat ehhez kell igazítani. A kész modell alkalmazása, a saját modell tanítása és a scanner-kimenet összefoglalása különböző feladatok.
- Forrás: jelen beszélgetés és a felhasználó három kérdésre adott válasza.

## 2026-09-19 – M1 szakirodalmi és technológiai áttekintés

- Állapot: kezdeti áttekintés elkészült, nem szisztematikus teljességű irodalomkutatás.
- Hét kutatási cikk, egy NIST benchmarkkiadvány és kilenc hivatalos technikai forrás került a `research/SOURCES.md` jegyzékbe. Minden tételnél elérhetőség, hozzáférési dátum és feldolgozási mélység szerepel.
- Hazai kutatás: Viszkok Tamás, Hegedűs Péter és Ferenc Rudolf JavaScript-sérülékenység-előrejelzésről szóló tanulmánya (R03). Angol nyelvű, szegedi intézményi kötődésű kutatás.
- Kutatási tanulságok és saját következtetések elkülönítve a `research/MILESTONE_1.md` és `research/SOURCES.md` fájlokban. Fő későbbi vizsgálati szempontok: címkék megbízhatósága, adatszivárgás, téves riasztások, sérülékeny/javított párok és az AI hozzáadott értékének elkülönítése.
- A hibrid, statikus elemzésre épülő segédeszköz javasolt irány, nem elfogadott architektúra. CodeQL és ZAP összehasonlítási jelölt; Ollama és egy kódorientált Qwen-modell lehetséges későbbi helyi modellmegoldás. Ezek nincsenek telepítve vagy kipróbálva.
- Korlát: több cikkből egyelőre az absztrakt és a bibliográfiai adatok kerültek feldolgozásra; a megvalósításba bevont módszerek további részletes olvasást igényelnek.

## 2026-09-19 – M1 környezet és telepítési ellenőrzések

- Állapot: megvalósított környezet, méréssel ellenőrzött telepítési működés; termékfejlesztés és AI-kísérlet még nincs.
- Környezet: projektlokális `.venv`, uv 0.10.11, CPython 3.11.13, pontos csomagverziók a `uv.lock` fájlban. A gépen lévő Python-könyvtárak neve nem minden esetben felelt meg a futtatott verziónak, ezért explicit verzióválasztást alkalmaztunk.
- Telepítve: Bandit 1.9.4, Semgrep 1.177.0, HTTPX 0.28.1, Pydantic 2.13.5, scikit-learn 1.9.1, pytest 9.1.1, Ruff 0.16.8 és tranzitív függőségeik; összesen 81 csomag.
- A függőségellenőrzés sikeres. Az HTTPX, Pydantic és scikit-learn importja, valamint egy minimális numerikus művelet működött. Ez nem modellpontossági kísérlet.
- Hardver és környezetmegfigyelések: `artifacts/m1/environment.json`. NVIDIA GeForce RTX 4070, a gyártói segédeszköz szerint 12 282 MiB memória. GPU-s modellfuttatás nem történt.
- Tesztadat: három saját, szintetikus Python-forrásminta a `tests/fixtures/` alatt; a veszélyes kódrészletet nem futtatjuk. Egy direkt eval-hívás, egy literálfeldolgozásra módosított változat, valamint csak szövegben és kommentben szereplő eval-említés.
- Módszer: Bandit B307 és egy helyi Semgrep-szabály, elemzőnként három próba; kilépési kód, JSON, hibák hiánya, ténylegesen vizsgált fájl, találatszám, szabályazonosító és a pozitív eset sorszáma ellenőrizve.
- Eredmény: mind a hat ellenőrzés sikeres. Az első futás 6,85 s; a tesztkód formázását és UTC-kezelését követő végső futás 6,33 s. Ezek környezetellenőrzési idők, nem általános teljesítményeredmények.
- Első bizonyíték: `artifacts/m1/20260919T105807365784Z/`. Végső bizonyíték: `artifacts/m1/20260919T110250501158Z/`, benne nyers kimenetekkel, parancsokkal, időkkel, csomagverziókkal, bemeneti SHA-256 hash-ekkel és a `pytest.xml` összesítővel.
- Ruff végső ellenőrzése sikeres. Egy kezdeti UTC-stílusjelzést javítottunk. Telepítéskor a hardlink helyett másolás történt, sikeresen; a Semgrep súgó formázási figyelmeztetést adott, a tesztelt scanek nem jelentettek feldolgozási hibát.
- Szakdolgozati jelentőség: a későbbi kísérletekhez reprodukálható alap és ellenőrizhető nyomvonal készült. A hat sikeres telepítési próba nem bizonyít általános sérülékenység-felismerési pontosságot vagy működő AI-asszisztenst.
- M1 átadás: `README.md`, `research/MILESTONE_1.md`, `research/SOURCES.md`. A második mérföldkő előtt tisztázandó a célpont és a modell tanításával kapcsolatos elvárás. A szakdolgozat szövege továbbra sem készült el és nem kezdődött meg.

## 2026-09-19 – M2 irányválasztás és engedélyezés

- A felhasználó a forráskód elemzését választotta, és jelenleg nem szeretne saját modellt tanítani. Kérésére a második mérföldkő a következő heti témavezetői beszélgetés előtt elkészült.
- A Python mint célnyelv az asszisztens módosítható munkafeltételezése. A forráskód-elemzés és a kész modell használata felhasználói döntés; a témavezető jóváhagyása még nincs meg.
- A módosíthatóság érdekében külön elemzőkapcsolat, találatformátum, modellkapcsolat és tesztadat-kezelés készült. A nagyobb irányváltás (saját modell tanítása, dinamikus webes vizsgálat) ütemezési következményét nem szabad elhallgatni.
- Döntések és kapcsolódó bizonyítékok: `research/MILESTONE_2.md`.

## 2026-09-19 – M2 komponensek, tesztanyagok és tényleges modellkapcsolat

- Megvalósított: forráskönyvtáron belüli fájlellenőrzés; Bandit- és Semgrep-adapter; szigorú találat- és jelentésformátum; helyi Ollama-kapcsolat strukturált válasszal; diagnosztikai adatátadási próba.
- Modell: qwen2.5-coder:7b, 7.6B, Q4_K_M, 4 683 087 561 bájt. Digest: `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364`. Runtime: Ollama 0.34.2, hivatalos archívum SHA-256 ellenőrzésével telepítve. Saját modell tanítása nem történt.
- A szerver projektindítással, háttérben, kizárólag 127.0.0.1:11435 címen fut; a cloud funkciók letiltva. Rendszerszolgáltatás és PATH-módosítás nem készült. A modellcsomag adatai és licence: `artifacts/m2/model-install.json`.
- Adatok: 18 saját szintetikus forrásminta (6 javasolt sérülékeny, 6 páros javítás, 6 kontextusfüggő negatív kontroll), három CWE-családdal, egyedi hash-ekkel és címkeindoklással. Emberi felülvizsgálat még nincs; a minták fejlesztési adatok.
- További előkészítés: 12 magyar/angol kéréshelyzet. Ezek specifikációk, nem sikeresen teljesített természetesnyelv-feldolgozási tesztek.
- Fontos későbbi mérési követelmény: a végső tesztadat legyen új és külön ellenőrzött; a fájlnevek, címkék és metaadatok ne árulják el a modellnek a helyes választ.

## 2026-09-19 – M2 hibakezelési felismerés és javítás

- Az első futásban 39 teszt sikeres, 1 sikertelen: a Semgrep 1.177.0 a `def broken(:` forrásra sikeres, üres találati listát adott a használt beállítások mellett.
- Nyers bizonyíték: `artifacts/m2/investigations/semgrep-invalid-syntax-before-fix.json`; első tesztjegyzőkönyv: `artifacts/m2/investigations/initial-failing-tests.xml`.
- Javítás: az elemzők előtt külön Python 3.11 szintaktikai ellenőrzés. Érvénytelen vagy e verzió által nem támogatott szintaxis esetén az eredmény sikertelen elemzés, nem üres, sikeres jelentés.
- Végső tesztfutás: 40 sikeres ellenőrzés, 10,94 s; Ruff sikeres. Az előző állítás erre a konkrét verzióra és tesztbemenetre vonatkozik, nem minden Semgrep-használatra.
- Szakdolgozati jelentőség: az eszköz hibás vagy részleges feldolgozását külön kell választani a valódi negatív eredménytől.

## 2026-09-19 – M2 integrációs eredmények és korlátok

- Futás: `artifacts/m2/20260919T111932119119Z/`. A 18 fejlesztési mintán mindkét elemző lefutott, összesen 36 sikeres feldolgozás.
- Nyers megfigyelés: Bandit 10 mintán, a három helyi Semgrep-szabály 8 mintán jelzett. Mindkettő kihagyta az aliasváltozóval hívott eval-példát, és több negatív kontrollon is riasztott. A konkatenált SQL-példát Bandit jelezte, a szűk Semgrep-szabály nem. A címkéket nem igazítottuk a kimenetekhez.
- Ezek nem független benchmarkeredmények, és nem a teljes szabálykészletek tisztességes összehasonlítása. M4-ben külön, előre meghatározott protokoll kell a pontossági állításokhoz.
- A valódi helyi modell egy Bandit-találat metaadatait kapta, és pontosan visszaigazolta annak azonosítóját és az eszköz nevét. Ez az adatkapcsolatot igazolja; érdemi sérülékenység-értékelés, magyarázat vagy természetesnyelv-vezérlés még nem készült.
- A diagnosztikai modellhívás beállításai: 4096 kontextus, 0 hőmérséklet, 0 seed, 256 kimeneti tokenkorlát. Jelentett teljes idő 33,17 s, ezen belül betöltés 18,17 s; egy hideg próba, nem teljesítménybenchmark.
- A bemeneti hash-ek, pontos csomagverziók, parancsok, nyers kimenetek, modellazonosító, kérés/válasz és idők a futási könyvtárban vannak.
- Elkészült az angol M2-terv és a magyar témavezetői egyeztető. A szakdolgozat fejezeteit továbbra sem írjuk; M3 és M4 még hátravan.
- Záráskor a modellkiszolgáló leállító segédje a JSON-ból automatikusan dátummá alakított időbélyeg miatt téves azonosítási eltérést jelzett. UTC tick-alapú összehasonlításra javítottuk; a folyamatútvonal és PID ellenőrzése megmaradt. A javítás után a leállítás–indítás–leállítás próba sikeres. Az előző segédváltozat az `artifacts/m2/investigations/` alatt megőrizve; a szerver átadáskor nem fut.

## 2026-10-17 – Projektátadás másik chatnek

- A felhasználó a teljes projekt másik chatben használható átadását kérte, majd pontosította, hogy ZIP nem kell, mert ugyanebben a mappában folytatja a munkát.
- Elkészült a `CHAT_HANDOFF.txt`: a beszélgetés összefoglalója, olvasási sorrend, döntések, kész és hiányzó funkciók, bizonyítékok, futtatási tudnivalók és a szeptember 26-án javasolt témavezetői kérdések teljes témalistája.
- Témavezetői válasz vagy új fejlesztési engedély még nem érkezett. A régi „jövő héten” hivatkozásokat nem tekintjük új határidőnek.
- A forráskód, modell, függőségek és eredmények helyben maradtak. Export céljából fejlesztés, modellindítás vagy új tesztfutás nem történt; a 40 teszt és 36 mintavizsgálat eredménye továbbra is a szeptember 19-i futásra vonatkozik.

## A későbbi bejegyzések mintája

Az alábbi mezőket a tényleges tevékenységhez igazítsd; ami nem alkalmazható, elhagyható.

- Dátum és rövid cím:
- Kapcsolódó mérföldkő:
- Tevékenység / kérdés:
- Állapot: terv, hipotézis, megvalósítás vagy ellenőrzött eredmény.
- Megállapítás / döntés és indoklása:
- Mérlegelt alternatívák, ha voltak:
- Források / bizonyítékok: bibliográfiai adatok, dokumentum-URL vagy DOI, hozzáférési dátum; illetve helyi fájl vagy verziókezelési hivatkozás.
- Kísérlet / teszt esetén: adatok és eredetük, módszer, eszköz-/modellverzió, beállítások, mérőszámok, tényleges eredmények és reprodukálási körülmények.
- Korlátok, hibák, sikertelen próbálkozások és javítások:
- Jelentőség a szakdolgozat számára:
- Nyitott kérdések / következő lépések:
