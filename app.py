import os, sqlite3, hashlib, datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
DB="noorbook.db"
def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
    d=db()
    d.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT UNIQUE, password TEXT, bio TEXT DEFAULT '', avatar TEXT DEFAULT '')")
    d.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT, media TEXT DEFAULT '', media_type TEXT DEFAULT 'none', post_type TEXT DEFAULT 'post', created_at TEXT, views INTEGER DEFAULT 0, boosted INTEGER DEFAULT 0)")
    d.execute("CREATE TABLE IF NOT EXISTS likes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, post_id INTEGER, UNIQUE(user_id, post_id))")
    d.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, user_id INTEGER, content TEXT, created_at TEXT)")
    d.execute("CREATE TABLE IF NOT EXISTS stories (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, media TEXT, text TEXT, created_at TEXT)")
    d.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER, receiver_id INTEGER, content TEXT, created_at TEXT)")
    d.execute("CREATE TABLE IF NOT EXISTS follows (id INTEGER PRIMARY KEY AUTOINCREMENT, follower_id INTEGER, following_id INTEGER, UNIQUE(follower_id, following_id))")
    d.execute("CREATE TABLE IF NOT EXISTS saved (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, post_id INTEGER, UNIQUE(user_id, post_id))")
    d.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, price TEXT, img TEXT DEFAULT '', seller TEXT DEFAULT '')")
    d.execute("CREATE TABLE IF NOT EXISTS settings (user_id INTEGER PRIMARY KEY, delta_sync INTEGER DEFAULT 1, mqtt INTEGER DEFAULT 1, dark INTEGER DEFAULT 0)")
    d.commit(); d.close()
