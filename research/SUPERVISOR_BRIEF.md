# Témavezetői egyeztetés – előzetes projektirány

**Szerző:** Nagy István  
**Témavezető:** Girászi Tamás  
**Tervezett cím:** AI-alapú segédeszköz fejlesztése kibervédelmi sérülékenység-felderítés támogatására

## Javasolt feladat

Helyben futó segédeszköz készítése, amely természetes nyelvű kérés alapján statikus forráskódelemzőket használ, majd a találatokat előre betanított nyelvi modell segítségével értelmezi és magyarázza. Saját modell tanítása jelenleg nem része a tervnek.

Első célterületként Python-forráskódot, azon belül dinamikus kódkiértékelést, parancsbefecskendezést és SQL-befecskendezést vizsgálunk. A célnyelv és a hibacsaládok még módosíthatók.

## Mi adhatja a szakdolgozat önálló hozzájárulását?

- A kérések, elemzőeszközök és modell közötti ellenőrizhető együttműködés megtervezése és megvalósítása.
- A találatokhoz visszakövethető magyarázatok, a bizonytalanság és a hibás működés kezelése.
- Az AI nélküli és az AI-val kiegészített működés összehasonlító vizsgálata: találatok értékelése, alátámasztott magyarázatok, kérésértelmezés, időigény és ismételhetőség.

A terv nem állítja, hogy új gépi tanulási algoritmust készítünk, vagy hogy az AI már bizonyítottan javítja a sérülékenység-felismerést. Az utóbbi mérendő kérdés.

## Mi készült el eddig?

- Kezdeti szakirodalmi és technológiai áttekintés, hazai kutatási forrással is.
- Elkülönített, verziózott függőségekkel reprodukálható Python-környezet.
- Bandit- és Semgrep-kapcsolat, egységes találatformátummal és hibakezeléssel.
- Helyi Ollama-futtató és előre betanított Qwen2.5-Coder modell; tényleges adatátadási próba az elemző és a modell között.
- 18 saját fejlesztési kódminta, 12 előkészített felhasználói teszthelyzet és 40 sikeres automatizált teszt.

A teljes természetes nyelvű munkafolyamat, az eredmények AI-alapú érdemi értékelése és a végső összehasonlító mérés még nem készült el. A saját kódminták címkéi emberi felülvizsgálatot igényelnek; ezek nem független végső tesztadatok.

## Az egyeztetésen tisztázandó kérdések

1. Megfelel-e a témakiírásnak előre betanított modell alkalmazása saját modell tanítása nélkül?
2. Elfogadható-e a Python-forráskód és a három kijelölt hibacsalád mint kezdeti, lehatárolt célterület?
3. Az AI hozzájárulását elsősorban a találatok értékelésében, a magyarázatok minőségében, a felhasználói kérések értelmezésében vagy ezek kombinációjában érdemes mérni?
4. Milyen mennyiségű és eredetű végső tesztadatot vár el a témavezető, és megfelelő-e az elemző önmagában / elemző AI-kiegészítéssel összehasonlítás?

## Módosíthatóság

A modell és a kódelemző cserélhető részek. Más célnyelv vagy új hibacsalád esetén főleg az elemzési szabályokat és a tesztadatokat kell cserélni. Saját modell tanítása vagy futó webalkalmazások vizsgálata nagyobb módosítás: új adat- és mérési tervvel, valamint az ütemezés felülvizsgálatával járna.
