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

## 2026-10-17 – Új chat: M1–M2 kritikai felülvizsgálata

- Mérföldkő: M2 utóellenőrzés, M3 előtt. Állapot: **javaslatok, nem elfogadott döntések**; a felhasználó és a témavezető dönt.
- Módszer: a dokumentumok, a `src/`, `rules/`, `data/m2/`, `scripts/` forrásának átolvasása. Új tesztfutás nem történt: az asszisztens felhőkörnyezetéből a PyPI nem volt elérhető, a felhasználó gépén pedig nem volt parancsfuttatási lehetőség. A 40/36-os eredmények továbbra is a 09-19-i futásra vonatkoznak.
- Megerősített, jó döntések: hibrid (determinisztikus elemző + előre betanított helyi modell) irány; `completed`/`failed` szétválasztása; nyers bizonyítékok és hash-ek megőrzése; loopback-only, sémavalidált modellkapcsolat; az eredeti találatok megőrzése a modellítélettől külön; elemző önmagában vs. elemző + AI összehasonlítási terv; címkeszivárgás és fejlesztési/végső adat elkülönítésének felismerése.
- Gyengeségek / javaslatok:
  1. Verziókezelés hiányzik: a projektmappában nincs `.git`, bár a dokumentáció Gitre hivatkozik. Javaslat: `git init`, első commit, privát távoli tároló vagy más mentés.
  2. Az alapvonal szándékosan szűk (3 Bandit-teszt, 3 mintaalapú Semgrep-szabály). Az „AI javít” állítás így szalmabáb-összehasonlítás kockázatát hordozza. Javaslat: legalább egy erősebb alapvonal – teljes Bandit-tesztkészlet CWE-szűréssel, és/vagy Semgrep `mode: taint` szabályok forrás → nyelő → sanitizer (`int(...)`) leírással. A Semgrep dokumentációja szerint a taint mód CE-ben függvényen belüli; a függvények és fájlok közötti követés Pro-funkció. A kontextusfüggő negatív kontrollok egy részét (pl. `int()` utáni SQL) egy taint-szabály már determinisztikusan kezelheti; ezt mérni kell, nem feltételezni.
  3. Az AI hozzájárulásának mérhető magja legyen a scanner-találatok **téves riasztás-szűrése / triázsa** (igaz vs. hamis pozitív, indoklással és bizonytalansággal); ez illeszkedik a témakiírás „gépi tanulási módszerek … felismerés” megfogalmazásához (vö. R05 IRIS kontextuális riasztásértékelés). A természetes nyelvű vezérlés és a magyarázat másodlagos, külön mért cél.
  4. Modell: qwen2.5-coder:7b (2024 végi kiadás) a kapcsolati próbára megfelelő, de a triázs-kísérlethez érdemes 2–3 helyi modellt összevetni, pl. Qwen2.5-Coder 14B és Qwen3 14B (Q4 kb. 9 GB, 12 GB VRAM-on futhat). A Qwen3-Coder 30B-A3B kb. 19 GB, csak részleges CPU-kiszervezéssel. Forrás: bestllmfor.com, 12 GB VRAM-ajánló (2026-09-29-i frissítés, hozzáférés 2026-10-17); ez nem minőségi rangsor, helyben mérni kell.
  5. Modellbeállítások M3-hoz: a `num_ctx 4096` / `num_predict 256` / `keep_alive 0` a kézfogáshoz jó, triázshoz kevés (forráskontextus + indoklás), sorozatfuttatásnál pedig a betöltés (kb. 18 s) minden hívásnál ismétlődne. A sémában az indoklás mező álljon az ítélet előtt.
  6. Végső tesztadat: független, valós eredetű Python-minták kellenek. Jelölt: VUDENC (Wartschinski és mtsai., Python, GitHub-javítócommitok, többek közt 406 SQL-injekciós és 106 parancsinjekciós commit; automatikus, zajos címkék). Forrás: https://arxiv.org/abs/2201.08441, hozzáférés 2026-10-17. További jelöltek (ellenőrizendők, még nem olvasottak): CVEfixes, SecurityEval, OWASP PyGoat. A licencet és a címkeminőséget ellenőrizni kell (vö. R04 PrimeVul).
  7. Az egyfájlos, fájlonként külön folyamatot indító elemzés valós projektekre lassú, és elveszíti a fájlok közötti kontextust. M3-ban könyvtárszintű futtatás és találatleképezés javasolt.
  8. A scikit-learn telepítve van, de nincs használva. Megtartása akkor indokolt, ha a kiértékelési metrikákhoz vagy egy esetleg előírt kis tanított triázs-alapvonalhoz kell (ha a témavezető ML-tanítást vár, ez a legolcsóbb tartalékterv).