init()
def hp(p): return hashlib.sha256((p or "").encode()).hexdigest()
def now(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

HTML="""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NoorBook - نور - النهائي</title><style>
*{box-sizing:border-box}body{font-family:Arial;background:#f0f2f5;margin:0;padding-bottom:80px}body.dark{background:#18191a;color:#e4e6eb}
.top{position:sticky;top:0;z-index:20;background:#fff;display:flex;gap:8px;align-items:center;padding:10px}body.dark .top{background:#242526}
.logo{font-weight:900;color:#1877f2;font-size:22px}
.card{background:#fff;border-radius:14px;padding:14px;margin:10px;box-shadow:0 1px 3px #ccc}body.dark .card{background:#242526}
input,textarea,select{width:100%;padding:11px;border:1px solid #ddd;border-radius:10px;margin:5px 0}
button{background:#1877f2;color:#fff;border:none;padding:11px;border-radius:10px;font-weight:bold;cursor:pointer;width:100%;margin-top:6px}
button.green{background:#42b72a}button.gray{background:#e4e6eb;color:#000}button.red{background:#ff3b30}button.pink{background:#e91e63}button.orange{background:#ff9800}
.avatar{width:44px;height:44px;border-radius:50%;background:#1877f2;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:bold;flex-shrink:0;overflow:hidden}.avatar img{width:100%;height:100%;object-fit:cover}
.flex{display:flex;gap:10px;align-items:center}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.menu-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.menu-item{background:#fff;border:1px solid #ddd;border-radius:14px;padding:14px;text-align:center;cursor:pointer;font-weight:bold}body.dark .menu-item{background:#242526}
.menu-row{display:flex;justify-content:space-between;padding:12px;border-bottom:1px solid #eee;cursor:pointer}
.drawer{position:fixed;top:0;right:0;bottom:0;width:330px;max-width:88vw;background:#fff;z-index:40;overflow:auto;transform:translateX(105%);transition:.3s}body.dark .drawer{background:#242526}.drawer.open{transform:translateX(0)}.drawer-overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:35;display:none}.drawer-overlay.show{display:block}
.storyRow{display:flex;gap:10px;overflow:auto}.story{min-width:110px;height:175px;border-radius:14px;background:#ddd;position:relative;overflow:hidden}.story img,.story video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.story b{position:absolute;bottom:8px;right:8px;color:#fff;text-shadow:0 0 5px #000;z-index:2}
.tabs{position:fixed;bottom:0;left:0;right:0;background:#fff;display:flex;justify-content:space-around;padding:8px 2px;border-top:1px solid #ddd;z-index:30}body.dark .tabs{background:#242526}.tabs div{text-align:center;font-size:12px;cursor:pointer}.tabs .active{color:#1877f2;font-weight:900}
.modal{position:fixed;inset:0;background:rgba(0,0,0,.6);display:none;align-items:flex-end;justify-content:center;z-index:50}.modal .box{background:#fff;width:100%;max-width:500px;border-radius:20px 20px 0 0;padding:16px;max-height:90vh;overflow:auto}body.dark .modal .box{background:#242526}
.postImg{width:100%;border-radius:12px;margin-top:8px}.postVideo{width:100%;border-radius:12px;margin-top:8px}.act{display:flex;gap:6px}.act button{flex:1;background:#e4e6eb;color:#000}
.chip{padding:12px;border-radius:12px;background:#f0f2f5;text-align:center;cursor:pointer;font-weight:bold}.chip.active{background:#1877f2;color:#fff}
.tab{display:none}.tab.active{display:block}.msg{padding:9px 12px;border-radius:14px;margin:5px 0;max-width:80%}.me{background:#1877f2;color:#fff;margin-left:auto}.other{background:#e4e6eb}
</style></head><body>
<header class="top"><button style="width:auto" class="gray" onclick="openDrawer()">☰</button><input id="searchInput" placeholder="🔍 بحث في NoorBook" oninput="searchUsers()" style="margin:0"><button style="width:auto" class="gray" onclick="showTab('notifications')">🔔</button><button style="width:auto" class="gray" onclick="showTab('talk')">💬</button><div class="logo">NoorBook نور</div></header>
<div id="drawerOverlay" class="drawer-overlay" onclick="closeDrawer()"></div>
<div id="drawer" class="drawer"><div style="padding:14px"><div class="flex"><div class="avatar" id="dAvatar">ن</div><div><b id="dName">حساب حقيقي</b><br><small id="dEmail"></small><br><span onclick="showTab('profile');closeDrawer()" style="color:#1877f2;cursor:pointer">عرض الملف الشخصي</span></div><button style="width:auto" class="gray" onclick="closeDrawer()">✕</button></div>
<div class="menu-grid" style="margin-top:12px"><div class="menu-item" onclick="showTab('profile');closeDrawer()">👤<br>بروفايل</div><div class="menu-item" onclick="showTab('saved');closeDrawer()">🔖<br>المحفوظة</div><div class="menu-item" onclick="showTab('friends');closeDrawer()">👥<br>الأصدقاء</div><div class="menu-item" onclick="showTab('reels');closeDrawer()">🎬<br>ريلز</div><div class="menu-item" onclick="showTab('feed');closeDrawer()">📰<br>الأخبار</div><div class="menu-item" onclick="showTab('events');closeDrawer()">📅<br>المناسبات</div><div class="menu-item" onclick="showTab('games');closeDrawer()">🎮<br>الألعاب</div><div class="menu-item" onclick="showTab('market');closeDrawer()">🛒<br>السوق</div><div class="menu-item" onclick="showTab('memories');closeDrawer()">🕐<br>الذكريات</div><div class="menu-item" onclick="showTab('groups');closeDrawer()">👥<br>المجموعات</div><div class="menu-item" onclick="showTab('ads');closeDrawer()">📣<br>الترقيات</div><div class="menu-item" onclick="showTab('settings');closeDrawer()">⚙️<br>الإعدادات</div></div>
<div class="card" style="margin:10px 0"><h3>⚙️ الإعدادات والخصوصية</h3><div class="menu-row" onclick="toggleSub('settings')">⚙️ الإعدادات <span>›</span></div><div id="sub-settings" style="display:none;padding:10px"><div>مركز الخصوصية</div><div>إدارة الوقت</div><div>طلبات الأجهزة</div><div>أحدث نشاط إعلاني</div><div>سجل الروابط</div></div><div class="menu-row" onclick="toggleSub('help')">❓ المساعدة والدعم <span>›</span></div><div id="sub-help" style="display:none;padding:10px"><div>مركز المساعدة</div><div>الإبلاغ عن مشكلة</div></div></div>
<div class="card" style="margin:10px 0"><h3>✨ الترقيات - Noor Pro</h3><div style="background:linear-gradient(135deg,#a855f7,#ec4899);color:#fff;padding:14px;border-radius:14px"><b>Noor Free / Free Boost</b><p>روّج لمنشورك مجاناً</p><button onclick="boostFree()" style="background:#fff;color:#a855f7">🚀 تفعيل Free Boost</button></div></div>
<div class="card" style="margin:10px 0"><h3>🧩 أيضاً من Noor</h3><div class="menu-row" onclick="showTab('threads');closeDrawer()">🧵 Threads</div><div class="menu-row" onclick="showTab('gram');closeDrawer()">📸 نور قرام</div><div class="menu-row" onclick="showTab('talk');closeDrawer()">💬 نور شات</div><div class="menu-row" onclick="showTab('talk');closeDrawer()">💚 نور واتساب</div></div>
<button class="gray" onclick="logout()">تسجيل الخروج</button></div></div>

<div id="auth" class="card" style="max-width:420px;margin:30px auto"><h2 id="aTitle">تسجيل الدخول - حقيقي 100%</h2><input id="username" placeholder="اسم المستخدم الحقيقي" style="display:none"><input id="email" placeholder="البريد"><input id="password" type="password" placeholder="كلمة السر"><button onclick="doAuth()" id="aBtn">دخول</button><button class="green" onclick="toggleAuth()">إنشاء حساب جديد حقيقي</button><p style="font-size:13px;color:#666">ما في أي حساب وهمي. السوق والمنشورات كلها من ناس سجلوا براهم.</p><p id="aMsg" style="color:red"></p></div>

<div id="app" style="display:none">
<div id="tab-feed" class="tab active"><div class="card"><div class="flex"><div class="avatar" id="av1">ن</div><input placeholder="بم تفكر؟ اكتب بوست..." onclick="openPublish('post')"></div><div class="grid2" style="margin-top:8px"><button class="green" onclick="openPublish('image')">📷 صورة</button><button class="orange" onclick="openPublish('video')">🎬 فيديو</button><button class="pink" onclick="openPublish('reel')">🎞️ ريلز</button><button onclick="openPublish('post')">📝 بوست</button></div></div><div class="card"><h3>📸 القصص - حقيقية</h3><div class="storyRow" id="stories"></div><button class="gray" onclick="addStory()">+ أضف قصتك</button></div><div class="card"><h3>👥 أشخاص حقيقيين قد تعرفهم</h3><div id="suggest"></div></div><div id="posts"></div><div id="feed"></div></div>
<div id="tab-gram" class="tab"><div class="card"><h2>📸 نور قرام</h2><div id="gramList"></div></div></div>
<div id="tab-reels" class="tab"><div class="card"><h2>🎬 ريلز - NoorRank Score</h2><div id="reelsList"></div><button onclick="openPublish('reel')">+ نشر ريلز</button></div></div>
<div id="tab-talk" class="tab"><div class="card"><h2>💬 نور شات - Talk</h2><div id="usersList"></div></div><div class="card"><h3 id="chatTitle">اختر شخص حقيقي</h3><div id="chatBox"></div><input id="chatInput" placeholder="اكتب رسالة..."><button onclick="sendMsg()">إرسال</button></div></div>
<div id="tab-threads" class="tab"><div class="card"><h2>🧵 ثريدز</h2><input id="threadInput" placeholder="اكتب ثريد..."><button onclick="postThread()">نشر ثريد</button><div id="threadsList"></div></div></div>
<div id="tab-profile" class="tab"><div class="card" style="text-align:center"><div class="avatar" style="width:80px;height:80px;font-size:28px;margin:auto" id="pAvatar">ن</div><h2 id="pName"></h2><p id="pBio"></p><p><b id="pStats">0 متابع • 0 منشور</b></p><input id="bioIn" placeholder="البايو..."><input id="avIn" placeholder="رابط صورتك..."><button onclick="saveProfile()">حفظ البروفايل</button></div><div id="myPosts"></div></div>
<div id="tab-saved" class="tab"><div class="card"><h2>🔖 المحفوظة</h2><div id="savedList"></div></div></div>
<div id="tab-friends" class="tab"><div class="card"><h2>👥 الأصدقاء الحقيقيين</h2><div id="friendsList"></div></div></div>
<div id="tab-groups" class="tab"><div class="card"><h2>👥 المجموعات - حقيقية</h2><div id="groupsList"></div><input id="groupInput" placeholder="اسم مجموعة جديدة..."><button onclick="createGroup()">إنشاء مجموعة</button></div></div>
<div id="tab-memories" class="tab"><div class="card"><h2>🕐 الذكريات</h2><div id="memoriesList"></div></div></div>
<div id="tab-events" class="tab"><div class="card"><h2>📅 المناسبات</h2><p>🎉 عيد الاستقلال - 1 يناير</p></div></div>
<div id="tab-games" class="tab"><div class="card"><h2>🎮 الألعاب</h2><p>نقاطك: <span id="gameScore">0</span></p><button onclick="playGame()">🎲 العب XO</button></div></div>
<div id="tab-market" class="tab"><div class="card"><h2>🛒 السوق - Market - حقيقي فقط</h2><input id="marketSearch" placeholder="🔍 بحث في السوق..." oninput="filterMarket()"><div id="marketGrid" style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px"></div><p style="font-size:13px;color:#666">ما في منتجات وهمية من Unsplash. أي منتج هنا نشرو زول حقيقي.</p><input id="marketName" placeholder="اسم المنتج الحقيقي..."><input id="marketPrice" placeholder="السعر..."><input id="marketImg" placeholder="رابط صورة المنتج - اختياري"><button onclick="addProduct()">+ إضافة منتج حقيقي</button></div></div>
<div id="tab-settings" class="tab"><div class="card"><h2>⚙️ الإعدادات</h2><div class="menu-row"><span>🌙 Dark Mode</span><button style="width:auto" onclick="toggleDark()">تبديل</button></div><div class="menu-row"><span>🔄 Delta Sync</span><input type="checkbox" id="deltaSync" checked style="width:auto" onchange="saveSettings()"></div><div class="menu-row"><span>📡 MQTT</span><input type="checkbox" id="mqttSync" checked style="width:auto" onchange="saveSettings()"></div><div><label>⚡ LoadFeed: <span id="loadFeedVal">50</span>%</label><input type="range" min="0" max="100" value="50" oninput="document.getElementById('loadFeedVal').innerText=this.value"></div><button class="gray" onclick="saveSettings()">حفظ الإعدادات</button></div></div>
<div id="tab-ads" class="tab"><div class="card"><h2>📣 الترقيات - Ads / Free Boost</h2><button onclick="boostFree()">🚀 تفعيل Free Boost مجاناً</button></div></div>
<div id="tab-notifications" class="tab"><div class="card"><h2>🔔 الإشعارات</h2><div id="notifList"></div></div></div>
</div>

<div class="tabs"><div onclick="showTab('feed')" id="b-feed" class="active">📘<br>نور بوك</div><div onclick="showTab('gram')" id="b-gram">📸<br>نور قرام</div><div onclick="showTab('reels')" id="b-reels">🎬<br>ريلز</div><div onclick="showTab('talk')" id="b-talk">💬<br>نور شات</div><div onclick="showTab('threads')" id="b-threads">🧵<br>ثريدز</div><div onclick="openDrawer()">☰<br>القائمة</div></div>
<button onclick="openPublish('post')" style="position:fixed;bottom:75px;left:50%;transform:translateX(-50%);width:55px;height:55px;border-radius:50%;font-size:26px;z-index:25">+</button>

<div class="modal" id="publishModal"><div class="box"><h3 id="pubTitle">📝 نشر بوست</h3><textarea id="pContent" rows="4" placeholder="بم تفكر؟ اكتب بوست حقيقي..."></textarea>
<div style="background:#f0f2f5;padding:12px;border-radius:12px"><b>1️⃣ عن طريق الرابط:</b><input id="pLink" placeholder="الصق رابط صورة أو فيديو..."><button class="gray" onclick="previewLink()">👁️ معاينة الرابط</button></div>
<div style="background:#e8f5e9;padding:12px;border-radius:12px;margin-top:8px"><b>2️⃣ عن طريق الملفات:</b><input type="file" id="fileIn" accept="image/*,video/*" onchange="previewFile()"><small>اختار من تلفونك صورة أو فيديو</small></div>
<div style="background:#fff3e0;padding:12px;border-radius:12px;margin-top:8px"><b>نوع النشر:</b><div class="grid2"><div class="chip active" id="chip-post" onclick="setPub('post')">📝 بوست</div><div class="chip" id="chip-image" onclick="setPub('image')">📷 صورة</div><div class="chip" id="chip-video" onclick="setPub('video')">🎬 فيديو</div><div class="chip" id="chip-reel" onclick="setPub('reel')">🎞️ ريلز</div></div></div>
<img id="previewImg" style="width:100%;border-radius:12px;display:none"><video id="previewVideo" controls style="width:100%;border-radius:12px;display:none"></video>
<button onclick="createPost()">🚀 نشر الآن - حقيقي</button><button class="pink" onclick="doPublishReel()">🎬 نشر كـ ريلز</button><button class="gray" onclick="closePublish()">إلغاء</button></div></div>

<script>
// ===== نفس أسماء الدوال في كودك القديم - ما غيرتها =====
let MY_ID = parseInt(localStorage.getItem('noor_my_id')||'0');
let user=JSON.parse(localStorage.getItem('noor_user')||'null');
let isReg=false;let chatWith=null;let pubType='post';let pubMedia='';let pubMediaType='none';let gameScore=0;let lastSync=0;
// API - زي كودك القديم: لو localhost اشتغل محلي، لو Render اشتغل على رابط Render
const API = location.hostname==='localhost' ? 'http://localhost:8000' : '';
function toggleDark(){document.body.classList.toggle('dark');saveSettings()}
function openDrawer(){document.getElementById('drawer').classList.add('open');document.getElementById('drawerOverlay').classList.add('show')}
function closeDrawer(){document.getElementById('drawer').classList.remove('open');document.getElementById('drawerOverlay').classList.remove('show')}
function toggleSub(id){let e=document.getElementById('sub-'+id);e.style.display=e.style.display=='none'?'block':'none'}
function saveSettings(){if(!user)return;let s={delta:document.getElementById('deltaSync')?.checked?1:0,mqtt:document.getElementById('mqttSync')?.checked?1:0,dark:document.body.classList.contains('dark')?1:0};fetch('/api/settings/'+user.id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(s)})}
function showTab(tab){let map={feed:'feed',home:'feed',gram:'gram',reels:'reels',chat:'talk',talk:'talk',threads:'threads',profile:'profile',saved:'saved',friends:'friends',groups:'groups',memories:'memories',events:'events',games:'games',market:'market',settings:'settings',ads:'ads',notifications:'notifications',notif:'notifications'};let id=map[tab]||tab;document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));let el=document.getElementById('tab-'+id);if(el)el.classList.add('active');document.querySelectorAll('.tabs div').forEach(e=>e.classList.remove('active'));let b=document.getElementById('b-'+id);if(b)b.classList.add('active');closeDrawer();window.scrollTo(0,0);if(id=='saved')loadSaved();if(id=='friends')loadUsers();if(id=='market')loadMarket();if(id=='memories')loadMemories();if(id=='groups')loadGroups()}
function toggleAuth(){isReg=!isReg;document.getElementById('aTitle').innerText=isReg?'إنشاء حساب حقيقي':'تسجيل الدخول';document.getElementById('aBtn').innerText=isReg?'تسجيل':'دخول';document.getElementById('username').style.display=isReg?'block':'none'}
if(user){MY_ID=user.id;showApp()}
function showApp(){document.getElementById('auth').style.display='none';document.getElementById('app').style.display='block';document.getElementById('dName').innerText=user.username;document.getElementById('dEmail').innerText=user.email;document.getElementById('pName').innerText=user.username;document.getElementById('av1').innerText=user.username[0];document.getElementById('dAvatar').innerText=user.username[0];document.getElementById('pAvatar').innerText=user.username[0];loadAll()}
async function doAuth(){let u=document.getElementById('username').value,e=document.getElementById('email').value,p=document.getElementById('password').value;let url=isReg?'/api/register':'/api/login';let body=isReg?{username:u,email:e,password:p}:{email:e,password:p};let r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let d=await r.json();if(d.user){localStorage.setItem('noor_user',JSON.stringify(d.user));localStorage.setItem('noor_my_id',d.user.id);user=d.user;MY_ID=d.user.id;showApp()}else document.getElementById('aMsg').innerText=d.error||'خطأ'}
function logout(){localStorage.removeItem('noor_user');localStorage.removeItem('noor_my_id');location.reload()}
function openPublish(type){pubType=type;setPub(type);document.getElementById('publishModal').style.display='flex';document.getElementById('pubTitle').innerText=type=='reel'?'🎞️ نشر ريلز':type=='video'?'🎬 نشر فيديو':type=='image'?'📷 نشر صورة':'📝 نشر بوست'}
function closePublish(){document.getElementById('publishModal').style.display='none';pubMedia='';pubMediaType='none'}
function setPub(t){pubType=t;['post','image','video','reel'].forEach(x=>{let e=document.getElementById('chip-'+x);if(e)e.classList.toggle('active',x==t)})}
function previewLink(){let link=document.getElementById('pLink').value.trim();if(!link)return alert('الصق رابط أولا');pubMedia=link;let isVideo=link.includes('.mp4')||link.includes('video');pubMediaType=isVideo?'video':'image';if(isVideo){document.getElementById('previewVideo').src=link;document.getElementById('previewVideo').style.display='block';document.getElementById('previewImg').style.display='none'}else{document.getElementById('previewImg').src=link;document.getElementById('previewImg').style.display='block';document.getElementById('previewVideo').style.display='none'}}
function previewFile(){let f=document.getElementById('fileIn').files[0];if(!f)return;let r=new FileReader();r.onload=e=>{pubMedia=e.target.result;pubMediaType=f.type.startsWith('video')?'video':'image';if(pubMediaType=='video'){document.getElementById('previewVideo').src=pubMedia;document.getElementById('previewVideo').style.display='block';document.getElementById('previewImg').style.display='none'}else{document.getElementById('previewImg').src=pubMedia;document.getElementById('previewImg').style.display='block';document.getElementById('previewVideo').style.display='none'}};r.readAsDataURL(f)}
// ===== createPost - بنفس اسم كودك القديم =====
async function createPost(){let content=document.getElementById('pContent').value;if(!content&&!pubMedia)return alert('اكتب شي أو أضف صورة/فيديو');await fetch(API+'/api/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:MY_ID,content:content,media:pubMedia,media_type:pubMediaType,post_type:pubType})});closePublish();document.getElementById('pContent').value='';document.getElementById('pLink').value='';loadPosts()}
async function doPublishReel(){pubType='reel';createPost()}
async function boostFree(){alert('تم تفعيل Free Boost مجاناً!');await fetch(API+'/api/boost',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:MY_ID})});await fetch(API+'/api/ads/free',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:MY_ID})}).catch(()=>{});loadPosts()}
async function loadAll(){loadPosts();loadStories();loadUsers();loadNotif();loadMarket();loadSuggest()}
async function loadPosts(){let r=await fetch(API+'/api/posts?user_id='+MY_ID);let d=await r.json();let h='';for(let p of d.posts){let media='';if(p.media){if(p.media_type=='video')media='<video class="postVideo" controls src="'+p.media+'"></video>';else media='<img class="postImg" src="'+p.media+'">'}h+='<div class="card"><div class="flex"><div class="avatar">'+p.username[0]+'</div><b>'+p.username+'</b><small>'+p.created_at+' • '+p.views+' مشاهدة • NoorRank: '+p.score+'</small>'+(p.boosted?' <span style="background:#a855f7;color:#fff;padding:2px 6px;border-radius:8px">Boost</span>':'')+'</div><p>'+p.content+'</p>'+media+'<div class="act"><button onclick="likePost('+p.id+')">❤️ '+p.likes+'</button><button onclick="toggleC('+p.id+')">💬 '+p.comments+'</button><button onclick="savePost('+p.id+')">🔖 حفظ</button><button onclick="sharePost()">↗️ مشاركة</button></div><div id="c-'+p.id+'" style="display:none"><div id="cl-'+p.id+'"></div><input id="ci-'+p.id+'" placeholder="اكتب تعليق..."><button onclick="addComment('+p.id+')">تعليق</button></div>'+(p.user_id==MY_ID?'<button class="red" onclick="delPost('+p.id+')">حذف</button>':'')+'</div>'}document.getElementById('posts').innerHTML=h||'<div class="card"><h3>لسه ما في أي منشور حقيقي</h3><p>انت أول زول! دوس + وانشر أول بوست حقيقي.</p><button onclick="openPublish(\\'post\\')">+ انشر أول بوست</button></div>';document.getElementById('feed').innerHTML=document.getElementById('posts').innerHTML;document.getElementById('gramList').innerHTML=d.posts.filter(p=>p.media&&p.media_type=='image').map(p=>'<img src="'+p.media+'" style="width:100%;border-radius:12px;margin:5px 0"><p>'+p.username+': '+p.content+'</p>').join('')||'لسه ما في صور حقيقية';document.getElementById('reelsList').innerHTML=d.posts.filter(p=>p.post_type=='reel').map(p=>'<div class="card"><b>'+p.username+'</b><p>'+p.content+'</p>'+(p.media?'<video class="postVideo" controls src="'+p.media+'"></video>':'')+'<p>NoorRank: '+p.score+'</p></div>').join('')||'لسه ما في ريلز حقيقية';document.getElementById('threadsList').innerHTML=d.posts.filter(p=>p.post_type=='thread').map(p=>'<div class="card"><b>'+p.username+'</b><p>'+p.content+'</p></div>').join('');document.getElementById('pStats').innerText='0 متابع • '+d.posts.filter(p=>p.user_id==MY_ID).length+' منشور';document.getElementById('myPosts').innerHTML=d.posts.filter(p=>p.user_id==MY_ID).map(p=>'<div class="card">'+p.content+'</div>').join('')}
async function likePost(id){await fetch(API+'/api/like',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:MY_ID,post_id:id})});loadPosts()}
async function savePost(id){await fetch(API+'/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:MY_ID,post_id:id})});alert('تم الحفظ')}
async function loadSaved(){let r=await fetch(API+'/api/saved/'+MY_ID);let d=await r.json();document.getElementById('savedList').innerHTML=d.posts.map(p=>'<div class="card">'+p.content+'</div>').join('')||'لا توجد محفوظات'}
async function delPost(id){await fetch(API+'/api/posts/'+id,{method:'DELETE'});loadPosts()}
async function toggleC(id){let e=document.getElementById('c-'+id);e.style.display=e.style.display=='none'?'block':'none';let r=await fetch(API+'/api/comments/'+id);let d=await r.json();document.getElementById('cl-'+id).innerHTML=d.comments.map(c=>'<div><b>'+c.username+': </b>'+c.content+'</div>').join('')}
async function addComment(id){let c=document.getElementById('ci-'+id).value;if(!c)return;await fetch(API+'/api/comments/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:MY_ID,content:c})});loadPosts()}
function sharePost(){alert('تم نسخ رابط المنشور!')}
async function loadStories(){let r=await fetch(API+'/api/stories');let d=await r.json();document.getElementById('stories').innerHTML=d.stories.map(s=>'<div class="story">'+(s.media?'<img src="'+s.media+'">':'')+'<b>'+s.username+'<br>'+s.text+'</b></div>').join('')||'<div class="story" onclick="addStory()"><b>+ أضف قصتك</b></div>'}
async function addStory(){let t=prompt('اكتب نص القصة');let img=prompt('رابط صورة القصة');if(!t&&!img)return;await fetch(API+'/api/stories',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:MY_ID,text:t||'',media:img||''})});loadStories()}
async function loadUsers(){let r=await fetch(API+'/api/users');let d=await r.json();let others=d.users.filter(x=>x.id!=MY_ID);document.getElementById('usersList').innerHTML=others.map(x=>'<div class="flex" style="justify-content:space-between;margin:8px 0"><span>👤 '+x.username+'</span><button style="width:auto" onclick="openChat('+x.id+',\\''+x.username+'\\')">مراسلة</button></div>').join('')||'لسه ما في مستخدم حقيقي تاني';document.getElementById('friendsList').innerHTML=others.map(x=>'<div>👤 '+x.username+'</div>').join('')||'لسه ما عندك أصدقاء'}
async function loadSuggest(){let r=await fetch(API+'/api/users');let d=await r.json();let others=d.users.filter(x=>x.id!=MY_ID);document.getElementById('suggest').innerHTML=others.map(x=>'<div class="flex" style="justify-content:space-between;margin:8px 0"><div class="flex"><div class="avatar">'+x.username[0]+'</div><div><b>'+x.username+'</b><br><small>حساب حقيقي • '+x.followers+' متابع</small></div></div><div style="display:flex;gap:5px"><button style="width:auto" onclick="followUser('+x.id+')">+ متابعة</button><button style="width:auto" class="gray" onclick="this.parentElement.parentElement.remove()">إزالة</button></div></div>').join('')||'ما في اقتراحات لسه - انت أول حساب حقيقي'}
async function searchUsers(){let q=document.getElementById('searchInput').value;if(q.length<1){loadSuggest();return}let r=await fetch(API+'/api/users?q='+q);let d=await r.json();document.getElementById('suggest').innerHTML=d.users.filter(x=>x.id!=MY_ID).map(x=>'<div>'+x.username+'</div>').join('')}
async function followUser(id){await fetch(API+'/api/follow',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({follower_id:MY_ID,following_id:id})});loadSuggest();loadNotif()}
async function openChat(id,name){chatWith=id;document.getElementById('chatTitle').innerText='محادثة مع '+name;showTab('talk');let r=await fetch(API+'/api/messages?user_id='+MY_ID+'&other_id='+id);let d=await r.json();document.getElementById('chatBox').innerHTML=d.messages.map(m=>'<div class="msg '+(m.sender_id==MY_ID?'me':'other')+'">'+m.content+'</div>').join('')}
async function sendMsg(){let c=document.getElementById('chatInput').value;if(!c||!chatWith)return alert('اختر شخص أولا');await fetch(API+'/api/messages',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sender_id:MY_ID,receiver_id:chatWith,content:c})});document.getElementById('chatInput').value='';openChat(chatWith,document.getElementById('chatTitle').innerText.replace('محادثة مع ',''))}
async function loadNotif(){let r=await fetch(API+'/api/notifications/'+MY_ID);let d=await r.json();document.getElementById('notifList').innerHTML=d.notifications.map(n=>'<div style="padding:10px;border-bottom:1px solid #eee">'+n.content+'</div>').join('')}
async function saveProfile(){await fetch(API+'/api/profile/'+MY_ID,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({bio:document.getElementById('bioIn').value,avatar:document.getElementById('avIn').value})});alert('تم الحفظ')}
async function postThread(){let c=document.getElementById('threadInput').value;if(!c)return;await fetch(API+'/api/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:MY_ID,content:c,post_type:'thread'})});document.getElementById('threadInput').value='';loadPosts()}
// ===== السوق - حقيقي فقط، شلت Unsplash =====
let products=[]; // ما في منتجات وهمية - بتجي من السيرفر بس
async function loadMarket(){let r=await fetch(API+'/api/products');let d=await r.json();products=d.products;renderMarket(products)}
function renderMarket(list){document.getElementById('marketGrid').innerHTML=list.map(p=>'<div class="card" style="margin:0"><b>'+p.name+'</b><p>'+p.price+' • بائع: '+p.seller+'</p>'+(p.img?'<img src="'+p.img+'" style="width:100%;border-radius:10px">':'')+'<button onclick="alert(\\'تواصل مع البائع الحقيقي\\')">تواصل</button></div>').join('')||'لسه ما في منتجات حقيقية - انت أول واحد اعرض منتج'}
function filterMarket(){let q=document.getElementById('marketSearch').value.toLowerCase();renderMarket(products.filter(p=>p.name.toLowerCase().includes(q)))}
async function addProduct(){let n=document.getElementById('marketName').value,pr=document.getElementById('marketPrice').value,img=document.getElementById('marketImg').value;if(!n)return alert('اكتب اسم المنتج');await fetch(API+'/api/products',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:MY_ID,name:n,price:pr,img:img,seller:user.username})});loadMarket()}
async function loadMemories(){let r=await fetch(API+'/api/posts?user_id='+MY_ID);let d=await r.json();document.getElementById('memoriesList').innerHTML=d.posts.filter(p=>p.user_id==MY_ID).slice(0,3).map(p=>'<div class="card">🕐 ذكرى: '+p.content+'</div>').join('')||'لسه ما عندك ذكريات'}
async function loadGroups(){document.getElementById('groupsList').innerHTML='<div class="card">مجموعات حقيقية - أنشئ أول مجموعة</div>'}
async function createGroup(){let n=document.getElementById('groupInput').value;if(!n)return;alert('تم إنشاء مجموعة '+n+' - حقيقية')}
function playGame(){gameScore+=10;document.getElementById('gameScore').innerText=gameScore;alert('كسبت 10 نقاط!')}
</script></body></html>"""

@app.route("/")
def home(): return HTML
@app.route("/api/register", methods=["POST"])
def reg():
    d=request.get_json() or {}
    if not d.get("username") or not d.get("email"): return jsonify({"error":"املا البيانات"}),400
    c=db()
    try:
        c.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)",(d.get("username"),d.get("email"),hp(d.get("password")))); c.commit()
        u=c.execute("SELECT * FROM users WHERE email=?",(d.get("email"),)).fetchone(); return jsonify({"user":{"id":u["id"],"username":u["username"],"email":u["email"]}})
    except: return jsonify({"error":"الايميل موجود"}),400
    finally: c.close()
