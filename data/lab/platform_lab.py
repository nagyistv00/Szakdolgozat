"""Többlépéses üzleti munkafolyamatok, szándékos SQLi és XSS pontokkal."""
import hashlib
import html
import secrets
from core import query, page, table, transaction
from contextlib import nullcontext

SESSIONS = {}

def esc(value): return html.escape(str(value), quote=True)

def setup():
    statements = [
        'CREATE TABLE IF NOT EXISTS accounts (project INTEGER, id INTEGER, username TEXT, password_hash TEXT, role TEXT, PRIMARY KEY(project,id))',
        'CREATE TABLE IF NOT EXISTS items (project INTEGER, id INTEGER, owner_id INTEGER, title TEXT, body TEXT, status TEXT, amount INTEGER, PRIMARY KEY(project,id))',
        'CREATE TABLE IF NOT EXISTS notes (project INTEGER, item_id INTEGER, author_id INTEGER, body TEXT)',
        'CREATE TABLE IF NOT EXISTS saved_filters (project INTEGER, owner_id INTEGER, name TEXT, expression TEXT, PRIMARY KEY(project,owner_id,name))',
        'CREATE TABLE IF NOT EXISTS orders (project INTEGER, owner_id INTEGER, item_id INTEGER, quantity INTEGER)',
        'CREATE TABLE IF NOT EXISTS mail (project INTEGER, recipient TEXT, sender TEXT, subject TEXT, body TEXT)',
    ]
    for sql in statements: query(sql)
    from workflows import initialize as workflow_setup
    workflow_setup()
    for p in range(1,11):
        for i,name,role in [(1,'anna','user'),(2,'bela','user'),(3,'admin','admin')]:
            digest=hashlib.sha256(('LabPass123!:'+name).encode()).hexdigest()
            query('INSERT INTO accounts VALUES (?,?,?,?,?) ON CONFLICT(project,id) DO NOTHING',(p,i,name,digest,role))
        for i in range(1,13):
            query('INSERT INTO items VALUES (?,?,?,?,?,?,?) ON CONFLICT(project,id) DO NOTHING',
                  (p,i,1+(i%2),f'{CONFIG[p]["entity"]} #{i}',f'Kitalált tesztrekord {i}. Részletes leírás, hozzászólásokkal és állapotkezeléssel.', 'published' if i<10 else 'internal',i*1490))
        if not query('SELECT * FROM mail WHERE project = ?',(p,)):
            query('INSERT INTO mail VALUES (?,?,?,?,?)',(p,'anna@example.test','bela@example.test','Labor értesítés','Ez egy helyi, kitalált tesztlevél.'))

CONFIG = {
1:dict(title='SocialHub – közösségi média',entity='Bejegyzés',action='Közzététel',states=['published','draft','internal'],description='Profilok, hírfolyam, bejegyzések, hozzászólások és mentett keresések.'),
2:dict(title='LocalMail – helyi levelező',entity='Levélsablon',action='Sablon mentése',states=['published','draft','internal'],description='Beérkező levelek, levélírás, HTML megjelenítés és helyi SMTP fogadás.'),
3:dict(title='MarketLab – webáruház',entity='Termék',action='Termék létrehozása',states=['published','sold','internal'],description='Termékkatalógus, kosár, rendelések és termékértékelések.'),
4:dict(title='HelpDesk – ügyfélszolgálat',entity='Hibajegy',action='Hibajegy nyitása',states=['open','progress','closed'],description='Hibajegyek, válaszok, státuszváltás és ügyintézői riport.'),
5:dict(title='PeopleOps – HR portál',entity='Munkatársi adatlap',action='Adatlap létrehozása',states=['active','leave','internal'],description='Munkatársi adatlapok, megjegyzések és belső listák.'),
6:dict(title='TeamWiki – tudásbázis',entity='Wiki oldal',action='Oldal létrehozása',states=['published','draft','archived'],description='Cikkek, szerkesztés, véleményezés és HTML előnézet.'),
7:dict(title='EventDesk – rendezvénykezelő',entity='Rendezvény',action='Rendezvény létrehozása',states=['published','full','closed'],description='Rendezvények, regisztrációk, szervezői üzenetek és résztvevői riport.'),
8:dict(title='StayLab – szállásfoglalás',entity='Szállás',action='Szállás felvétele',states=['available','reserved','closed'],description='Szálláskereső, foglalások, leírások és vendégértékelések.'),
9:dict(title='SalesFlow – CRM',entity='Ügyfél',action='Ügyfél felvétele',states=['lead','active','closed'],description='Ügyféladatlapok, értékesítési megjegyzések és mentett riportok.'),
10:dict(title='BuildBoard – projektkezelő',entity='Feladat',action='Feladat felvétele',states=['open','progress','done'],description='Feladatok, felelősök, státuszváltás, hozzászólások és csapatriport.'),
}

