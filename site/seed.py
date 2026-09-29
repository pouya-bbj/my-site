#!/usr/bin/env python3
"""Seed SQLite from current site data (idempotent)."""
import re, os, json, sqlite3, subprocess, secrets, hashlib, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'data', 'site.db')
os.makedirs(os.path.join(BASE, 'data'), exist_ok=True)

def hashpw(pw, salt):
    return hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 120000).hex()

c = sqlite3.connect(DB)
c.executescript('''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, salt TEXT, hash TEXT);
CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id INTEGER, created TEXT);
CREATE TABLE IF NOT EXISTS props(id TEXT PRIMARY KEY, status TEXT, district TEXT, type TEXT, price_num INTEGER, added INTEGER, img TEXT, rating REAL, year INTEGER, floor TEXT, floors INTEGER, view TEXT, dist TEXT, ams TEXT, t TEXT, loc TEXT, price TEXT, s1 TEXT, s2 TEXT, s3 TEXT, d TEXT);
CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY, img TEXT, date TEXT, c TEXT);
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, contact TEXT, topic TEXT, msg TEXT, lang TEXT, created TEXT, readed INTEGER);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS i18n(lang TEXT, key TEXT, value TEXT, PRIMARY KEY(lang,key));
''')

# admin user
if not c.execute('SELECT id FROM users WHERE username=?', ('admin',)).fetchone():
    salt = secrets.token_hex(8)
    c.execute('INSERT INTO users(username,salt,hash) VALUES(?,?,?)', ('admin', salt, hashpw('admin123', salt)))

LANGS = ['en','fa','ar','ru','zh','uk','pt']
def dicts_from(path):
    s = open(os.path.join(BASE, path), encoding='utf-8').read()
    out = {}
    for lang in LANGS:
        m = re.search(r'^%s:\{(.*?)\}(,?)$' % lang, s, re.M)
        if m:
            out[lang] = dict(re.findall(r'([A-Za-z_]\w*):"((?:[^"\\]|\\.)*)"', m.group(1)))
    return out

# union of dicts across pages
UNI = {}
for f in ['index.html','projects.html','property.html','services.html','about.html','blog.html','post.html','contact.html']:
    for lang, d in dicts_from(f).items():
        UNI.setdefault(lang, {}).update(d)

def js_eval_array(path, var):
    s = open(os.path.join(BASE, path), encoding='utf-8').read()
    m = re.search(r'const %s=(\[.*?\]);' % var, s, re.S)
    code = 'const %s=%s; console.log(JSON.stringify(%s))' % (var, m.group(1), var)
    r = subprocess.run(['node','-e',code], capture_output=True)
    return json.loads(r.stdout.decode())

props_p = js_eval_array('projects.html', 'PROJECTS')
props_d = js_eval_array('property.html', 'PROPS')
by_id = {p['id']: p for p in props_p}
for p in props_d:
    by_id.setdefault(p['id'], {}).update(p)

KEYMAP = {
 'marinada': dict(t='p1Title', loc='p1Loc', price='p1Price', s=['p1S1','p1S2','p1S3'], d='d1'),
 'bayview':  dict(t='p2Title', loc='p2Loc', price='p2Price', s=['p2S1','p2S2','p2S3'], d='d2'),
 'villa':    dict(t='p3Title', loc='p3Loc', price='p3Price', s=['p3S1','p3S2','p3S3'], d='d3'),
 'office':   dict(t='p4Title', loc='p4Loc', price='p4Price', s=['p4S1','p4S2','p4S3'], d='d4'),
 'bosphorus':dict(t='bTitle',  loc='bLoc',  price='bPrice',  s=['bS1','bS2','bS3'],    d='d5'),
 'galata':   dict(t='gTitle',  loc='gLoc',  price='gPrice',  s=['gS1','gS2','gS3'],    d='d6'),
}
for pid, p in by_id.items():
    km = KEYMAP.get(pid)
    t = {}; loc = {}; pr = {}; s1 = {}; s2 = {}; s3 = {}; dd = {}
    if km:
        for lang in LANGS:
            d = UNI.get(lang, {})
            t[lang] = d.get(km['t'],''); loc[lang] = d.get(km['loc'],''); pr[lang] = d.get(km['price'],'')
            s1[lang] = d.get(km['s'][0],''); s2[lang] = d.get(km['s'][1],''); s3[lang] = d.get(km['s'][2],'')
            dd[lang] = d.get(km['d'],'')
    c.execute('INSERT OR REPLACE INTO props(id,status,district,type,price_num,added,img,rating,year,floor,floors,view,dist,ams,t,loc,price,s1,s2,s3,d) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        (pid, p.get('status','sale'), p.get('district',''), p.get('type','apt'), p.get('priceNum'), p.get('added',0), p.get('img',''), p.get('rating',4.5), p.get('year'), p.get('floor',''), p.get('floors'), p.get('view','city'),
         json.dumps(p.get('dist',{}), ensure_ascii=False), json.dumps(p.get('ams',[]), ensure_ascii=False),
         json.dumps(t, ensure_ascii=False), json.dumps(loc, ensure_ascii=False), json.dumps(pr, ensure_ascii=False),
         json.dumps(s1, ensure_ascii=False), json.dumps(s2, ensure_ascii=False), json.dumps(s3, ensure_ascii=False), json.dumps(dd, ensure_ascii=False)))

# posts
sub = subprocess.run(['node','-e',"var src=require('fs').readFileSync('js/posts.js','utf8').replace('const POSTS=','var POSTS='); eval(src); console.log(JSON.stringify(POSTS))"], cwd=BASE, capture_output=True)
posts = json.loads(sub.stdout.decode())
for p in posts:
    c.execute('INSERT OR REPLACE INTO posts(id,img,date,c) VALUES(?,?,?,?)', (p['id'], p['img'], p['date'], json.dumps(p['c'], ensure_ascii=False)))

# settings
dst = []
for i, did in enumerate(['besiktas','atakoy','galata','zekeriyakoy','beylikduzu','levent'], 1):
    imgs = {'besiktas':'images/district-ortakoy.jpg','atakoy':'images/district-atakoy.jpg','galata':'images/district-galata.jpg','zekeriyakoy':'images/prop1.jpg','beylikduzu':'images/city-istanbul.jpg','levent':'images/office.jpg'}
    name = {}; count = {}
    for lang in LANGS:
        d = UNI.get(lang, {})
        name[lang] = d.get('c%dN' % i, '')
        count[lang] = d.get('c%dC' % i, '')
    dst.append({'id': did, 'img': imgs[did], 'name': name, 'count': count})
settings = {
 'whatsapp': '+90 545 110 90 00',
 'wa_link': '905451109000',
 'address': UNI['en'].get('address',''),
 'hero_slides': ['images/hero.jpg','images/city-istanbul.jpg','images/district-ortakoy.jpg','images/prop1.jpg','images/district-galata.jpg'],
 'destinations': dst,
}
for k, v in settings.items():
    c.execute('INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)', (k, json.dumps(v, ensure_ascii=False)))

# i18n union
for lang, d in UNI.items():
    for k, v in d.items():
        c.execute('INSERT OR REPLACE INTO i18n(lang,key,value) VALUES(?,?,?)', (lang, k, v))

c.commit()
print('seeded: props', c.execute('SELECT COUNT(*) FROM props').fetchone()[0],
      '| posts', c.execute('SELECT COUNT(*) FROM posts').fetchone()[0],
      '| i18n keys/en', c.execute("SELECT COUNT(*) FROM i18n WHERE lang='en'").fetchone()[0])
c.close()