@app.route("/api/login", methods=["POST"])
def log():
    d=request.get_json() or {}; c=db(); u=c.execute("SELECT * FROM users WHERE email=? AND password=?",(d.get("email"),hp(d.get("password")))).fetchone(); c.close()
    if u: return jsonify({"user":{"id":u["id"],"username":u["username"],"email":u["email"]}})
    return jsonify({"error":"بيانات خاطئة"}),401
@app.route("/api/users")
def users():
    q=request.args.get("q",""); c=db(); rows=c.execute("SELECT * FROM users").fetchall(); out=[]
    for u in rows:
        if q and q.lower() not in u["username"].lower(): continue
        f=c.execute("SELECT COUNT(*) c FROM follows WHERE following_id=?",(u["id"],)).fetchone()["c"]; out.append({"id":u["id"],"username":u["username"],"email":u["email"],"followers":f})
    c.close(); return jsonify({"users":out})
@app.route("/api/profile/<int:uid>", methods=["PUT"])
def prof(uid):
    d=request.get_json() or {}; c=db(); c.execute("UPDATE users SET bio=?, avatar=? WHERE id=?",(d.get("bio",""),d.get("avatar",""),uid)); c.commit(); c.close(); return jsonify({"message":"تم"})
@app.route("/api/settings/<int:uid>", methods=["POST"])
def settings(uid):
    d=request.get_json() or {}; c=db(); c.execute("INSERT OR REPLACE INTO settings (user_id,delta_sync,mqtt,dark) VALUES (?,?,?,?)",(uid,d.get("delta",1),d.get("mqtt",1),d.get("dark",0))); c.commit(); c.close(); return jsonify({"message":"تم"})
