"""Kizárólag kitalált, reprodukálható helyi tesztadatok."""
from core import query

TITLES={
1:['Megérkezett a közösségi munkatér','Min dolgozik most a termékcsapat?','Pénteki közös ötletelés','Új kollégák a műhelyben','Könyvajánló: a hét olvasmánya','Így készült a prototípus','Kérdezz a fejlesztőktől','Közös tanulás, közös siker','A hét pillanatai','Moderátori megjegyzések','Belső kommunikációs terv','Még nem publikált történet'],
2:['Üdvözlő levél','Heti összefoglaló','Találkozó visszaigazolása','Megrendelési értesítő','Csapatfrissítés','Szabadság visszaigazolása','Emlékeztető','Projektátadás','Ügyfélválasz','Belső sablon','Titkos tervezet','Adminisztrációs értesítő'],
3:['Kerámia asztali lámpa','Mechanikus billentyűzet','Vászon hátizsák','Acél termosz','Fa monitortartó','Vezeték nélküli egér','Jegyzetfüzet szett','USB-C dokkoló','Asztali növénytartó','Prototípus fejhallgató','Belső beszerzési csomag','Raktári mintatermék'],
4:['Nem érkezik meg az értesítés','Nem működik a fájlfeltöltés','Hibás összeg a kimutatásban','Új csapattag hozzáadása','Lassú jelentésbetöltés','Lejárt meghívó','Helytelen dátum a naptárban','Számlázási kérdés','Belépési probléma','Belső jogosultsági vizsgálat','Tervezett karbantartás','Reprodukálható UI hiba'],
5:['Kovács Anna','Nagy Béla','Szabó Csilla','Tóth Dóra','Varga Erik','Kiss Fanni','Balogh Gábor','Fekete Hanna','Molnár Imre','Papp Júlia','Lakatos Károly','Horváth Luca'],
6:['Üdvözlünk a csapatban','Fejlesztői környezet','Kódellenőrzési útmutató','Release folyamat','Termékstratégia','API konvenciók','Design rendszer','Incidenskezelés','Tesztelési irányelvek','Belső biztonsági jegyzet','Architektúra tervezet','Onboarding ellenőrzőlista'],
7:['Terméktervező workshop','Python gyakorlati nap','Nyílt műhely','Közösségi hackathon','Adatvizualizációs est','Frontend meetup','Kutatói kerekasztal','Biztonsági labor','Alkotói reggeli','Szervezői egyeztetés','Technikai főpróba','Évzáró találkozó'],
8:['Erdei faház','Folyóparti apartman','Tetőtéri stúdió','Kerti vendégház','Panoráma lakosztály','Csendes városi lakás','Műhelyből loft','Domboldali házikó','Tóparti pihenő','Teszt szállásegység','Belső szolgáltatói adatlap','Családi apartman'],
9:['Fiktív Menta Stúdió','Fiktív Orion Műhely','Fiktív Kavics Design','Fiktív Boróka Labor','Fiktív Papírkert','Fiktív Észak Projekt','Fiktív Kobalt Csapat','Fiktív Csend Tér','Fiktív Mozaik Bolt','Fiktív Vonal Csoport','Fiktív Tölgy Tervező','Fiktív Pixel Udvar'],
10:['Belépési képernyő átdolgozása','API szerződés felülvizsgálata','Adatbázis-migráció','Navigáció javítása','Naplózási modul','Egységtesztek bővítése','Mobilnézet javítása','Release dokumentáció','CI állapotjelző','Belső hozzáférések áttekintése','Integrációs tesztek','Teljesítménymérés']}

def initialize():
    query('CREATE TABLE IF NOT EXISTS app_migrations (version TEXT PRIMARY KEY)')
    if query('SELECT version FROM app_migrations WHERE version = ?',('v2-realistic-seed',)): return
    for p,titles in TITLES.items():
        for i,title in enumerate(titles,1):
            states={4:['open','progress','closed'],5:['active','leave','active'],9:['lead','qualified','proposal','won','lost'],10:['open','progress','done']}.get(p,['published','published','draft'])
            status=states[(i-1)%len(states)]
            if i>=10 and p not in (4,5,9,10): status='internal'
            amount=(80000+i*27500 if p==9 else 4900+i*2100 if p==8 else i*1490)
            body=f'{title} – kitalált laboradat. A rekord részletei megnyithatók, szerkesztési és hozzászólási munkafolyamatokkal. Tulajdonos: {"Anna" if i%2==0 else "Béla"}.'
            query('UPDATE items SET title=?,body=?,status=?,amount=? WHERE project=? AND id=?',(title,body,status,amount,p,i))
    for subject,sender,body in [('Projektindító egyeztetés','bela@example.test','<p>Szia Anna!</p><p>A közös műhely projektindító anyaga elkészült. Kérlek, nézd át a feladatokat.</p>'),('Heti csapatösszefoglaló','admin@example.test','<h3>A hét eredményei</h3><p>Elkészült a prototípus és a tesztterv.</p>'),('Meghívó a szakmai napra','bela@example.test','<p>Helyi tesztmeghívó. A részletek az EventDesk alkalmazásban találhatók.</p>')]:
        query('INSERT INTO mail VALUES (?,?,?,?,?)',(2,'anna@example.test',sender,subject,body))
    query('INSERT INTO app_migrations VALUES (?)',('v2-realistic-seed',))
