#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build projects.html from index.html pieces + new i18n/JS/CSS."""
import re

src = open('index.html', encoding='utf-8').read()
HDR = '<header class="site-header" id="siteHeader">'
assert HDR in src

# ---------- extract pieces ----------
head = src[:src.index('</head>') + 7]
head = re.sub(r'<title>.*?</title>', '<title>Projects | Safe Invest Turkey</title>', head, flags=re.S)

h0, h1 = src.index(HDR), src.index('</header>') + len('</header>')
header = src[h0:h1]
header = header.replace('<a class="brand" href="#">', '<a class="brand" href="index.html">')
header = header.replace('href="#projects" target="_blank" rel="noopener"', 'href="#grid"')
header = header.replace('href="#projects"', 'href="#grid"')
header = header.replace('href="#"', 'href="index.html"')

c0, c1 = src.index('<section class="container contact" id="contact">'), src.index('<footer')
contact = src[c0:c1].strip()

f0, f1 = src.index('<footer'), src.index('</footer>') + len('</footer>')
footer = src[f0:f1]
footer = footer.replace('href="#" data-i18n="navProjects"', 'href="#grid" data-i18n="navProjects"')

dicts = {}
for m in re.finditer(r'^(\w+):\{(.*)\},?$', src, re.M):
    dicts[m.group(1)] = m.group(2)
langs_line = re.search(r'^const LANGS = .*$', src, re.M).group(0)

script = src[src.index('<script>') + 8: src.index('</script>')]
dropdown_js = script[script.index('const langWrap'):script.index('/* Header scroll state */')].strip()
scroll_js = script[script.index('/* Header scroll state */'):script.index("applyLang('en');")].strip()
form_js = script[script.index('/* ===== Contact form'):].strip()