@app.route("/api/follow", methods=["POST"])
def fol():
    d=request.get_json() or {}; c=db(); ex=c.execute("SELECT * FROM follows WHERE follower_id=? AND following_id=?",(d.get("follower_id"),d.get("following_id"))).fetchone()
    if ex: c.execute("DELETE FROM follows WHERE id=?",(ex["id"],))
    else: c.execute("INSERT INTO follows (follower_id,following_id) VALUES (?,?)",(d.get("follower_id"),d.get("following_id")))
    c.commit(); c.close(); return jsonify({"message":"تم"})
@app.route("/api/posts", methods=["GET","POST"])
def posts():
    c=db()
    if request.method=="POST":
        d=request.get_json() or {}; c.execute("INSERT INTO posts (user_id,content,media,media_type,post_type,created_at) VALUES (?,?,?,?,?,?)",(d.get("user_id"),d.get("content",""),d.get("media",""),d.get("media_type","none"),d.get("post_type","post"),now())); c.commit(); c.close(); return jsonify({"message":"تم"})
    my_id=request.args.get("user_id",type=int) or 0
    rows=c.execute("SELECT p.*, u.username, (SELECT COUNT(*) FROM likes l WHERE l.post_id=p.id) as lc, (SELECT COUNT(*) FROM comments cm WHERE cm.post_id=p.id) as cc, (SELECT COUNT(*) FROM follows f WHERE f.follower_id=? AND f.following_id=p.user_id) as is_f FROM posts p LEFT JOIN users u ON u.id=p.user_id",(my_id,)).fetchall()
    c.execute("UPDATE posts SET views=views+1"); c.commit()
    # NoorRank Score - خوارزمية كودك القديم
    data=[{"id":p["id"],"content":p["content"],"media":p["media"],"media_type":p["media_type"],"post_type":p["post_type"],"user_id":p["user_id"],"username":p["username"] or "","likes":p["lc"],"comments":p["cc"],"views":p["views"],"boosted":p["boosted"],"score":p["lc"]*10+p["cc"]*15+p["views"]+(50 if p["is_f"] else 0)+(100 if p["boosted"] else 0)} for p in rows]
    data=sorted(data,key=lambda x:x["score"],reverse=True)
    c.close(); return jsonify({"posts":data})
