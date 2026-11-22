import os, sqlite3, json, hashlib, datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = "noorbook-2026"

DB = "noorbook.db"

def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, email TEXT UNIQUE, password TEXT, bio TEXT DEFAULT '', avatar TEXT DEFAULT '', cover TEXT DEFAULT '')")
    db.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT, image TEXT DEFAULT '', created_at TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS likes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, post_id INTEGER, UNIQUE(user_id, post_id))")
    db.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, user_id INTEGER, content TEXT, created_at TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS stories (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, image TEXT, text TEXT, created_at TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER, receiver_id INTEGER, content TEXT, created_at TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS follows (id INTEGER PRIMARY KEY AUTOINCREMENT, follower_id INTEGER, following_id INTEGER, UNIQUE(follower_id, following_id))")
    db.commit(); db.close()

init_db()

def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()
def now(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

HTML = r"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NoorBook</title><style>
*{box-sizing:border-box}body{font-family:Arial;background:#f0f2f5;margin:0}
.top{background:#fff;padding:10px 14px;display:flex;gap:10px;align-items:center;position:sticky;top:0;z-index:10;box-shadow:0 1px 5px #ddd}
.logo{font-size:26px;font-weight:900;color:#1877f2}.search{flex:1;background:#f0f2f5;border-radius:20px;padding:9px 14px;border:none;outline:none}
.main{display:flex;max-width:1100px;margin:14px auto;gap:14px;padding:0 10px}
.left{width:260px}.center{flex:1}.right{width:260px}
.card{background:#fff;border-radius:12px;padding:14px;margin-bottom:12px;box-shadow:0 1px 3px #ddd}
input,textarea{width:100%;padding:11px;border:1px solid #ddd;border-radius:10px;margin:5px 0;font-size:15px}
button{background:#1877f2;color:#fff;border:none;padding:11px;border-radius:8px;font-weight:bold;cursor:pointer;width:100%;margin-top:6px}
button.green{background:#42b72a}button.gray{background:#e4e6eb;color:#000}button.red{background:#ff4444}
.avatar{width:42px;height:42px;border-radius:50%;background:#1877f2;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:bold;flex-shrink:0;overflow:hidden}
.avatar img{width:100%;height:100%;object-fit:cover}.flex{display:flex;gap:10px;align-items:center}
.storyRow{display:flex;gap:10px;overflow:auto}.story{min-width:110px;height:180px;border-radius:12px;background:#1877f2;color:#fff;padding:10px;position:relative;cursor:pointer;overflow:hidden}.story img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.tabs{display:flex;gap:8px}.tabs button{flex:1}.tabs button.active{background:#0f5ac0}
.menuItem{padding:10px;border-radius:10px;cursor:pointer}.menuItem:hover{background:#eee}
.postImg{width:100%;border-radius:10px;margin-top:8px}.act{display:flex;gap:6px}.act button{flex:1;background:#f0f2f5;color:#000}
.msg{padding:8px 12px;border-radius:14px;margin:5px 0;max-width:80%}.me{background:#1877f2;color:#fff;margin-left:auto}.other{background:#e4e6eb}
@media(max-width:900px){.left,.right{display:none}.main{display:block}}
</style></head><body>
<div class="top"><div class="logo">NoorBook</div><input class="search" id="searchInput" placeholder="🔍 بحث في NoorBook" oninput="searchUsers()"><button style="width:auto" onclick="showTab('notif')">🔔</button><button style="width:auto" onclick="showTab('chat')">💬</button><button style="width:auto" onclick="logout()">خروج</button></div>
<div id="auth" class="card" style="max-width:420px;margin:30px auto"><h2 id="authTitle">تسجيل الدخول</h2><input id="username" placeholder="اسم المستخدم - للتسجيل" style="display:none"><input id="email" placeholder="البريد"><input id="password" type="password" placeholder="كلمة السر"><button onclick="doAuth()" id="authBtn">دخول</button><button class="green" onclick="toggleAuth()">إنشاء حساب جديد</button><p id="authMsg" style="color:red"></p></div>
<div id="app" style="display:none"><div class="main">
<div class="left"><div class="card"><div class="flex"><div class="avatar" id="myAvatar">N</div><b id="myName"></b></div><div class="menuItem" onclick="showTab('posts')">🏠 الرئيسية</div><div class="menuItem" onclick="showTab('profile')">👤 بروفايلي</div><div class="menuItem" onclick="showTab('chat')">💬 نور شات</div><div class="menuItem" onclick="showTab('notif')">🔔 الإشعارات</div><div class="menuItem">⭐ الذكريات</div><div class="menuItem">🔖 المحفوظة</div><div class="menuItem">👥 المجموعات</div><div class="menuItem">👥 الأصدقاء</div></div><div class="card"><h3>أيضاً من Noor</h3><div class="menuItem">📸 نور قرام</div><div class="menuItem">🎬 نور ريلز</div><div class="menuItem">💬 نور شات</div><div class="menuItem">🧵 ثريدز نور</div></div></div>
<div class="center"><div id="tab-posts"><div class="card"><div class="flex"><div class="avatar" id="myAvatar2">N</div><input id="postInput" placeholder="بم تفكر؟"></div><input id="postImage" placeholder="رابط صورة - اختياري"><button onclick="createPost()">+ نشر منشور</button><div class="act"><button onclick="addStory()">📸 قصة</button><button onclick="alert('ريلز قريبا')">🎬 ريلز</button><button onclick="alert('بث مباشر قريبا')">📺 بث مباشر</button></div></div><div class="card"><h3>📸 القصص</h3><div class="storyRow" id="stories"></div></div><div id="postsList"></div></div>
<div id="tab-chat" style="display:none"><div class="card"><h3>نور شات - المحادثات</h3><div id="usersList"></div></div><div class="card"><h3 id="chatTitle">اختر شخص</h3><div id="chatBox" style="max-height:300px;overflow:auto"></div><input id="chatInput" placeholder="اكتب رسالة..."><button onclick="sendMsg()">إرسال</button></div></div>
<div id="tab-notif" style="display:none"><div class="card"><h3>الإشعارات</h3><div id="notifList"></div></div></div>
<div id="tab-profile" style="display:none"><div class="card"><h2 id="pName"></h2><p id="pBio"></p><input id="bioInput" placeholder="اكتب البايو..."><input id="avatarInput" placeholder="رابط صورتك..."><button onclick="saveProfile()">حفظ البروفايل</button><div id="pStats"></div></div><div id="myPosts"></div></div>
</div>
<div class="right"><div class="card"><h3>أشخاص قد تعرفهم</h3><div id="suggest"></div></div><div class="card"><h3>المتابعين</h3><div id="followList"></div></div></div>
</div></div>
<script>
let user=JSON.parse(localStorage.getItem('noor_user')||'null');let isReg=false;let chatWith=null;
function toggleAuth(){isReg=!isReg;document.getElementById('authTitle').innerText=isReg?'إنشاء حساب':'تسجيل الدخول';document.getElementById('authBtn').innerText=isReg?'تسجيل':'دخول';document.getElementById('username').style.display=isReg?'block':'none'}
if(user) showApp();
function showApp(){document.getElementById('auth').style.display='none';document.getElementById('app').style.display='block';document.getElementById('myName').innerText=user.username;document.getElementById('pName').innerText=user.username;document.getElementById('myAvatar').innerText=user.username[0];document.getElementById('myAvatar2').innerText=user.username[0];loadAll()}
async function doAuth(){let u=document.getElementById('username').value,e=document.getElementById('email').value,p=document.getElementById('password').value;let url=isReg?'/api/register':'/api/login';let body=isReg?{username:u,email:e,password:p}:{email:e,password:p};let r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let d=await r.json();if(d.user){localStorage.setItem('noor_user',JSON.stringify(d.user));user=d.user;showApp()}else document.getElementById('authMsg').innerText=d.error||'خطأ'}
function logout(){localStorage.removeItem('noor_user');location.reload()}
function showTab(t){['posts','chat','notif','profile'].forEach(x=>document.getElementById('tab-'+x).style.display=x==t?'block':'none')}
async function loadAll(){loadPosts();loadStories();loadUsers();loadNotif()}
async function loadPosts(){let r=await fetch('/api/posts');let d=await r.json();let h='';for(let p of d.posts){let liked=p.liked?'❤️':'🤍';h+='<div class="card"><div class="flex"><div class="avatar">'+p.username[0]+'</div><b>'+p.username+'</b><small>'+p.created_at+'</small></div><p>'+p.content+'</p>'+(p.image?'<img class="postImg" src="'+p.image+'">':'')+'<div class="act"><button onclick="likePost('+p.id+')">'+liked+' '+p.likes+'</button><button onclick="toggleC('+p.id+')">💬 '+p.comments+'</button><button onclick="sharePost()">↗️ مشاركة</button></div><div id="c-'+p.id+'" style="display:none"><div id="cl-'+p.id+'"></div><input id="ci-'+p.id+'" placeholder="اكتب تعليق..."><button onclick="addComment('+p.id+')">تعليق</button></div>'+(p.user_id==user.id?'<button class="red" onclick="delPost('+p.id+')">حذف</button>':'')+'</div>'}document.getElementById('postsList').innerHTML=h||'لا توجد منشورات'}
async function createPost(){let c=document.getElementById('postInput').value;if(!c)return;await fetch('/api/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,content:c,image:document.getElementById('postImage').value})});document.getElementById('postInput').value='';loadPosts()}
async function likePost(id){await fetch('/api/like',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,post_id:id})});loadPosts()}
async function delPost(id){await fetch('/api/posts/'+id,{method:'DELETE'});loadPosts()}
async function toggleC(id){let e=document.getElementById('c-'+id);e.style.display=e.style.display=='none'?'block':'none';let r=await fetch('/api/comments/'+id);let d=await r.json();document.getElementById('cl-'+id).innerHTML=d.comments.map(c=>'<div><b>'+c.username+': </b>'+c.content+'</div>').join('')}
async function addComment(id){let c=document.getElementById('ci-'+id).value;if(!c)return;await fetch('/api/comments/'+id,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,content:c})});toggleC(id);toggleC(id);loadPosts()}
function sharePost(){alert('تم نسخ رابط المنشور!')}
async function loadStories(){let r=await fetch('/api/stories');let d=await r.json();document.getElementById('stories').innerHTML=d.stories.map(s=>'<div class="story">'+(s.image?'<img src="'+s.image+'">':'')+'<b>'+s.username+'</b><br>'+s.text+'</div>').join('')||'لا توجد قصص'}
async function addStory(){let t=prompt('اكتب نص القصة');let img=prompt('رابط صورة القصة - اختياري');if(!t&&!img)return;await fetch('/api/stories',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,text:t||'',image:img||''})});loadStories()}
async function loadUsers(){let r=await fetch('/api/users');let d=await r.json();let others=d.users.filter(x=>x.id!=user.id);document.getElementById('usersList').innerHTML=others.map(x=>'<div class="menuItem" onclick="openChat('+x.id+',\''+x.username+'\')">👤 '+x.username+'</div>').join('')||'لا يوجد مستخدمين';document.getElementById('suggest').innerHTML=others.map(x=>'<div class="flex" style="justify-content:space-between"><span>'+x.username+'</span><button style="width:auto" onclick="followUser('+x.id+')">+ متابعة</button></div>').join('');document.getElementById('followList').innerHTML=others.map(x=>'<div>'+x.username+' - '+x.followers+' متابع</div>').join('')}
async function searchUsers(){let q=document.getElementById('searchInput').value;if(q.length<1){loadUsers();return}let r=await fetch('/api/users?q='+q);let d=await r.json();document.getElementById('suggest').innerHTML=d.users.filter(x=>x.id!=user.id).map(x=>'<div>'+x.username+'</div>').join('')}
async function followUser(id){await fetch('/api/follow',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({follower_id:user.id,following_id:id})});loadUsers();loadNotif()}
async function openChat(id,name){chatWith=id;document.getElementById('chatTitle').innerText='محادثة مع '+name;showTab('chat');let r=await fetch('/api/messages?user_id='+user.id+'&other_id='+id);let d=await r.json();document.getElementById('chatBox').innerHTML=d.messages.map(m=>'<div class="msg '+(m.sender_id==user.id?'me':'other')+'">'+m.content+'</div>').join('')}
async function sendMsg(){let c=document.getElementById('chatInput').value;if(!c||!chatWith)return alert('اختر شخص أولا');await fetch('/api/messages',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sender_id:user.id,receiver_id:chatWith,content:c})});document.getElementById('chatInput').value='';openChat(chatWith,document.getElementById('chatTitle').innerText.replace('محادثة مع ',''))}
async function loadNotif(){let r=await fetch('/api/notifications/'+user.id);let d=await r.json();document.getElementById('notifList').innerHTML=d.notifications.map(n=>'<div style="padding:10px;border-bottom:1px solid #eee">'+n.content+'</div>').join('')||'لا توجد إشعارات'}
async function saveProfile(){await fetch('/api/profile/'+user.id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({bio:document.getElementById('bioInput').value,avatar:document.getElementById('avatarInput').value})});alert('تم حفظ البروفايل')}
</script></body></html>"""

@app.route("/")
def home(): return HTML

@app.route("/api/register", methods=["POST"])
def reg():
    d=request.get_json() or {}; db=get_db()
    try:
        db.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)",(d.get("username"),d.get("email"),hash_pw(d.get("password","")))); db.commit()
        u=db.execute("SELECT * FROM users WHERE email=?",(d.get("email"),)).fetchone()
        return jsonify({"user":{"id":u["id"],"username":u["username"],"email":u["email"],"followers":0}})
    except: return jsonify({"error":"الاسم أو الايميل موجود"}),400
    finally: db.close()

@app.route("/api/login", methods=["POST"])
def log():
    d=request.get_json() or {}; db=get_db()
    u=db.execute("SELECT * FROM users WHERE email=? AND password=?",(d.get("email"),hash_pw(d.get("password","")))).fetchone(); db.close()
    if u: return jsonify({"user":{"id":u["id"],"username":u["username"],"email":u["email"],"followers":0}})
    return jsonify({"error":"بيانات خاطئة"}),401

@app.route("/api/users")
def users():
    q=request.args.get("q",""); db=get_db()
    rows=db.execute("SELECT * FROM users").fetchall()
    out=[]
    for u in rows:
        if q and q.lower() not in u["username"].lower(): continue
        f=db.execute("SELECT COUNT(*) c FROM follows WHERE following_id=?",(u["id"],)).fetchone()["c"]
        out.append({"id":u["id"],"username":u["username"],"email":u["email"],"followers":f})
    db.close(); return jsonify({"users":out})

@app.route("/api/profile/<int:uid>", methods=["PUT"])
def prof(uid):
    d=request.get_json() or {}; db=get_db()
    db.execute("UPDATE users SET bio=?, avatar=? WHERE id=?",(d.get("bio",""),d.get("avatar",""),uid)); db.commit(); db.close()
    return jsonify({"message":"تم"})

@app.route("/api/follow", methods=["POST"])
def fol():
    d=request.get_json() or {}; db=get_db()
    ex=db.execute("SELECT * FROM follows WHERE follower_id=? AND following_id=?",(d.get("follower_id"),d.get("following_id"))).fetchone()
    if ex: db.execute("DELETE FROM follows WHERE id=?",(ex["id"],))
    else: db.execute("INSERT INTO follows (follower_id,following_id) VALUES (?,?)",(d.get("follower_id"),d.get("following_id")))
    db.commit(); db.close(); return jsonify({"message":"تم"})

@app.route("/api/posts", methods=["GET","POST"])
def posts():
    db=get_db()
    if request.method=="POST":
        d=request.get_json() or {}
        db.execute("INSERT INTO posts (user_id,content,image,created_at) VALUES (?,?,?,?)",(d.get("user_id"),d.get("content"),d.get("image",""),now())); db.commit(); db.close(); return jsonify({"message":"تم"})
    rows=db.execute("SELECT p.*, u.username FROM posts p LEFT JOIN users u ON u.id=p.user_id ORDER BY p.id DESC").fetchall()
    out=[]
    for p in rows:
        likes=db.execute("SELECT COUNT(*) c FROM likes WHERE post_id=?",(p["id"],)).fetchone()["c"]
        comments=db.execute("SELECT COUNT(*) c FROM comments WHERE post_id=?",(p["id"],)).fetchone()["c"]
        out.append({"id":p["id"],"content":p["content"],"image":p["image"],"user_id":p["user_id"],"username":p["username"] or "","likes":likes,"comments":comments,"created_at":p["created_at"],"liked":False})
    db.close(); return jsonify({"posts":out})

@app.route("/api/posts/<int:pid>", methods=["DELETE"])
def delp(pid):
    db=get_db(); db.execute("DELETE FROM posts WHERE id=?",(pid,)); db.commit(); db.close(); return jsonify({"message":"تم"})

@app.route("/api/like", methods=["POST"])
def like():
    d=request.get_json() or {}; db=get_db()
    ex=db.execute("SELECT * FROM likes WHERE user_id=? AND post_id=?",(d.get("user_id"),d.get("post_id"))).fetchone()
    if ex: db.execute("DELETE FROM likes WHERE id=?",(ex["id"],))
    else: db.execute("INSERT INTO likes (user_id,post_id) VALUES (?,?)",(d.get("user_id"),d.get("post_id")))
    db.commit(); db.close(); return jsonify({"message":"تم"})

@app.route("/api/comments/<int:pid>", methods=["GET","POST"])
def comm(pid):
    db=get_db()
    if request.method=="POST":
        d=request.get_json() or {}
        db.execute("INSERT INTO comments (post_id,user_id,content,created_at) VALUES (?,?,?,?)",(pid,d.get("user_id"),d.get("content"),now())); db.commit(); db.close(); return jsonify({"message":"تم"})
    rows=db.execute("SELECT c.*, u.username FROM comments c LEFT JOIN users u ON u.id=c.user_id WHERE c.post_id=? ORDER BY c.id ASC",(pid,)).fetchall()
    out=[{"id":r["id"],"content":r["content"],"username":r["username"] or ""} for r in rows]; db.close(); return jsonify({"comments":out})

@app.route("/api/stories", methods=["GET","POST"])
def stories():
    db=get_db()
    if request.method=="POST":
        d=request.get_json() or {}
        db.execute("INSERT INTO stories (user_id,image,text,created_at) VALUES (?,?,?,?)",(d.get("user_id"),d.get("image",""),d.get("text",""),now())); db.commit(); db.close(); return jsonify({"message":"تم"})
    rows=db.execute("SELECT s.*, u.username FROM stories s LEFT JOIN users u ON u.id=s.user_id ORDER BY s.id DESC").fetchall()
    out=[{"id":r["id"],"username":r["username"] or "","image":r["image"],"text":r["text"]} for r in rows]; db.close(); return jsonify({"stories":out})

@app.route("/api/messages", methods=["GET","POST"])
def msgs():
    db=get_db()
    if request.method=="POST":
        d=request.get_json() or {}
        db.execute("INSERT INTO messages (sender_id,receiver_id,content,created_at) VALUES (?,?,?,?)",(d.get("sender_id"),d.get("receiver_id"),d.get("content"),now())); db.commit(); db.close(); return jsonify({"message":"تم"})
    uid=request.args.get("user_id",type=int); oid=request.args.get("other_id",type=int)
    rows=db.execute("SELECT * FROM messages WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?) ORDER BY id ASC",(uid,oid,oid,uid)).fetchall()
    out=[{"id":r["id"],"sender_id":r["sender_id"],"content":r["content"]} for r in rows]; db.close(); return jsonify({"messages":out})

@app.route("/api/notifications/<int:uid>")
def notif(uid):
    db=get_db()
    rows=db.execute("SELECT * FROM comments c JOIN posts p ON p.id=c.post_id WHERE p.user_id=? ORDER BY c.id DESC LIMIT 20",(uid,)).fetchall()
    out=[{"content":f"علق {r['content'][:30]} على منشورك"} for r in rows]; db.close()
    if not out: out=[{"content":"مرحباً بك في NoorBook - أنشئ أول منشور"}]
    return jsonify({"notifications":out})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