# ---------- new i18n keys ----------
NEW = {
    'en': dict(pageTitle="Projects | Safe Invest Turkey", phTitle="Signature Projects & Residences", phSub="A curated portfolio of verified properties across Istanbul — filter by status or district.", fAll="All Projects", fSale="For Sale", fRent="For Rent", fDistrict="All Districts", found="projects found", empty="No projects match your selection — try different filters.", waAsk="Inquire on WhatsApp", waMsg="Hello, I'm interested in this project: ",
               d1="Marina-side living with full amenities in Ataköy's most sought-after residence.", d2="Contemporary apartments with sweeping bay views in Beylikdüzü.", d3="Private villa with pool surrounded by forest, minutes from the Black Sea coast.", d4="Premium furnished office space in the heart of Istanbul's business district.",
               bTitle="Bosphorus Panorama Suites", bLoc="Beşiktaş, Istanbul", bPrice="$480,000", bS1="2 Beds", bS2="2 Baths", bS3="128 m²", d5="Front-row Bosphorus views from every suite in this landmark glass tower.",
               gTitle="Galata Heritage Lofts", gLoc="Galata, Beyoğlu — Istanbul", gPrice="$1,200 / Month", gS1="1 Bed", gS2="1 Bath", gS3="74 m²", d6="Character lofts with exposed brick, steps from Galata Tower."),
    'ar': dict(pageTitle="المشاريع | سيف إنفست تركيا", phTitle="مشاريع وإقامات مميزة", phSub="محفظة مختارة من عقارات موثّقة في أنحاء إسطنبول — صفّوا حسب الحالة أو الحي.", fAll="كل المشاريع", fSale="للبيع", fRent="للإيجار", fDistrict="كل الأحياء", found="مشاريع", empty="لا توجد مشاريع مطابقة لاختياركم — جرّبوا فلاتر أخرى.", waAsk="استفسار عبر واتساب", waMsg="مرحباً، أنا مهتم بهذا المشروع: ",
               d1="معيشة راقية بجانب المارينا مع كل الخدمات في أشهر مجمعات أتاكوي.", d2="شقق عصرية بإطلالات خلابة على الخليج في بيليك دوزو.", d3="فيلا خاصة مع مسبح تحيطها الغابات على مقربة من ساحل البحر الأسود.", d4="مساحة مكتبية فاخرة مفروشة في قلب الحي المالي في إسطنبول.",
               bTitle="أجنحة بانوراما البوسفور", bLoc="بشيكتاش، إسطنبول", bPrice="480,000 دولار", bS1="غرفتان", bS2="حمامان", bS3="128 م²", d5="إطلالة مباشرة على البوسفور من كل جناح في هذا البرج الزجاجي المميز.",
               gTitle="لوفتات غلطة التراثية", gLoc="غلطة، بيوغلو — إسطنبول", gPrice="1,200 دولار شهرياً", gS1="غرفة واحدة", gS2="حمام واحد", gS3="74 م²", d6="لوفتات بطابع تراثي وطوب مكشوف على بُعد خطوات من برج غلطة."),
    'zh': dict(pageTitle="项目 | Safe Invest Turkey", phTitle="精选项目与住宅", phSub="伊斯坦布尔精选认证房产组合——按状态或区域筛选。", fAll="全部项目", fSale="出售", fRent="出租", fDistrict="全部区域", found="个项目", empty="没有符合条件的项目，请尝试其他筛选条件。", waAsk="WhatsApp 咨询", waMsg="您好，我对这个项目感兴趣：",
               d1="阿塔科伊最受欢迎的住宅项目，毗邻码头、配套齐全。", d2="贝利克杜祖的现代公寓，尽享开阔海湾景观。", d3="被森林环抱的私人泳池别墅，临近黑海海岸。", d4="位于伊斯坦布尔商务中心地段的高端精装办公空间。",
               bTitle="博斯普鲁斯全景套房", bLoc="伊斯坦布尔 · 贝西克塔斯", bPrice="$480,000", bS1="2 卧", bS2="2 卫", bS3="128 m²", d5="地标级玻璃塔楼，每间套房尽揽博斯普鲁斯海峡景观。",
               gTitle="加拉塔传承阁楼公寓", gLoc="伊斯坦布尔 · 加拉塔", gPrice="$1,200 / 月", gS1="1 卧", gS2="1 卫", gS3="74 m²", d6="红砖特色阁楼公寓，步行即达加拉塔。"),
    'ru': dict(pageTitle="Проекты | Safe Invest Turkey", phTitle="Избранные проекты и резиденции", phSub="Подборка проверенных объектов по всему Стамбулу — фильтруйте по статусу или району.", fAll="Все проекты", fSale="Продажа", fRent="Аренда", fDistrict="Все районы", found="проектов", empty="Ничего не найдено — попробуйте другие фильтры.", waAsk="Спросить в WhatsApp", waMsg="Здравствуйте, меня интересует проект: ",
               d1="Жизнь у марины со всей инфраструктурой в самой востребованной резиденции Атакёя.", d2="Современные квартиры с панорамным видом на залив в Бейликдюзю.", d3="Частная вилла с бассейном в окружении леса, в минутах от черноморского побережья.", d4="Премиальный меблированный офис в сердце делового района Стамбула.",
               bTitle="Панорамные апартаменты Босфор", bLoc="Бешикташ, Стамбул", bPrice="$480,000", bS1="2 спальни", bS2="2 ванные", bS3="128 м²", d5="Вид на Босфор из каждого номера в этой знаковой стеклянной башне.",
               gTitle="Лофты Галата", gLoc="Галата, Стамбул", gPrice="$1,200 / мес", gS1="1 спальня", gS2="1 ванная", gS3="74 м²", d6="Атмосферные лофты с кирпичной кладкой в шаге от Галатской башни."),
    'tr': dict(pageTitle="Projeler | Safe Invest Turkey", phTitle="Seçkin Projeler ve Rezidanslar", phSub="İstanbul genelinde doğrulanmış seçkin portföy — duruma veya semte göre filtreleyin.", fAll="Tüm Projeler", fSale="Satılık", fRent="Kiralık", fDistrict="Tüm Semtler", found="proje bulundu", empty="Seçiminize uyan proje yok — farklı filtreler deneyin.", waAsk="WhatsApp'tan Sorun", waMsg="Merhaba, bu projeyle ilgileniyorum: ",
               d1="Ataköy'ün en gözde rezidansında, marina yanında tam donanımlı yaşam.", d2="Beylikdüzü'nde geniş körfez manzaralı çağdaş daireler.", d3="Karadeniz kıyısına birkaç dakika, orman içinde havuzlu özel villa.", d4="İstanbul'un iş merkezinde premium mobilyalı ofis alanı.",
               bTitle="Boğaz Panorama Süitleri", bLoc="Beşiktaş, İstanbul", bPrice="$480,000", bS1="2 Oda", bS2="2 Banyo", bS3="128 m²", d5="Bu simgesel cam kulede her süitten kesintisiz Boğaz manzarası.",
               gTitle="Galata Tarihî Loftları", gLoc="Galata, Beyoğlu — İstanbul", gPrice="Aylık $1,200", gS1="1 Oda", gS2="1 Banyo", gS3="74 m²", d6="Galata Kulesi'ne birkaç adım, tuğla dokulu karakterli loftlar."),
    'es': dict(pageTitle="Proyectos | Safe Invest Turkey", phTitle="Proyectos y Residencias Exclusivas", phSub="Un portafolio curado de propiedades verificadas en Estambul: filtre por estado o distrito.", fAll="Todos", fSale="En Venta", fRent="En Alquiler", fDistrict="Todos los Distritos", found="proyectos", empty="Ningún proyecto coincide con su selección: pruebe otros filtros.", waAsk="Consultar por WhatsApp", waMsg="Hola, me interesa este proyecto: ",
               d1="Vida junto a la marina con todas las comodidades en la residencia más exclusiva de Ataköy.", d2="Apartamentos contemporáneos con amplias vistas a la bahía en Beylikdüzü.", d3="Villa privada con piscina rodeada de bosque, a minutos de la costa del Mar Negro.", d4="Oficina premium amueblada en el corazón del distrito financiero de Estambul.",
               bTitle="Suites Panorama del Bósforo", bLoc="Beşiktaş, Estambul", bPrice="$480,000", bS1="2 Hab.", bS2="2 Baños", bS3="128 m²", d5="Vistas frontales al Bósforo desde cada suite de esta torre emblemática.",
               gTitle="Lofts Históricos de Gálata", gLoc="Gálata, Beyoğlu — Estambul", gPrice="$1,200 / mes", gS1="1 Hab.", gS2="1 Baño", gS3="74 m²", d6="Lofts con carácter y ladrillo visto, a pasos de la Torre de Gálata."),
    'fr': dict(pageTitle="Projets | Safe Invest Turkey", phTitle="Projets & Résidences Signature", phSub="Un portefeuille choisi de biens vérifiés à travers Istanbul — filtrez par statut ou quartier.", fAll="Tous les projets", fSale="À Vendre", fRent="À Louer", fDistrict="Tous les quartiers", found="projets", empty="Aucun projet ne correspond à votre sélection — essayez d'autres filtres.", waAsk="Demander sur WhatsApp", waMsg="Bonjour, je suis intéressé par ce projet : ",
               d1="Vie au bord de la marina avec toutes les commodités dans la résidence la plus prisée d'Ataköy.", d2="Appartements contemporains avec vue dégagée sur la baie à Beylikdüzü.", d3="Villa privée avec piscine entourée de forêt, à quelques minutes de la côte de la mer Noire.", d4="Bureaux haut de gamme meublés au cœur du quartier d'affaires d'Istanbul.",
               bTitle="Suites Panorama du Bosphore", bLoc="Beşiktaş, Istanbul", bPrice="480 000 $", bS1="2 ch.", bS2="2 bains", bS3="128 m²", d5="Vue frontale sur le Bosphore depuis chaque suite de cette tour emblématique.",
               gTitle="Lofts Historiques de Galata", gLoc="Galata, Beyoğlu — Istanbul", gPrice="1 200 $ / mois", gS1="1 ch.", gS2="1 bain", gS3="74 m²", d6="Lofts de caractère aux briques apparentes, à deux pas de la tour de Galata."),
}