- Ütemezési kockázat: a témavezetői válasz 09-26 óta nincs rögzítve; a scope-ot leginkább befolyásoló kérdés az, hogy elfogadható-e az előre betanított modell saját tanítás nélkül.
- Források: https://docs.semgrep.dev/writing-rules/data-flow/taint-mode/overview.md ; https://arxiv.org/abs/2201.08441 ; https://bestllmfor.com/best/vram-12gb/ – mind 2026-10-17-i hozzáférés.

## 2026-10-17 – Témavezetői válaszok és következményeik

- Mérföldkő: M2 lezárása, M3 előkészítése. M3/M4 indítására külön felhasználói engedély még nem érkezett.
- Forrás: a felhasználó 2026-10-17-i üzenete, amelyben közölte Girászi Tamás témavezető válaszait. Az egyeztetés dátuma és formája nincs megadva, írásos dokumentum nem áll rendelkezésre. A kérdéseket a felhasználó fogalmazta meg (a 09-26-i javaslatlista alapján).
- A felhasználó által közölt válaszok, szó szerint:
  1. Saját modell tanítása: „Teljesen megfelel, nem írtunk elő olyat, hogy saját modellt kell tanítani.”
  2. Új felismerési módszer: „Szerintem nem szükséges, ilyen követelményt sem fogalmaztunk meg.”
  3. Python + három hibacsalád: „Persze, de szükség esetén én is tudok biztosítani olyan példákat, amelyeken tesztelni lehet a rendszert.”
  4. Az AI scope-ja: „Elsősorban a hibák felismerése és azok magyarázata a fontos. Ha prioritási sorrendet kell felállítani, akkor az a következő: hibák felismerése > magyarázat adása > nyelvi vezérlés > téves detektálások felismerése.”
  5. Összehasonlítás és mérés: „Ez egy kulcsfontosságú pont. A pontosság (accuracy), a precision és a recall metrikák elegendőek lesznek az értékeléshez.” (A kérdés: elemző vs. ugyanaz az elemző + AI.)
  6. Tesztadat: „A saját példaprojekt teljesen elegendő lehet. Egy teljes, például webalkalmazás-projekt bemutatása nem is feltétlenül szükséges. Elég egy kisebb kódrészlet vagy funkcionális egység, amelyen keresztül demonstrálható, hogy a rendszer felismeri a hibát, és megfelelő magyarázatot ad rá.”