def form(fields,button='Mentés',action=''):
    return f'<form method="post" action="{esc(action)}">'+fields+f'<button>{esc(button)}</button></form>'

def handle(p,sub,params,method,account):
    c=CONFIG[p]; prefix=f'/p{p:02d}'
    title=c['title']
    from ui import render as render_ui
    def page(title, body): return render_ui(p,title,body,account,sub)
    nav=''
    # A kontroll kapcsoló minden megjelenítési útvonalon külön választandó.
    safe=params.get('safe')=='1'
    render=esc if safe else str
    if sub=='login':
        if method=='POST':
            rows=query('SELECT * FROM accounts WHERE project = ? AND username = ?',(p,params.get('username','')))
            digest=hashlib.sha256((params.get('password','')+':'+params.get('username','')).encode()).hexdigest()
            if rows and secrets.compare_digest(rows[0]['password_hash'],digest):
                token=secrets.token_urlsafe(32); SESSIONS[token]=rows[0]
                return 303,{'Location':prefix+'/','Set-Cookie':f'lab_session_{p}={token}; Path={prefix}; HttpOnly; SameSite=Lax'},''
            return 401,{},page(title,'Hibás felhasználónév vagy jelszó.')
        body='<p>Laborfiókok: anna, bela, admin. Jelszó mindháromhoz: LabPass123!</p>'+form('<input name="username" value="anna"><input name="password" type="password" value="LabPass123!">','Belépés')
        return 200,{},page(title,body)
    if sub=='logout':
        for token,value in list(SESSIONS.items()):
            if value==account: SESSIONS.pop(token,None)
        return 303,{'Location':prefix+'/login','Set-Cookie':f'lab_session_{p}=; Path={prefix}; Max-Age=0'},''
    if not account:
        return 303,{'Location':prefix+'/login'},''
    uid=account['id']
    from advanced import handle as advanced_handle
    with transaction() if method=='POST' else nullcontext():
        advanced_result=advanced_handle(p,sub,params,method,account)
    if advanced_result is not None:
        status,advanced_body=advanced_result
        return status,{},page(title,advanced_body)
    body=''
    if sub=='workflow':
        from workflows import handle as workflow_handle, LABELS
        with transaction() if method=='POST' else nullcontext():
            body='<h2>'+esc(LABELS[p])+'</h2>'+workflow_handle(p,uid,params,method)
    elif sub=='':
        q=params.get('q','')
        # SZÁNDÉKOS SQLi: valós adatbázis, többtáblás kereső, nyers szövegillesztés.
        base='SELECT i.id, i.title, i.body, i.status, i.amount, a.username AS owner FROM items i JOIN accounts a ON a.project=i.project AND a.id=i.owner_id WHERE i.project = ?'
        if safe:
            rows=query(base+' AND i.title LIKE ? ORDER BY i.id',(p,'%'+q+'%'))
        else:
            rows=query(base+" AND i.title LIKE '%"+q+"%' ORDER BY i.id",(p,))
        from ui import home
        body=home(p,uid,rows,params)
    elif sub=='new':
        if method=='POST':
            # A bevitelt paraméterezve tároljuk; a hiba csak később, megjelenítéskor lép fel.
            rows=query('SELECT COALESCE(MAX(id),0)+1 AS next FROM items WHERE project = ?',(p,))
            with __import__('core').LOCK:
                new_id=query('SELECT COALESCE(MAX(id),0)+1 AS next FROM items WHERE project = ?',(p,))[0]['next']
                query('INSERT INTO items VALUES (?,?,?,?,?,?,?)',(p,new_id,uid,params.get('title',''),params.get('body',''),c['states'][0],1000))
            return 303,{'Location':f'{prefix}/item?id={new_id}'},''
        body=form('<label>Cím<input name="title" required></label><label style="display:block">Leírás<textarea name="body"></textarea></label>',c['action'])
    elif sub=='item':
        item_id=int(params.get('id','1'))
        rows=query('SELECT * FROM items WHERE project = ? AND id = ?',(p,item_id))
        if not rows: return 404,{},page(title,'Nincs ilyen rekord.')
        item=rows[0]
        if method=='POST':
            if 'status' in params:
                if item['owner_id']!=uid and account['role']!='admin': return 403,{},page(title,'Csak a tulajdonos vagy admin módosíthatja.')
                if params['status'] not in c['states']: return 400,{},page(title,'Ismeretlen állapot.')
                query('UPDATE items SET status = ? WHERE project = ? AND id = ?',(params['status'],p,item_id))
            elif 'body' in params: query('INSERT INTO notes VALUES (?,?,?,?)',(p,item_id,uid,params['body']))
            return 303,{'Location':f'{prefix}/item?id={item_id}'},''
        body='<p><a href="?id='+str(item_id)+'&safe=1">Szöveges nézet</a></p><article><h2>'+render(item['title'])+'</h2>'+render(item['body'])+'</article>'
        body+=form('<input type="hidden" name="id" value="'+str(item_id)+'"><textarea name="body" placeholder="Hozzászólás"></textarea>','Hozzászólás')
        notes=query('SELECT n.body,a.username FROM notes n JOIN accounts a ON a.project=n.project AND a.id=n.author_id WHERE n.project = ? AND n.item_id = ?',(p,item_id))
        body+=''.join('<article><b>'+esc(n['username'])+'</b><p>'+render(n['body'])+'</p></article>' for n in notes)
        if item['owner_id']==uid or account['role']=='admin':
            body+=form('<input type="hidden" name="id" value="'+str(item_id)+'"><select name="status">'+''.join('<option>'+esc(s)+'</option>' for s in c['states'])+'</select>','Állapotváltás')
        if p==3: body+=f'<p><a class="btn" href="{prefix}/checkout?add={item_id}">Kosárba</a></p>'
        elif p==7: body+=f'<p><a class="btn" href="{prefix}/workflow?id={item_id}">Jelentkezés</a></p>'
        elif p==8: body+=f'<p><a class="btn" href="{prefix}/quote?id={item_id}">Ajánlatkérés</a></p>'
    elif sub=='orders':
        if method=='POST':
            item_id=int(params.get('id','1')); quantity=int(params.get('quantity','1'))
            if not 1<=quantity<=100: return 400,{},page(title,'A mennyiség 1–100 lehet.')
            if not query('SELECT id FROM items WHERE project = ? AND id = ?',(p,item_id)): return 404,{},page(title,'Ismeretlen tétel.')
            query('INSERT INTO orders VALUES (?,?,?,?)',(p,uid,item_id,quantity))
        body=table(query('SELECT i.title,o.quantity,i.amount,(i.amount*o.quantity) AS total FROM orders o JOIN items i ON i.project=o.project AND i.id=o.item_id WHERE o.project = ? AND o.owner_id = ?',(p,uid)))
    elif sub=='report':
        if method=='POST':
            query('INSERT INTO saved_filters VALUES (?,?,?,?) ON CONFLICT(project,owner_id,name) DO UPDATE SET expression=excluded.expression',(p,uid,params.get('name','sajat'),params.get('expression','published')))
        body='<h1>Mentett szűrők</h1><p>Válassz egy korábbi szűrőt, vagy ments új keresést állapot szerint.</p>'
        body+=form('<label>Szűrő neve<input name="name" value="sajat"></label><label>Állapot<input name="expression" value="published"></label>','Szűrő mentése')
        filters=query('SELECT name,expression FROM saved_filters WHERE project = ? AND owner_id = ?',(p,uid))
        body+=''.join('<article>'+esc(f['name'])+' · <a href="'+prefix+'/report?run='+__import__('urllib.parse',fromlist=['quote']).quote(f['name'],safe='')+'">Futtatás</a> · <a href="'+prefix+'/report?run='+__import__('urllib.parse',fromlist=['quote']).quote(f['name'],safe='')+'&safe=1">Biztonságos futtatás</a></article>' for f in filters)
        if 'run' in params:
            found=query('SELECT expression FROM saved_filters WHERE project = ? AND owner_id = ? AND name = ?',(p,uid,params['run']))
            if found:
                expression=found[0]['expression']
                if safe: rows=query('SELECT * FROM items WHERE project = ? AND status = ?',(p,expression))
                else: rows=query("SELECT * FROM items WHERE project = ? AND status = '"+expression+"'",(p,))
                body+=table(rows)
    elif sub=='preview':
        body='<form><textarea name="q">'+esc(params.get('q','<b>Előnézet</b>'))+'</textarea><label><input type="checkbox" name="safe" value="1">Biztonságos kontroll</label><button>Előnézet</button></form><article id="preview"></article>'
        sink='textContent' if safe else 'innerHTML'
        body+='<script>const input=new URLSearchParams(location.search).get("q")||"Előnézet";document.getElementById("preview").'+sink+'=input;</script>'
    elif sub=='inbox' and p==2:
        rows=query('SELECT sender,subject,body FROM mail WHERE project = ? AND recipient = ? ORDER BY rowid DESC',(p,account['username']+'@example.test'))
        from ui import inbox
        body=inbox(rows,params)
    elif sub=='compose' and p==2:
        if method=='POST':
            recipient=params.get('recipient','')
            if recipient not in ['anna@example.test','bela@example.test','admin@example.test']: return 400,{},page(title,'Csak a három helyi laborpostafiók használható.')
            query('INSERT INTO mail VALUES (?,?,?,?,?)',(p,recipient,account['username']+'@example.test',params.get('subject',''),params.get('body','')))
            body='<p>A levelet elküldtük.</p>'
        body+=form('<label>Címzett<input name="recipient" value="bela@example.test"></label><label>Tárgy<input name="subject"></label><label style="display:block">Üzenet<textarea name="body"></textarea></label>','Küldés')
    else: return 404,{},page(title,'Ismeretlen aloldal.')
    return 200,{},page(title,body)
