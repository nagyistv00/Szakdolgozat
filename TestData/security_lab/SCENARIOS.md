# Helyi reprodukciós útvonalak

Minden lépés a csomag saját, helyi végpontjára vonatkozik. Először indítsd az
app.py fájlt, majd lépj be a megfelelő projektbe `anna / LabPass123!` adatokkal.
A kontrollokat ugyanarra a műveletre kell kiválasztani; nem globális beállítások.
A kereső és az összetett űrlapok kontrollkapcsolója a Tesztbeállítások lenyitható részben található.
A példák sikerét böngészőben kell megfigyelni; az automatizált tesztek HTTP
válaszokat, adatbázisállapotot és kódolást ellenőriznek.

## 1. SocialHub – profilból moderátori attribútum-XSS

1. `/p01/profile`, megjelenített név:
   `"><img src=x onerror=alert(101)>`
2. Mentsd a profilt.
3. Jelentkezz ki, majd lépj be admin fiókkal, ugyanazzal a jelszóval.
4. Nyisd meg `/p01/moderation`: a profilnév HTML attribútumba kerül.
5. Kontroll: `/p01/moderation?safe=1`.

A profil mentése paraméterezett SQL-lel történik; a hiba a másik szerepkörű
felhasználó nézetében, a HTML-környezetnél van.

## 2. LocalMail – aggregált SQLi és SMTP-ből tárolt HTML

`/p02/contacts`, keresett név:

```text
unlikely' OR 1=1 -- 
```

A hiba a címjegyzék és a mail tábla JOIN-ja után, a GROUP BY előtt van.
A kontroll ugyanazt a nevet paraméterként kezeli, nem SQL-részletként.
Az SMTP mintában küldhetsz `<img src=x onerror=alert(102)>` tartalmat az Anna
postafiókba; ez a levélolvasóban jut el HTML környezetbe. `safe=1` szöveges kontroll.

## 3. MarketLab – second-order SQLi a kuponrendszerben

1. Tegyél a kosárba egy 2-es azonosítójú terméket a katalógusból.
2. A checkout oldalon nyisd ki a Kupon beállítása panelt.
3. Kód: `TEST`, kedvezmény: `20`, scope:

```text
none' OR 1=1 -- 
```

4. Mentsd a szabályt: ekkor még paraméterezett INSERT fut.
5. A kuponmezőbe írd: `TEST`, majd alkalmazd.
6. A tárolt scope a termékkategória-lekérdezést módosítja, így olyan tételre is
   kedvezmény járhat, amelyre a szó szerinti scope nem illeszkedne.
7. Kontroll: `/p03/checkout?coupon=TEST&safe=1`, itt a kedvezmény 0.
8. A megerősítés helyi tesztmegrendelést hoz létre és készletet csökkent.

## 4. HelpDesk – boolean-based blind SQLi

A `/p04/triage` prioritásmezőjében hasonlítsd össze:

```sql
1 AND (SELECT salary FROM employees WHERE item_id=1)>400000
```

```sql
1 AND (SELECT salary FROM employees WHERE item_id=1)>9000000
```

Csak a találatszám változik: az alapadatokkal 4, illetve 0. Nem az SQL eredménysor
vagy a fizetés jelenik meg. A kontroll csak egész prioritást fogad.
A kiosztás belső megjegyzése külön tárolt XSS pont: a mentés után az auditnapló
olvassa vissza. Példa: `<img src=x onerror=alert(104)>`.

## 5. PeopleOps – ORDER BY kifejezés-injekció

`/p05/payroll`, rendezési kifejezés:

```sql
CASE WHEN (SELECT salary FROM employees WHERE item_id=1)>400000 THEN salary ELSE -salary END DESC
```

A lekérdezés a kifejezést rendezésként értelmezi. A feltétel megváltoztatásával
az eredménysorrend megfordítható. A kontroll szűk rendezési engedélylistát használ,
a fenti kifejezést 400-as válasszal elutasítja. Minden fizetési adat kitalált.

## 6. TeamWiki – hibás HTML tisztítás, piszkozat, publikálás

1. `/p06/editor?id=2`, szerkesztés Anna fiókkal (ő a tulajdonos).
2. Tartalom:
   `<script>alert(0)</script><img src=x onerror=alert(106)>`
3. Piszkozat mentése: a script elem eltűnik, az eseményattribútum megmarad.
4. A verzió előnézete megjeleníti a tartalmat.
5. Publikálás után `/p06/item?id=2` is a hibásan tisztított HTML-t jeleníti meg.
6. Kontroll: `safe=1` a szerkesztő és a részletoldal megfelelő URL-jén.

## 7. EventDesk – CSV importból publikált XSS

`/p07/speakers`, importálható CSV:

```csv
name,topic,bio
Fiktiv Speaker,Lab,<img src=x onerror=alert(107)>
```

Import után piszkozat jön létre. Publikáld a Programba publikálás gombbal.
Béla fiókkal megnyitva ugyanazt a programoldalt a közzétett bio HTML-ként jelenik
meg. A `safe=1` kontroll escape-eli a tartalmat.

## 8. StayLab – JSON scriptkörnyezet-XSS

1. `/p08/quote?id=1`.
2. Vendégnév: `</script><img src=x onerror=alert(108)>`.
3. Érvényes, 1–60 éjszakás dátumpár, majd ajánlat mentése.
4. A JSON stringben megengedett `</script>` lezárhatja a befoglaló HTML script
   elemet, még `type="application/json"` esetén is.
5. A kontroll a `<`, `>` és `&` karaktereket Unicode escape-pel kódolja az
   inline JSON adatban. A látható vendégnév megjelenítése textContent alapú.

## 9. SalesFlow – mentett riportsablon, beágyazott dokumentum

1. `/p09/analytics`, sablonnév: `test`.
2. Fejléc: `<script>alert(109)</script>`.
3. Mentsd, majd nyisd meg a mentett sablont.
4. A külső HTML attribútum escape-elve van, de az iframe `srcdoc` ezt új HTML
   dokumentumként értelmezi. Sandbox nélkül a fejléc aktív tartalma futtatható.
5. Kontroll: `/p09/analytics?run=test&safe=1`: szöveges tartalom és üres sandbox.

## 10. BuildBoard – JSON webhook és ANSI naplófeldolgozás

`/p10/integrations`, webhook payload:

```json
{
  "task_id": 1,
  "branch": "feature/lab",
  "status": "success",
  "log": "\u001b[32m<img src=x onerror=alert(110)>\u001b[0m"
}
```

Feldolgozás után a buildrekord SQL-ben tárolódik. A konzol színkód-eltávolítója
csak ANSI vezérlőkódokat kezel, a HTML-t nem kódolja. A `pre` elem nem HTML
biztonsági határ. Kontroll: `/p10/integrations?safe=1`.
