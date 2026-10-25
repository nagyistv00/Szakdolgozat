"""Helyi SMTP fogadó, kizárólag example.test címzettekhez. Nincs továbbítás."""
import socketserver
import threading
from email import policy
from email.parser import BytesParser
from core import query

class SMTP(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(20)
        sender=None; recipients=[]
        def reply(text): self.wfile.write((text+'\r\n').encode()); self.wfile.flush()
        reply('220 localmail.example.test ESMTP lab')
        while True:
            line=self.rfile.readline(8193)
            if not line: return
            if len(line)>8192: reply('500 Line too long'); return
            text=line.decode(errors='replace').strip(); command=text.split(' ',1)[0].upper()
            if command in ('EHLO','HELO'): reply('250 localmail.example.test')
            elif command=='QUIT': reply('221 Bye'); return
            elif command=='NOOP': reply('250 OK')
            elif command=='RSET': sender=None; recipients=[]; reply('250 Reset')
            elif text.upper().startswith('MAIL FROM:'):
                sender=text[10:].strip().strip('<>'); recipients=[]; reply('250 OK')
            elif text.upper().startswith('RCPT TO:'):
                recipient=text[8:].strip().strip('<>')
                if sender is None: reply('503 MAIL first')
                elif recipient not in ['anna@example.test','bela@example.test','admin@example.test']: reply('550 Local mailbox only')
                else: recipients.append(recipient); reply('250 OK')
            elif command=='DATA':
                if not recipients: reply('503 RCPT first'); continue
                reply('354 End with dot')
                data=bytearray()
                while True:
                    line=self.rfile.readline(65537)
                    if not line: return
                    if line in (b'.\r\n',b'.\n'): break
                    data.extend(line[1:] if line.startswith(b'..') else line)
                    if len(data)>1048576: reply('552 Too large'); return
                message=BytesParser(policy=policy.default).parsebytes(bytes(data))
                part=message.get_body(preferencelist=('html','plain')) if message.is_multipart() else message
                body=part.get_content() if part else ''
                if not isinstance(body,str): body=str(body)
                for recipient in recipients:
                    query('INSERT INTO mail VALUES (?,?,?,?,?)',(2,recipient,sender,str(message.get('Subject','')),body))
                sender=None; recipients=[]; reply('250 Stored locally')
            else: reply('502 Unsupported command')

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address=True
    daemon_threads=True

def start_smtp(host,port):
    server=Server((host,port),SMTP)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    return server
