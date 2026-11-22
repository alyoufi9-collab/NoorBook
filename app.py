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
    d.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT, image TEXT DEFAULT '', type TEXT DEFAULT 'post', created_at TEXT)")
    d.execute("CREATE TABLE IF NOT EXISTS likes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, post_id INTEGER, UNIQUE(user_id, post_id))")
    d.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, user_id INTEGER, content TEXT, created_at TEXT)")
    d.execute("CREATE TABLE IF NOT EXISTS stories (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, image TEXT, text TEXT, created_at TEXT)")
    d.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER, receiver_id INTEGER, content TEXT, created_at TEXT)")
    d.execute("CREATE TABLE IF NOT EXISTS follows (id INTEGER PRIMARY KEY AUTOINCREMENT, follower_id INTEGER, following_id INTEGER, UNIQUE(follower_id, following_id))")
    d.execute("CREATE TABLE IF NOT EXISTS saved (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, post_id INTEGER, UNIQUE(user_id, post_id))")
    d.execute("CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, desc TEXT, members INTEGER DEFAULT 0)")
    d.execute("CREATE TABLE IF NOT EXISTS pages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, cat TEXT)")
    d.commit(); d.close()
    d=db()
    if d.execute("SELECT COUNT(*) c FROM groups").fetchone()["c"]==0:
        for n,desc in [("سودانيين في عطبرة","أهل عطبرة"),("نور قرام السودان","صور السودان"),("وظائف السودان","شغل"),("بيع وشراء عطبرة","سوق")]:
            d.execute("INSERT INTO groups (name,desc,members) VALUES (?,?,?)",(n,desc,120))
    d.commit(); d.close()
