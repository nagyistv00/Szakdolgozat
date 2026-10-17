# Szakdolgozat – munkautasítások és formai követelmények

## A munka aktuális állapota

- Másik chat számára készült összefoglaló: `CHAT_HANDOFF.txt` (2026-10-17). Ugyanebben a projektmappában kell folytatni; ZIP nem készült. Az átadás önmagában nem engedélyezi M3/M4 megkezdését. A témavezető válaszait a felhasználó 2026-10-17-én közölte; lásd lent a „Témavezetői visszajelzés” szakaszt és a `RESEARCH_LOG.md` azonos dátumú bejegyzését.

- A felhasználó megadta a formai követelményeket, a témakiírást, a tervezett dolgozatcímet, a szerző és a témavezető nevét, valamint a négyhavi munkatervet.
- Az első mérföldkő alapozó munkája elkészült. A felhasználó engedélyezte a második mérföldkő elkészítését a következő heti témavezetői egyeztetés előtt: rendszerterv, komponensek és kapcsolataik előkészítése, dokumentációk, tesztadatok, műveleti minták és tesztesetek rendszerezése.
- A második mérföldkő keretében önállóan haladj. (Történeti.)
- 2026-10-17: a felhasználó engedélyezte M3 megkezdését, előtte a meglévő kód felülvizsgálatát kérte. M3 állapota: `research/MILESTONE_3.md`. M4 (végső kiértékelés) még nem engedélyezett.
- A szakdolgozat fejezeteinek megírása továbbra is csak a négy mérföldkő elvégzése után kezdődhet.
- A felhasználó elfogadta a helyben futó Python-alapú előkészítést, fizetős szolgáltatás nélkül; nincs megadott korábbi kód vagy technológiai megkötés.
- A felhasználó a forráskód-elemzést választotta első iránynak, és jelenleg nem kíván saját modellt tanítani. Előre betanított modell alkalmazásával haladjunk. A Python célnyelv módosítható munkafeltételezés; külön célnyelvet a felhasználó nem kötött ki.
- Az első mérföldkő kutatási összegzése: `research/MILESTONE_1.md`; forrásjegyzék és olvasási mélység: `research/SOURCES.md`; reprodukálás: `README.md`; futási bizonyítékok: `artifacts/m1/`.
- A telepítési minták nem kutatási benchmarkok. A sikeres környezetellenőrzést ne állítsd be a sérülékenység-felismerési pontosság vagy AI-működés igazolásaként.
- Az első mérföldkő zárásakor AI-modell még nem volt telepítve, tanítva vagy futtatva; a későbbi változásokat a kutatási naplóban és a mérföldkő-leírásban kell követni.
- (Történeti, 2026-09-19:) A témavezető akkor még nem erősítette meg az irányt; az elemző, a modellkapcsolat és a tesztadatok ezért készültek cserélhető részekként.
- 2026-10-17: a témavezető a felhasználó közlése szerint megerősítette az irányt; részletek a „Témavezetői visszajelzés” szakaszban.
- M2 elkészült az ideiglenes scope szerint. Aktuális terv és eredmények: `research/MILESTONE_2.md`; témavezetői egyeztető: `research/SUPERVISOR_BRIEF.md`. A saját modell tanítását ne indítsd el.
- Előre betanított helyi modell: Ollama 0.34.2 + qwen2.5-coder:7b, a pontos digest és konfiguráció a M2-jegyzőkönyvben. A modell és az elemző tényleges adatkapcsolata ellenőrizve; a természetes nyelvű teljes munkafolyamat és érdemi AI-értékelés még M3-feladat.
- M2-adatok: `data/m2/` alatt 18 saját, ideiglenesen címkézett fejlesztési kódminta és 12 előkészített kéréshelyzet. Az emberi címkefelülvizsgálat még hátravan. Ezeket tilos független, korábban nem látott végső tesztkészletként bemutatni.
- A M2 kapcsolódó tesztjei és a korábbi M1-próbák együtt 40 sikeres ellenőrzést adtak; 36 mintavizsgálat lefutott. Ez nem bizonyítja, hogy az AI javítja a detektálást. A modellpróba csak találati azonosítók és eszköznév visszaigazolása volt.
- A képzési szint, a szak pontos megnevezése, a tanszék, a témavezető beosztása és a benyújtás éve még nincs megadva. Ne találj ki adatokat.

## Témavezetői visszajelzés – a felhasználó 2026-10-17-i közlése szerint

A szó szerinti válaszok a `RESEARCH_LOG.md` 2026-10-17-i bejegyzésében. Az egyeztetés dátuma és formája nincs megadva; írásos dokumentum nincs.

