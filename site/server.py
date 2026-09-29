#!/usr/bin/env python3
"""Safe Invest Turkey — backend: static files + REST API (stdlib only, SQLite)."""
import http.server, socketserver, json, sqlite3, os, re, hashlib, secrets, urllib.parse, datetime, mimetypes

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'data')
DB = os.path.join(DATA, 'site.db')
os.makedirs(DATA, exist_ok=True)

mimetypes.add_type('font/woff2', '.woff2')
mimetypes.add_type('application/javascript', '.js')

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA journal_mode=WAL')
    try: c.execute('ALTER TABLE users ADD COLUMN role TEXT DEFAULT \'user\'')
    except Exception: pass
    try: c.execute('ALTER TABLE users ADD COLUMN display TEXT DEFAULT \'\'')
    except Exception: pass
    c.execute('UPDATE users SET role=\'admin\' WHERE username=\'admin\'')
    return c

def now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def hashpw(pw, salt):
    return hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 120000).hex()

JCOLS_PROPS = ['gal','dist','ams','t','loc','price','s1','s2','s3','d']
JCOLS_POSTS = ['c']

def row_prop(r):
    o = dict(r)
    for k in JCOLS_PROPS:
        if o.get(k): o[k] = json.loads(o[k])
    return o

def row_post(r):
    o = dict(r)
    if o.get('c'): o['c'] = json.loads(o['c'])
    return o

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=BASE, **kw)

    def log_message(self, fmt, *args): pass

    # ---------- helpers ----------
    def send_json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(n) if n else b'{}'
        try: return json.loads(raw.decode() or '{}')
        except Exception: return {}

    def token(self):
        t = self.headers.get('X-Token')
        if t: return t
        h = self.headers.get('Authorization','')
        if h.startswith('Bearer '): return h[7:]
        return None

    def authed(self):
        t = self.token()
        if not t: return None
        c = db()
        r = c.execute('SELECT u.username FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?', (t,)).fetchone()
        c.close()
        return r['username'] if r else None

    # ---------- routing ----------
    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        if p.startswith('/api/'): return self.api_get(p)
        return super().do_GET()

    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        if p.startswith('/api/'): return self.api_write(p, 'POST')
        self.send_json({'error':'not found'}, 404)

    def do_PUT(self):
        p = urllib.parse.urlparse(self.path).path
        if p.startswith('/api/'): return self.api_write(p, 'PUT')
        self.send_json({'error':'not found'}, 404)

    def do_DELETE(self):
        p = urllib.parse.urlparse(self.path).path
        if p.startswith('/api/'): return self.api_write(p, 'DELETE')
        self.send_json({'error':'not found'}, 404)

    # ---------- GET api ----------
    def api_get(self, p):
        c = db()
        if p == '/api/me':
            u = self.authed()
            if not u:
                c.close(); return self.send_json({'ok': False, 'username': None})
            r = c.execute('SELECT role,display FROM users WHERE username=?', (u,)).fetchone()
            c.close()
            return self.send_json({'ok': True, 'username': u, 'role': r['role'] or 'user', 'display': r['display'] or ''})
        if p == '/api/props':
            rows = [row_prop(r) for r in c.execute('SELECT * FROM props ORDER BY added DESC')]
            c.close(); return self.send_json(rows)
        if p == '/api/posts':
            rows = [row_post(r) for r in c.execute('SELECT * FROM posts ORDER BY id')]
            c.close(); return self.send_json(rows)
        if p == '/api/messages':
            if not self.authed(): c.close(); return self.send_json({'error':'unauthorized'}, 401)
            rows = [dict(r) for r in c.execute('SELECT * FROM messages ORDER BY id DESC')]
            c.close(); return self.send_json(rows)
        if p == '/api/settings':
            out = {r['key']: json.loads(r['value']) for r in c.execute('SELECT * FROM settings')}
            c.close(); return self.send_json(out)
        if p == '/api/i18n':
            out = {}
            for r in c.execute('SELECT lang,key,value FROM i18n'):
                out.setdefault(r['lang'], {})[r['key']] = r['value']
            c.close(); return self.send_json(out)
        c.close()
        return self.send_json({'error':'not found'}, 404)

    # ---------- write api ----------
    def api_write(self, p, method):
        c = db()
        data = self.body()
        # public
        if p == '/api/login' and method == 'POST':
            u = data.get('username','').strip(); pw = data.get('password','')
            r = c.execute('SELECT * FROM users WHERE username=?', (u,)).fetchone()
            if r and hashpw(pw, r['salt']) == r['hash']:
                t = secrets.token_hex(24)
                c.execute('INSERT INTO sessions(token,user_id,created) VALUES(?,?,?)', (t, r['id'], now()))
                c.commit()
                role = c.execute('SELECT role FROM users WHERE username=?', (u,)).fetchone()['role'] or 'user'
                c.close()
                return self.send_json({'ok': True, 'token': t, 'username': u, 'role': role})
            c.close(); return self.send_json({'error':'invalid credentials'}, 401)
        if p == '/api/messages' and method == 'POST':
            c.execute('INSERT INTO messages(name,contact,topic,msg,lang,created,readed) VALUES(?,?,?,?,?,0,0)',
                      (data.get('name',''), data.get('contact',''), data.get('topic',''), data.get('msg',''), data.get('lang','en'), now()))
            c.commit(); c.close(); return self.send_json({'ok': True})
        if p == '/api/register' and method == 'POST':
            u = data.get('username','').strip(); pw = data.get('password',''); dn = data.get('name','').strip()
            if len(u) < 3 or len(pw) < 4:
                c.close(); return self.send_json({'error':'weak credentials'}, 400)
            if c.execute('SELECT id FROM users WHERE username=?', (u,)).fetchone():
                c.close(); return self.send_json({'error':'taken'}, 409)
            salt = secrets.token_hex(8)
            c.execute('INSERT INTO users(username,salt,hash,role,display) VALUES(?,?,?,\'user\',?)', (u, salt, hashpw(pw, salt), dn))
            uid = c.execute('SELECT id FROM users WHERE username=?', (u,)).fetchone()['id']
            t = secrets.token_hex(24)
            c.execute('INSERT INTO sessions(token,user_id,created) VALUES(?,?,?)', (t, uid, now()))
            c.commit(); c.close()
            return self.send_json({'ok': True, 'token': t, 'username': u, 'role': 'user'})
        # authed below
        me = self.authed()
        if not me: c.close(); return self.send_json({'error':'unauthorized'}, 401)
        if p == '/api/logout' and method == 'POST':
            c.execute('DELETE FROM sessions WHERE token=?', (self.token(),)); c.commit(); c.close()
            return self.send_json({'ok': True})
        # props
        if p == '/api/props' and method == 'POST':
            pid = data.get('id') or ('p%d' % int(datetime.datetime.now().timestamp()))
            c.execute('INSERT OR REPLACE INTO props(id,status,district,type,price_num,added,img,rating,year,floor,floors,view,dist,ams,t,loc,price,s1,s2,s3,d) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (pid, data.get('status','sale'), data.get('district',''), data.get('type','apt'), data.get('price_num'), int(data.get('added') or 0), data.get('img',''), data.get('rating') or 4.5, data.get('year'), data.get('floor',''), data.get('floors'), data.get('view','city'),
                 json.dumps(data.get('dist') or {}, ensure_ascii=False), json.dumps(data.get('ams') or [], ensure_ascii=False),
                 json.dumps(data.get('t') or {}, ensure_ascii=False), json.dumps(data.get('loc') or {}, ensure_ascii=False), json.dumps(data.get('price') or {}, ensure_ascii=False),
                 json.dumps(data.get('s1') or {}, ensure_ascii=False), json.dumps(data.get('s2') or {}, ensure_ascii=False), json.dumps(data.get('s3') or {}, ensure_ascii=False), json.dumps(data.get('d') or {}, ensure_ascii=False)))
            c.commit(); c.close(); return self.send_json({'ok': True, 'id': pid})
        m = re.match(r'^/api/props/([\w-]+)$', p)
        if m and method == 'PUT':
            pid = m.group(1); data['id'] = pid
            return self.api_props_put(c, data)
        if m and method == 'DELETE':
            c.execute('DELETE FROM props WHERE id=?', (m.group(1),)); c.commit(); c.close()
            return self.send_json({'ok': True})
        # posts
        if p == '/api/posts' and method == 'POST':
            nid = data.get('id') or (c.execute('SELECT COALESCE(MAX(id),0)+1 FROM posts').fetchone()[0])
            c.execute('INSERT OR REPLACE INTO posts(id,img,date,c) VALUES(?,?,?,?)', (nid, data.get('img',''), data.get('date',''), json.dumps(data.get('c') or {}, ensure_ascii=False)))
            c.commit(); c.close(); return self.send_json({'ok': True, 'id': nid})
        m = re.match(r'^/api/posts/(\d+)$', p)
        if m and method == 'PUT':
            c.execute('INSERT OR REPLACE INTO posts(id,img,date,c) VALUES(?,?,?,?)', (int(m.group(1)), data.get('img',''), data.get('date',''), json.dumps(data.get('c') or {}, ensure_ascii=False)))
            c.commit(); c.close(); return self.send_json({'ok': True})
        if m and method == 'DELETE':
            c.execute('DELETE FROM posts WHERE id=?', (int(m.group(1),),)); c.commit(); c.close()
            return self.send_json({'ok': True})
        # messages
        m = re.match(r'^/api/messages/(\d+)$', p)
        if m and method == 'PUT':
            c.execute('UPDATE messages SET readed=? WHERE id=?', (1 if data.get('read') else 0, int(m.group(1))))
            c.commit(); c.close(); return self.send_json({'ok': True})
        if m and method == 'DELETE':
            c.execute('DELETE FROM messages WHERE id=?', (int(m.group(1),),)); c.commit(); c.close()
            return self.send_json({'ok': True})
        # settings
        if p == '/api/settings' and method == 'PUT':
            for k, v in data.items():
                c.execute('INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)', (k, json.dumps(v, ensure_ascii=False)))
            c.commit(); c.close(); return self.send_json({'ok': True})
        # i18n
        if p == '/api/i18n' and method == 'PUT':
            for lang, kv in data.items():
                for k, v in kv.items():
                    c.execute('INSERT OR REPLACE INTO i18n(lang,key,value) VALUES(?,?,?)', (lang, k, v))
            c.commit(); c.close(); return self.send_json({'ok': True})
        # password change
        if p == '/api/password' and method == 'PUT':
            r = c.execute('SELECT * FROM users WHERE username=?', (me,)).fetchone()
            if hashpw(data.get('current',''), r['salt']) != r['hash']:
                c.close(); return self.send_json({'error':'wrong current password'}, 401)
            salt = secrets.token_hex(8)
            c.execute('UPDATE users SET salt=?, hash=? WHERE username=?', (salt, hashpw(data.get('new',''), salt), me))
            c.commit(); c.close(); return self.send_json({'ok': True})
        c.close()
        return self.send_json({'error':'not found'}, 404)

    def api_props_put(self, c, data):
        pid = data['id']
        c.execute('INSERT OR REPLACE INTO props(id,status,district,type,price_num,added,img,rating,year,floor,floors,view,dist,ams,t,loc,price,s1,s2,s3,d) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (pid, data.get('status','sale'), data.get('district',''), data.get('type','apt'), data.get('price_num'), int(data.get('added') or 0), data.get('img',''), data.get('rating') or 4.5, data.get('year'), data.get('floor',''), data.get('floors'), data.get('view','city'),
             json.dumps(data.get('dist') or {}, ensure_ascii=False), json.dumps(data.get('ams') or [], ensure_ascii=False),
             json.dumps(data.get('t') or {}, ensure_ascii=False), json.dumps(data.get('loc') or {}, ensure_ascii=False), json.dumps(data.get('price') or {}, ensure_ascii=False),
             json.dumps(data.get('s1') or {}, ensure_ascii=False), json.dumps(data.get('s2') or {}, ensure_ascii=False), json.dumps(data.get('s3') or {}, ensure_ascii=False), json.dumps(data.get('d') or {}, ensure_ascii=False)))
        c.commit(); c.close()
        return self.send_json({'ok': True, 'id': pid})

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == '__main__':
    srv = ThreadingHTTPServer(('0.0.0.0', 8000), Handler)
    print('server ready on :8000')
    srv.serve_forever()