def esc(v):
    return v.replace('\\', '\\\\').replace('"', '\\"')

order = ['en', 'ar', 'zh', 'ru', 'tr', 'es', 'fr']
new_dict_lines = []
for i, l in enumerate(order):
    extra = ','.join('%s:"%s"' % (k, esc(v)) for k, v in NEW[l].items())
    new_dict_lines.append('%s:{%s,%s}%s' % (l, dicts[l], extra, ',' if i < len(order) - 1 else ''))
i18n_js = 'const I18N = {\n' + '\n'.join(new_dict_lines) + '\n};\n'

apply_lang_js = """let lang = 'en';
function applyLang(l){
  lang = l;
  const d = I18N[l];
  document.documentElement.lang = l;
  document.documentElement.dir = LANGS[l].rtl ? 'rtl' : 'ltr';
  document.title = d.pageTitle;
  document.querySelectorAll('[data-i18n]').forEach(el=>{
    const k = el.getAttribute('data-i18n');
    if (d[k] !== undefined) el.textContent = d[k];
  });
  document.querySelectorAll('[data-i18n-ph]').forEach(el=>{
    const k = el.getAttribute('data-i18n-ph');
    if (d[k] !== undefined) el.setAttribute('placeholder', d[k]);
  });
  document.getElementById('langLabel').textContent = LANGS[l].native;
  document.querySelectorAll('.lang-menu button').forEach(b=>b.classList.toggle('active', b.dataset.lang === l));
  if (typeof renderGrid === 'function') renderGrid();
}
"""