- Saját modell tanítása nem követelmény; az előre betanított modell megfelel.
- Új felismerési módszer fejlesztése nem követelmény; a tervezés, megvalósítás és kiértékelés meglévő eszközökkel elegendő.
- Python-forráskód és a három hibacsalád (CWE-89, CWE-78, CWE-95) elfogadott célterület. A témavezető szükség esetén tesztpéldákat is tud adni.
- Az AI prioritási sorrendje: hibák felismerése > magyarázat adása > nyelvi vezérlés > téves detektálások felismerése.
- Az elemző vs. ugyanaz az elemző + AI összehasonlítás kulcsfontosságú; a kiértékeléshez az accuracy, precision és recall elegendő.
- Saját, kisebb kódrészletek vagy funkcionális egységek elegendők; teljes (pl. webalkalmazás-) projekt nem szükséges. A demonstráció célja: a rendszer felismeri a hibát és megfelelő magyarázatot ad.
- Ebből nem következik automatikusan M3/M4 engedélyezése; azt a felhasználó adja meg.

## Munkamenet és folyamatos jegyzetelés

- Először a négy mérföldkő (a korábbi terv Hónap 1–4. szakaszai) kutatási és fejlesztési munkáját kell elvégezni. A szakdolgozat dokumentumának összeállítása csak mind a négy mérföldkő elvégzése után kezdődhet.
- A negyedik mérföldkőben említett dokumentálás ebben a munkamenetben az eredmények és a fejlesztési bizonyítékok rögzítését jelenti; a dolgozat fejezeteinek megírása későbbi feladat.
- A kutatás és fejlesztés során a szakdolgozat számára fontos információkat folyamatosan, külön kérés nélkül mentsd a projekt `RESEARCH_LOG.md` fájljába. Ne csak a beszélgetési memóriára támaszkodj, és ne halaszd a jegyzetelést a munka végére.
- A jelentős döntéseket, megfigyeléseket és eredményeket az adott munkaszakaszban rögzítsd, legkésőbb a munkamenet lezárása előtt. Folytatáskor olvasd el a releváns korábbi bejegyzéseket.
- A bejegyzésekben legyen dátum, kapcsolódó mérföldkő, elvégzett tevékenység vagy megállapítás, annak szakdolgozati jelentősége, illetve ellenőrizhető forrás vagy bizonyíték, ha rendelkezésre áll.
- Őrizd meg a szakirodalmi források pontos adatait és dokumentumszintű URL-jét vagy DOI-ját, a hozzáférés dátumát és a belőlük felhasznált állításokat. Válaszd külön a forrás állítását a saját következtetéstől.
- Rögzítsd a technológiai és tervezési döntéseket, indokaikat, a ténylegesen mérlegelt alternatívákat, valamint a lényeges változtatásokat.
- Kísérleteknél és teszteknél jegyezd fel a módszert, az adatokat és eredetüket, a használt eszközök/modellek verzióját, a releváns beállításokat, a mérőszámokat, eredményeket és az ismételhetőséghez szükséges körülményeket. A részletes bizonyítékokat fájlútvonallal vagy verziókezelési hivatkozással kapcsold a bejegyzéshez, ha vannak ilyenek.
- A hibákat, sikertelen próbálkozásokat, korlátokat, javításokat, nyitott kérdéseket és továbbfejlesztési lehetőségeket is rögzítsd, ha fontosak a dolgozat számára.
- Különítsd el a tervet, a hipotézist, a ténylegesen megvalósított funkciót és a méréssel igazolt eredményt. Ne állíts elvégzettnek vagy igazoltnak olyasmit, ami még nem az.
- A napló munkajegyzet, nem kész dolgozatszöveg. A később elkészülő dolgozat nyelve továbbra is angol.
- A korábbi bejegyzéseket őrizd meg; megváltozott döntést vagy javított következtetést új, a korábbira visszautaló bejegyzéssel dokumentálj.

## Téma és személyi adatok

- Témakiírás címe: Gépi tanulási módszerek alkalmazása automatikus sérülékenységfelderítésben
- Tervezett dolgozatcím: AI-alapú segédeszköz fejlesztése kibervédelmi sérülékenység-felderítés támogatására
- Szerző: Nagy István.
- Témavezető: Girászi Tamás.
- Külső témavezető neve: nincs megadva (üres mező).
- Külső témavezető munkahelye: nincs megadva (üres mező).
- A két címet és a hozzájuk tartozó leírásokat külön őrizd meg; a tervezett címet ne tekintsd automatikusan véglegesen jóváhagyott címnek.

### A témakiírás általános leírása – a felhasználó szövege

A dolgozat célja annak vizsgálata, hogy a mesterséges intelligencia hogyan alkalmazható szoftverek sebezhetőségeinek automatikus felismerésére. A kutatás statikus kódelemzési technikákat és gépi tanulási modelleket használ a potenciális biztonsági hibák azonosítására.