init()
def hp(p): return hashlib.sha256(p.encode()).hexdigest()
def now(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

HTML=open(__file__,encoding="utf-8").read().split('HTML2="""')[1].split('"""')[0] if 'HTML2="""' in open(__file__,encoding="utf-8").read() else ""
# --- HTML سيتم وضعه تحت ---
HTML2="""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>نور Noor</title><style>
*{box-sizing:border-box}body{font-family:Arial;background:#f0f2f5;margin:0;padding-bottom:70px}
.top{background:#fff;padding:10px;display:flex;gap:8px;align-items:center;position:sticky;top:0;z-index:20;box-shadow:0 1px 5px #ddd}
.logo{font-weight:900;color:#1877f2;font-size:24px}.logo small{color:#000;font-size:18px}
.card{background:#fff;border-radius:14px;padding:14px;margin:10px;box-shadow:0 1px 3px #ddd}
input,textarea,select{width:100%;padding:11px;border:1px solid #ddd;border-radius:10px;margin:5px 0}
button{background:#1877f2;color:#fff;border:none;padding:11px;border-radius:10px;font-weight:bold;cursor:pointer;width:100%;margin-top:6px}
button.green{background:#42b72a}button.gray{background:#e4e6eb;color:#000}button.red{background:#ff3b30}button.pink{background:#e91e63}
.avatar{width:44px;height:44px;border-radius:50%;background:#1877f2;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:bold;flex-shrink:0;overflow:hidden}.avatar img{width:100%;height:100%;object-fit:cover}
.flex{display:flex;gap:10px;align-items:center}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}.menuBtn{background:#fff;border-radius:14px;padding:16px;text-align:center;box-shadow:0 1px 3px #ddd;cursor:pointer;font-weight:bold}
.storyRow{display:flex;gap:10px;overflow:auto}.story{min-width:110px;height:175px;border-radius:14px;background:#ddd;position:relative;overflow:hidden;cursor:pointer}.story img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.story b{position:absolute;bottom:8px;right:8px;color:#fff;text-shadow:0 0 5px #000}
.bottom{position:fixed;bottom:0;left:0;right:0;background:#fff;display:flex;justify-content:space-around;padding:8px 2px;border-top:1px solid #ddd;z-index:30}.bottom div{text-align:center;font-size:12px;cursor:pointer;padding:4px}.bottom .active{color:#1877f2;font-weight:900}
.modal{position:fixed;inset:0;background:rgba(0,0,0,.5);display:none;align-items:flex-end;justify-content:center;z-index:50}.modal .box{background:#fff;width:100%;max-width:480px;border-radius:20px 20px 0 0;padding:16px;max-height:85vh;overflow:auto}
.rowBtn{display:flex;justify-content:space-between;align-items:center;padding:12px;border-bottom:1px solid #eee;cursor:pointer}
.postImg{width:100%;border-radius:12px;margin-top:8px}.act{display:flex;gap:6px}.act button{flex:1;background:#f0f2f5;color:#000}
.chip{padding:10px;border-radius:12px;background:#f0f2f5;text-align:center;cursor:pointer;font-weight:bold}.chip.active{background:#1877f2;color:#fff}
.tab{display:none}.tab.active{display:block}
.msg{padding:9px 12px;border-radius:14px;margin:5px 0;max-width:80%}.me{background:#1877f2;color:#fff;margin-left:auto}.other{background:#e4e6eb}
</style></head><body>
<div class="top"><div style="display:flex;gap:6px"><button style="width:auto" onclick="openCreate()">+</button><button style="width:auto" class="gray" onclick="show('menu')">☰</button><button style="width:auto" class="gray" onclick="show('chat')">💬<span id="cChat">+9</span></button><button style="width:auto" class="gray" onclick="show('notif')">🔔<span>3</span></button></div><div style="flex:1;text-align:left"><div><span class="logo">Noor</span> <b>نور</b></div><small>نور بوك • نور شات • نور قرام</small></div><div class="avatar" id="topAvatar">ن</div></div>

<div id="auth" class="card" style="max-width:420px;margin:30px auto"><h2 id="aTitle">تسجيل الدخول</h2><input id="username" placeholder="اسم المستخدم" style="display:none"><input id="email" placeholder="البريد"><input id="password" type="password" placeholder="كلمة السر"><button onclick="doAuth()" id="aBtn">دخول</button><button class="green" onclick="toggleAuth()">إنشاء حساب جديد</button><p id="aMsg" style="color:red"></p></div>

<div id="app" style="display:none">
<!-- الرئيسية -->
<div id="tab-home" class="tab active">
<div class="card"><div class="flex"><div class="avatar" id="av1">ن</div><input id="postText" placeholder="بم تفكر؟ اكتب بوست..." onclick="openCreatePost()"></div><div class="grid2" style="margin-top:8px"><div class="chip" onclick="openCreatePost()">📷 اختر صورة</div><div class="chip" onclick="openCreatePost()">🎬 اختر فيديو</div><div class="chip" onclick="openCreatePost()">🎞️ اختر ريلز</div><div class="chip" onclick="openCreatePost()">📝 ملاحظة</div></div></div>
<div class="card"><h3>📸 القصص</h3><div class="storyRow" id="stories"></div></div>
<div class="card"><h3>👥 أشخاص قد تعرفهم</h3><div id="suggest"></div><button class="gray" onclick="loadUsers()">عرض الكل ></button></div>
<div id="posts"></div>
</div>

<!-- نور قرام -->
<div id="tab-gram" class="tab"><div class="card"><h2>📸 نور قرام</h2><p>صور و ريلز من الناس</p><div id="gramList"></div></div></div>
<!-- ريلز -->
<div id="tab-reels" class="tab"><div class="card"><h2>🎬 ريلز</h2><div id="reelsList"></div><button onclick="openCreatePost()">+ نشر ريلز</button></div></div>
<!-- شات -->
<div id="tab-chat" class="tab"><div class="card"><h2>💬 نور شات</h2><div id="usersList"></div></div><div class="card"><h3 id="chatTitle">اختر شخص للمحادثة</h3><div id="chatBox"></div><input id="chatInput" placeholder="اكتب رسالة..."><button onclick="sendMsg()">إرسال</button></div></div>
<!-- ثريدز -->
<div id="tab-threads" class="tab"><div class="card"><h2>🧵 ثريدز</h2><input id="threadInput" placeholder="اكتب ثريد..."><button onclick="postThread()">نشر ثريد</button><div id="threadsList"></div></div></div>
<!-- القائمة -->
<div id="tab-menu" class="tab"><div class="card"><div class="flex"><div class="avatar" id="av2">ن</div><div><b id="myName">يوسف إبراهيم</b><br><small onclick="show('profile')" style="color:#1877f2">عرض الملف الشخصي</small></div></div><button onclick="createPage()">+ إنشاء صفحة على نور بوك</button></div>
<div class="card"><div class="grid2"><div class="menuBtn" onclick="show('saved')">🕐<br>الذكريات</div><div class="menuBtn" onclick="show('saved')">🔖<br>العناصر المحفوظة</div><div class="menuBtn" onclick="show('groups')">👥<br>المجموعات</div><div class="menuBtn" onclick="show('friends')">👤<br>الأصدقاء</div><div class="menuBtn" onclick="show('news')">📰<br>الأخبار</div><div class="menuBtn" onclick="show('reels')">🎬<br>ريلز</div><div class="menuBtn" onclick="show('events')">📅<br>المناسبات</div><div class="menuBtn" onclick="show('games')">🎮<br>الألعاب</div></div><button class="gray" onclick="alert('عرض المزيد')">▼ عرض المزيد</button></div>
<div class="card"><h3>⚙️ الإعدادات والخصوصية</h3><div class="rowBtn" onclick="show('profile')">👤 الإعدادات <span>‹</span></div><div class="rowBtn" onclick="alert('مركز الخصوصية')">🔒 مركز الخصوصية <span>‹</span></div><div class="rowBtn" onclick="alert('إدارة الوقت')">🕐 إدارة الوقت <span>‹</span></div><div class="rowBtn" onclick="alert('طلبات الأجهزة')">📱 طلبات الأجهزة <span>‹</span></div><div class="rowBtn" onclick="alert('أحدث نشاط إعلاني')">🖼️ أحدث نشاط إعلاني <span>‹</span></div><div class="rowBtn" onclick="alert('مركز خدمات الهاتف المحمول Zain Sudan')">📡 مركز خدمات الهاتف المحمول • Zain Sudan <span>‹</span></div><div class="rowBtn" onclick="alert('الطلبات وعمليات الدفع')">💳 الطلبات وعمليات الدفع <span>‹</span></div><div class="rowBtn" onclick="alert('سجل الروابط')">🔗 سجل الروابط <span>‹</span></div></div>
<div class="card"><h3>❓ المساعدة والدعم</h3><div class="rowBtn" onclick="alert('مركز المساعدة')">مركز المساعدة</div><div class="rowBtn" onclick="alert('الإبلاغ عن مشكلة')">الإبلاغ عن مشكلة</div></div>
<div class="card"><h3>✨ الترقيات</h3><div style="background:#e9d5ff;padding:12px;border-radius:12px"><b>الحضور العام</b><p>احصل على أدوات تساعدك على النمو...</p><button onclick="alert('تم تفعيل الحضور العام')">تفعيل</button></div></div>
<div class="card"><h3>🧩 أيضاً من Noor</h3><div class="rowBtn" onclick="show('reels')">🎬 Edits</div><div class="rowBtn" onclick="show('threads')">🧵 Threads - ثريدز نور</div><div class="rowBtn" onclick="show('gram')">📸 نور قرام - Instagram</div><div class="rowBtn" onclick="alert('نور بيسك')">⚡ نور بيسك - Free Basics</div><div class="rowBtn" onclick="show('chat')">💬 نور شات - Messenger</div><div class="rowBtn" onclick="show('chat')">💚 نور واتساب - واتساب</div></div>
<div class="card"><button class="gray" onclick="logout()">تسجيل الخروج</button></div></div>

<!-- باقي الأقسام -->
<div id="tab-profile" class="tab"><div class="card"><h2 id="pName"></h2><p id="pBio"></p><input id="bioIn" placeholder="البايو..."><input id="avIn" placeholder="رابط صورتك..."><button onclick="saveProfile()">حفظ البروفايل</button><div id="pStats"></div></div><div id="myPosts"></div></div>
<div id="tab-saved" class="tab"><div class="card"><h2>🔖 المحفوظة / الذكريات</h2><div id="savedList"></div></div></div>
<div id="tab-groups" class="tab"><div class="card"><h2>👥 المجموعات</h2><div id="groupsList"></div></div></div>
<div id="tab-friends" class="tab"><div class="card"><h2>👥 الأصدقاء</h2><div id="friendsList"></div></div></div>
<div id="tab-news" class="tab"><div class="card"><h2>📰 الأخبار</h2><p>أخبار السودان - Alhadath.Alsudani</p><div id="newsList"></div></div></div>
<div id="tab-events" class="tab"><div class="card"><h2>📅 المناسبات</h2><div>🎉 مناسبة: عيد الاستقلال - 1 يناير<br>🎂 عيد ميلاد صديقك غداً</div></div></div>
<div id="tab-games" class="tab"><div class="card"><h2>🎮 الألعاب</h2><button onclick="alert('لعبة XO')">لعبة XO</button><button onclick="alert('لعبة الذاكرة')">لعبة الذاكرة</button></div></div>
<div id="tab-notif" class="tab"><div class="card"><h2>🔔 الإشعارات</h2><div id="notifList"></div></div></div>
</div>

<div class="bottom"><div onclick="show('home')" id="b-home" class="active">📘<br>نور بوك</div><div onclick="show('gram')" id="b-gram">📸<br>نور قرام</div><div onclick="show('reels')" id="b-reels">🎬<br>ريلز</div><div onclick="show('chat')" id="b-chat">💬<br>نور شات</div><div onclick="show('threads')" id="b-threads">🧵<br>ثريدز</div><div onclick="show('menu')" id="b-menu">☰<br>القائمة</div></div>

<div class="modal" id="createModal"><div class="box"><h2>إنشاء</h2><div class="rowBtn" onclick="openCreatePost()">📝 منشور <span>‹</span></div><div class="rowBtn" onclick="addStory()">➕ قصة <span>‹</span></div><div class="rowBtn" onclick="openCreatePost()">🎬 مقطع ريلز <span>‹</span></div><div class="rowBtn" onclick="alert('بث مباشر قريبا - تحتاج 1250 متابع')">📹 بث مباشر <span>‹</span></div><div class="rowBtn" onclick="openCreatePost()">💬 ملاحظة <span>‹</span></div><button class="gray" onclick="closeModal()">إلغاء</button></div></div>

<div class="modal" id="postModal"><div class="box"><h3>بم تفكر؟ اكتب بوست...</h3><textarea id="pContent" rows="4" placeholder="بم تفكر؟ اكتب بوست..."></textarea><input id="pImage" placeholder="رابط صورة / فيديو - أو من رابط"><div class="grid2"><div class="chip active" onclick="setType('post',this)">📁 من الملفات</div><div class="chip" onclick="setType('link',this)">🔗 من رابط</div><div class="chip" onclick="setType('image',this)">🎨 صنع صورة</div><div class="chip" onclick="setType('reel',this)">🎬 صنع فيديو / ريلز</div></div><p><small>اختر من تلفونك - حتظهر المعاينة تحت</small></p><input type="file" id="fileIn" accept="image/*,video/*" onchange="previewFile()"><img id="preview" style="width:100%;border-radius:12px;display:none"><button onclick="createPost()">🚀 نشر بوست</button><button class="pink" onclick="createPostReel()">🎬 نشر كـ ريلز</button><button class="gray" onclick="closePost()">إلغاء</button></div></div>

<script>
let user=JSON.parse(localStorage.getItem('noor_user')||'null');let isReg=false;let chatWith=null;let postType='post';
function toggleAuth(){isReg=!isReg;document.getElementById('aTitle').innerText=isReg?'إنشاء حساب':'تسجيل الدخول';document.getElementById('aBtn').innerText=isReg?'تسجيل':'دخول';document.getElementById('username').style.display=isReg?'block':'none'}
if(user) showApp();
function showApp(){document.getElementById('auth').style.display='none';document.getElementById('app').style.display='block';document.getElementById('myName').innerText=user.username;document.getElementById('pName').innerText=user.username;document.getElementById('av1').innerText=user.username[0];document.getElementById('av2').innerText=user.username[0];document.getElementById('topAvatar').innerText=user.username[0];loadAll()}
async function doAuth(){let u=document.getElementById('username').value,e=document.getElementById('email').value,p=document.getElementById('password').value;let url=isReg?'/api/register':'/api/login';let body=isReg?{username:u,email:e,password:p}:{email:e,password:p};let r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let d=await r.json();if(d.user){localStorage.setItem('noor_user',JSON.stringify(d.user));user=d.user;showApp()}else document.getElementById('aMsg').innerText=d.error||'خطأ'}
function logout(){localStorage.removeItem('noor_user');location.reload()}
function show(t){let map={home:'home',gram:'gram',reels:'reels',chat:'chat',threads:'threads',menu:'menu',profile:'profile',saved:'saved',groups:'groups',friends:'friends',news:'news',events:'events',games:'games',notif:'notif'};let id=map[t]||t;document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));let el=document.getElementById('tab-'+id);if(el)el.classList.add('active');document.querySelectorAll('.bottom div').forEach(e=>e.classList.remove('active'));let b=document.getElementById('b-'+id);if(b)b.classList.add('active');window.scrollTo(0,0);if(id=='groups')loadGroups();if(id=='friends')loadUsers();if(id=='saved')loadSaved()}
function openCreate(){document.getElementById('createModal').style.display='flex'}
function closeModal(){document.getElementById('createModal').style.display='none'}
function openCreatePost(){closeModal();document.getElementById('postModal').style.display='flex'}
function closePost(){document.getElementById('postModal').style.display='none'}
function setType(t,el){postType=t;document.querySelectorAll('.chip').forEach(c=>c.classList.remove('active'));el.classList.add('active')}
function previewFile(){let f=document.getElementById('fileIn').files[0];if(!f)return;let r=new FileReader();r.onload=e=>{let p=document.getElementById('preview');p.src=e.target.result;p.style.display='block';document.getElementById('pImage').value=e.target.result};r.readAsDataURL(f)}
async function loadAll(){loadPosts();loadStories();loadUsers();loadNotif();loadGroups()}
async function loadPosts(){let r=await fetch('/api/posts');let d=await r.json();let h='';for(let p of d.posts){h+='<div class="card"><div class="flex"><div class="avatar">'+p.username[0]+'</div><b>'+p.username+'</b><small>'+p.created_at+'</small></div><p>'+p.content+'</p>'+(p.image?'<img class="postImg" src="'+p.image+'">':'')+'<div class="act"><button onclick="likePost('+p.id+')">❤️ '+p.likes+'</button><button onclick="toggleC('+p.id+')">💬 '+p.comments+'</button><button onclick="savePost('+p.id+')">🔖 حفظ</button><button onclick="sharePost()">↗️ مشاركة</button></div><div id="c-'+p.id+'" style="display:none"><div id="cl-'+p.id+'"></div><input id="ci-'+p.id+'" placeholder="اكتب تعليق..."><button onclick="addComment('+p.id+')">تعليق</button></div>'+(p.user_id==user.id?'<button class="red" onclick="delPost('+p.id+')">حذف</button>':'')+'</div>'}document.getElementById('posts').innerHTML=h||'لسه ما في منشورات - انت أول واحد انشر';document.getElementById('gramList').innerHTML=d.posts.filter(p=>p.image).map(p=>'<img src="'+p.image+'" style="width:100%;border-radius:12px;margin:5px 0"><p>'+p.content+'</p>').join('')||'لا توجد صور';document.getElementById('reelsList').innerHTML=d.posts.filter(p=>p.type=='reel').map(p=>'<div class="card">'+p.content+(p.image?'<img class="postImg" src="'+p.image+'">':'')+'</div>').join('')||'لا توجد ريلز';document.getElementById('newsList').innerHTML=d.posts.map(p=>'<div class="card"><b>'+p.username+'</b><p>'+p.content+'</p></div>').join('')}
async function createPost(){let c=document.getElementById('pContent').value||document.getElementById('postText').value;if(!c&&!document.getElementById('pImage').value)return alert('اكتب شي');await fetch('/api/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,content:c,image:document.getElementById('pImage').value,type:postType})});closePost();document.getElementById('pContent').value='';loadPosts()}
async function createPostReel(){postType='reel';createPost()}
async function likePost(id){await fetch('/api/like',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,post_id:id})});loadPosts()}
async function savePost(id){await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,post_id:id})});alert('تم الحفظ في العناصر المحفوظة')}
async function loadSaved(){let r=await fetch('/api/saved/'+user.id);let d=await r.json();document.getElementById('savedList').innerHTML=d.posts.map(p=>'<div class="card">'+p.content+'</div>').join('')||'لا توجد محفوظات'}
async function delPost(id){await fetch('/api/posts/'+id,{method:'DELETE'});loadPosts()}
async function toggleC(id){let e=document.getElementById('c-'+id);e.style.display=e.style.display=='none'?'block':'none';let r=await fetch('/api/comments/'+id);let d=await r.json();document.getElementById('cl-'+id).innerHTML=d.comments.map(c=>'<div><b>'+c.username+': </b>'+c.content+'</div>').join('')}
async function addComment(id){let c=document.getElementById('ci-'+id).value;if(!c)return;await fetch('/api/comments/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,content:c})});loadPosts()}
function sharePost(){alert('تم نسخ رابط المنشور!')}
async function loadStories(){let r=await fetch('/api/stories');let d=await r.json();document.getElementById('stories').innerHTML=d.stories.map(s=>'<div class="story">'+(s.image?'<img src="'+s.image+'">':'')+'<b>'+s.username+'<br>'+s.text+'</b></div>').join('')||'<div class="story" onclick="addStory()"><b>+ أضف قصتك</b></div>'}
async function addStory(){closeModal();let t=prompt('اكتب نص القصة');let img=prompt('رابط صورة القصة');if(!t&&!img)return;await fetch('/api/stories',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,text:t||'',image:img||''})});loadStories()}
async function loadUsers(){let r=await fetch('/api/users');let d=await r.json();let others=d.users.filter(x=>x.id!=user.id);document.getElementById('usersList').innerHTML=others.map(x=>'<div class="flex" style="justify-content:space-between"><span>👤 '+x.username+' - '+x.followers+' متابع</span><button style="width:auto" onclick="openChat('+x.id+',\\''+x.username+'\\')">مراسلة</button></div>').join('')||'لا يوجد مستخدمين';document.getElementById('suggest').innerHTML=others.map(x=>'<div class="flex" style="justify-content:space-between;margin:8px 0"><div class="flex"><div class="avatar">'+x.username[0]+'</div><div><b>'+x.username+'</b><br><small>'+x.followers+' متابع • ٥٠ صديق مشترك</small></div></div><div style="display:flex;gap:5px"><button style="width:auto" onclick="followUser('+x.id+')">+ إضافة صديق</button><button style="width:auto" class="gray" onclick="this.parentElement.parentElement.remove()">إزالة</button></div></div>').join('');document.getElementById('friendsList').innerHTML=others.map(x=>'<div>👤 '+x.username+'</div>').join('')}
async function followUser(id){await fetch('/api/follow',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({follower_id:user.id,following_id:id})});loadUsers();loadNotif()}
async function openChat(id,name){chatWith=id;document.getElementById('chatTitle').innerText='محادثة مع '+name;show('chat');let r=await fetch('/api/messages?user_id='+user.id+'&other_id='+id);let d=await r.json();document.getElementById('chatBox').innerHTML=d.messages.map(m=>'<div class="msg '+(m.sender_id==user.id?'me':'other')+'">'+m.content+'</div>').join('')}
async function sendMsg(){let c=document.getElementById('chatInput').value;if(!c||!chatWith)return alert('اختر شخص أولا');await fetch('/api/messages',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sender_id:user.id,receiver_id:chatWith,content:c})});document.getElementById('chatInput').value='';openChat(chatWith,document.getElementById('chatTitle').innerText.replace('محادثة مع ',''))}
async function loadNotif(){let r=await fetch('/api/notifications/'+user.id);let d=await r.json();document.getElementById('notifList').innerHTML=d.notifications.map(n=>'<div style="padding:10px;border-bottom:1px solid #eee">'+n.content+'</div>').join('')}
async function loadGroups(){let r=await fetch('/api/groups');let d=await r.json();document.getElementById('groupsList').innerHTML=d.groups.map(g=>'<div class="card"><b>'+g.name+'</b><p>'+g.desc+' - '+g.members+' عضو</p><button onclick="alert(\\'انضممت للمجموعة\\')">انضمام</button></div>').join('')}
async function saveProfile(){await fetch('/api/profile/'+user.id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({bio:document.getElementById('bioIn').value,avatar:document.getElementById('avIn').value})});alert('تم حفظ البروفايل')}
async function createPage(){let n=prompt('اسم الصفحة؟');if(!n)return;await fetch('/api/pages',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,name:n})});alert('تم إنشاء صفحة '+n+' على نور بوك')}
async function postThread(){let c=document.getElementById('threadInput').value;if(!c)return;await fetch('/api/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,content:c,type:'thread'})});document.getElementById('threadInput').value='';let r=await fetch('/api/posts');let d=await r.json();document.getElementById('threadsList').innerHTML=d.posts.filter(p=>p.type=='thread').map(p=>'<div class="card"><b>'+p.username+'</b><p>'+p.content+'</p></div>').join('')}
</script></body></html>"""

@app.route("/")
def home(): return HTML2
@app.route("/api/register", methods=["POST"])
def reg():
    d=request.get_json() or {}; c=db()
    try:
        c.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)",(d.get("username"),d.get("email"),hp(d.get("password","")))); c.commit()
        u=c.execute("SELECT * FROM users WHERE email=?",(d.get("email"),)).fetchone(); return jsonify({"user":{"id":u["id"],"username":u["username"],"email":u["email"]}})
    except: return jsonify({"error":"الاسم أو الايميل موجود"}),400
    finally: c.close()
