"""Az alaprekordok szövegei. A csomagban szereplő adatok kitaláltak."""
from core import query
from seed_data import TITLES

DESCRIPTIONS={
1:[
'A közös híreket mostantól ide írjuk. A napi egyeztetések maradnak a csatornában, a hosszabb összefoglalóknak itt lesz helyük.',
'A kereső új változatát ezen a héten próbáljuk ki. Ha üres találati listába futtok, írjátok meg, milyen kifejezésre kerestetek.',
'Pénteken 10-kor a tárgyalóban találkozunk. Hozzatok egy problémát, amire a következő két hétben megoldást szeretnétek.',
'Dóra a felületek tervezésében, Erik az adatfeldolgozásban segít ezentúl. Az első feladataikat a projekt tábláján találjátok.',
'A közös polcra tettem két könyvet. Ha kölcsönveszitek valamelyiket, jelezzétek egy hozzászólásban, kinél van.',
'Az első változatban még csak a keresés és az adatlap működik. A szűrők elrendezéséről várjuk a véleményeket.',
'Ide gyűjtsük azokat a technikai kérdéseket, amelyeket a heti egyeztetésen szeretnétek átbeszélni.',
'A következő belső alkalmon az SQL lekérdezések végrehajtási tervét nézzük meg. Saját példát is hozhattok.',
'Lezártuk az adatimport javítását, és elkészült az új listanézet. A mobilos ellenőrzés még hátravan.',
'Az ismétlődő bejegyzéseket összevonjuk. A módosítás előtt a szerzővel egyeztetünk.',
'A következő kiadás előtt külön összefoglaló készül a csapatnak. A végleges dátumot még egyeztetjük.',
'A bejegyzés szövege kész, a képek ellenőrzése után lehet közzétenni.'
],
2:[
'Szia! A hozzáférésed elkészült. Belépés után ellenőrizd a profilodon megadott adatokat.',
'Sziasztok! Röviden összeszedtem az elmúlt hét lezárt feladatait és a nyitott kérdéseket.',
'A megbeszélést visszaigazoltuk. Ha másik időpontot szeretnél, válaszolj erre a levélre.',
'A megrendelést rögzítettük. A tételeket a rendelési összesítőben tudod ellenőrizni.',
'Sziasztok! Frissült a feladatlista, a felelősök és a következő egyeztetés napirendje.',
'A szabadságkérelmet megkaptuk. A jóváhagyásról külön értesítést küldünk.',
'Emlékeztető a korábban egyeztetett határidőről. Kérlek, jelezd, ha változott a feladat állapota.',
'Az átadáshoz szükséges jegyzeteket összegyűjtöttük. A nyitott kérdéseket a következő megbeszélésen nézzük át.',
'Köszönjük a jelzést. A hibát rögzítettük, és a vizsgálat eredményével visszajelzünk.',
'Ez a sablon a csapaton belüli egyeztetésekhez használható. Küldés előtt töltsd ki a tárgyat és a határidőt.',
'A szöveg még egyeztetés alatt áll. Kiküldés előtt a mellékelt feladatlistát is ellenőrizni kell.',
'A felhasználói adatok módosítását rögzítettük. Ha nem te kérted a változtatást, jelezd az ügyfélszolgálatnak.'
],
3:[
'Matt fehér kerámiatalp, textilbúra. E27 foglalat, kapcsoló a vezetéken. Az izzó nem tartozék.',
'Kompakt, vezetékes billentyűzet cserélhető kupakokkal. USB-C csatlakozás; a kábel a csomag része.',
'Párnázott vállpánt, belső laptoptartó rekesz és cipzáras elülső zseb. Tisztítása nedves ruhával ajánlott.',
'Duplafalú, rozsdamentes acél palack csavaros kupakkal. Űrtartalom: 500 ml. Kézi mosogatással tisztítható.',
'Bükkfa állvány asztali monitorhoz. Alatta elfér a billentyűzet; összeszerelve szállítjuk.',
'Jobbkezes kialakítású egér USB vevőegységgel. Két oldalsó gomb és állítható érzékenység. Elem nélkül.',
'Három A5 méretű, pontozott lapú füzet. Puha borító, fűzött kötés; füzetenként 80 oldal.',
'Asztali dokkoló két USB-A aljzattal és HDMI kimenettel. Vásárlás előtt ellenőrizd a géped USB-C képességeit.',
'Kis méretű kaspótartó, kivehető belső betéttel. Beltéri használatra. A növény külön vásárolható meg.',
'Fejlesztői mintadarab, vezetékes csatlakozással. A dokumentáció és a végleges csomagolás még nem készült el.',
'Irodai indulókészlet jegyzetfüzettel, tollal és kábeltartóval. A csomag tartalmát a beszerzési lista rögzíti.',
'Raktári ellenőrzésre fenntartott mintadarab. Az állapota az adatlapon követhető.'
],
4:[
'A felhasználó szerint az új hozzászólásról nem érkezik levél. A felületen az esemény megjelenik; a levélküldési naplót ellenőrizni kell.',
'A feltöltés a folyamat végén megszakad, a fájl nem jelenik meg a listában. A hiba ismételt próbálkozással is jelentkezik.',
'A havi összesítő végösszege eltér a tételes listától. Ellenőrizni kell, hogy a jóváírások beleszámítanak-e.',
'A bejelentő új csapattagot szeretne felvenni a közös munkaterületre. A meghíváshoz szükséges emailcímet megadta.',
'A riport nagyobb dátumtartománynál lassan tölt be. A szűrés eredménye helyes, a válaszidőt kell megvizsgálni.',
'A meghívó hivatkozása lejárt, mielőtt a címzett használta volna. Új meghívó kiküldését kérte.',
'A naptárban egy nappal korábbra kerül az esemény. Vizsgálandó a dátumkezelés és az időzóna beállítása.',
'A megrendelő a számlázási adatok javítását kéri. A módosítás előtt ellenőrizni kell a kapcsolódó rendelést.',
'A jelszó visszaállítása után a felhasználó nem tud belépni. A hibajelzés szerint a fiók zárolt.',
'Ellenőrizni kell a korábban kiosztott belső hozzáféréseket. Az eredményről rövid feljegyzés készül.',
'A karbantartás előtti és utáni ellenőrzések listája. A munkát az ügyeletes kolléga zárja le.',
'A gomb kisebb ablakméretnél a táblázat alá kerül. A bejelentésben szereplő lépésekkel újra előidézhető.'
],
5:[
'A terméktervezési feladatok és az ügyfélinterjúk koordinálása. Kapcsolattartás a fejlesztői csapattal.',
'A kiszolgálóoldali fejlesztések és az adatbázis-módosítások karbantartása.',
'A napi működéshez szükséges beszerzések és a külső szolgáltatókkal való kapcsolattartás.',
'A felületek megtervezése, az új képernyők átadása és a megvalósítás ellenőrzése.',
'Adatfeldolgozási feladatok, rendszeres kimutatások és az importálási folyamat felügyelete.',
'Belső szervezési feladatok, új munkatársak belépésének előkészítése.',
'Ügyféligények felmérése és a kiadásra váró változtatások egyeztetése.',
'A webes felület karbantartása és a közös komponensek fejlesztése.',
'A működéshez szükséges dokumentáció és nyilvántartások rendben tartása.',
'A vizuális anyagok elkészítése és a dokumentációban használt ábrák frissítése.',
'Belső eszközök fejlesztése és a rendszeres adatellenőrzések automatizálása.',
'Kapcsolattartás az ügyfelekkel, a beérkező kérések továbbítása a felelős csapatnak.'
],
6:[
'Az első napokon szükséges hozzáférések, a csapat elérhetőségei és a rendszeres egyeztetések rendje.',
'A helyi környezet indításának lépései. Az adatbázist az alkalmazás első indításkor hozza létre.',
'A módosítást a szerzőtől eltérő kolléga nézi át. A megjegyzések lezárása után indulhat a beolvasztás.',
'Kiadás előtt ellenőrizni kell a nyitott hibákat, az adatbázis-változásokat és a visszaállítás lépéseit.',
'A következő időszakban a meglévő munkafolyamatok egyszerűsítése kap elsőbbséget. Az új igények a feladatlistába kerülnek.',
'A végpontok névkonvenciói, a hibaválaszok formátuma és a lapozási paraméterek használata.',
'A közös színek, űrlapmezők és táblázatok használata. Az eltérő állapotokat szöveggel is jelölni kell.',
'A bejelentés rögzítése után ki kell jelölni a felelőst. A lezáráskor az okot és a megtett lépéseket is rögzítjük.',
'A javításhoz olyan ellenőrzés tartozzon, amely az eredeti hibát újra előidézi. A tesztadatok ne érintsék a napi munkát.',
'Belső használatú jegyzet az adatkezelési és hozzáférési ellenőrzésekről. A változtatásokat külön egyeztetjük.',
'A modulok közötti hívások és az adatbázis-kapcsolat tervezete. Az átnézendő kérdések még nyitottak.',
'Belépéskor ellenőrizendő fiókok, eszközök és dokumentumok. A felelős jelzi, ha az adott pont elkészült.'
],
7:[
'Kiscsoportos alkalom egy termékötlet első változatának megtervezésére. A regisztráció szükséges.',
'Gyakorlati feladatok fájlfeldolgozással és adatbázis-kezeléssel. Saját laptopot érdemes hozni.',
'A műhely munkáinak bemutatása és kötetlen beszélgetés. A jelentkezőknek külön tájékoztatást küldünk.',
'Közös fejlesztési nap kisebb csapatokban. A feladatot az alkalom elején választják ki a résztvevők.',
'Adatok értelmezése és egyszerű ábrák készítése. A bemutatók után kérdésekre is jut idő.',
'Rövid szakmai bemutatók a felületfejlesztésben felmerülő gyakorlati problémákról.',
'Kerekasztal-beszélgetés a kutatási eredmények bemutatásáról és megismételhetőségéről.',
'Gyakorlati foglalkozás elkülönített tesztkörnyezetben. A résztvevők előzetes felkészítő anyagot kapnak.',
'Reggeli egyeztetés a folyamatban lévő munkákról. A programot az aktuális jelentkezésekhez igazítjuk.',
'A szervezők belső egyeztetése a helyszínről, a programról és a feladatok kiosztásáról.',
'A vetítés és a bemutatók ellenőrzése a rendezvény előtt. Az előadók jelenlétére számítunk.',
'Rövid összefoglaló az év munkáiról, majd kötetlen beszélgetés a résztvevőkkel.'
],
8:[
'Különálló faház fedett terasszal. A konyha önellátásra alkalmas, az udvaron parkolási lehetőség van.',
'Emeleti apartman külön hálószobával. A nappaliban étkező és kisebb konyhasarok található.',
'Egylégterű stúdió tetőtéri kialakítással. A bejutás lépcsőn történik, lift nincs.',
'Kertkapcsolatos vendégház saját bejárattal. A fedett kiülőt a vendégek önállóan használhatják.',
'Tágas szállás külön nappalival. Az ablakok a kert felé néznek; az érkezés időpontját előre egyeztetjük.',
'Udvarra néző lakás csendes épületben. Felszerelt konyha és külön fürdőszoba tartozik hozzá.',
'Átalakított műhelyépület nagy belmagasságú nappalival. A hálórész galérián kapott helyet.',
'Kisebb ház lejtős telken, terasszal. A bejáratot néhány lépcsőfokon lehet megközelíteni.',
'Önálló apartman kerttel és kiülővel. Az érkezés és a távozás részleteit foglaláskor egyeztetjük.',
'A szolgáltatói adatlap ellenőrzés alatt áll. Foglalás előtt a feltételeket külön szükséges egyeztetni.',
'A szállásadó belső feljegyzései és az adategyeztetéshez szükséges információk.',
'Két külön hálórészből és nappaliból álló apartman. Étkezőasztal és felszerelt konyha tartozik hozzá.'
],
9:[
'A bemutató után árajánlatot kértek a közös munkatér kialakítására. A kapcsolattartó a következő egyeztetésig pontosítja a létszámot.',
'A jelenlegi nyilvántartást szeretnék kiváltani. Először az importálható adatok körét kell tisztázni.',
'A felület bemutatása megtörtént. A döntéshez a bevezetési ütemtervet várják.',
'Az első megrendelést lezártuk. A további igényeket a használat tapasztalatai alapján egyeztetjük.',
'A megkeresést egyelőre nem követi megrendelés. A későbbi kapcsolatfelvételhez megtartjuk az egyeztetés jegyzeteit.',
'Új érdeklődés a riportolási funkciók iránt. Rövid bemutató időpontját egyeztetjük.',
'A csapat adatkezelési elvárásait megkaptuk. Az ajánlat előtt a jogosultsági szerepeket szükséges átbeszélni.',
'Az árajánlat elkészült, a visszajelzést várjuk. A bevezetéshez egy rövid oktatást is kértek.',
'A megrendelés visszaigazolása megérkezett. Az átadáshoz szükséges hozzáféréseket előkészítjük.',
'A tervezett beszerzést elhalasztották. Új megkeresés esetén a korábbi igényfelmérést lehet folytatni.',
'Első kapcsolatfelvétel a közös dokumentumtár használatáról. A résztvevők listája még nem végleges.',
'A technikai kérdéseket átbeszéltük. A következő lépés a részletes feladatlista jóváhagyása.'
],
10:[
'A belépési űrlap mezőit és hibajelzéseit kell rendezni. Az ellenőrzés mobilos ablakméretben is szükséges.',
'A végpontok kérés- és válaszmezőit össze kell vetni a kliens által használt adatokkal.',
'Az új mezők létrehozása mellé visszaállítási lépés és induláskori ellenőrzés szükséges.',
'A keskeny ablakban összecsúszó menüpontokat kell javítani. A kijelentkezés maradjon elérhető.',
'A fontosabb állapotváltozásokhoz követhető naplóbejegyzés kell. A személyes adatokat nem másoljuk a naplóba.',
'A korábban javított hibákhoz hiányzó teszteseteket kell összegyűjteni és beilleszteni.',
'A táblázatok és a hosszabb űrlapok ne lógjanak ki a képernyőről. A vízszintes görgetés a táblázaton belül maradjon.',
'A kiadáshoz tartozó változásokat és az indítás lépéseit a leírásban frissíteni kell.',
'A build eredménye és a kapcsolódó feladat legyen elérhető a projekt oldaláról.',
'A korábban kiosztott hozzáféréseket össze kell vetni az aktuális szerepkörökkel.',
'A levélfogadás és az adatbázisba mentés közötti adatút ellenőrzése, külön tesztpostafiókkal.',
'A hosszabb lekérdezéseket azonos adatokkal, ismételhető módon kell összehasonlítani.'
]}