### A tervezett dolgozat általános leírása – a felhasználó szövege

A szakdolgozat egy AI-alapú segédeszköz fejlesztésével foglalkozik, amely a kibervédelmi vizsgálatok során támogatja a biztonsági hibák felismerését. A munka célja egy olyan megoldás kialakítása, amely természetes nyelvű feldolgozási képességekkel segíti a lehetséges sérülékenységek azonosítását és az eredmények értékelését.

## Elvégzendő munka és ütemezése – a felhasználó terve

Az alábbiak tervezett feladatok, nem elvégzett munkáról szóló állítások. Konkrét naptári hónapok vagy határidők még nincsenek megadva.

### Hónap 1

A szakdolgozat témájához kapcsolódó szakirodalom és technológiai háttér áttekintése. Meglévő megoldások megismerése. A fejlesztési és tesztelési környezet kialakítása, valamint a szükséges keretrendszerek és függőségek telepítése.

### Hónap 2

Az AI-alapú segédeszköz alapfelépítésének és működésének megtervezése. A rendszer főbb részeinek, gépi tanuló modell és a háttérben elérhető eszközök közötti kapcsolatnak a kialakítása. A szükséges dokumentációk, tesztadatok, műveleti minták és tesztesetek összegyűjtése és rendszerezése.

### Hónap 3

A biztonsági hibák felismerését támogató funkciók fejlesztése. A természetes nyelvű felhasználói kérések feldolgozása, az elemzéshez szükséges információk azonosítása, valamint a háttérben elérhető eszközök bevonásának megvalósítása. Egyszerű irányítási és ellenőrzési logika kialakítása annak érdekében, hogy a rendszer a bemeneteket megfelelően kezelje, és a vizsgálatok értelmezhető módon kerüljenek végrehajtásra. A kapott eredmények rövid, természetes nyelvű összefoglalásának kialakítása.

### Hónap 4

A fejlesztett funkciók és ellenőrzési megoldások tesztelése és kiértékelése. A rendszer válaszainak pontossági, stabilitási és használhatósági vizsgálata különböző biztonsági szempontú tesztesetek és felhasználói kérések alapján. Az eredmények rendszerezése, a hibás vagy pontatlan működések azonosítása és javítása. A szakdolgozat eredményeinek dokumentálása, a fejlesztési folyamat, az alkalmazott megoldások, a tesztelések, a rendszer korlátai és a továbbfejlesztési lehetőségek bemutatása.

## Nyelv és együttműködés

- A felhasználóval magyarul kommunikálj.
- A dolgozat szövegét angolul kell megírni; a magyar fordítást a felhasználó maga végzi.
- A felhasználó a fordítás indokaként az AI közreműködésének felismerhetetlenségét említette. Ez rögzített kontextus, nem detektorkijátszási feladat: a fordítás nem garantál felismerhetetlenséget. Ne ígérj ilyet.
- A munkát a felhasználó saját kutatására, megvalósítására és ellenőrzött forrásokra kell alapozni. Ne találj ki forrásokat, kutatási eredményeket vagy elvégzett munkát. Az AI használatánál az alkalmazandó egyetemi előírásokat kell követni.
- Az oldalterjedelmet a végleges magyar változatban is ellenőrizni kell, mert fordításkor változhat.

## A követelmények forrása és értelmezése

- Az alábbiak a felhasználó által ebben a beszélgetésben bemásolt teljes formai útmutatón alapulnak.
- Őrizd meg a különbséget a kötelező előírások, az ajánlások és a később választott szerkesztési megoldások között.
- Címlapminta: https://inf.unideb.hu/sites/default/files/inline-files/C%C3%ADmlap%202026.pdf
- A minta 2026-os évszámot tartalmaz; a dolgozatra a tényleges benyújtási év kerüljön.

## Ajánlott szerkezeti sorrend

1. Cím / címlap.
2. Tartalomjegyzék.
3. Bevezetés.
4. Tárgyalási (leíró, elemző) rész.
5. Összefoglalás.
6. Irodalomjegyzék.
7. Függelék.
8. Köszönetnyilvánítás – helye a dolgozatban szabadon megválasztható.

## Címlap

- Lap tetején, középre rendezve: egyetem, kar, tanszék.
- Felső harmadban, középen: alapképzés esetén SZAKDOLGOZAT, mesterképzés esetén DIPLOMAMUNKA.
- Középen: a dolgozat címe.
- Alsó harmadban, jobb oldalon: a szerző neve és a szak megnevezése.
- Alsó harmadban, bal oldalon: a témavezető neve és beosztása.
- Lap alján, középre rendezve: Debrecen és a benyújtás éve.
- A linkelt mintán DEBRECENI EGYETEM és INFORMATIKAI KAR szerepel. A szöveges előírás tanszéket is említ, a mintán ez nem szerepel; a végleges címlapnál ezt az eltérést rendezni kell, tanszéknevet ne találj ki.

