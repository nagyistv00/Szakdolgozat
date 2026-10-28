"""Összetettebb, alkalmazásspecifikus SQLi/XSS laborfolyamatok.
A VULN megjegyzések jelzik a szándékos hibákat. Nincs külső célpont.
"""
import csv
import io
import json
import re
from datetime import date
from urllib.parse import quote
from core import query, table, LOCK
from platform_lab import esc, form

SCHEMAS=[
'CREATE TABLE IF NOT EXISTS profiles (project INTEGER, account_id INTEGER, display_name TEXT, bio TEXT, PRIMARY KEY(project,account_id))',
'CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, owner_id INTEGER, name TEXT, email TEXT, company TEXT)',
'CREATE TABLE IF NOT EXISTS products (item_id INTEGER PRIMARY KEY, sku TEXT, category TEXT, stock INTEGER)',
'CREATE TABLE IF NOT EXISTS carts (owner_id INTEGER, item_id INTEGER, quantity INTEGER, PRIMARY KEY(owner_id,item_id))',
'CREATE TABLE IF NOT EXISTS coupons (owner_id INTEGER, code TEXT, scope TEXT, discount INTEGER, PRIMARY KEY(owner_id,code))',
'CREATE TABLE IF NOT EXISTS purchases (id INTEGER PRIMARY KEY, owner_id INTEGER, total INTEGER, snapshot TEXT)',
'CREATE TABLE IF NOT EXISTS tickets (item_id INTEGER PRIMARY KEY, priority INTEGER, assignee TEXT, sla_hours INTEGER)',
'CREATE TABLE IF NOT EXISTS employees (item_id INTEGER PRIMARY KEY, department TEXT, salary INTEGER, location TEXT, leave_days INTEGER)',
'CREATE TABLE IF NOT EXISTS wiki_revisions (id INTEGER PRIMARY KEY, item_id INTEGER, author_id INTEGER, content TEXT, state TEXT)',
'CREATE TABLE IF NOT EXISTS speakers (id INTEGER PRIMARY KEY, owner_id INTEGER, name TEXT, topic TEXT, bio TEXT, state TEXT)',
'CREATE TABLE IF NOT EXISTS properties (item_id INTEGER PRIMARY KEY, city TEXT, beds INTEGER, amenities TEXT)',
'CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, owner_id INTEGER, item_id INTEGER, guest TEXT, nights INTEGER, total INTEGER)',
'CREATE TABLE IF NOT EXISTS crm_reports (owner_id INTEGER, name TEXT, template TEXT, PRIMARY KEY(owner_id,name))',
'CREATE TABLE IF NOT EXISTS builds (id INTEGER PRIMARY KEY, owner_id INTEGER, task_id INTEGER, branch TEXT, log TEXT, status TEXT)',
'CREATE TABLE IF NOT EXISTS audit_events (id INTEGER PRIMARY KEY, project INTEGER, actor TEXT, action TEXT, detail TEXT)',
]

def initialize():
    for sql in SCHEMAS: query(sql)
    for uid,name in [(1,'Anna'),(2,'Béla'),(3,'Admin')]:
        query('INSERT INTO profiles VALUES (?,?,?,?) ON CONFLICT(project,account_id) DO NOTHING',(1,uid,name,'A csapat tagja.'))
        query('INSERT INTO contacts VALUES (?,?,?,?,?) ON CONFLICT(id) DO NOTHING',(uid,1,name,name.lower().replace('é','e')+'@example.test','Műhely'))
    for i in range(1,13):
        query('INSERT INTO products VALUES (?,?,?,?) ON CONFLICT(item_id) DO NOTHING',(i,f'ML-{i:04d}',['office','tech','accessory'][i%3],5+i))
        query('INSERT INTO tickets VALUES (?,?,?,?) ON CONFLICT(item_id) DO NOTHING',(i,1+i%3,'anna' if i%2==0 else 'bela',4*(1+i%3)))
        query('INSERT INTO employees VALUES (?,?,?,?,?) ON CONFLICT(item_id) DO NOTHING',(i,['Design','Engineering','Operations'][i%3],450000+i*35000,['Debrecen','Budapest','Remote'][i%3],20+i%6))
        query('INSERT INTO properties VALUES (?,?,?,?) ON CONFLICT(item_id) DO NOTHING',(i,['Erdőliget','Tófalva','Kertváros'][i%3],2+i%4,'Wi-Fi, konyha, kert'))
    if not query('SELECT id FROM speakers'):
        query('INSERT INTO speakers VALUES (?,?,?,?,?,?)',(1,1,'Kovács Anna','Közös tervezés','Terméktervezés és csapatmunka.','published'))
    if not query('SELECT id FROM builds'):
        query('INSERT INTO builds VALUES (?,?,?,?,?,?)',(1,1,2,'main','Build started\nTests passed\nArtifact ready','success'))

