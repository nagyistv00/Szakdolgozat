"""Szándékosan sérülékeny, helyi SQLi/XSS oktatólabor."""
import html
import json
import os
import sqlite3
import threading
from contextlib import closing, contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOCK = threading.RLock()

def connection():
    (ROOT / 'data').mkdir(exist_ok=True)
    db=sqlite3.connect(ROOT / 'data/lab.sqlite3',isolation_level=None,timeout=10)
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA busy_timeout=10000')
    return db

LOCAL=threading.local()

def _execute(db,sql,params):
    cur=db.execute(sql,params)
    if not cur.description: return []
    names=[x[0] for x in cur.description]
    return [dict(zip(names,row)) for row in cur.fetchall()]

def query(sql,params=()):
    with LOCK:
        active=getattr(LOCAL,'db',None)
        if active is not None: return _execute(active,sql,params)
        with closing(connection()) as db: return _execute(db,sql,params)

@contextmanager
def transaction():
    with LOCK:
        if getattr(LOCAL,'db',None) is not None:
            yield
            return
        with closing(connection()) as db:
            db.execute('BEGIN IMMEDIATE')
            LOCAL.db=db
            try:
                yield
                db.commit()
            except BaseException:
                db.rollback()
                raise
            finally:
                del LOCAL.db

def initialize():
    query('CREATE TABLE IF NOT EXISTS records (project INTEGER, id INTEGER, name TEXT, email TEXT, price INTEGER, secret TEXT, PRIMARY KEY(project,id))')
    query('CREATE TABLE IF NOT EXISTS comments (project INTEGER, body TEXT)')
    for p in range(1,11):
        for i in range(1,7):
            query('INSERT INTO records VALUES (?,?,?,?,?,?) ON CONFLICT(project,id) DO NOTHING',
                  (p,i,['Anna','Bela','Csilla','Dora','Erik','Fanni'][i-1],f'user{i}@example.test',i*1250,f'LAB-P{p:02d}-SECRET-{i}'))

def page(title, body):
    return f'''<!doctype html><html lang="hu"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{html.escape(title)}</title>
<style>body{{font:16px system-ui;max-width:1050px;margin:40px auto;background:#eef2f7;color:#172338;padding:20px}}section,article{{background:white;padding:24px;margin:15px 0;border-radius:12px}}input,textarea,button{{font:inherit;padding:10px;margin:5px}}a{{color:#2058a5}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}table{{border-collapse:collapse}}td,th{{border:1px solid #bbb;padding:9px}}</style>
<nav><a href="/">Labor kezdőlap</a></nav><h1>{html.escape(title)}</h1><p>Szándékosan sérülékeny tesztkörnyezet. Minden rekord kitalált tesztadat.</p>{body}</html>'''

COLUMN_LABELS={'id':'Azonosító','item_id':'Tétel','title':'Megnevezés','name':'Név','email':'Email','company':'Cég','message_count':'Levelek','body':'Tartalom','status':'Állapot','amount':'Összeg','quantity':'Mennyiség','total':'Összesen','actor':'Felhasználó','action':'Művelet','detail':'Megjegyzés','priority':'Prioritás','assignee':'Ügyintéző','sla_hours':'SLA (óra)','department':'Részleg','salary':'Havi bér','location':'Munkavégzés helye','leave_days':'Szabadság (nap)','kind':'Típus','value':'Érték','start_date':'Kezdés','end_date':'Vége','username':'Felhasználónév','owner':'Felelős','price':'Ár','project':'Alkalmazás','secret':'Belső adat'}

def table(rows):
    if not rows: return '<p>Nincs találat.</p>'
    return '<table><tr>'+''.join('<th data-field="'+html.escape(k,quote=True)+'">'+html.escape(COLUMN_LABELS.get(k,k))+'</th>' for k in rows[0])+'</tr>'+''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in r.values())+'</tr>' for r in rows)+'</table>'

def sql_project(spec, params, method):
    n, title, field, default = spec
    value = params.get('q',default)
    safe = params.get('safe') == '1'
    column = 'name' if field == 'username' else 'email' if field == 'email' else 'id'
    if safe:
        sql = f'SELECT * FROM records WHERE project = ? AND {column} = ?'
        args = (n,value)
    else:
        literal = value if column == 'id' else "'"+value+"'"
        # SZÁNDÉKOS SQLi: megbízhatatlan bemenet közvetlenül az SQL-ben.
        sql = f'SELECT * FROM records WHERE project = {n} AND {column} = '+literal
        args = ()
    try: result = table(query(sql,args))
    except Exception as e: result = '<pre>'+html.escape(str(e))+'</pre>'
    return page(title, f'<section><form><label>{field}: <input name="q" value="{html.escape(value,quote=True)}"></label><label><input type="checkbox" name="safe" value="1" {"checked" if safe else ""}>Paraméterezett kontroll</label><button>Keresés</button></form><pre>{html.escape(sql)}</pre>{result}</section>')

def xss_project(spec, params, method):
    n,title,kind = spec
    value = params.get('q','Szia, labor!')
    safe = params.get('safe') == '1'
    field = '<textarea name="q">'+html.escape(value)+'</textarea>'
    form = f'<form method="{"post" if kind == "stored" else "get"}">{field}<label><input type="checkbox" name="safe" value="1" {"checked" if safe else ""}>Biztonságos kontroll</label><button>Megjelenítés</button></form>'
    if kind == 'stored':
        if method == 'POST': query('INSERT INTO comments VALUES (?,?)',(n,value))
        rows = query('SELECT body FROM comments WHERE project = ?',(n,))
        result = ''.join('<article>'+(html.escape(r['body']) if safe else r['body'])+'</article>' for r in rows)
    elif kind == 'reflected':
        result = '<article>'+(html.escape(value) if safe else value)+'</article>'
    elif kind == 'js':
        # Biztonságos kontroll: JSON + HTML scriptzáró karakterek kódolása.
        encoded = json.dumps(value).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        expression = encoded if safe else "'"+value+"'"
        result = '<script>alert("Hello " + '+expression+');</script>'
    else:
        sink = 'textContent' if safe else 'innerHTML'
        action = f'document.getElementById("output").{sink} = user_input;'
        if kind == 'write' and not safe: action = 'document.write(user_input);'
        result = '<article id="output"></article><script>const user_input = new URLSearchParams(location.search).get("q") || "Szia, labor!";'+action+'</script>'
    return page(title,'<section>'+form+'</section>'+result)