@app.route("/api/login", methods=["POST"])
def log():
    d=request.get_json() or {}; c=db(); u=c.execute("SELECT * FROM users WHERE email=? AND password=?",(d.get("email"),hp(d.get("password","")))).fetchone(); c.close()
    if u: return jsonify({"user":{"id":u["id"],"username":u["username"],"email":u["email"]}})
    return jsonify({"error":"بيانات خاطئة"}),401
@app.route("/api/users")
def users():
    c=db(); rows=c.execute("SELECT * FROM users").fetchall(); out=[]
    for u in rows:
        f=c.execute("SELECT COUNT(*) c FROM follows WHERE following_id=?",(u["id"],)).fetchone()["c"]; out.append({"id":u["id"],"username":u["username"],"email":u["email"],"followers":f})
    c.close(); return jsonify({"users":out})
@app.route("/api/profile/<int:uid>", methods=["PUT"])
def prof(uid):
    d=request.get_json() or {}; c=db(); c.execute("UPDATE users SET bio=?, avatar=? WHERE id=?",(d.get("bio",""),d.get("avatar",""),uid)); c.commit(); c.close(); return jsonify({"message":"تم"})
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
        d=request.get_json() or {}; c.execute("INSERT INTO posts (user_id,content,image,type,created_at) VALUES (?,?,?,?,?)",(d.get("user_id"),d.get("content"),d.get("image",""),d.get("type","post"),now())); c.commit(); c.close(); return jsonify({"message":"تم"})
    rows=c.execute("SELECT p.*, u.username FROM posts p LEFT JOIN users u ON u.id=p.user_id ORDER BY p.id DESC").fetchall(); out=[]
    for p in rows:
        likes=c.execute("SELECT COUNT(*) c FROM likes WHERE post_id=?",(p["id"],)).fetchone()["c"]; comments=c.execute("SELECT COUNT(*) c FROM comments WHERE post_id=?",(p["id"],)).fetchone()["c"]
        out.append({"id":p["id"],"content":p["content"],"image":p["image"],"type":p["type"],"user_id":p["user_id"],"username":p["username"] or "","likes":likes,"comments":comments,"created_at":p["created_at"]})
    c.close(); return jsonify({"posts":out})