@app.route("/api/feed")
def feed(): return posts()
@app.route("/api/posts/<int:pid>", methods=["DELETE"])
def delp(pid):
    c=db(); c.execute("DELETE FROM posts WHERE id=?",(pid,)); c.commit(); c.close(); return jsonify({"message":"تم"})
@app.route("/api/like", methods=["POST"])
def like():
    d=request.get_json() or {}; c=db(); ex=c.execute("SELECT * FROM likes WHERE user_id=? AND post_id=?",(d.get("user_id"),d.get("post_id"))).fetchone()
    if ex: c.execute("DELETE FROM likes WHERE id=?",(ex["id"],))
    else: c.execute("INSERT INTO likes (user_id,post_id) VALUES (?,?)",(d.get("user_id"),d.get("post_id")))
    c.commit(); c.close(); return jsonify({"message":"تم"})
@app.route("/api/boost", methods=["POST"])
def boost():
    d=request.get_json() or {}; c=db(); c.execute("UPDATE posts SET boosted=1 WHERE user_id=? ORDER BY id DESC LIMIT 1",(d.get("user_id"),)); c.commit(); c.close(); return jsonify({"message":"تم تفعيل Free Boost"})
@app.route("/api/ads/free", methods=["POST"])
def ads_free():
    d=request.get_json() or {}; c=db(); c.execute("UPDATE posts SET boosted=1 WHERE user_id=? ORDER BY id DESC LIMIT 1",(d.get("user_id"),)); c.commit(); c.close(); return jsonify({"message":"تم تفعيل Free Boost"})