## Formátum

| Beállítás | Előírás / ajánlás |
| --- | --- |
| Bal margó | 3 cm |
| Jobb margó | 2 cm |
| Felső margó | 3 cm |
| Alsó margó | 3 cm |
| Betűtípus | Times New Roman |
| Főszöveg betűmérete | Ajánlott 12 pont |
| Címlap és fejezetcímek | 14–16 pontos betű használható |
| Sortávolság | Ajánlott 1,5-es sorköz |

- A margókat a szövegszerkesztés megkezdése előtt kell beállítani.
- A betűkészletnek támogatnia kell a magyar ékezetes betűket, különösen az ő és ű karaktereket.

## Az egyes részek követelményei

### Cím

- Legyen rövid, érthető, és fejezze ki jól a tartalmat.

### Tartalomjegyzék

- A belső címlap utáni oldalon helyezkedjen el.
- Decimális fejezetszámozást használjon, például 1., 1.1., 1.1.1.
- Tartalmazza a részek, fejezetek, alfejezetek és kisebb egységek címét és oldalszámát.
- A főszövegen kívüli járulékos részeket is fel kell tüntetni.

### Bevezetés – 2–3 oldal

- Indokolja a témaválasztást.
- Mutassa be az elméleti és gyakorlati jelentőséget.
- Fogalmazza meg a célkitűzéseket és a vizsgálati módszereket.

### Tárgyalási rész – 30–40 oldal

- Az érdemi tartalmat a hallgató és a témavezető határozzák meg.
- A téma részletes kifejtését és a hazai szakirodalom feldolgozását tartalmazza.
- A külföldi források használata értéknövelő ajánlás.
- Az útmutató az internetes lehetőségeket és a kari könyvtár külföldi folyóiratait is ajánlja forráskereséshez.

### Összefoglalás – 2–3 oldal

- Röviden, tömören és világosan ismertesse a fontosabb megállapításokat és következtetéseket.
- Egyértelműen jelezze az esetleg nem teljesült célkitűzéseket, megfelelő indoklással. Az útmutató szerint ez önmagában nem csökkenti a dolgozat értékét.

### Irodalomjegyzék

- Minden ténylegesen felhasznált könyvet, periodikát és elektronikus forrást tartalmazzon, akkor is, ha abból nincs szó szerinti idézet.
- Javasolt csoportosítás:
  - könyvek, cikkek, tanulmányok;
  - statisztikai adatforrások;
  - jogszabályok;
  - internetes adatgyűjtés.
- Megfelelő számú forrás esetén magyar és külföldi részekre bontás is célszerű lehet.
- Internetes hivatkozásokat dokumentum mélységig kell megadni: a konkrét dokumentumot vagy aloldalt hivatkozd, ne csak a honlap főoldalát.

### Függelék – az útmutató megfogalmazásával „maximum 8–10 oldal”

- Nagyobb táblázatok és ábrák.
- Kérdőíves felmérés alapdokumentumai.
- Statisztikai és matematikai számítások alaptáblái.
- Indokolt esetben rövidebb szöveges dokumentumok, például szerződés- vagy jogszabályrészletek.

### Köszönetnyilvánítás

- Az elméleti, gyakorlati, erkölcsi vagy egyéb segítséget nyújtóknak szól.
- Helye tetszőlegesen választható meg a dolgozatban.

## Terjedelem

- A bevezetés, tárgyalás és összefoglalás együtt számított ajánlott terjedelme 34–46 oldal.
- Ez nem a teljes dokumentumra megadott oldalszám: a címlap, tartalomjegyzék, irodalomjegyzék és további járulékos részek ezen felül értendők.

## Plágiumnyilatkozat

- A plágiumnyilatkozat NEM része a szakdolgozatnak, ne kerüljön a dokumentumba.
- Kizárólag a Neptun rendszerben, az „IK Szakdolgozat leadás / Plágium nyilatkozat” kérvényen kell leadni.

## A megküldött útmutatóban nem szabályozott részletek

- Pontos hivatkozási stílus.
- Szövegigazítás.
- Bekezdésbehúzás és bekezdések közötti térköz.
- Oldalszámozás kezdőpontja, helye és megjelenítése.
- Papírméret.
- Az egyes címsorszintek pontos formázása a megadott mérettartományon belül.

Ezekre ne hivatkozz intézményi követelményként. A későbbi kidolgozás során következetes szerkesztési megoldást kell választani, figyelembe véve a felhasználó és a témavezető további útmutatását.