@app.route("/api/posts/<int:pid>", methods=["DELETE"])
def delp(pid):
    c=db(); c.execute("DELETE FROM posts WHERE id=?",(pid,)); c.commit(); c.close(); return jsonify({"message":"تم"})
@app.route("/api/like", methods=["POST"])
def like():
    d=request.get_json() or {}; c=db(); ex=c.execute("SELECT * FROM likes WHERE user_id=? AND post_id=?",(d.get("user_id"),d.get("post_id"))).fetchone()
    if ex: c.execute("DELETE FROM likes WHERE id=?",(ex["id"],))
    else: c.execute("INSERT INTO likes (user_id,post_id) VALUES (?,?)",(d.get("user_id"),d.get("post_id")))
    c.commit(); c.close(); return jsonify({"message":"تم"})
@app.route("/api/save", methods=["POST"])
def save():
    d=request.get_json() or {}; c=db()
    try: c.execute("INSERT INTO saved (user_id,post_id) VALUES (?,?)",(d.get("user_id"),d.get("post_id"))); c.commit()
    except: pass
    c.close(); return jsonify({"message":"تم"})
@app.route("/api/saved/<int:uid>")
def saved(uid):
    c=db(); rows=c.execute("SELECT p.*, u.username FROM saved s JOIN posts p ON p.id=s.post_id LEFT JOIN users u ON u.id=p.user_id WHERE s.user_id=?",(uid,)).fetchall(); out=[{"content":r["content"],"username":r["username"] or ""} for r in rows]; c.close(); return jsonify({"posts":out})
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
        d=request.get_json() or {}; c.execute("INSERT INTO stories (user_id,image,text,created_at) VALUES (?,?,?,?)",(d.get("user_id"),d.get("image",""),d.get("text",""),now())); c.commit(); c.close(); return jsonify({"message":"تم"})
    rows=c.execute("SELECT s.*, u.username FROM stories s LEFT JOIN users u ON u.id=s.user_id ORDER BY s.id DESC").fetchall(); out=[{"username":r["username"] or "","image":r["image"],"text":r["text"]} for r in rows]; c.close(); return jsonify({"stories":out})
