# Security Lab 2 – tíz eltérő alkalmazás

## Indítás

Python **3.10 vagy újabb**. Nincs Docker, pip install, npm, külső font vagy CDN.

```bash
python app.py
```

- Kezdőlap: http://127.0.0.1:8000
- Helyi SMTP fogadó: 127.0.0.1:8025
- Fiókok minden projektben: `anna`, `bela`, `admin`
- Jelszó: `LabPass123!`
- Leállítás: Ctrl+C. Windows alatt a `start.bat` is használható.

Az `app.py` létrehozza és feltölti a tartós adatbázist, elindítja a webkiszolgálót,
a helyi SMTP fogadót és a háttérben futó metrikagyűjtőt. A következő indítás
megőrzi az adatokat. A háttérfolyamat 30 másodpercenként valós adatbázis-darabszámokat
rögzít, legfeljebb 120 mintát tart meg.

**Adatbázis: beágyazott SQLite**, a `data/lab.sqlite3` fájlban. Ez valódi SQL-adatbázis,
de nem külön PostgreSQL vagy Microsoft SQL Server folyamat. A Docker nélküli,
telepítésmentes egyparancsos indítás ezt a megoldást használja. A csomag minden
személye, cége, termékleírása, fizetése és levele kitalált tesztadat.

```bash
# Másik port, ha foglalt az alapértelmezett:
python app.py --port 8001 --smtp 8026

# SMTP kikapcsolása:
python app.py --smtp 0

# Egyetlen projekt útvonalainak engedélyezése:
python app.py --project 3
```

## A tíz alkalmazás

| Útvonal | Felület | Saját munkafolyamat |
|---|---|---|
| `/p01/` SocialHub | Háromoszlopos közösségi hírfolyam, profilkártyák | Bejegyzés, hozzászólás, követés, profilszerkesztés, külön moderátori nézet |
| `/p02/` LocalMail | Sötét mappasáv, levéllista és olvasópanel | Helyi SMTP, HTML levél, belső kézbesítés, címjegyzék és aggregált levelezési kereső |
| `/p03/` MarketLab | Felső menü, termékrács, kosár és külön összesítő | Termék, készlet, kosár, mennyiség, mentett kupon, kedvezmény, tesztmegrendelés |
| `/p04/` HelpDesk | Operátori táblázat, KPI-k, triage/SLA panel | Hibajegy, prioritás, ügyintéző kijelölése, belső auditnapló |
| `/p05/` PeopleOps | Meleg színű HR munkatér, munkatárskártyák | Dolgozók, szabadságidőszakok, bérriport és SQL rendezési kifejezés |
| `/p06/` TeamWiki | Dokumentumfa, szerif dokumentumoldal, kétpaneles szerkesztő | Tulajdonosi szerkesztés, mentett piszkozatok, változatok és publikálás |
| `/p07/` EventDesk | Sötét rendezvényportál, eseménylisták és program | Férőhelyes regisztráció, előadók CSV importja, piszkozat és publikálás |
| `/p08/` StayLab | Utazási katalógus, szálláskártyák, ajánlatpanel | Dátumos ajánlat, vendégnév, mentett ajánlat, átfedést ellenőrző foglalás |
| `/p09/` SalesFlow | Lila CRM, ötoszlopos értékesítési pipeline | Ügyfelek, fázisváltás, mentett riportfejlécek és beágyazott export-előnézet |
| `/p10/` BuildBoard | Sötét fejlesztői Kanban és buildkonzol | Feladatok, ciklusellenőrzött függőségek, JSON webhook, ANSI buildnapló |

Ezek helyben futó üzleti prototípusok, közös Python backenddel, eltérő nézetekkel
és saját adattáblákkal. Nem teljes késztermékek: nincs valódi fizetés, külső
emailküldés, IMAP, TLS, vagy harmadik félhez kapcsolt CI rendszer.
A katalógus és a szálláslista szöveges adatlapokat használ; a csomag nem tartalmaz termék- vagy szállásfotókat.
A dátumok és összegek laborpéldák. A számlálók a tárolt adatokból származnak.

## Adatmodell és tartósság

Közös táblák: accounts, items, notes, saved_filters, orders, workflow, mail.
Saját táblák: profiles, contacts, products, carts, coupons, purchases, tickets,
employees, wiki_revisions, speakers, properties, quotes, crm_reports, builds,
audit_events. A metrikák runtime_metrics táblába kerülnek.

Az összetett POST munkafolyamatok SQLite tranzakciót kapnak. A megrendelés
pillanatképet tárol, csökkenti a készletet és kiüríti a kosarat. A wiki változatok
külön rekordok. A CSV importált előadói először piszkozatok. Az SQL backend
projektazonosítós közös tárolást használ: az alkalmazások nem biztonsági izolációs
határok, és a szándékos SQLi a többi helyi teszttáblát is elérheti.

A munkamenetek memóriában élnek, újraindítás után új bejelentkezés kell.
A beépített felhasználók a teszteléshez készültek; a labor nem teljes IAM rendszer.

## Összetettebb sérülékenységek

A részletes, lépésenkénti útvonalak a **SCENARIOS.md** fájlban találhatók.
A **vulnerability_manifest.json** géppel olvasható térképet tartalmaz.