def initialize():
    # Csak az előző változat változatlan alapleírásait cseréljük ki.
    for project,texts in DESCRIPTIONS.items():
        for item_id,description in enumerate(texts,1):
            row=query('SELECT body FROM items WHERE project=? AND id=?',(project,item_id))
            expected=f'{TITLES[project][item_id-1]} – kitalált laboradat. A rekord részletei megnyithatók, szerkesztési és hozzászólási munkafolyamatokkal. Tulajdonos: {"Anna" if item_id%2==0 else "Béla"}.'
            if row and row[0]['body']==expected:
                query('UPDATE items SET body=? WHERE project=? AND id=?',(description,project,item_id))
    query('UPDATE profiles SET bio=? WHERE project=1 AND bio=?',('A csapat tagja.','A helyi labor közösségének tagja.'))
    for old,new in [('Fiktív Erdőliget','Erdőliget'),('Fiktív Tófalva','Tófalva'),('Fiktív Kertváros','Kertváros')]:
        query('UPDATE properties SET city=? WHERE city=?',(new,old))
    query('UPDATE contacts SET company=? WHERE company=?',('Műhely','Fiktív Műhely'))
    query('UPDATE mail SET body=? WHERE body=?',('<p>Meghívunk a következő szakmai napra. A programot a rendezvények között találod.</p>','<p>Helyi tesztmeghívó. A részletek az EventDesk alkalmazásban találhatók.</p>'))
