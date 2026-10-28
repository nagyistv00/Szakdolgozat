import http.cookiejar
import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor
from http.server import ThreadingHTTPServer
import core
from app import Handler, initialize_all
from ui import SPECIAL

class AdvancedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.original=core.ROOT;core.ROOT=Path(cls.tmp.name)
        initialize_all()
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();core.ROOT=cls.original;cls.tmp.cleanup()
    def setUp(self): self.client=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def get(self,path): return self.client.open(self.base+path).read().decode()
    def post(self,path,params): return self.client.open(self.base+path,urlencode(params).encode()).read().decode()
    def login(self,p,user='anna'):
        self.post(f'/p{p:02d}/login',{'username':user,'password':'LabPass123!'})
    def test_10_layouts_and_screens(self):
        for p in range(1,11):
            with self.subTest(project=p):
                self.login(p)
                self.assertIn(f'data-layout="{p}"',self.get(f'/p{p:02d}/'))
                self.assertIn('<h1>',self.get(f'/p{p:02d}/'+SPECIAL[p][1]))
    def test_profile_cross_role_attribute_xss(self):
        self.login(1)
        payload='"><img src=x onerror=alert(101)>'
        self.post('/p01/profile',{'display_name':payload,'bio':'Test'})
        with self.assertRaises(HTTPError) as cm: self.get('/p01/moderation')
        self.assertEqual(cm.exception.code,403)
        self.login(1,'admin')
        self.assertIn(payload,self.get('/p01/moderation'))
        self.assertNotIn(payload,self.get('/p01/moderation?safe=1'))
    def test_join_aggregate_sqli(self):
        self.login(2)
        payload="unlikely' OR 1=1 -- "
        self.assertIn('Műhely',self.get('/p02/contacts?'+urlencode({'q':payload})))
        self.assertIn('Nincs találat',self.get('/p02/contacts?'+urlencode({'q':payload,'safe':'1'})))
    def test_coupon_second_order_and_purchase(self):
        self.login(3)
        self.get('/p03/checkout?add=2')
        self.post('/p03/checkout',{'action':'coupon','code':'TEST','scope':"none' OR 1=1 -- ",'discount':'20'})
        self.assertIn('Kedvezmény: <b>596 Ft',self.get('/p03/checkout?coupon=TEST'))
        self.assertIn('Kedvezmény: <b>0 Ft',self.get('/p03/checkout?coupon=TEST&safe=1'))
        before=core.query('SELECT stock FROM products WHERE item_id=2')[0]['stock']
        self.post('/p03/checkout',{'action':'confirm','coupon':'TEST'})
        self.assertEqual(core.query('SELECT stock FROM products WHERE item_id=2')[0]['stock'],before-1)
        self.assertEqual(core.query('SELECT total FROM purchases WHERE owner_id=1')[-1]['total'],2384)
    def test_boolean_blind_sqli_and_audit_xss(self):
        self.login(4)
        yes=self.get('/p04/triage?'+urlencode({'priority':'1 AND (SELECT salary FROM employees WHERE item_id=1)>400000'}))
        no=self.get('/p04/triage?'+urlencode({'priority':'1 AND (SELECT salary FROM employees WHERE item_id=1)>9000000'}))
        self.assertIn('id="matches">4<',yes);self.assertIn('id="matches">0<',no)
        payload='<img src=x onerror=alert(104)>'
        self.post('/p04/triage',{'id':'1','assignee':'anna','note':payload})
        self.assertIn(payload,self.get('/p04/triage'))
        self.assertNotIn(payload,self.get('/p04/triage?safe=1'))
    def test_order_expression_and_allowlist(self):
        self.login(5)
        expr='CASE WHEN (SELECT salary FROM employees WHERE item_id=1)>400000 THEN salary ELSE -salary END DESC'
        self.assertIn('870000',self.get('/p05/payroll?'+urlencode({'sort':expr})))
        with self.assertRaises(HTTPError) as cm:self.get('/p05/payroll?'+urlencode({'sort':expr,'safe':'1'}))
        self.assertEqual(cm.exception.code,400)
    def test_wiki_draft_publish_sanitizer_bypass(self):
        self.login(6)
        payload='<img src=x onerror=alert(106)>'
        result=self.post('/p06/editor',{'id':'2','content':'<script>alert(0)</script>'+payload})
        self.assertIn(payload,result);self.assertNotIn('<script>alert(0)</script>',result)
        revision=core.query('SELECT id FROM wiki_revisions ORDER BY id DESC')[0]['id']
        self.post('/p06/editor',{'id':'2','action':'publish','revision':str(revision)})
        self.assertIn(payload,self.get('/p06/item?id=2'))
        self.assertNotIn(payload,self.get('/p06/item?id=2&safe=1'))
    def test_csv_to_published_xss(self):
        self.login(7)
        payload='<img src=x onerror=alert(107)>'
        self.post('/p07/speakers',{'csv':'name,topic,bio\nFiktiv Speaker,Lab,'+payload})
        speaker=core.query('SELECT id FROM speakers ORDER BY id DESC')[0]['id']
        self.post('/p07/speakers',{'action':'publish','id':str(speaker)})
        self.login(7,'bela')
        self.assertIn(payload,self.get('/p07/speakers'))
        self.assertNotIn(payload,self.get('/p07/speakers?safe=1'))
    def test_json_script_context_escape(self):
        self.login(8)
        payload='</script><img src=x onerror=alert(108)>'
        params={'id':'1','guest':payload,'start':'2026-12-01','end':'2026-12-04'}
        self.post('/p08/quote',params)
        self.assertIn(payload,self.get('/p08/quote?'+urlencode(params)))
        params['safe']='1'
        self.assertNotIn(payload,self.get('/p08/quote?'+urlencode(params)))
        self.assertEqual(core.query('SELECT nights FROM quotes ORDER BY id DESC')[0]['nights'],3)
    def test_report_nested_document_xss(self):
        self.login(9)
        self.post('/p09/analytics',{'name':'test','template':'<script>alert(109)</script>'})
        self.assertIn('&lt;script&gt;alert(109)',self.get('/p09/analytics?run=test'))
        self.assertNotIn('sandbox=""',self.get('/p09/analytics?run=test'))
        self.assertIn('sandbox=""',self.get('/p09/analytics?run=test&safe=1'))
    def test_webhook_ansi_log_xss(self):
        self.login(10)
        payload='<img src=x onerror=alert(110)>'
        self.post('/p10/integrations',{'payload':json.dumps({'task_id':1,'branch':'test','status':'success','log':'\u001b[32m'+payload+'\u001b[0m'})})
        self.assertIn(payload,self.get('/p10/integrations'))
        self.assertNotIn(payload,self.get('/p10/integrations?safe=1'))
    def test_transaction_rollback(self):
        with self.assertRaises(RuntimeError):
            with core.transaction():
                core.query('INSERT INTO audit_events(project,actor,action,detail) VALUES (?,?,?,?)',(99,'test','rollback','none'))
                raise RuntimeError('rollback test')
        self.assertEqual(core.query('SELECT COUNT(*) AS n FROM audit_events WHERE project=99')[0]['n'],0)
    def test_session_logout(self):
        self.login(3)
        self.get('/p03/logout')
        self.assertIn('<h1>Belépés</h1>',self.get('/p03/'))

if __name__=='__main__': unittest.main()