@app.route("/api/save", methods=["POST"])
def save():
    d=request.get_json() or {}; c=db()
    try: c.execute("INSERT INTO saved (user_id,post_id) VALUES (?,?)",(d.get("user_id"),d.get("post_id"))); c.commit()
    except: pass
    c.close(); return jsonify({"message":"تم"})
@app.route("/api/saved/<int:uid>")
def saved(uid):
    c=db(); rows=c.execute("SELECT p.* FROM saved s JOIN posts p ON p.id=s.post_id WHERE s.user_id=?",(uid,)).fetchall(); out=[{"content":r["content"]} for r in rows]; c.close(); return jsonify({"posts":out})
@app.route("/api/comments/<int:pid>", methods=["GET","POST"])
def comm(pid):
    c=db()
    if request.method=="POST":
        d=request.get_json() or {}; c.execute("INSERT INTO comments (post_id,user_id,content,created_at) VALUES (?,?,?,?)",(pid,d.get("user_id"),d.get("content"),now())); c.commit(); c.close(); return jsonify({"message":"تم"})
    rows=c.execute("SELECT c.*, u.username FROM comments c LEFT JOIN users u ON u.id=c.user_id WHERE c.post_id=? ORDER BY c.id ASC",(pid,)).fetchall(); out=[{"content":r["content"],"username":r["username"] or ""} for r in rows]; c.close(); return jsonify({"comments":out})