def audit(p,actor,action,detail):
    query('INSERT INTO audit_events(project,actor,action,detail) VALUES (?,?,?,?)',(p,actor,action,detail))

def head(kicker,title,description):
    return '<div class="page-head"><div><span class="eyebrow">'+esc(kicker)+'</span><h1>'+esc(title)+'</h1><p class="muted">'+esc(description)+'</p></div></div>'

def choice(name,values):
    return '<select name="'+name+'">'+''.join('<option value="'+esc(v)+'">'+esc(label)+'</option>' for v,label in values)+'</select>'

def control(): return '<details class="test-options"><summary>Tesztbeállítások</summary><label><input type="checkbox" name="safe" value="1">Kontroll</label></details>'

def handle(p,sub,params,method,account):
    uid=account['id']; safe=params.get('safe')=='1'; pre=f'/p{p:02d}'
    render=esc if safe else str
    if p==1 and sub in ('profile','moderation'):
        if sub=='moderation':
            if account['role']!='admin': return 403,'<p>Moderátori szerep szükséges. Lépj be az admin fiókkal.</p>'
            rows=query('SELECT p.display_name,p.bio,a.username FROM profiles p JOIN accounts a ON a.project=p.project AND a.id=p.account_id WHERE p.project=1')
            # VULN: a mentett profilnév HTML attribútumkörnyezetbe kerül.
            body=''.join('<article data-author="'+render(r['display_name'])+'"><h3>'+esc(r['username'])+'</h3><p>'+render(r['bio'])+'</p></article>' for r in rows)
            return 200,head('SocialHub / Moderáció','Moderációs várólista','A tagok által megadott nevek és bemutatkozások.')+'<a href="?safe=1">Szöveges nézet</a>'+body
        if method=='POST':
            query('UPDATE profiles SET display_name=?,bio=? WHERE project=1 AND account_id=?',(params.get('display_name',''),params.get('bio',''),uid))
            audit(1,account['username'],'profile.updated',params.get('display_name',''))
        profile=query('SELECT * FROM profiles WHERE project=1 AND account_id=?',(uid,))[0]
        fields='<label>Megjelenített név<input name="display_name" value="'+esc(profile['display_name'])+'"></label><textarea name="bio">'+esc(profile['bio'])+'</textarea>'
        return 200,head('SocialHub / Profil','Profil szerkesztése','A megjelenített nevedet és a bemutatkozásodat itt módosíthatod.')+'<div class="subgrid"><section class="panel">'+form(fields,'Profil mentése')+'</section><aside class="panel"><h3>Moderáció</h3><p>A profilváltozások megjelennek a moderátor felületén.</p><a href="'+pre+'/moderation">Moderációs nézet</a></aside></div>'
    if p==2 and sub=='contacts':
        if method=='POST':
            query('INSERT INTO contacts(owner_id,name,email,company) VALUES (?,?,?,?)',(uid,params.get('name',''),params.get('email',''),params.get('company','')))
        q=params.get('q','')
        base='SELECT c.name,c.email,c.company,COUNT(m.subject) AS message_count FROM contacts c LEFT JOIN mail m ON m.sender=c.email AND m.project=2 WHERE c.owner_id=? AND '
        if safe: rows=query(base+'c.name LIKE ? GROUP BY c.id',(uid,'%'+q+'%'))
        else: rows=query(base+"c.name LIKE '%"+q+"%' GROUP BY c.id",(uid,)) # VULN: SQLi JOIN + aggregáció előtt.
        return 200,head('LocalMail / Címjegyzék','Kapcsolatok és levelezési előzmények','Keresés név szerint, a korábbi levelek számával.')+'<div class="panel"><form><input name="q" value="'+esc(q)+'" placeholder="Kapcsolat neve">'+control()+'<button>Keresés</button></form>'+table(rows)+'</div><div class="panel"><h2>Új kapcsolat</h2>'+form('<input name="name" placeholder="Név"><input name="email" placeholder="Email"><input name="company" placeholder="Cég">','Hozzáadás')+'</div>'
    if p==3 and sub=='checkout':
        if 'add' in params:
            item_id=int(params['add'])
            if not query('SELECT item_id FROM products WHERE item_id=?',(item_id,)): return 404,'Nincs ilyen termék.'
            query('INSERT INTO carts VALUES (?,?,1) ON CONFLICT(owner_id,item_id) DO UPDATE SET quantity=carts.quantity+1',(uid,item_id))
        if method=='POST' and params.get('action')=='coupon':
            discount=max(0,min(50,int(params.get('discount','10'))))
            query('INSERT INTO coupons VALUES (?,?,?,?) ON CONFLICT(owner_id,code) DO UPDATE SET scope=excluded.scope,discount=excluded.discount',(uid,params.get('code','LOCAL10'),params.get('scope','tech'),discount))
        if method=='POST' and params.get('action')=='quantity':
            quantity=int(params.get('quantity','1'))
            if not 0<=quantity<=100: return 400,'Érvénytelen mennyiség.'
            query('UPDATE carts SET quantity=? WHERE owner_id=? AND item_id=?',(quantity,uid,int(params['id'])))
        cart=query('SELECT i.id,i.title,i.amount,p.category,p.stock,c.quantity FROM carts c JOIN items i ON i.project=3 AND i.id=c.item_id JOIN products p ON p.item_id=i.id WHERE c.owner_id=? AND c.quantity>0',(uid,))
        coupon=params.get('coupon',''); discount=0; eligible=[]
        found=query('SELECT * FROM coupons WHERE owner_id=? AND code=?',(uid,coupon))
        if found:
            cp=found[0]
            base='SELECT p.item_id FROM products p JOIN carts c ON c.item_id=p.item_id WHERE c.owner_id=? AND '
            if safe: eligible=query(base+'p.category=?',(uid,cp['scope']))
            else: eligible=query(base+"p.category='"+cp['scope']+"'",(uid,)) # VULN: tárolt kuponszabályból second-order SQLi.
            ids={x['item_id'] for x in eligible}
            discount=sum(r['amount']*r['quantity']*cp['discount']//100 for r in cart if r['id'] in ids)
        total=sum(r['amount']*r['quantity'] for r in cart)-discount
        notice=''
        if method=='POST' and params.get('action')=='confirm':
            with LOCK:
                if not cart: return 400,'Üres a kosár.'
                if any(r['quantity']>query('SELECT stock FROM products WHERE item_id=?',(r['id'],))[0]['stock'] for r in cart): return 409,'Nincs elegendő készlet.'
                query('INSERT INTO purchases(owner_id,total,snapshot) VALUES (?,?,?)',(uid,total,json.dumps(cart,ensure_ascii=False)))
                for r in cart: query('UPDATE products SET stock=stock-? WHERE item_id=?',(r['quantity'],r['id']))
                query('DELETE FROM carts WHERE owner_id=?',(uid,))
            notice='<p class="notice">A megrendelést rögzítettük.</p>'
            cart=[]
        rows=table(cart)
        purchase_rows=query('SELECT id,total FROM purchases WHERE owner_id=? ORDER BY id DESC',(uid,))
        body=head('MarketLab / Checkout','Kosár','Ellenőrizd a tételeket és a szállítás előtti összeget.')+notice
        body+='<div class="subgrid"><section><div class="panel">'+rows+form('<input type="hidden" name="action" value="quantity"><label>Termékazonosító<input name="id" type="number" value="1"></label><label>Mennyiség<input name="quantity" type="number" value="1"></label>','Mennyiség frissítése')+'</div><details class="panel"><summary>Kupon beállítása</summary>'+form('<input type="hidden" name="action" value="coupon"><label>Kuponkód<input name="code" value="LOCAL10"></label><label>Termékkategória<input name="scope" value="tech"></label><label>Kedvezmény (%)<input name="discount" type="number" value="10"></label>','Szabály mentése')+'</details><div class="panel"><h3>Korábbi megrendelések</h3>'+table(purchase_rows)+'</div></section><aside class="panel"><h2>Összesítő</h2><form><input name="coupon" value="'+esc(coupon)+'" placeholder="Kupon">'+control()+'<button>Alkalmazás</button></form><p>Kedvezmény: <b>'+str(discount)+' Ft</b></p><p class="price">'+str(total)+' Ft</p>'+form('<input type="hidden" name="action" value="confirm"><input type="hidden" name="coupon" value="'+esc(coupon)+'">'+('<input type="hidden" name="safe" value="1">' if safe else ''),'Megrendelés rögzítése')+'</aside></div>'
        return 200,body
    if p==4 and sub=='triage':
        priority=params.get('priority','1')
        if safe:
            try: priority=int(priority)
            except ValueError: return 400,'A kontroll prioritása egész szám.'
            rows=query('SELECT COUNT(*) AS matches FROM tickets t JOIN items i ON i.project=4 AND i.id=t.item_id WHERE t.priority=?',(priority,))
        else:
            # VULN: csak darabszám látszik; boolean-based SQLi reprodukálható.
            rows=query('SELECT COUNT(*) AS matches FROM tickets t JOIN items i ON i.project=4 AND i.id=t.item_id WHERE t.priority='+str(priority))
        if method=='POST':
            query('UPDATE tickets SET assignee=? WHERE item_id=?',(params.get('assignee','anna'),int(params.get('id','1'))))
            audit(4,account['username'],'ticket.assigned',params.get('note',''))
        audit_rows=query('SELECT actor,action,detail FROM audit_events WHERE project=4 ORDER BY id DESC LIMIT 20')
        logs=''.join('<article><b>'+esc(r['actor'])+'</b> · '+esc(r['action'])+'<p>'+render(r['detail'])+'</p></article>' for r in audit_rows)
        return 200,head('HelpDesk / Triage','Prioritás és kiosztás','Szűrés prioritás szerint és hibajegyek kiosztása.')+'<div class="grid g2"><section class="panel"><form><label>Prioritás<input name="priority" aria-label="Prioritás" value="'+esc(priority)+'"></label>'+control()+'<button>Ellenőrzés</button></form><h2>Találatok: <span id="matches">'+str(rows[0]['matches'])+'</span></h2>'+table(query('SELECT t.item_id,t.priority,t.assignee,t.sla_hours FROM tickets t ORDER BY t.priority DESC'))+'</section><section><div class="panel"><h2>Hibajegy kiosztása</h2>'+form('<label>Hibajegy azonosítója<input name="id" value="1"></label><label>Ügyintéző<input name="assignee" value="anna"></label><textarea name="note" placeholder="Belső megjegyzés"></textarea>','Kiosztás és naplózás')+'</div><h3>Auditnapló</h3>'+logs+'</section></div>'
    if p==5 and sub=='payroll':
        sort=params.get('sort','salary DESC')
        allowed={'salary DESC','salary ASC','department','title'}
        if safe and sort not in allowed: return 400,'Nem engedélyezett rendezési kulcs.'
        # VULN: ORDER BY kifejezés-injekció, nem egyszerű idézőjel lezárás.
        sql='SELECT i.id,i.title,e.department,e.salary,e.location,e.leave_days FROM employees e JOIN items i ON i.project=5 AND i.id=e.item_id ORDER BY '+sort
        rows=query(sql)
        return 200,head('PeopleOps / HR analytics','Bér- és létszámriport','Munkatársak, részlegek és a nyilvántartott havi bérek.')+'<div class="panel"><form><label>Rendezés<input name="sort" value="'+esc(sort)+'"></label>'+control()+'<button>Riport frissítése</button></form>'+table(rows)+'</div><div class="notice">Az összegek forintban szerepelnek.</div>'
    if p==6 and sub=='editor':
        item_id=int(params.get('id','2'))
        row=query('SELECT * FROM items WHERE project=6 AND id=?',(item_id,))
        if not row: return 404,'Nincs ilyen wiki oldal.'
        row=row[0]
        if method=='POST':
            if row['owner_id']!=uid and account['role']!='admin': return 403,'Csak a tulajdonos vagy admin szerkeszthet.'
            if params.get('action')=='publish':
                revision=query('SELECT * FROM wiki_revisions WHERE id=? AND item_id=?',(int(params['revision']),item_id))
                if revision:
                    query('UPDATE wiki_revisions SET state=? WHERE id=?',('published',revision[0]['id']))
                    query('UPDATE items SET body=? WHERE project=6 AND id=?',(revision[0]['content'],item_id))
            else:
                content=params.get('content','')
                # VULN: script tagek eltávolítása nem HTML sanitizálás (event attribútumok maradnak).
                cleaned=re.sub(r'<script\b[^>]*>.*?</script\s*>','',content,flags=re.I|re.S)
                query('INSERT INTO wiki_revisions(item_id,author_id,content,state) VALUES (?,?,?,?)',(item_id,uid,cleaned,'draft'))
        revisions=query('SELECT * FROM wiki_revisions WHERE item_id=? ORDER BY id DESC',(item_id,))
        history=''.join('<article><span class="badge">'+esc(r['state'])+'</span><h3>Változat #'+str(r['id'])+'</h3><div>'+render(r['content'])+'</div>'+form('<input type="hidden" name="id" value="'+str(item_id)+'"><input type="hidden" name="revision" value="'+str(r['id'])+'"><input type="hidden" name="action" value="publish">','Publikálás')+'</article>' for r in revisions)
        body=head('TeamWiki / Editor','Oldalszerkesztő','A mentett piszkozatot ellenőrzés után tudod közzétenni.')
        body+='<div class="grid g2"><section class="panel">'+form('<input name="id" type="number" value="'+str(item_id)+'"><textarea name="content">'+esc(row['body'])+'</textarea>','Piszkozat mentése')+'</section><section><a href="?id='+str(item_id)+'&safe=1">Szöveges nézet</a>'+history+'</section></div>'
        return 200,body
    if p==7 and sub=='speakers':
        if method=='POST' and params.get('action')=='publish':
            query('UPDATE speakers SET state=? WHERE id=? AND owner_id=?',('published',int(params['id']),uid))
        elif method=='POST':
            parsed=list(csv.DictReader(io.StringIO(params.get('csv',''))))
            if len(parsed)>100: return 400,'Legfeljebb 100 előadó importálható.'
            for row in parsed:
                if not all(k in row for k in ('name','topic','bio')): return 400,'Kötelező oszlopok: name,topic,bio.'
                query('INSERT INTO speakers(owner_id,name,topic,bio,state) VALUES (?,?,?,?,?)',(uid,row['name'],row['topic'],row['bio'],'draft'))
        rows=query('SELECT * FROM speakers ORDER BY id DESC')
        # VULN: külső CSV → paraméterezett tárolás → publikált program HTML.
        program=''.join('<article><span class="badge">'+esc(r['state'])+'</span><h2>'+esc(r['name'])+'</h2><h3>'+esc(r['topic'])+'</h3><div>'+render(r['bio'])+'</div>'+ (form('<input type="hidden" name="action" value="publish"><input type="hidden" name="id" value="'+str(r['id'])+'">','Programba publikálás') if r['state']=='draft' and r['owner_id']==uid else '')+'</article>' for r in rows if r['state']=='published' or r['owner_id']==uid)
        example='name,topic,bio\nNagy Béla,Prototípusépítés,A műhely gyakorlati tapasztalatai.'
        return 200,head('EventDesk / Program','Előadók és program','Új előadók feltöltése és a program összeállítása.')+'<div class="subgrid"><section>'+program+'</section><aside class="panel"><h3>Előadók importja</h3>'+form('<textarea name="csv">'+esc(example)+'</textarea>','CSV importálása')+'<a href="?safe=1">Szöveges nézet</a></aside></div>'
    if p==8 and sub=='quote':
        item_id=int(params.get('id','1'))
        item=query('SELECT i.*,p.city,p.beds,p.amenities FROM items i JOIN properties p ON p.item_id=i.id WHERE i.project=8 AND i.id=?',(item_id,))
        if not item: return 404,'Ismeretlen szállás.'
        item=item[0]
        guest=params.get('guest','Anna'); start=params.get('start','2026-12-01'); end=params.get('end','2026-12-03')
        try: nights=(date.fromisoformat(end)-date.fromisoformat(start)).days
        except ValueError: return 400,'Érvénytelen dátum.'
        if not 1<=nights<=60: return 400,'1–60 éjszaka választható.'
        total=item['amount']*nights
        if method=='POST': query('INSERT INTO quotes(owner_id,item_id,guest,nights,total) VALUES (?,?,?,?,?)',(uid,item_id,guest,nights,total))
        # VULN: inline JSON adatba interpolált vendégnév; a JSON quoting önmagában nem HTML-safe.
        data=json.dumps({'guest':guest,'total':total},ensure_ascii=False)
        if safe: data=data.replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        fields='<input name="id" type="hidden" value="'+str(item_id)+'"><label>Vendég<input name="guest" value="'+esc(guest)+'"></label><label>Érkezés<input type="date" name="start" value="'+esc(start)+'"></label><label>Távozás<input type="date" name="end" value="'+esc(end)+'"></label>'+control()
        output='<script id="quote-data" type="application/json">'+data+'</script><div id="quote-greeting"></div><script>const d=JSON.parse(document.getElementById("quote-data").textContent);document.getElementById("quote-greeting").textContent="Ajánlat: "+d.guest+" / "+d.total+" Ft";</script>'
        return 200,head('StayLab / Személyes ajánlat',item['title'],item['city']+' · '+str(item['beds'])+' férőhely')+'<div class="subgrid"><section class="panel"><h2>Szállásadatok</h2><p>'+esc(item['amenities'])+'</p>'+form(fields,'Ajánlat mentése')+'</section><aside class="panel"><h2>'+str(nights)+' éjszaka</h2><p class="price">'+str(total)+' Ft</p>'+output+'<a href="'+pre+'/workflow">Foglalás</a></aside></div>'
    if p==9 and sub=='analytics':
        if method=='POST':
            query('INSERT INTO crm_reports VALUES (?,?,?) ON CONFLICT(owner_id,name) DO UPDATE SET template=excluded.template',(uid,params.get('name','pipeline'),params.get('template','<h2>Pipeline riport</h2>')))
        reports=query('SELECT name,template FROM crm_reports WHERE owner_id=?',(uid,))
        body=head('SalesFlow / Analytics','Riportsablonok','Mentett fejlécek és az ügyféllista nyomtatási előnézete.')
        body+='<div class="grid g2"><section class="panel">'+form('<input name="name" value="pipeline"><textarea name="template"><h2>Értékesítési összefoglaló</h2></textarea>','Sablon mentése')+'</section><section class="panel"><h2>Mentett sablonok</h2>'+''.join('<p><a href="?run='+quote(r['name'],safe='')+'">'+esc(r['name'])+'</a></p>' for r in reports)+'</section></div>'
        selected=[r for r in reports if r['name']==params.get('run')]
        if selected:
            # VULN: riportfejléc egy teljes HTML dokumentum srcdoc attribútumába kerül.
            doc=selected[0]['template']+table(query('SELECT title,status,amount FROM items WHERE project=9 ORDER BY amount DESC'))
            if safe: doc='<pre>'+esc(doc)+'</pre>'
            body+='<section class="panel"><h2>Export előnézet</h2><iframe title="Riport előnézet" style="width:100%;height:500px;border:1px solid #ddd" srcdoc="'+esc(doc)+'"'+(' sandbox=""' if safe else '')+'></iframe><p><a href="?run='+quote(selected[0]['name'],safe='')+'&safe=1">Szöveges nézet</a></p></section>'
        return 200,body
    if p==10 and sub=='integrations':
        error=''
        if method=='POST':
            try: payload=json.loads(params.get('payload','{}'))
            except json.JSONDecodeError: return 400,'Érvénytelen JSON.'
            task=int(payload.get('task_id',1))
            if not query('SELECT id FROM items WHERE project=10 AND id=?',(task,)): return 404,'Ismeretlen feladat.'
            query('INSERT INTO builds(owner_id,task_id,branch,log,status) VALUES (?,?,?,?,?)',(uid,task,str(payload.get('branch','main')),str(payload.get('log','')),str(payload.get('status','success'))))
            audit(10,account['username'],'webhook.received',str(payload.get('branch','main')))
        builds=query('SELECT * FROM builds ORDER BY id DESC')
        # VULN: webhookból jött ANSI log konverter csak színkódot távolít el, HTML-t nem escape-el.
        logs=''.join('<article><div class="row between"><h3>'+esc(b['branch'])+' · Build #'+str(b['id'])+'</h3><span class="badge">'+esc(b['status'])+'</span></div><pre>'+render(re.sub(r'\x1b\[[0-9;]*m','',b['log']))+'</pre><a href="'+pre+'/item?id='+str(b['task_id'])+'">Feladat megnyitása</a></article>' for b in builds)
        payload=json.dumps({'task_id':1,'branch':'feature/login','status':'success','log':'Build started\nTests passed\nArtifact ready'},indent=2)
        return 200,head('BuildBoard / Integrations','Buildnapló','A beérkezett buildértesítések és a hozzájuk tartozó kimenet.')+'<div class="subgrid"><section>'+logs+'</section><aside class="panel"><h2>Értesítés beküldése</h2>'+form('<textarea name="payload" style="height:260px;font-family:monospace">'+esc(payload)+'</textarea>','Beküldés')+'<a href="?safe=1">Szöveges nézet</a></aside></div>'
    return None