- Megerősített keret (témavezetői válasz): előre betanított modell saját tanítás nélkül; a hozzájárulás a tervezés, megvalósítás és kiértékelés meglévő eszközökkel; Python és CWE-95/78/89 mint célterület; az összehasonlítás elemző vs. elemző + AI; kötelező mérőszám: accuracy, precision, recall; saját, kisebb példák elegendők.
- Tervezési következtetések (javaslat, nem jóváhagyott döntés):
  - **Felülírja az előző bejegyzés 3. javaslatát.** Ott a téves riasztások szűrését javasoltam az AI mérhető magjának; a témavezetői prioritás szerint ez a legutolsó. Az AI-nak a **felismeréshez** kell közvetlenül hozzájárulnia: a modell maga is vizsgálja a kódegységet a három hibacsaládra, és találatai az elemző találataival egyesítve, forrásmegjelöléssel kerülnek a jelentésbe. Mérhető várakozás (hipotézis): elsősorban a recall nőhet (pl. az alias-eval típusú esetek), a precision romolhat – ezt mérni kell.
  - A magyarázat a második cél. Mérőszámot a témavezető nem adott; javasolt egyszerű, előre rögzített ellenőrzőlista (helyes CWE, helyes sor, a bemenet útja, javítási irány), amelyet a felhasználó kézzel pontoz, nem a modell.
  - A természetes nyelvű vezérlés harmadik: minimális parancssoros, magyar/angol kérésértelmezés a 12 előkészített kéréshelyzet mint elfogadási teszt alapján.
  - A téves riasztások külön felismerése nem önálló fejlesztési cél; a precision mérőszám ettől függetlenül megmutatja a hamis pozitívok hatását.
  - Mérés: accuracy, precision, recall, a konfúziós mátrix darabszámaival (TP/FP/TN/FN) és nevezőkkel. Az accuracy érzékeny az osztályarányra, ezért a tesztkészlet legyen kiegyensúlyozott (sérülékeny / javított / kontroll). Az időigény olcsón naplózható kiegészítő adat; formális használhatósági vizsgálatot a témavezető nem kért.
  - Tesztadat: a `data/m2/` 18 mintája fejlesztési adat marad (címkeszivárgás, a fejlesztést befolyásolta). Új, előre címkézett, semleges fájlnevű, a rendszer futtatása előtt lezárt tesztkészlet szükséges. A legerősebb független forrás a témavezető által felajánlott példák lennének – javasolt elkérni. Külső adatkészlet (pl. VUDENC) a válasz alapján nem szükséges, legfeljebb opcionális.
  - Mivel a felismerés a fő cél, a modellválasztás súlya nő: javasolt a jelenlegi 7B és egy 14B helyi modell összevetése, ismételt futtatással (stabilitás).
- Nyitott: M3 engedélyezése; elkérjük-e a témavezető példáit; a végső tesztkészlet mérete; a magyarázat pontozásának végleges módja.

## 2026-10-17 – M3 engedélyezése, kódfelülvizsgálat és megvalósítás

- Mérföldkő: 3. A felhasználó engedélyezte M3-at, előtte a meglévő kód felülvizsgálatát kérte. M4 nem engedélyezett.
- Állapot: **megvalósítva, a célgépen még nem ellenőrizve.** Részletek: `research/MILESTONE_3.md`.
- Kódfelülvizsgálat – ellenőrizhető hibák a rögzített M2-bizonyítékban:
  - A Bandit az eval-hívásra (B307) CWE-78-at jelent (`artifacts/m2/20260919T111932119119Z/bandit-eval_direct_bad.json`); hibacsaládonkénti méréshez saját, szabályazonosító-alapú hozzárendelés kell. Javítva: `Finding.family`.
  - A Semgrep-szabályazonosító az abszolút útvonalat és a Windows-felhasználónevet tartalmazta; a találatazonosító gépfüggő volt. Javítva: normalizálás. Következmény: az új futások Semgrep-azonosítói eltérnek az M2-ben rögzítettektől, a találatszám és a szabály nem.
  - A modellhívás 33,17 s-ából 18,17 s betöltés volt, a modell 29/29 rétege GPU-n futott (`runtime-gpu-excerpt.txt`); a hívásonkénti kiürítés okozta a hidegindítást. Javítva: hívástípusonkénti, rögzített beállítások.
  - További tervezési hiányok: szűk Bandit-tesztkör, mintaalapú Semgrep-szabályok, csak egyfájlos cél, egybefésült elemzőkód, nincs verziókezelés. Mindegyikre megoldás készült (lásd MILESTONE_3 táblázat).