| Projekt | Specifikus hiba | Miért többlépéses / eltérő? |
|---|---|---|
| SocialHub | Tárolt, attribútumkörnyezetű XSS | Felhasználó ment → admin külön moderációs oldalt nyit |
| LocalMail | JOIN + aggregáció előtti SQLi, SMTP-ből tárolt XSS | A címjegyzék a levelezési előzményekkel kapcsolódik össze |
| MarketLab | Second-order kuponszabály SQLi | Paraméterezett mentés után, a checkout későbbi lekérdezésében aktiválódik |
| HelpDesk | Boolean-based blind SQLi és auditnapló XSS | A lekérdezésből csak találatszám látszik; a megjegyzés később naplóként jelenik meg |
| PeopleOps | ORDER BY SQL-kifejezés-injekció | A bemenet rendezési kifejezés, nem idézőjeles WHERE érték |
| TeamWiki | Hibás HTML tisztításból tárolt XSS | Scripteltávolítás → piszkozat → előnézet → publikált oldal |
| EventDesk | Importból származó tárolt XSS | CSV → SQL tárolás → külön publikálás → másik felhasználó programoldala |
| StayLab | JSON scriptkörnyezetből kitörő XSS | JSON-kódolás után HTML `script` elembe kerül a vendégnév |
| SalesFlow | Beágyazott dokumentum XSS | Mentett riportsablon → HTML export-előnézet → sandbox nélküli iframe |
| BuildBoard | Naplófeldolgozási XSS | JSON webhook → SQL tárolás → ANSI színkód-eltávolítás → HTML napló |

A `safe=1` az adott nézet vagy művelet biztonságos kontrollváltozatát választja;
nem globális alkalmazásvédelmi kapcsoló. A sérülékeny ágak alapból engedélyezettek.
A belépés önmagában nem SQLi-s: a példák a belépés utáni üzleti műveletekben vannak.

Az eredeti egyszerű laborok is megmaradtak: `/p01/lab`–`/p10/lab`.
Az eredeti CSV a source könyvtárban, változatlanul. 1000 sor, 500 SQLi + 500 XSS,
10 különböző kódrészlet. Egy sima `alert('Hello ' + user_input)` önmagában nem XSS;
a CSV hasonló címkézési pontatlanságait a labor nem kezeli bizonyított hibaként.

## Helyi SMTP teszt

```python
import smtplib
from email.message import EmailMessage
m = EmailMessage()
m['From'] = 'bela@example.test'
m['To'] = 'anna@example.test'
m['Subject'] = 'Helyi tesztlevél'
m.set_content('<h2>HTML levél</h2><p>A laborból érkezett.</p>', subtype='html')
with smtplib.SMTP('127.0.0.1', 8025) as smtp:
    smtp.send_message(m)
```

Belépés Anna fiókkal, majd `/p02/inbox`. A legújabb levél az első.
Csak anna/bela/admin@example.test címzett támogatott. Nincs külső relay.

## Tesztek

```bash
python -m unittest discover -s tests -v
```

20 automatizált teszt, valódi HTTP és helyi SMTP kérésekkel, ideiglenes adatbázissal.
Ellenőrzik a tíz eltérő nézet kiszolgálását és saját útvonalait, az üzleti
alapfolyamatokat, a külön SQLi-kat és kontrolljaikat, a XSS adatútvonalakat és
HTML kódolásukat, a megrendelés utáni készletcsökkenést, a tranzakció-visszagörgetést,
a dátumütközést, a függőségi ciklust és a kijelentkezést.

Böngészőmotor ebben a környezetben nem állt rendelkezésre: a tesztek nem állítják,
hogy JavaScript popupokat vagy a vizuális megjelenést böngészőben ellenőrizték.
A XSS-reprodukciók tényleges scriptfutását helyi böngészőben lehet ellenőrizni.

## Fájlok

- app.py: központi indítás, HTTP útvonalválasztás és életciklus
- core.py: SQLite, tranzakciók és egyszerű kontrolllaborok
- platform_lab.py: bejelentkezés, közös üzleti alapfolyamatok
- ui.py: tíz eltérő felület, reszponzív CSS, kezdőoldalak és levélolvasó
- content.py: alkalmazásonként eltérő alapleírások; a korábbi, változatlan alapadatok frissítése
- advanced.py: alkalmazásspecifikus funkciók és szándékos sérülékenységek
- workflows.py: követések, kosár, szabadság, foglalás és feladatfüggőségek
- seed_data.py: kitalált, témához illeszkedő alapadatok
- smtp_local.py: helyi SMTP fogadó
- runtime_services.py: SMTP és háttérmetrikák közös indítása/leállítása

Alaphelyzet: állítsd le az alkalmazást, töröld a data/lab.sqlite3 fájlt, majd indítsd újra.
Alapértelmezett elérés: csak a helyi gép (127.0.0.1).

## Frissítés korábbi csomagról

Az indítás és a fiókok változatlanok. A csomag nem tartalmaz kész SQLite fájlt,
így a meglévő mappára kicsomagolva nem írja felül az adatbázisodat. Új mappában
az első indítás feltölti az alapadatokat. A korábbi sablonleírások frissülnek,
a saját bejegyzések és módosított tartalmak megmaradnak.

A kontrollkapcsolók a keresőknél és az összetett űrlapoknál a
**Tesztbeállítások** lenyitható részbe kerültek. A prioritásmező saját feliratot
kapott a HelpDesk triage oldalán. A hibák technikai leírása a SCENARIOS.md
fájlban található, az üzleti nézetek a használathoz szükséges feliratokat mutatják.
