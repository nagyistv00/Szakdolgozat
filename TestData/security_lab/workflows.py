"""Alkalmazásspecifikus, tartós üzleti műveletek."""
from datetime import date
from core import query, table
from platform_lab import esc, form

LABELS={1:'Követések és személyes hírfolyam',2:'Levélarchívum',3:'Kosár és fizetési összesítő',4:'Ügyintéző kijelölése',5:'Szabadságkérelem',6:'Wiki verziótörténet',7:'Rendezvényregisztráció',8:'Dátumos szállásfoglalás',9:'Értékesítési folyamat',10:'Feladatfüggőségek'}

def initialize():
    query('CREATE TABLE IF NOT EXISTS workflow (project INTEGER, owner_id INTEGER, item_id INTEGER, kind TEXT, value TEXT, start_date TEXT, end_date TEXT)')

def handle(p,uid,params,method):
    item_id=int(params.get('id','1'))
    items=query('SELECT id,title FROM items WHERE project = ? ORDER BY id',(p,))
    if not any(x['id']==item_id for x in items): return '<p>Ismeretlen rekord.</p>'
    message=''
    if method=='POST':
        kind=str(p); value=params.get('value',''); start=params.get('start',''); end=params.get('end','')
        if p==1:
            target=int(value)
            if not query('SELECT id FROM accounts WHERE project = ? AND id = ?',(p,target)): return '<p>Nincs ilyen felhasználó.</p>'
            value=str(target)
        elif p==3:
            amount=int(value)
            if not 1<=amount<=100: return '<p>A mennyiség 1–100 lehet.</p>'
            value=str(amount)
        elif p==4:
            if not query('SELECT id FROM accounts WHERE project = ? AND username = ?',(p,value)): return '<p>Ismeretlen ügyintéző.</p>'
        elif p in (5,8):
            try:
                if date.fromisoformat(start)>=date.fromisoformat(end): return '<p>A kezdődátum előzze meg a záródátumot.</p>'
            except ValueError: return '<p>Érvénytelen dátum.</p>'
            if p==8 and query('SELECT * FROM workflow WHERE project = ? AND item_id = ? AND start_date < ? AND end_date > ?',(p,item_id,end,start)):
                return '<p>Erre az időszakra már van foglalás.</p>'
        elif p==6:
            row=query('SELECT * FROM items WHERE project = ? AND id = ?',(p,item_id))[0]
            if row['owner_id']!=uid: return '<p>Csak a tulajdonos szerkesztheti.</p>'
            query('INSERT INTO workflow VALUES (?,?,?,?,?,?,?)',(p,uid,item_id,'previous',row['body'],'',''))
            query('UPDATE items SET body = ? WHERE project = ? AND id = ?',(value,p,item_id))
        elif p==7:
            with __import__('core').LOCK:
                if query('SELECT * FROM workflow WHERE project = ? AND owner_id = ? AND item_id = ?',(p,uid,item_id)): return '<p>Már regisztráltál.</p>'
                count=query('SELECT COUNT(*) AS n FROM workflow WHERE project = ? AND item_id = ?',(p,item_id))[0]['n']
                if count>=5: return '<p>A rendezvény betelt (5 férőhely).</p>'
                value='confirmed'
                query('INSERT INTO workflow VALUES (?,?,?,?,?,?,?)',(p,uid,item_id,kind,value,start,end))
            message='<p>Regisztráció rögzítve.</p>'
        elif p==9:
            if value not in ('lead','qualified','proposal','won','lost'): return '<p>Érvénytelen értékesítési fázis.</p>'
            query('UPDATE items SET status = ? WHERE project = ? AND id = ?',(value,p,item_id))
        elif p==10:
            target=int(value)
            if target==item_id or not any(x['id']==target for x in items): return '<p>Érvénytelen előfeltétel.</p>'
            edges=query('SELECT item_id,value FROM workflow WHERE project = ?',(p,))
            graph={}
            for edge in edges: graph.setdefault(edge['item_id'],[]).append(int(edge['value']))
            stack=[target]; visited=set()
            while stack:
                node=stack.pop()
                if node==item_id: return '<p>A függőség ciklust hozna létre.</p>'
                if node not in visited: visited.add(node); stack.extend(graph.get(node,[]))
            value=str(target)
        if p!=7:
            query('INSERT INTO workflow VALUES (?,?,?,?,?,?,?)',(p,uid,item_id,kind,value,start,end))
            message='<p>Művelet rögzítve.</p>'
    options='<select name="id">'+''.join(f'<option value="{i["id"]}"{" selected" if i["id"]==item_id else ""}>{esc(i["title"])}</option>' for i in items)+'</select>'
    prompts={1:'Követendő felhasználó azonosítója (1, 2, 3)',2:'Archívumcímke',3:'Mennyiség (1–100)',4:'Ügyintéző neve: anna, bela vagy admin',5:'Szabadság indoklása',6:'Új HTML wiki tartalom',7:'Regisztráció megjegyzése',8:'Foglalás megjegyzése',9:'lead / qualified / proposal / won / lost',10:'Előfeltétel feladatazonosítója'}
    value_field='<textarea name="value" required></textarea>'
    if p==1:
        value_field='<select name="value">'+''.join('<option value="'+str(a['id'])+'">'+esc(a['username'])+'</option>' for a in query('SELECT id,username FROM accounts WHERE project=1 ORDER BY id'))+'</select>'
    elif p==4:
        value_field='<select name="value">'+''.join('<option>'+esc(a['username'])+'</option>' for a in query('SELECT username FROM accounts WHERE project=4 ORDER BY id'))+'</select>'
    elif p==9:
        value_field='<select name="value">'+''.join('<option value="'+key+'">'+label+'</option>' for key,label in [('lead','Új érdeklődő'),('qualified','Egyeztetés'),('proposal','Ajánlat'),('won','Megnyert'),('lost','Elvesztett')])+'</select>'
    elif p==10:
        value_field='<select name="value">'+''.join('<option value="'+str(i['id'])+'">'+esc(i['title'])+'</option>' for i in items if i['id']!=item_id)+'</select>'
    elif p==3: value_field='<input name="value" type="number" min="1" max="100" value="1">'
    field_labels={1:'Követendő felhasználó',4:'Ügyintéző',9:'Értékesítési fázis',10:'Előfeltétel'}
    fields='<label>Tétel'+options+'</label><p>'+field_labels.get(p,prompts[p])+'</p>'+value_field
    if p in (5,8): fields+='<label>Kezdés<input type="date" name="start" required></label><label>Vége (kizáró)<input type="date" name="end" required></label>'
    result=message+form(fields,LABELS[p])
    if p==1:
        rows=query("SELECT i.id,i.title,i.body FROM items i WHERE i.project = ? AND i.owner_id IN (SELECT CAST(value AS INTEGER) FROM workflow WHERE project = ? AND owner_id = ? AND kind = '1')",(p,p,uid))
        result+='<h2>Követett felhasználók bejegyzései</h2>'+table(rows)
    elif p==3:
        rows=query('SELECT i.title,CAST(w.value AS INTEGER) AS quantity,i.amount,CAST(w.value AS INTEGER)*i.amount AS total FROM workflow w JOIN items i ON w.project=i.project AND w.item_id=i.id WHERE w.project = ? AND w.owner_id = ?',(p,uid))
        result+=table(rows)+'<p>Összesen: '+str(sum(r['total'] for r in rows))+' Ft.</p>'
    else:
        result+=table(query('SELECT item_id,kind,value,start_date,end_date FROM workflow WHERE project = ? AND owner_id = ?',(p,uid)))
    return result
