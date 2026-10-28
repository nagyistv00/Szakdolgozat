import http.cookiejar
import os
import smtplib
import tempfile
import threading
import unittest
from email.message import EmailMessage
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor, Request
import core
from app import Handler, dispatch, initialize_all
from http.server import ThreadingHTTPServer
from platform_lab import setup, SESSIONS
from smtp_local import start_smtp

class LabTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.original=core.ROOT
        core.ROOT=Path(cls.tmp.name)
        initialize_all()
        cls.http=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        threading.Thread(target=cls.http.serve_forever,daemon=True).start()
        cls.base=f'http://127.0.0.1:{cls.http.server_port}'
        cls.smtp=start_smtp('127.0.0.1',0)
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown(); cls.http.server_close()
        cls.smtp.shutdown(); cls.smtp.server_close()
        core.ROOT=cls.original; cls.tmp.cleanup()
    def setUp(self):
        self.client=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def get(self,path):
        return self.client.open(self.base+path).read().decode()
    def post(self,path,params):
        return self.client.open(self.base+path,urlencode(params).encode()).read().decode()
    def login(self,p):
        self.post(f'/p{p:02d}/login',{'username':'anna','password':'LabPass123!'})
    def test_all_ten_business_flows(self):
        for p in range(1,11):
            with self.subTest(project=p):
                self.login(p)
                prefix=f'/p{p:02d}'
                self.assertIn('Bejelentkezve',self.get(prefix+'/'))
                self.assertIn('Szűrő mentése',self.get(prefix+'/report'))
                content=self.post(prefix+'/new',{'title':f'Created-{p}','body':'<b>stored content</b>'})
                self.assertIn(f'Created-{p}',content)
                self.assertIn('<b>stored content</b>',content)
                self.post(prefix+'/item?id=1',{'body':'<img src=x onerror=alert(1)>'})
                self.assertIn('onerror=alert(1)',self.get(prefix+'/item?id=1'))
                self.assertIn('&lt;img',self.get(prefix+'/item?id=1&safe=1'))
                self.post(prefix+'/orders',{'id':'1','quantity':'2'})
                self.assertIn('total',self.get(prefix+'/orders'))
    def test_specific_workflows(self):
        values={1:'2',2:'archive',3:'2',4:'bela',5:'Pihenes',6:'<b>Wiki update</b>',7:'Registration',8:'Booking',9:'qualified',10:'2'}
        for p,value in values.items():
            self.login(p)
            result=self.post(f'/p{p:02d}/workflow',{'id':'2' if p==6 else '1','value':value,'start':'2027-01-01','end':'2027-01-03'})
            self.assertIn('rögzítve',result)
        self.login(8)
        self.assertIn('már van foglalás',self.post('/p08/workflow',{'id':'1','value':'Overlap','start':'2027-01-02','end':'2027-01-04'}))
        self.login(10)
        self.assertIn('ciklust',self.post('/p10/workflow',{'id':'2','value':'1'}))
    def test_sqli_and_control(self):
        self.login(1)
        payload="unlikely' OR 1=1 -- "
        bad=self.get('/p01/?'+urlencode({'q':payload}))
        good=self.get('/p01/?'+urlencode({'q':payload,'safe':'1'}))
        self.assertIn('internal',bad)
        self.assertIn('Nincs találat',good)
    def test_second_order(self):
        self.login(9)
        self.post('/p09/report',{'name':'saved','expression':"unlikely' OR 1=1 -- "})
        self.assertIn('Fiktív',self.get('/p09/report?run=saved'))
        self.assertIn('Nincs találat',self.get('/p09/report?run=saved&safe=1'))
    def test_controls_and_labs(self):
        for p in range(1,11): self.assertIn('<html',self.get(f'/p{p:02d}/lab'))
        self.login(6)
        self.assertIn('.innerHTML=input',self.get('/p06/preview'))
        self.assertIn('.textContent=input',self.get('/p06/preview?safe=1'))
    def test_mail_and_no_relay(self):
        msg=EmailMessage();msg['From']='sender@example.test';msg['To']='anna@example.test';msg['Subject']='SMTP test'
        msg.set_content('<b>SMTP delivery</b>',subtype='html')
        with smtplib.SMTP('127.0.0.1',self.smtp.server_address[1]) as smtp:
            smtp.send_message(msg)
            with self.assertRaises(smtplib.SMTPRecipientsRefused): smtp.sendmail('sender@example.test',['outside@example.org'],'Subject: denied\r\n\r\nnone')
        self.login(2)
        self.assertIn('<b>SMTP delivery</b>',self.get('/p02/inbox'))
        self.assertIn('&lt;b&gt;SMTP delivery',self.get('/p02/inbox?safe=1'))
    def test_project_session_isolation(self):
        self.login(1)
        self.assertIn('Belépés',self.get('/p02/'))
        self.assertEqual(dispatch('/p02/',{},selected=1)[0],404)

if __name__=='__main__': unittest.main()
