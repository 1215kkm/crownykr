"""CROWNY optional settings/funding service. Python 3.10+, standard library only.
Run from this folder: set CROWNY_ADMIN_PASSWORD, then python app.py.
Default loopback only. Production: authenticated HTTPS reverse proxy/hosting required.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlsplit, unquote
import csv, io, json, os, re, secrets, sqlite3, threading, time, hmac

ROOT=Path(__file__).resolve().parent.parent
PORT=int(os.environ.get('CROWNY_PORT','8766'))
ORIGIN=os.environ.get('CROWNY_ORIGIN',f'http://127.0.0.1:{PORT}').rstrip('/')
PASSWORD=os.environ.get('CROWNY_ADMIN_PASSWORD','')
DATA=Path(os.environ.get('CROWNY_DATA_DIR',str(Path.home()/'.crowny-data'))).resolve()
DEFAULT={'version':1,'detail':{'layout':'horizontal','smooth':True},'community':{'scrollType':True},'funding':{'enabled':False,'campaign':'crowny-funding','title':'CROWNY FUNDING','consentText':''}}
SESSIONS={};LIMITS={};LOCK=threading.Lock()

def db():
    connection=sqlite3.connect(DATA/'crowny.sqlite3',timeout=10);connection.row_factory=sqlite3.Row;return connection

def init():
    DATA.mkdir(parents=True,exist_ok=True,mode=0o700)
    with db() as c:
        c.executescript('CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL); CREATE TABLE IF NOT EXISTS applicants(id TEXT PRIMARY KEY, campaign TEXT NOT NULL,name TEXT NOT NULL,contact TEXT NOT NULL,contact_key TEXT NOT NULL,note TEXT NOT NULL,consent_text TEXT NOT NULL,created_at TEXT NOT NULL,UNIQUE(campaign,contact_key));')
        c.execute('INSERT OR IGNORE INTO settings VALUES(1,?)',(json.dumps(DEFAULT,ensure_ascii=False),))
    try:os.chmod(DATA/'crowny.sqlite3',0o600)
    except OSError:pass

def settings(c):return json.loads(c.execute('SELECT value FROM settings WHERE id=1').fetchone()[0])
def clean_config(s):
    if not isinstance(s,dict):raise ValueError('설정 형식이 올바르지 않습니다.')
    d=s.get('detail',{});community=s.get('community',{});f=s.get('funding',{})
    if not all(isinstance(x,dict) for x in [d,community,f]):raise ValueError('설정 형식 오류')
    if d.get('layout') not in ('horizontal','vertical'):raise ValueError('상세 방향을 선택해주세요.')
    if any(type(x) is not bool for x in [d.get('smooth'),community.get('scrollType'),f.get('enabled')]):raise ValueError('설정값 오류')
    campaign=str(f.get('campaign',''));title=str(f.get('title','')).strip();consent=str(f.get('consentText','')).strip()
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',campaign) or not 1<=len(title)<=100 or len(consent)>2000:raise ValueError('프로젝트 정보 오류')
    if f['enabled'] and not consent:raise ValueError('접수 전에 개인정보 수집·이용 안내를 입력해주세요.')
    return {'version':1,'detail':{'layout':d['layout'],'smooth':d['smooth']},'community':{'scrollType':community['scrollType']},'funding':{'enabled':f['enabled'],'campaign':campaign,'title':title,'consentText':consent}}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def log_message(self,*args):pass # Do not log application bodies or personal data.
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','same-origin');self.send_header('X-Frame-Options','SAMEORIGIN')
        if self.path.startswith('/api/'):self.send_header('Cache-Control','no-store')
        super().end_headers()
    def reply(self,status,data,headers=None):
        body=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)))
        for key,value in (headers or {}).items():self.send_header(key,value)
        self.end_headers();self.wfile.write(body)
    def host_ok(self):return self.headers.get('Host')==urlsplit(ORIGIN).netloc
    def origin_ok(self):return self.host_ok() and self.headers.get('Origin')==ORIGIN
    def body(self):
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise ValueError('JSON 요청이 필요합니다.')
        size=int(self.headers.get('Content-Length','0'))
        if not 0<size<=16384:raise ValueError('요청 크기 오류')
        value=json.loads(self.rfile.read(size))
        if not isinstance(value,dict):raise ValueError('요청 형식 오류')
        return value
    def session(self):
        try:cookie=SimpleCookie(self.headers.get('Cookie',''));token=cookie['crowny_admin'].value
        except (KeyError,Exception):return None
        with LOCK:
            entry=SESSIONS.get(token)
            if entry and entry['expires']>time.time():return (token,entry)
            SESSIONS.pop(token,None)
        return None
    def limited(self,kind,limit):
        now=time.time();key=(kind,self.client_address[0])
        with LOCK:
            for old in list(LIMITS):
                if not LIMITS[old] or LIMITS[old][-1]<now-60:del LIMITS[old]
            hits=[t for t in LIMITS.get(key,[]) if t>now-60]
            if len(hits)>=limit:return True
            LIMITS[key]=hits+[now]
        return False
    def static_ok(self):
        path=unquote(urlsplit(self.path).path)
        if path=='/':return True
        p=(ROOT/path.lstrip('/')).resolve()
        if ROOT not in p.parents:return False
        return (p.parent==ROOT and p.suffix=='.html') or ('assets' in p.relative_to(ROOT).parts[:1] and p.suffix.lower() in {'.jpg','.jpeg','.png','.webp','.woff2','.js','.svg','.gif'})
    def do_HEAD(self):
        if not self.host_ok() or not self.static_ok():self.send_error(404);return
        super().do_HEAD()
    def do_GET(self):
        if not self.host_ok():self.reply(403,{'error':'잘못된 호스트입니다.'});return
        path=urlsplit(self.path).path
        if path=='/api/settings':
            with db() as c:self.reply(200,settings(c))
        elif path in ('/api/admin/applicants','/api/admin/applicants.csv'):
            if not self.session():self.reply(401,{'error':'관리 서버에 로그인해주세요.'});return
            with db() as c:
                if path.endswith('.csv'):
                    output=io.StringIO();writer=csv.writer(output);writer.writerow(['접수번호','접수일','프로젝트','이름','연락처','메모','동의한 안내문'])
                    def safe(value):return "'"+value if value and (value[0] in '=+-@\t\r' or value.lstrip().startswith(('=','+','-','@'))) else value
                    for row in c.execute('SELECT id,created_at,campaign,name,contact,note,consent_text FROM applicants ORDER BY created_at DESC'):writer.writerow([safe(str(x)) for x in row])
                    body=('\ufeff'+output.getvalue()).encode();self.send_response(200);self.send_header('Content-Type','text/csv; charset=utf-8');self.send_header('Content-Disposition','attachment; filename="crowny-funding.csv"');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
                else:
                    rows=c.execute('SELECT id,created_at,campaign,name,contact FROM applicants ORDER BY created_at DESC LIMIT 200').fetchall();total=c.execute('SELECT COUNT(*) FROM applicants').fetchone()[0];self.reply(200,{'items':[dict(r) for r in rows],'total':total})
        elif path.startswith('/api/') or not self.static_ok():self.reply(404,{'error':'페이지를 찾을 수 없습니다.'})
        else:super().do_GET()
    def do_PUT(self):self.mutate('PUT')
    def do_POST(self):self.mutate('POST')
    def mutate(self,method):
        if not self.origin_ok():self.reply(403,{'error':'허용되지 않은 출처입니다.'});return
        try:
            payload=self.body();path=urlsplit(self.path).path
            if path=='/api/admin/login' and method=='POST':
                if self.limited('login',5):self.reply(429,{'error':'잠시 후 다시 시도해주세요.'});return
                if not hmac.compare_digest(str(payload.get('password','')).encode(),PASSWORD.encode()):self.reply(401,{'error':'관리 비밀번호를 확인해주세요.'});return
                token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32)
                with LOCK:
                    for old in list(SESSIONS):
                        if SESSIONS[old]['expires']<=time.time():del SESSIONS[old]
                    SESSIONS[token]={'csrf':csrf,'expires':time.time()+28800}
                cookie=f'crowny_admin={token}; HttpOnly; SameSite=Strict; Path=/api; Max-Age=28800'+('; Secure' if ORIGIN.startswith('https://') else '')
                self.reply(200,{'csrf':csrf},{'Set-Cookie':cookie});return
            if path in ('/api/settings','/api/admin/logout'):
                session=self.session()
                if not session or not hmac.compare_digest(self.headers.get('X-CSRF-Token',''),session[1]['csrf']):self.reply(403,{'error':'관리 서버에 다시 로그인해주세요.'});return
                if path=='/api/settings' and method=='PUT':
                    value=clean_config(payload)
                    with db() as c:c.execute('UPDATE settings SET value=? WHERE id=1',(json.dumps(value,ensure_ascii=False),))
                    self.reply(200,value);return
                if path=='/api/admin/logout' and method=='POST':
                    with LOCK:SESSIONS.pop(session[0],None)
                    self.reply(200,{'ok':True},{'Set-Cookie':'crowny_admin=; HttpOnly; SameSite=Strict; Path=/api; Max-Age=0'});return
            if path=='/api/funding/applicants' and method=='POST':
                if self.limited('apply',10):self.reply(429,{'error':'잠시 후 다시 시도해주세요.'});return
                if payload.get('website'):raise ValueError('접수할 수 없습니다.')
                name=str(payload.get('name','')).strip();contact=str(payload.get('contact','')).strip();note=str(payload.get('note','')).strip()
                if not 1<=len(name)<=80 or not 3<=len(contact)<=160 or len(note)>1000:raise ValueError('이름·연락처·메모를 확인해주세요.')
                phone=re.sub(r'[\s()+-]','',contact)
                if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',contact) and not re.fullmatch(r'\d{8,15}',phone):raise ValueError('이메일 또는 전화번호를 입력해주세요.')
                with db() as c:
                    c.execute('BEGIN IMMEDIATE');f=settings(c)['funding']
                    if not f['enabled'] or payload.get('campaign')!=f['campaign']:raise ValueError('현재 접수 중인 프로젝트가 아닙니다.')
                    if payload.get('consent') is not True or not f['consentText'] or payload.get('consentText')!=f['consentText']:raise ValueError('페이지를 새로고침하고 수집·이용 안내에 동의해주세요.')
                    receipt=secrets.token_hex(8);stamp=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());contact_key=contact.casefold() if '@' in contact else phone
                    c.execute('INSERT INTO applicants VALUES(?,?,?,?,?,?,?,?)',(receipt,f['campaign'],name,contact,contact_key,note,f['consentText'],stamp))
                self.reply(201,{'receipt':receipt});return
            self.reply(404,{'error':'지원하지 않는 요청입니다.'})
        except sqlite3.IntegrityError:self.reply(409,{'error':'동일한 연락처로 이미 신청했습니다.'})
        except (ValueError,TypeError,UnicodeError):self.reply(400,{'error':'입력값 또는 동의 내용을 확인해주세요.'})
        except Exception:self.reply(500,{'error':'저장하지 못했습니다. 잠시 후 다시 시도해주세요.'})

if __name__=='__main__':
    if len(PASSWORD)<12:raise SystemExit('CROWNY_ADMIN_PASSWORD에 12자 이상의 관리 비밀번호를 설정해주세요.')
    init();print(f'CROWNY: {ORIGIN} (Ctrl+C to stop)')
    ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