projects_js = """
/* ===== Projects grid & filters ===== */
const PIN='<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-5.2-7-11a7 7 0 1 1 14 0c0 5.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.6"/></svg>';
const SPEC_ICONS=[
 '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-8a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v8"/><path d="M3 18h18"/><path d="M6 8V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2"/></svg>',
 '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16v2a4 4 0 0 1-4 4H8a4 4 0 0 1-4-4v-2z"/><path d="M6 12V5a2 2 0 0 1 4 0"/></svg>',
 '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 15l6-6"/></svg>'];
const WA_ICON='<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.6-1.2A9 9 0 1 0 12 3z"/><path d="M9.4 9.3c.5 2.2 2.6 4.3 4.8 4.8l1.2-1.2 2.3 1.2c-.4 1.6-1.9 2.3-3.5 1.9-3-.8-5.7-3.5-6.5-6.5-.4-1.6.3-3.1 1.9-3.5l1.2 2.3z"/></svg>';
const PROJECTS=[
 {img:'images/prop4.jpg',  status:'sale', district:'atakoy',      t:'p1Title', loc:'p1Loc', price:'p1Price', specs:['p1S1','p1S2','p1S3'], d:'d1'},
 {img:'images/prop2.jpg',  status:'sale', district:'beylikduzu',  t:'p2Title', loc:'p2Loc', price:'p2Price', specs:['p2S1','p2S2','p2S3'], d:'d2'},
 {img:'images/prop1.jpg',  status:'sale', district:'zekeriyakoy', t:'p3Title', loc:'p3Loc', price:'p3Price', specs:['p3S1','p3S2','p3S3'], d:'d3'},
 {img:'images/prop5.jpg',  status:'sale', district:'besiktas',    t:'bTitle',  loc:'bLoc',  price:'bPrice',  specs:['bS1','bS2','bS3'],    d:'d5'},
 {img:'images/prop6.jpg',  status:'rent', district:'galata',      t:'gTitle',  loc:'gLoc',  price:'gPrice',  specs:['gS1','gS2','gS3'],    d:'d6'},
 {img:'images/office.jpg', status:'rent', district:'levent',      t:'p4Title', loc:'p4Loc', price:'p4Price', specs:['p4S1','p4S2','p4S3'], d:'d4'}
];
let fStatus='all', fDistrict='all';
function renderGrid(){
  const d = I18N[lang] || I18N.en;
  const grid = document.getElementById('pGrid');
  if(!grid) return;
  const list = PROJECTS.filter(p => (fStatus==='all'||p.status===fStatus) && (fDistrict==='all'||p.district===fDistrict));
  document.getElementById('pCount').textContent = list.length;
  document.getElementById('pEmpty').hidden = list.length > 0;
  grid.innerHTML = list.map((p,i)=>{
    const badge = p.status==='sale' ? d.p1Badge : d.p4Badge;
    const specs = p.specs.map((k,j)=>'<span class="stat">'+SPEC_ICONS[j%3]+'<span>'+d[k]+'</span></span>').join('');
    const wa = 'https://wa.me/905451109000?text=' + encodeURIComponent(d.waMsg + d[p.t]);
    return '<article class="card reveal" data-d="'+((i%3)+1)+'">'
      + '<div class="card-media"><img src="'+p.img+'" alt="'+d[p.t]+'" loading="lazy"><span class="badge '+p.status+'">'+badge+'</span></div>'
      + '<div class="card-body">'
      + '<div class="card-loc">'+PIN+'<span>'+d[p.loc]+'</span></div>'
      + '<h3>'+d[p.t]+'</h3>'
      + '<p class="card-desc">'+d[p.d]+'</p>'
      + '<div class="price">'+d[p.price]+'</div>'
      + '<div class="card-foot"><div class="stats">'+specs+'</div></div>'
      + '<a class="wa-mini" href="'+wa+'" target="_blank" rel="noopener">'+WA_ICON+'<span>'+d.waAsk+'</span></a>'
      + '</div></article>';
  }).join('');
  grid.querySelectorAll('.reveal').forEach(el=>io.observe(el));
}
document.querySelectorAll('.f-chip').forEach(c=>c.addEventListener('click',()=>{
  fStatus = c.dataset.f;
  document.querySelectorAll('.f-chip').forEach(x=>x.classList.toggle('active', x===c));
  renderGrid();
}));
document.getElementById('fDistrict').addEventListener('change', e=>{ fDistrict = e.target.value; renderGrid(); });
"""