- Megvalósított M3-elemek: teljes Bandit + saját CWE-leképezés; Semgrep taint-szabályok (`rules/m3_python_taint.yml`); modellalapú felismerés és magyarázat fájlonként egy hívásban; forráshoz kötés-ellenőrzés (a modellnek pontos kódrészletet kell idéznie a megadott sorból); unió-alapú összefésülés (a modell nem törölhet elemzői találatot); fix szövegezésű magyar/angol összefoglaló; szabályalapú és modellalapú kérésértelmező közös, determinisztikus védőkorlátokkal; parancssori felület (`python -m vuln_assistant analyse|ask`), előző jelentés megőrzése a „magyarázd el az előző találatot” kérésekhez; esetszintű accuracy/precision/recall számítás darabszámokkal, scikit-learn keresztellenőrzéssel.
- Mérlegelt alternatívák: (1) a modell csak téves riasztás-szűrő – elvetve, a témavezetői prioritásban utolsó; (2) külön magyarázóhívás találatonként – elvetve a késleltetés miatt; (3) a modell elvetheti az elemzői találatot – nem alapértelmezés, legfeljebb M4-es összehasonlító változat.
- Tudatos korlátok: a jelen összefésülési szabály mellett az AI a recallt növelheti, a precisiont nem; a forráshoz kötés nem ellenőrzi a hibacsalád helyességét; a modell nem kapja meg a fájlnevet (címkeszivárgás elkerülése); a promptinjekció ellen a határolás, séma, forráshoz kötés és unió csak korlátozó, nem teljes védelem.
- Címkeszivárgás és illesztés: a szabályalapú értelmező a 12 fejlesztési kéréshelyzet ismeretében készült, ezeken 12/12 a fejlesztői próbán – ez nem független eredmény. A felülvizsgálati promptból kivettem egy, a fejlesztési kontrollesethez túl közel álló mondatot (beépített név felülírása).
- Ellenőrzés eddig: Ruff sikeres; a tiszta logikai részek és a teljes folyamat szimulált modellel lefutott az asszisztens felhőkörnyezetében (Python 3.13, Pydantic 2.13.5). Valódi Bandit/Semgrep/Ollama-futás nem történt: a felhőkörnyezetben a csomagtároló tiltott, külső forráskód futtatását a rendszer letiltotta, a felhasználó terminálja pedig csak olvasható/kattintható jogosultságú. Ezért készült a `scripts/m3_check.ps1` egyparancsos ellenőrzés.
- Verziókezelés: git-előzmény rekonstruálva (M1–M2 kiinduló pillanatkép → témavezetői visszajelzés dokumentumai → M3), `scripts/init_git.ps1` hozza létre a tárolót a gépen.
- Szakdolgozati jelentőség: a mérési egység (fájl a címkézett hibacsaládra), a feltételek (elemzők vs. elemzők + modell) és a forráshoz kötés mint hallucináció-korlát a módszertani fejezet alapja lehet.
- Következő lépés: a felhasználó lefuttatja az ellenőrző szkriptet; az eredmények új naplóbejegyzésbe kerülnek.

## 2026-10-17 – M3 első futás a célgépen (fejlesztési eredmények)

- Mérföldkő: 3. Állapot: **mért fejlesztési eredmény** a 18 fejlesztési mintán – nem végső, független kiértékelés (a minták, a szabályok és a promptok a fejlesztést befolyásolták).
- Futtatás: a felhasználó indította a `scripts/m3_check.ps1`-et (Windows, CPython 3.11.13, Bandit 1.9.4, Semgrep 1.177.0, Ollama 0.34.2, qwen2.5-coder:7b; a digest futáskor ellenőrizve: `dae161e2…f4364`). Beállítások: num_ctx 8192, num_predict 2048, temperature 0, seed 0, keep_alive 10m, magyar magyarázatnyelv, 3 ismétlés.
- Első kísérlet (`artifacts/m3/check-20261017T102331Z/`): git, Ruff, pytest és M2-reprodukció sikeres, utána elakadt. Ok: a modellszerver-indító lépés kimenetét csővel gyűjtöttük, a háttérben induló `ollama.exe` örökölte a csőleírót, ezért a lépés sosem ért véget (a szerver 12:25:03-kor rendben elindult). Javítás: a szerver indítása/leállítása cső nélkül (commit „m3_check: start/stop model server outside the output pipe”). A felhasználónak az ablakot be kellett zárnia, mert a Ctrl+C nem hatott.
- Második, teljes futás: `artifacts/m3/check-20261017T104137Z/` – minden lépés 0 kilépési kóddal.
  - Git: tároló létrehozva (M1–M2 kiindulás → témavezetői dokumentumok → M3 → bizonyítékfájlok commitja).
  - Ruff sikeres; **pytest 88/88** (37,6 s), kihagyás nélkül; a taint-szabályok tervezett viselkedését a valódi Semgrep igazolta.
  - **M2-reprodukció:** mind a 36 elemzés állapota és találatszáma azonos a 2026-09-19-ivel (`artifacts/m2/20261017T102414455218Z/`).
