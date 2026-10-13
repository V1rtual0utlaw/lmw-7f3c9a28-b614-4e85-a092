import json, queue, threading, uuid, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from factory import Factory, ROOT
JOBS={}; Q=queue.Queue(); LOCK=threading.Lock()
def worker():
    while True:
        ident, data=Q.get()
        def log(msg):
            with LOCK: JOBS[ident]['log'].append(msg)
            (ROOT/'outputs'/ident/'status.json').write_text(json.dumps(JOBS[ident]),encoding='utf-8')
        try:
            JOBS[ident]['state']='running'
            Factory(json.loads((ROOT/'config.json').read_text(encoding='utf-8-sig')),log).produce(ROOT/'outputs'/ident,data['topic'],data['minutes'],data['notes'],data['demo'])
            JOBS[ident]['state']='review required'
        except Exception as e: JOBS[ident]['state']='failed'; log(str(e))
        finally: log('Job ended'); Q.task_done()
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**k): super().__init__(*a,directory=str(ROOT),**k)
    def do_GET(self):
        if self.path=='/api/jobs':
            self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers()
            with LOCK: self.wfile.write(json.dumps(JOBS).encode())
        elif self.path.startswith('/outputs/') or self.path=='/' or self.path=='/index.html': super().do_GET()
        else: self.send_error(404)
    def json_error(self, status, message):
        self.send_response(status); self.send_header('Content-Type','application/json'); self.end_headers()
        self.wfile.write(json.dumps({'error':message}).encode())
    def do_POST(self):
        # Browser cross-origin requests cannot enqueue jobs.
        if self.headers.get('Origin') not in (None,'http://127.0.0.1:8765','http://localhost:8765'):
            self.json_error(403,'Request origin is not allowed'); return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if self.path!='/api/jobs' or not 0<size<100000: raise ValueError('Invalid request')
            d=json.loads(self.rfile.read(size)); d['minutes']=int(d.get('minutes',10)); d['demo']=bool(d.get('demo',False))
            if not 1<=d['minutes']<=20 or not str(d.get('topic','')).strip(): raise ValueError('Topic and duration required')
            d['notes']=str(d.get('notes',''))
            ident=uuid.uuid4().hex[:12]; (ROOT/'outputs'/ident).mkdir(parents=True)
            (ROOT/'outputs'/ident/'request.json').write_text(json.dumps(d),encoding='utf-8')
            with LOCK: JOBS[ident]={'state':'queued','topic':d['topic'],'log':[]}
            Q.put((ident,d)); self.send_response(202); self.end_headers(); self.wfile.write(ident.encode())
        except (ValueError,KeyError) as e: self.json_error(400,str(e))
if __name__=='__main__':
    (ROOT/'outputs').mkdir(exist_ok=True)
    for p in (ROOT/'outputs').glob('*/status.json'):
        try:
            j=json.loads(p.read_text()); j['state']='interrupted' if j['state'] in ['running','queued'] else j['state']; JOBS[p.parent.name]=j
        except ValueError: pass
    threading.Thread(target=worker,daemon=True).start()
    print('True Science Stories: http://127.0.0.1:8765 — Ctrl+C to stop')
    webbrowser.open('http://127.0.0.1:8765')
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