extra_css = """
  /* ===== Projects page ===== */
  .page-hero{position:relative;padding:168px 0 66px;background:linear-gradient(rgba(8,15,28,.88),rgba(10,20,36,.96)),url('images/district-galata.jpg') center/cover;overflow:hidden}
  .page-hero .kicker{animation:none}
  .page-hero h1{font-size:clamp(34px,4.6vw,56px);line-height:1.14;margin:16px 0 6px;color:#fff}
  .page-hero .orn{display:flex;align-items:center;gap:8px;margin:14px 0}
  .page-hero .orn i{width:34px;height:2px;background:linear-gradient(90deg,var(--gold-light),transparent)}
  .page-hero .orn b{width:7px;height:7px;background:var(--gold);transform:rotate(45deg)}
  .ph-sub{color:var(--muted);max-width:660px;font-size:15px;line-height:1.85}
  #grid{scroll-margin-top:90px}
  .filterbar{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin:36px 0 28px}
  .f-chips{display:flex;gap:10px;flex-wrap:wrap}
  .f-chip{border:1px solid rgba(201,161,94,.4);background:rgba(255,255,255,.03);color:#D0D5DD;padding:9px 20px;border-radius:999px;font-size:13px;font-weight:600;cursor:pointer;transition:.25s;font-family:inherit}
  .f-chip:hover{border-color:var(--gold);color:var(--gold-light);transform:translateY(-1px)}
  .f-chip.active{background:linear-gradient(135deg,var(--gold-light),var(--gold-dark));border-color:transparent;color:#221604;font-weight:800;box-shadow:0 6px 18px rgba(201,161,94,.3)}
  .f-right{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
  .p-count{color:var(--muted);font-size:13px}
  .p-count b{color:var(--gold-light);font-size:15px;margin-inline-end:4px}
  .f-select{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.16);color:#fff;padding:10px 14px;border-radius:10px;font-size:13px;font-weight:600;min-width:172px;cursor:pointer;font-family:inherit}
  .f-select:focus{outline:none;border-color:var(--gold)}
  .f-select option{background:var(--navy-800);color:#fff}
  .p-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:26px}
  .card-desc{color:var(--muted);font-size:13.5px;line-height:1.7;margin:8px 0 12px}
  .wa-mini{display:inline-flex;align-items:center;gap:9px;margin-top:16px;padding:11px 18px;border-radius:10px;border:1px solid rgba(37,211,102,.5);background:rgba(37,211,102,.1);color:#8CE99A;font-size:12.5px;font-weight:700;transition:.25s}
  .wa-mini:hover{background:#25D366;border-color:#25D366;color:#06301B;transform:translateY(-2px);box-shadow:0 8px 22px rgba(37,211,102,.32)}
  #pEmpty{text-align:center;color:var(--muted);padding:70px 20px;font-size:15px;border:1px dashed rgba(201,161,94,.35);border-radius:16px;margin-top:8px}
  @media(max-width:1100px){.p-grid{grid-template-columns:repeat(2,1fr)}}
  @media(max-width:680px){.p-grid{grid-template-columns:1fr}.page-hero{padding:140px 0 52px}.filterbar{margin:28px 0 22px}}
"""
head = head.replace('</style>', extra_css + '\n</style>')