- Fejlesztési mérés (`dev/metrics.json`, `dev/predictions.csv`; egység: fájl a címkézett hibacsaládra; 6 sérülékeny, 12 nem sérülékeny; scikit-learn keresztellenőrzés minden feltételre egyezett):

  | Feltétel | TP | FP | TN | FN | Accuracy | Precision | Recall |
  |---|---|---|---|---|---|---|---|
  | m3: Bandit (teljes) | 5 | 5 | 7 | 1 | 0,667 | 0,500 | 0,833 |
  | m3: Semgrep taint | 5 | 1 | 11 | 1 | 0,889 | 0,833 | 0,833 |
  | m3: Bandit ∪ Semgrep | 5 | 5 | 7 | 1 | 0,667 | 0,500 | 0,833 |
  | m3: Bandit ∪ Semgrep + modell (×3, azonos) | 6 | 9 | 3 | 0 | 0,500 | 0,400 | 1,000 |

  - A modell hozzáadott egy valódi találatot (aliasos eval, amit mindkét elemző kihagyott), és 4 új téves riasztást: `ast.literal_eval` (eval_direct_fixed), csak szövegben szereplő parancs (shell_text_control), kötött paraméteres SQL-lekérdezés (sql_direct_fixed, sql_concat_fixed). A többi 5 téves riasztást már a Bandit is jelezte. Összegezve: recall 0,833 → 1,000, precision 0,500 → 0,400, accuracy 0,667 → 0,500.
  - A 3 ismétlés azonos előrejelzést adott (0 instabil eset), 0 modellhiba, 0 forráshoz nem köthető állítás (a forráshoz kötés-ellenőrzés egyszer sem lépett működésbe), 0 elvetett elemzői találat. Időigény: medián 3,85 s/fájl, az első (hideg) hívás 41,2 s.
  - Megfigyelés: a téves pozitívoknál a modell indoklása tartalmilag hibás (például a paraméteres lekérdezést „közvetlen beillesztésnek” nevezi). Az elemzés és indoklás magyarul készült, mert a magyarázatnyelvet a teljes válaszra alkalmaztuk; hipotézis, hogy angol nyelvű indoklással a 7B modell pontosabb (nem mért).
  - A Semgrep taint-szabályok a fejlesztési mintán messze a legjobb elemzők, de a CWE-szemantika alapján, a fejlesztési minták ismeretében készültek – az előny végső igazolása M4-feladat.
- Kéréshelyzetek (`requests/results.json`): szabályalapú értelmező 12/12 (a helyzetek ismeretében írva); modellalapú értelmező 12/12 művelet, 9/12 minden mező. Hibák: kétszer hibás/hiányzó nyelv (alapértékként „hu” került be, illetve magyar kérésre „en”), egyszer a fájlnévből (`sql_integer_control`) vett hibacsalád-szűrés, bár a prompt ezt tiltotta. Meleg modellnél 0,4–0,7 s/kérés.
- Bemutató (`demo/transcript.txt`): a teljes természetes nyelvű folyamat működik (elemzés → „magyarázd el az előző találatot” → mappa szűréssel → törlési kérés elutasítása). A magyar szövegek érthetők, de nyersek („untrusted data” fordítatlanul), és vannak tartalmi hibák: sqlite-hoz `%s` helyőrzőt javasol `?` helyett, illetve konstans parancsnál nem releváns javítást ad.
- Szakdolgozati jelentőség: ez a fejlesztési mérés már most is azt mutatja, hogy a témavezetői prioritás (felismerés, azaz recall) és a precision között a jelenlegi kis modellnél kompromisszum van. Ez dokumentálandó eredmény, nem elrejtendő.
- Javasolt következő fejlesztési kör (döntésre vár): determinisztikus nyelv- és szűrésellenőrzés a kérésértelmezőben; angol nyelvű indoklás, csak a magyarázat a felhasználó nyelvén; kétlépéses „javaslat → ellenőrzés” a csak modell által jelzett találatokra (vö. R07 VulAgent); nagyobb helyi modell összevetése (pl. qwen2.5-coder:14b, kb. 9 GB letöltés, a felhasználó engedélyével); az elemzőréteg (Semgrep-taint vs. unió) M4 előtti rögzítése indoklással.

