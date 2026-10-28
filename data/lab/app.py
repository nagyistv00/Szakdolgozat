"""Központi belépési pont: python app.py [--project 1..10]."""
import argparse
import importlib
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from core import initialize, page
from platform_lab import setup, handle, CONFIG, SESSIONS
from http.cookies import SimpleCookie

PROJECTS = [importlib.import_module(f'projects.p{i:02d}') for i in range(1,11)]

def dispatch(path, params, method='GET', selected=None, cookies=None):
    if path == '/health':
        from core import query
        query('SELECT 1')
        return 200, 'application/json', json.dumps({'status':'ok','database':'sqlite','version':2})
    if path == '/':
        from ui import hub
        return 200,'text/html',hub(selected)
    parts = path.strip('/').split('/')
    if parts[0] in [f'p{i:02d}' for i in range(1,11)]:
        n=int(parts[0][1:])
        if selected is None or n==selected:
            if len(parts)==2 and parts[1]=='lab':
                return 200,'text/html',PROJECTS[n-1].handle(params,method)
            token=(cookies or {}).get(f'lab_session_{n}')
            account=SESSIONS.get(token)
            if account and account['project']!=n: account=None
            status,headers,body=handle(n,'/'.join(parts[1:]),params,method,account)
            return status,headers,body
    return 404,'text/html',page('404','Ismeretlen végpont.')

class Handler(BaseHTTPRequestHandler):
    selected = None
    def do_GET(self): self.handle_request()
    def do_POST(self): self.handle_request()
    def handle_request(self):
        url = urlsplit(self.path)
        params = {k:v[-1] for k,v in parse_qs(url.query,keep_blank_values=True).items()}
        if self.command == 'POST':
            size=int(self.headers.get('Content-Length','0'))
            if size>65536:
                self.send_error(413); return
            params.update({k:v[-1] for k,v in parse_qs(self.rfile.read(size).decode(),keep_blank_values=True).items()})
        try:
            cookie=SimpleCookie(self.headers.get('Cookie',''))
            status,kind,body=dispatch(url.path,params,self.command,self.selected,{k:v.value for k,v in cookie.items()})
        except Exception:
            self.send_error(500,'Labor request failed'); return
        data=body.encode()
        self.send_response(status)
        headers=kind if isinstance(kind,dict) else {}
        content_type='text/html' if isinstance(kind,dict) else kind
        self.send_header('Content-Type',content_type+'; charset=utf-8')
        for key,value in headers.items(): self.send_header(key,value)
        self.send_header('Content-Length',str(len(data)))
        self.end_headers(); self.wfile.write(data)

def initialize_all():
    initialize(); setup()
    from seed_data import initialize as seed
    from advanced import initialize as advanced_setup
    seed(); advanced_setup()
    from content import initialize as content_setup
    content_setup()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--project',type=int,choices=range(1,11))
    parser.add_argument('--smtp',type=int,default=8025,help='Helyi SMTP port (alap: 8025); 0: kikapcsolás')
    args=parser.parse_args()
    initialize_all(); Handler.selected=args.project
    from runtime_services import Services
    services=Services(args.host,args.smtp)
    try:
        http=ThreadingHTTPServer((args.host,args.port),Handler)
        services.start()
        print(f'HTTP: http://{args.host}:{args.port}',flush=True)
        print(f'Adatbázis: SQLite (data/lab.sqlite3)',flush=True)
        if args.smtp: print(f'Helyi SMTP: {args.host}:{args.smtp}',flush=True)
        print('Fiókok: anna / bela / admin | Jelszó: LabPass123!',flush=True)
        print('Leállítás: Ctrl+C',flush=True)
        http.serve_forever()
    except KeyboardInterrupt:
        print('\nLeállítás...',flush=True)
    except OSError as exc:
        parser.exit(1,f'Nem sikerült az indítás: {exc}\nMásik port: --port 8001 --smtp 8026\n')
    finally:
        services.stop()
        if 'http' in locals(): http.server_close()
