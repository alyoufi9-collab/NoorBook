import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- إصلاح قاعدة البيانات - ده كان سبب المشكلة ---
db_url = os.environ.get('DATABASE_URL', '').strip()
if not db_url or '://' not in db_url:
    db_url = 'sqlite:///noorbook.db'
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'noorbook-secret-123')

db = SQLAlchemy(app)

# --- الجداول ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, default='')
    avatar = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500), default='')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='posts')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), default='message')
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print("DB Error:", e)

def user_dict(u):
    return {'id': u.id, 'username': u.username, 'email': u.email, 'bio': u.bio or '', 'avatar': u.avatar or '', 'created_at': u.created_at.isoformat() if u.created_at else ''}

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NoorBook - نور بوك</title>
<style>
*{box-sizing:border-box} body{font-family:Arial;background:#f0f2f5;margin:0}
.header{background:#fff;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 1px 5px #ddd;position:sticky;top:0;z-index:10}
.logo{font-size:24px;font-weight:900;color:#1877f2}
.container{max-width:600px;margin:16px auto;padding:0 12px}
.card{background:#fff;border-radius:12px;padding:16px;margin-bottom:12px;box-shadow:0 1px 3px #ddd}
input,textarea{width:100%;padding:12px;border:1px solid #ddd;border-radius:8px;margin:6px 0;font-size:15px}
button{background:#1877f2;color:#fff;border:none;padding:11px 18px;border-radius:8px;font-weight:bold;cursor:pointer;width:100%;margin-top:6px}
button.green{background:#42b72a} .post-avatar{width:40px;height:40px;border-radius:50%;background:#1877f2;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:bold}
.flex{display:flex;gap:10px;align-items:center} .tabs{display:flex;gap:8px;margin-bottom:12px} .tabs button{background:#e4e6eb;color:#000} .tabs button.active{background:#1877f2;color:#fff}
.chat-user{padding:10px;border-bottom:1px solid #eee;cursor:pointer} .msg{padding:8px 12px;border-radius:12px;margin:6px 0;max-width:80%} .me{background:#1877f2;color:#fff;margin-left:auto} .other{background:#e4e6eb}
</style></head>
<body>
<div class="header"><div class="logo">NoorBook</div><div id="headerUser"></div></div>
<div class="container">
<div id="authBox" class="card">
<h2 id="authTitle">تسجيل الدخول</h2>
<input id="username" placeholder="اسم المستخدم (للتسجيل)">
<input id="email" placeholder="البريد الإلكتروني">
<input id="password" type="password" placeholder="كلمة السر">
<button onclick="doAuth()" id="authBtn">دخول</button>
<button class="green" onclick="toggleAuth()">إنشاء حساب جديد</button>
<p id="authMsg" style="color:red"></p>
</div>
<div id="mainBox" style="display:none">
<div class="tabs"><button class="active" onclick="showTab('posts',this)">المنشورات</button><button onclick="showTab('chat',this)">NoorChat 💬</button><button onclick="showTab('notif',this)">الإشعارات 🔔</button></div>
<div id="tab-posts">
<div class="card"><textarea id="postContent" placeholder="شنو في بالك؟"></textarea><input id="postImage" placeholder="رابط صورة (اختياري)"><button onclick="createPost()">نشر</button></div>
<div id="postsList"></div>
</div>
<div id="tab-chat" style="display:none"><div class="card"><h3>المستخدمين</h3><div id="usersList"></div></div><div class="card"><h3 id="chatTitle">اختر مستخدم للشات</h3><div id="chatBox" style="max-height:300px;overflow:auto"></div><input id="chatInput" placeholder="اكتب رسالة..."><button onclick="sendMsg()">إرسال</button></div></div>
<div id="tab-notif" style="display:none"><div class="card"><div id="notifList"></div></div></div>
<button onclick="logout()" style="background:#888">تسجيل خروج</button>
</div></div>
<script>
let user=JSON.parse(localStorage.getItem('noor_user')||'null'); let isRegister=false; let chatWith=null;
function toggleAuth(){isRegister=!isRegister; document.getElementById('authTitle').innerText=isRegister?'إنشاء حساب':'تسجيل الدخول'; document.getElementById('authBtn').innerText=isRegister?'تسجيل':'دخول'; document.getElementById('username').style.display=isRegister?'block':'none';}
if(user){showMain()} else {document.getElementById('username').style.display='none'}
function showMain(){document.getElementById('authBox').style.display='none'; document.getElementById('mainBox').style.display='block'; document.getElementById('headerUser').innerText='أهلا '+user.username; loadPosts(); loadUsers(); loadNotif();}
async function doAuth(){let u=document.getElementById('username').value, e=document.getElementById('email').value, p=document.getElementById('password').value; let url=isRegister?'/api/register':'/api/login'; let body=isRegister?{username:u,email:e,password:p}:{email:e,password:p}; let r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); let d=await r.json(); if(d.user){localStorage.setItem('noor_user',JSON.stringify(d.user)); user=d.user; showMain();} else document.getElementById('authMsg').innerText=d.error||'خطأ';}
function logout(){localStorage.removeItem('noor_user'); location.reload();}
function showTab(t,btn){document.querySelectorAll('.tabs button').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); ['posts','chat','notif'].forEach(x=>document.getElementById('tab-'+x).style.display=x==t?'block':'none');}
async function loadPosts(){let r=await fetch('/api/posts'); let d=await r.json(); document.getElementById('postsList').innerHTML=d.posts.map(p=>`<div class="card"><div class="flex"><div class="post-avatar">${p.username[0]}</div><b>${p.username}</b><small>${p.created_at.slice(0,16)}</small></div><p>${p.content}</p>${p.image?`<img src="${p.image}" style="width:100%;border-radius:10px">`:''}${p.user_id==user.id?`<button onclick="delPost(${p.id})" style="background:#ff4444">حذف</button>`:''}</div>`).join('')||'لا توجد منشورات';}
async function createPost(){let c=document.getElementById('postContent').value; if(!c) return; await fetch('/api/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:user.id,content:c,image:document.getElementById('postImage').value})}); document.getElementById('postContent').value=''; loadPosts();}
async function delPost(id){await fetch('/api/posts/'+id,{method:'DELETE'}); loadPosts();}
async function loadUsers(){let r=await fetch('/api/users'); let d=await r.json(); document.getElementById('usersList').innerHTML=d.users.filter(x=>x.id!=user.id).map(x=>`<div class="chat-user" onclick="openChat(${x.id},'${x.username}')">👤 ${x.username}</div>`).join('');}
async function openChat(id,name){chatWith=id; document.getElementById('chatTitle').innerText='محادثة مع '+name; let r=await fetch(`/api/messages?user_id=${user.id}&other_id=${id}`); let d=await r.json(); document.getElementById('chatBox').innerHTML=d.messages.map(m=>`<div class="msg ${m.sender_id==user.id?'me':'other'}">${m.content}</div>`).join('');}
async function sendMsg(){let c=document.getElementById('chatInput').value; if(!c||!chatWith) return alert('اختر مستخدم أولا'); await fetch('/api/messages',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sender_id:user.id,receiver_id:chatWith,content:c})}); document.getElementById('chatInput').value=''; openChat(chatWith,document.getElementById('chatTitle').innerText); }
async function loadNotif(){let r=await fetch('/api/notifications/'+user.id); let d=await r.json(); document.getElementById('notifList').innerHTML=d.notifications.map(n=>`<div style="padding:10px;border-bottom:1px solid #eee">${n.content} <small>${n.created_at.slice(0,16)}</small></div>`).join('')||'لا توجد إشعارات';}
</script></body></html>
    '''

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': 'اسم المستخدم موجود'}), 400
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'الايميل موجود'}), 400
    u = User(username=data.get('username'), email=data.get('email'), password=generate_password_hash(data.get('password','')))
    db.session.add(u); db.session.commit()
    return jsonify({'user': user_dict(u)})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    u = User.query.filter_by(email=data.get('email')).first()
    if u and check_password_hash(u.password, data.get('password','')):
        return jsonify({'user': user_dict(u)})
    return jsonify({'error': 'بيانات خاطئة'}), 401

@app.route('/api/users')
def users():
    return jsonify({'users': [user_dict(u) for u in User.query.all()]})

@app.route('/api/profile/<int:user_id>', methods=['GET','PUT'])
def profile(user_id):
    u = User.query.get_or_404(user_id)
    if request.method == 'PUT':
        data = request.get_json() or {}
        u.bio = data.get('bio', u.bio); u.avatar = data.get('avatar', u.avatar)
        db.session.commit()
    posts = Post.query.filter_by(user_id=user_id).count()
    d = user_dict(u); d['posts_count'] = posts
    return jsonify(d)

@app.route('/api/posts', methods=['GET','POST'])
def posts():
    if request.method == 'POST':
        data = request.get_json() or {}
        p = Post(content=data.get('content'), image=data.get('image',''), user_id=data.get('user_id'))
        db.session.add(p); db.session.commit()
        return jsonify({'message': 'تم النشر'})
    all_posts = Post.query.order_by(Post.created_at.desc()).all()
    out = []
    for p in all_posts:
        out.append({'id': p.id, 'content': p.content, 'image': p.image, 'user_id': p.user_id, 'username': p.user.username if p.user else '', 'created_at': p.created_at.isoformat() if p.created_at else ''})
    return jsonify({'posts': out})

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    p = Post.query.get_or_404(post_id)
    db.session.delete(p); db.session.commit()
    return jsonify({'message': 'تم الحذف'})

@app.route('/api/messages', methods=['GET','POST'])
def messages():
    if request.method == 'POST':
        data = request.get_json() or {}
        m = Message(sender_id=data.get('sender_id'), receiver_id=data.get('receiver_id'), content=data.get('content'))
        db.session.add(m)
        sender = User.query.get(data.get('sender_id'))
        n = Notification(user_id=data.get('receiver_id'), type='message', content=f"رسالة جديدة من {sender.username if sender else ''}")
        db.session.add(n); db.session.commit()
        return jsonify({'message': 'تم الإرسال'})
    uid = request.args.get('user_id', type=int); oid = request.args.get('other_id', type=int)
    msgs = Message.query.filter(((Message.sender_id==uid)&(Message.receiver_id==oid))|((Message.sender_id==oid)&(Message.receiver_id==uid))).order_by(Message.created_at.asc()).all()
    for