## 2026-10-17 – M3 második fejlesztési kör (megvalósítva, futtatásra vár)

- Mérföldkő: 3. A felhasználó jóváhagyta az előző bejegyzés öt javaslatát, beleértve a nagyobb helyi modell letöltését. Állapot: **megvalósítva, helyben tesztelve szimulált modellel; a célgépi futás még hátravan.**
- Változtatások és indokuk:
  1. Kérésértelmezés: a nyelvet mindig determinisztikusan, a kérés szövegéből állapítjuk meg; a modell által javasolt hibacsalád-szűrést csak akkor fogadjuk el, ha a kérés szavai (a fájlnevek nélkül) alátámasztják. Ok: az első futás három mezőhibája. Bővített kulcsszavak: adatbázis, lekérdezés, operációs rendszer, kódbefecskendezés.
  2. Az áttekintő hívás az elemzést és az indoklást angolul írja, csak a bemenetforrás, a magyarázat és a javítás készül a felhasználó nyelvén. Hipotézis: a 7B modell angolul pontosabban érvel (mérendő). A prompt kéri, hogy a javítás az adott könyvtár API-ját kövesse (pl. az adatbázis-meghajtó helyőrzőjét).
  3. Kétlépéses ellenőrzés: a csak modell által jelzett (elemzői találathoz nem kötődő) állítást egy második, fókuszált hívás vizsgálja (nyomkövetés → attacker_controlled → reaches_dangerous_operation → neutralised → verdict). Csak akkor lesz belőle találat, ha a döntés és minden válasz összhangban van. Az eredeti indoklást az ellenőrző nem kapja meg (horgonyhatás elkerülése). Az ellenőrzés hibája láthatóvá teszi a jelentés hiányosságát. Szakirodalmi motiváció: hipotézis–validáció (R07 VulAgent), forrásállítás és saját megvalósítás elkülönítve.
  4. Modell-összevetés: qwen2.5-coder:7b és qwen2.5-coder:14b azonos beállításokkal. A kontextusméret hívásonként a legkisebbre igazodik (4096/8192/16384), hogy a 14B modell elférjen a 12 GB VRAM-ban. A letöltőszkript paraméterezve, a már telepített modellt nem tölti le újra; az azonosítót `artifacts/m3/model-install-*.json` rögzíti.
  5. Elemzőréteg: a mérés mindkét változatot futtatja (Bandit ∪ Semgrep, illetve csak Semgrep), mindegyiket a saját találataival tippként adva a modellnek. Ablációként a verifikáció nélküli változat is fut. A végleges „AI nélküli” alap kiválasztása ennek a futásnak az eredménye alapján, M4 előtt történik.
- Fontos módszertani megjegyzés: a 2. és 3. pont promptszövegei (például „a kötött paraméter nem része az SQL-szövegnek”, „a literálként értelmezett érték nem fut le”) CWE-definíciós tudást írnak le, de az első futás fejlesztési téves pozitívjai után kerültek be. Ezért a második kör fejlesztési eredményei optimisták; a javulás csak független, előre lezárt adaton (M4) igazolható.
- Egyéb: az ellenőrző szkript a futás előtt automatikusan commitolja a függő változásokat (üzenet: `scripts/git/pending_message.txt`), így minden futás commitolt kódon történik. Ismétlésszám 2 (az első futás 3 ismétlése azonos volt).
- Ellenőrzés eddig: Ruff sikeres; a kérésértelmező mind a 12 helyzetet és a három korábbi hibát helyesen kezeli; az ellenőrző lépés szimulált modellel megerősít, elutasít, és a hibát láthatóvá teszi; a bővített mérőszkript a célgépről vett valódi elemzői kimenetekkel és szimulált modellel végigfutott.

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