@app.route("/api/stories", methods=["GET","POST"])
def stories():
    c=db()
    if request.method=="POST":
        d=request.get_json() or {}; c.execute("INSERT INTO stories (user_id,media,text,created_at) VALUES (?,?,?,?)",(d.get("user_id"),d.get("media",""),d.get("text",""),now())); c.commit(); c.close(); return jsonify({"message":"تم"})
    rows=c.execute("SELECT s.*, u.username FROM stories s LEFT JOIN users u ON u.id=s.user_id ORDER BY s.id DESC").fetchall(); out=[{"username":r["username"] or "","media":r["media"],"text":r["text"]} for r in rows]; c.close(); return jsonify({"stories":out})
@app.route("/api/messages", methods=["GET","POST"])
def msgs():
    c=db()
    if request.method=="POST":
        d=request.get_json() or {}; c.execute("INSERT INTO messages (sender_id,receiver_id,content,created_at) VALUES (?,?,?,?)",(d.get("sender_id"),d.get("receiver_id"),d.get("content"),now())); c.commit(); c.close(); return jsonify({"message":"تم"})
    uid=request.args.get("user_id",type=int); oid=request.args.get("other_id",type=int); rows=c.execute("SELECT * FROM messages WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?) ORDER BY id ASC",(uid,oid,oid,uid)).fetchall(); out=[{"sender_id":r["sender_id"],"content":r["content"]} for r in rows]; c.close(); return jsonify({"messages":out})
@app.route("/api/notifications/<int:uid>")
def notif(uid):
    c=db(); rows=c.execute("SELECT * FROM comments c JOIN posts p ON p.id=c.post_id WHERE p.user_id=? ORDER BY c.id DESC LIMIT 20",(uid,)).fetchall(); out=[{"content":f"علق {r['content'][:40]} على منشورك"} for r in rows]; c.close()
    if not out: out=[{"content":"مرحباً بك في Noor الحقيقي - انت أول حساب"}]
    return jsonify({"notifications":out})
@app.route("/api/products", methods=["GET","POST"])
def products():
    c=db()
    if request.method=="POST":
        d=request.get_json() or {}; c.execute("INSERT INTO products (user_id,name,price,img,seller) VALUES (?,?,?,?,?)",(d.get("user_id"),d.get("name"),d.get("price",""),d.get("img",""),d.get("seller",""))); c.commit(); c.close(); return jsonify({"message":"تم"})
    rows=c.execute("SELECT * FROM products ORDER BY id DESC").fetchall(); out=[{"name":r["name"],"price":r["price"],"img":r["img"],"seller":r["seller"]} for r in rows]; c.close(); return jsonify({"products":out})
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
