/* Public auth: Sign In button -> login/register modal; admin creds -> admin panel */
(function(){
  var T = {
    en:{login:'Sign In',register:'Create Account',user:'Username',pass:'Password',name:'Full Name (optional)',toLogin:'Sign In',toReg:'Sign Up',have:'Already have an account?',no:'New here? Create an account',errBad:'Wrong username or password',errUser:'This username is already taken',errWeak:'Username min 3 chars, password min 4',errNet:'Server not reachable — try again',welcome:'Welcome',logout:'Sign Out',admin:'Admin Panel',title:'Your account'},
    fa:{login:'ورود',register:'ثبت‌نام',user:'نام کاربری',pass:'رمز عبور',name:'نام و نام خانوادگی (اختیاری)',toLogin:'ورود',toReg:'ثبت‌نام',have:'حساب دارید؟ وارد شوید',no:'حساب ندارید؟ ثبت‌نام کنید',errBad:'نام کاربری یا رمز اشتباه است',errUser:'این نام کاربری قبلاً گرفته شده',errWeak:'نام کاربری حداقل ۳ و رمز حداقل ۴ نویسه',errNet:'سرور در دسترس نیست — دوباره تلاش کنید',welcome:'خوش آمدید',logout:'خروج',admin:'پنل مدیریت',title:'حساب شما'},
    ar:{login:'تسجيل الدخول',register:'إنشاء حساب',user:'اسم المستخدم',pass:'كلمة المرور',name:'الاسم الكامل (اختياري)',toLogin:'دخول',toReg:'تسجيل',have:'لديك حساب؟ سجّل الدخول',no:'ليس لديك حساب؟ أنشئ حساباً',errBad:'اسم المستخدم أو كلمة المرور خاطئة',errUser:'اسم المستخدم محجوز',errWeak:'الاسم 3 أحرف والرمز 4 على الأقل',errNet:'الخادم غير متاح — حاول مجدداً',welcome:'مرحباً',logout:'خروج',admin:'لوحة الإدارة',title:'حسابك'},
    ru:{login:'Войти',register:'Регистрация',user:'Имя пользователя',pass:'Пароль',name:'Полное имя (необязательно)',toLogin:'Войти',toReg:'Создать',have:'Уже есть аккаунт? Войдите',no:'Нет аккаунта? Зарегистрируйтесь',errBad:'Неверный логин или пароль',errUser:'Имя пользователя занято',errWeak:'Логин от 3, пароль от 4 символов',errNet:'Сервер недоступен — попробуйте снова',welcome:'Добро пожаловать',logout:'Выйти',admin:'Админ‑панель',title:'Ваш аккаунт'},
    zh:{login:'登录',register:'注册',user:'用户名',pass:'密码',name:'姓名（可选）',toLogin:'登录',toReg:'注册',have:'已有账号？去登录',no:'没有账号？去注册',errBad:'用户名或密码错误',errUser:'用户名已被占用',errWeak:'用户名至少 3 字符，密码至少 4 字符',errNet:'服务器不可达，请重试',welcome:'欢迎',logout:'退出',admin:'管理后台',title:'您的账户'},
    uk:{login:'Увійти',register:'Реєстрація',user:'Імʼя користувача',pass:'Пароль',name:'Повне імʼя (необовʼязково)',toLogin:'Увійти',toReg:'Створити',have:'Вже є акаунт? Увійдіть',no:'Немає акаунта? Зареєструйтесь',errBad:'Невірний логін або пароль',errUser:'Імʼя користувача зайняте',errWeak:'Логін від 3, пароль від 4 символів',errNet:'Сервер недоступний — спробуйте знову',welcome:'Вітаємо',logout:'Вийти',admin:'Адмін‑панель',title:'Ваш акаунт'},
    pt:{login:'Entrar',register:'Criar Conta',user:'Usuário',pass:'Senha',name:'Nome completo (opcional)',toLogin:'Entrar',toReg:'Cadastrar',have:'Já tem conta? Entrar',no:'Não tem conta? Cadastre‑se',errBad:'Usuário ou senha incorretos',errUser:'Usuário já existe',errWeak:'Usuário mín. 3, senha mín. 4 caracteres',errNet:'Servidor inacessível — tente de novo',welcome:'Bem‑vindo',logout:'Sair',admin:'Painel Admin',title:'Sua conta'}
  };
  function L(){ var l = window.lang || 'en'; return T[l] || T.en; }
  var MEM = { token:'' };
  function getToken(){ try{ return localStorage.getItem('sit_token') || MEM.token; }catch(e){ return MEM.token; } }
  function setToken(t){ MEM.token = t; try{ if(t) localStorage.setItem('sit_token',t); else localStorage.removeItem('sit_token'); }catch(e){} }

  var css = document.createElement('style');
  css.textContent = '.am-wrap{position:fixed;inset:0;z-index:400;background:rgba(3,7,14,.82);backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;padding:16px}' +
    '.am-card{width:400px;max-width:100%;background:linear-gradient(160deg,#101B2E,#0C1524);border:1px solid rgba(201,161,94,.3);border-radius:20px;padding:30px 28px;box-shadow:0 30px 80px rgba(0,0,0,.55)}' +
    '.am-card h3{color:#fff;font-size:17px;font-weight:800;margin-bottom:18px;text-align:center}' +
    '.am-tabs{display:flex;gap:8px;margin-bottom:18px}' +
    '.am-tabs button{flex:1;padding:10px;border-radius:10px;border:1px solid rgba(201,161,94,.3);background:transparent;color:#98A2B3;font-size:13px;font-weight:700}' +
    '.am-tabs button.on{background:linear-gradient(135deg,#E4C580,#C9A15E);color:#221604;border-color:transparent}' +
    '.am-card input{width:100%;background:rgba(255,255,255,.05);border:1px solid rgba(201,161,94,.25);border-radius:11px;padding:12px 14px;color:#E8ECF2;font-size:13.5px;margin-bottom:11px;outline:none}' +
    '.am-card input:focus{border-color:#C9A15E}' +
    '.am-err{color:#E5735C;font-size:12px;min-height:16px;margin-bottom:8px;text-align:center}' +
    '.am-btn{width:100%;background:linear-gradient(135deg,#E4C580,#C9A15E);color:#221604;border:none;border-radius:11px;padding:13px;font-size:14px;font-weight:800;cursor:pointer}' +
    '.am-swap{display:block;text-align:center;color:#98A2B3;font-size:12px;margin-top:14px;cursor:pointer;text-decoration:underline;text-underline-offset:4px}' +
    '.am-close{position:absolute;top:14px;inset-inline-end:14px;background:transparent;border:none;color:#98A2B3;font-size:16px;cursor:pointer}' +
    '.am-menu{position:absolute;top:calc(100% + 10px);inset-inline-end:0;background:#101B2E;border:1px solid rgba(201,161,94,.35);border-radius:14px;padding:8px;min-width:180px;z-index:60;box-shadow:0 20px 50px rgba(0,0,0,.5)}' +
    '.am-menu button,.am-menu a{display:block;width:100%;text-align:start;padding:10px 12px;border:none;background:transparent;color:#E8ECF2;font-size:13px;border-radius:9px;cursor:pointer;text-decoration:none}' +
    '.am-menu button:hover,.am-menu a:hover{background:rgba(201,161,94,.12);color:#E4C580}' +
    '.signin-wrap{position:relative}';
  document.head.appendChild(css);

  var wrap = document.createElement('div');
  wrap.className = 'am-wrap';
  wrap.hidden = true;
  wrap.innerHTML = '<div class="am-card" style="position:relative"><button class="am-close" id="amClose">✕</button><h3 id="amTitle">Your account</h3>' +
    '<div class="am-tabs"><button id="amTabL" class="on">Sign In</button><button id="amTabR">Create Account</button></div>' +
    '<input id="amName" style="display:none" placeholder="Full name (optional)">' +
    '<input id="amUser" autocomplete="username" placeholder="Username">' +
    '<input id="amPass" type="password" autocomplete="current-password" placeholder="Password">' +
    '<div class="am-err" id="amErr"></div>' +
    '<button class="am-btn" id="amGo">Sign In</button>' +
    '<span class="am-swap" id="amSwap">New here? Create an account</span></div>';
  document.body.appendChild(wrap);
  try{ render(); }catch(e){}

  var mode = 'login';
  function render(){
    var d = L();
    document.getElementById('amTitle').textContent = d.title;
    document.getElementById('amTabL').textContent = d.login;
    document.getElementById('amTabR').textContent = d.register;
    document.getElementById('amTabL').classList.toggle('on', mode==='login');
    document.getElementById('amTabR').classList.toggle('on', mode==='reg');
    document.getElementById('amName').style.display = mode==='reg' ? 'block' : 'none';
    document.getElementById('amName').placeholder = d.name;
    document.getElementById('amUser').placeholder = d.user;
    document.getElementById('amPass').placeholder = d.pass;
    document.getElementById('amGo').textContent = mode==='reg' ? d.toReg : d.toLogin;
    document.getElementById('amSwap').textContent = mode==='reg' ? d.have : d.no;
    document.getElementById('amErr').textContent = '';
  }
  function openM(){ mode='login'; wrap.hidden=false; try{ render(); }catch(e){} }
  function closeM(){ wrap.hidden=true; }
  document.getElementById('amClose').onclick = closeM;
  wrap.addEventListener('click', function(e){ if(e.target===wrap) closeM(); });
  document.getElementById('amTabL').onclick = function(){ mode='login'; render(); };
  document.getElementById('amTabR').onclick = function(){ mode='reg'; render(); };
  document.getElementById('amSwap').onclick = function(){ mode = mode==='login'?'reg':'login'; render(); };
  document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeM(); });

  async function post(p, body){
    var r = await fetch(p, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    return r.json();
  }
  async function afterLogin(r){
    setToken(r.token);
    closeM();
    if(r.role === 'admin'){ window.location.href = 'admin.html'; return; }
    refreshBtn();
    var d = L();
    var t = document.querySelector('.signin-btn');
    if(t) toastMsg(d.welcome + ' ' + (r.username||''));
  }
  function toastMsg(s){
    var el = document.createElement('div');
    el.textContent = s;
    el.style.cssText = 'position:fixed;bottom:24px;inset-inline-start:24px;background:#101B2E;border:1px solid #C9A15E;color:#E4C580;border-radius:12px;padding:12px 20px;font-size:13px;font-weight:700;z-index:500;box-shadow:0 16px 40px rgba(0,0,0,.5)';
    document.body.appendChild(el);
    setTimeout(function(){ el.remove(); }, 2600);
  }
  document.getElementById('amGo').onclick = async function(){
    var d = L();
    var u = document.getElementById('amUser').value.trim();
    var p = document.getElementById('amPass').value;
    var err = document.getElementById('amErr');
    err.textContent = '';
    try{
      if(mode==='reg'){
        var r = await post('/api/register', {username:u, password:p, name:document.getElementById('amName').value});
        if(r.ok) return afterLogin(r);
        err.textContent = r.error==='taken' ? d.errUser : d.errWeak;
      } else {
        var r2 = await post('/api/login', {username:u, password:p});
        if(r2.ok) return afterLogin(r2);
        err.textContent = d.errBad;
      }
    }catch(e){ err.textContent = d.errNet; }
  };
  document.getElementById('amPass').addEventListener('keydown', function(e){ if(e.key==='Enter') document.getElementById('amGo').click(); });

  /* header button behaviour */
  var menu = null;
  function closeMenu(){ if(menu){ menu.remove(); menu=null; } }
  document.addEventListener('click', function(e){ if(menu && !menu.contains(e.target) && !e.target.classList.contains('signin-btn')) closeMenu(); });
  var SESSION = null;
  function refreshBtn(){
    var btn = document.querySelector('.signin-btn');
    if(!btn) return;
    if(SESSION){
      btn.textContent = (SESSION.display || SESSION.username);
    }
  }
  async function init(){
    var tk = getToken();
    var btn = document.querySelector('.signin-btn');
    if(!btn) return;
    var w = document.createElement('span');
    w.className = 'signin-wrap';
    btn.parentNode.insertBefore(w, btn);
    w.appendChild(btn);
    if(tk){
      try{
        var r = await fetch('/api/me', {headers:{'X-Token':tk}}).then(function(x){return x.json();});
        if(r.ok){ SESSION = r; refreshBtn(); }
        else setToken('');
      }catch(e){}
    }
    btn.addEventListener('click', async function(e){
      e.stopPropagation();
      if(!SESSION){ openM(); return; }
      closeMenu();
      var d = L();
      menu = document.createElement('div');
      menu.className = 'am-menu';
      menu.innerHTML = (SESSION.role==='admin' ? '<a href="admin.html">'+d.admin+'</a>' : '') + '<button id="amOut">'+d.logout+'</button>';
      w.appendChild(menu);
      menu.querySelector('#amOut').onclick = async function(){
        try{ await fetch('/api/logout', {method:'POST', headers:{'X-Token':getToken()}}); }catch(e){}
        setToken(''); SESSION = null; closeMenu();
        btn.textContent = (window.I18N && I18N[window.lang]) ? I18N[window.lang].signin : 'Sign In';
      };
    });
  }
  /* re-render modal labels when language changes */
  document.addEventListener('click', function(e){
    var b = e.target.closest && e.target.closest('.lang-menu button');
    if(b && !wrap.hidden) setTimeout(render, 50);
  });
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