@app.route("/api/messages", methods=["GET","POST"])
def msgs():
    c=db()
    if request.method=="POST":
        d=request.get_json() or {}; c.execute("INSERT INTO messages (sender_id,receiver_id,content,created_at) VALUES (?,?,?,?)",(d.get("sender_id"),d.get("receiver_id"),d.get("content"),now())); c.commit(); c.close(); return jsonify({"message":"تم"})
    uid=request.args.get("user_id",type=int); oid=request.args.get("other_id",type=int); rows=c.execute("SELECT * FROM messages WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?) ORDER BY id ASC",(uid,oid,oid,uid)).fetchall(); out=[{"sender_id":r["sender_id"],"content":r["content"]} for r in rows]; c.close(); return jsonify({"messages":out})
@app.route("/api/notifications/<int:uid>")
def notif(uid):
    c=db(); rows=c.execute("SELECT * FROM comments c JOIN posts p ON p.id=c.post_id WHERE p.user_id=? ORDER BY c.id DESC LIMIT 20",(uid,)).fetchall(); out=[{"content":f"علق {r['content'][:30]} على منشورك"} for r in rows]; c.close()
    if not out: out=[{"content":"مرحباً بك في Noor - أنشئ أول منشور"}]
    return jsonify({"notifications":out})
@app.route("/api/groups")
def groups():
    c=db(); rows=c.execute("SELECT * FROM groups").fetchall(); out=[{"name":r["name"],"desc":r["desc"],"members":r["members"]} for r in rows]; c.close(); return jsonify({"groups":out})
@app.route("/api/pages", methods=["POST"])
def pages():
    d=request.get_json() or {}; c=db(); c.execute("INSERT INTO pages (user_id,name,cat) VALUES (?,?,?)",(d.get("user_id"),d.get("name"),"عام")); c.commit(); c.close(); return jsonify({"message":"تم"})
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