body = """
<section class="page-hero">
  <div class="container">
    <div class="kicker" data-i18n="projectsBtn">Projects</div>
    <h1 class="reveal in" data-i18n="phTitle">Signature Projects &amp; Residences</h1>
    <div class="orn"><i></i><b></b></div>
    <p class="ph-sub" data-i18n="phSub">A curated portfolio of verified properties across Istanbul — filter by status or district.</p>
  </div>
</section>

<main class="page container" id="grid">
  <div class="filterbar reveal">
    <div class="f-chips">
      <button class="f-chip active" data-f="all" data-i18n="fAll">All Projects</button>
      <button class="f-chip" data-f="sale" data-i18n="fSale">For Sale</button>
      <button class="f-chip" data-f="rent" data-i18n="fRent">For Rent</button>
    </div>
    <div class="f-right">
      <span class="p-count"><b id="pCount">6</b><span data-i18n="found">projects found</span></span>
      <select id="fDistrict" class="f-select" aria-label="District">
        <option value="all" data-i18n="fDistrict">All Districts</option>
        <option value="atakoy">Ataköy</option>
        <option value="beylikduzu">Beylikdüzü</option>
        <option value="zekeriyakoy">Zekeriyaköy</option>
        <option value="besiktas">Beşiktaş</option>
        <option value="galata">Galata</option>
        <option value="levent">Levent</option>
      </select>
    </div>
  </div>

  <div id="pGrid" class="p-grid"></div>
  <p id="pEmpty" hidden data-i18n="empty"></p>
</main>
"""

script_js = (i18n_js + '\n' + langs_line + '\n' + apply_lang_js + '\n'
             + dropdown_js + '\n\n' + scroll_js + '\n' + projects_js
             + "\napplyLang('en');\n" + form_js + '\n')

html = (head + '\n<body>\n' + header + '\n' + body + '\n'
        + contact + '\n\n' + footer + '\n\n<script>\n' + script_js
        + '</script>\n</body>\n</html>\n')

open('projects.html', 'w', encoding='utf-8').write(html)
print('projects.html written:', len(html), 'chars')
