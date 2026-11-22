import os
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get('SECRET_KEY', 'noorbook-secret-key-2024')

# --- تصليح قاعدة البيانات لـ Vercel ---
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
if not db_url:
    db_url = 'sqlite:////tmp/noorbook.db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, default='')
    avatar = db.Column(db.String(200), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500), default='')
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='posts')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"DB Error: {e}")

# --- Helpers ---
def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)

# --- Auth ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not username or not email or not password:
        return jsonify({'error': 'All fields required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    user = User(username=username, email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    return jsonify({'message': 'Registered', 'user': {'id': user.id, 'username': user.username, 'email': user.email}})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    session['user_id'] = user.id
    return jsonify({'message': 'Logged in', 'user': {'id': user.id, 'username': user.username, 'email': user.email, 'bio': user.bio}})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'})

@app.route('/api/me')
def me():
    user = current_user()
    if not user:
        return jsonify({'user': None})
    return jsonify({'user': {'id': user.id, 'username': user.username, 'email': user.email, 'bio': user.bio, 'avatar': user.avatar}})

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    user = current_user()
    if not user:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json() or {}
    if 'bio' in data:
        user.bio = data['bio']
    if 'avatar' in data:
        user.avatar = data['avatar']
    db.session.commit()
    return jsonify({'message': 'Profile updated'})

@app.route('/api/users')
def get_users():
    user = current_user()
    users = User.query.all()
    result = []
    for u in users:
        if user and u.id == user.id:
            continue
        result.append({'id': u.id, 'username': u.username, 'bio': u.bio, 'avatar': u.avatar})
    return jsonify(result)

# --- Posts ---
@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    result = []
    for p in posts:
        result.append({'id': p.id, 'content': p.content, 'image': p.image, 'likes': p.likes, 'created_at': p.created_at.isoformat(), 'user': {'id': p.user.id, 'username': p.user.username, 'avatar': p.user.avatar}})
    return jsonify(result)

@app.route('/api/posts', methods=['POST'])
def create_post():
    user = current_user()
    if not user:
        return jsonify({'error': 'Login required'}), 401
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Content required'}), 400
    post = Post(user_id=user.id, content=content, image=data.get('image', ''))
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Post created', 'id': post.id})

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})

# --- Messages ---
@app.route('/api/messages/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Login required'}), 401
    msgs = Message.query.filter(((Message.sender_id == user.id) & (Message.receiver_id == user_id)) | ((Message.sender_id == user_id) & (Message.receiver_id == user.id))).order_by(Message.created_at.asc()).all()
    return jsonify([{'id': m.id, 'sender_id': m.sender_id, 'receiver_id': m.receiver_id, 'content': m.content, 'is_read': m.is_read, 'created_at': m.created_at.isoformat()} for m in msgs])

@app.route('/api/messages', methods=['POST'])
def send_message():
    user = current_user()
    if not user:
        return jsonify({'error': 'Login required'}), 401
    data = request.get_json() or {}
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()
    if not receiver_id or not content:
        return jsonify({'error': 'Missing data'}), 400
    msg = Message(sender_id=user.id, receiver_id=receiver_id, content=content)
    db.session.add(msg)
    notif = Notification(user_id=receiver_id, type='message', message=f'{user.username} sent you a message')
    db.session.add(notif)
    db.session.commit()
    return jsonify({'message': 'Sent'})

# --- Notifications ---
@app.route('/api/notifications')
def get_notifications():
    user = current_user()
    if not user:
        return jsonify([])
    notifs = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(20).all()
    return jsonify([{'id': n.id, 'type': n.type, 'message': n.message, 'is_read': n.is_read, 'created_at': n.created_at.isoformat()} for n in notifs])

@app.route('/api/notifications/mark-read', methods=['POST'])
def mark_read():
    user = current_user()
    if not user:
        return jsonify({'error': 'Login required'}), 401
    Notification.query.filter_by(user_id=user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'Marked read'})

# --- Frontend ---
@app.route('/')
def index():
    return """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NoorBook - نور بوك</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial;background:#f0f2f5}.header{background:#fff;padding:12px 20px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 1px 5px rgba(0,0,0,.1);position:sticky;top:0}.logo{font-size:24px;font-weight:bold;color:#1877f2}.nav{display:flex;gap:10px}.nav button{padding:8px 16px;border:none;border-radius:20px;cursor:pointer;background:#e4e6eb}.nav button.active{background:#1877f2;color:#fff}.container{max-width:800px;margin:20px auto;padding:0 15px}.card{background:#fff;padding:15px;border-radius:10px;margin-bottom:15px;box-shadow:0 1px 3px rgba(0,0,0,.1)}input,textarea{width:100%;padding:10px;margin:8px 0;border:1px solid #ddd;border-radius:8px}button.btn{background:#1877f2;color:#fff;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;width:100%}.post-user{font-weight:bold;margin-bottom:5px}.post-time{color:#888;font-size:12px}.user-item{display:flex;justify-content:space-between;padding:10px;border-bottom:1px solid #eee}.msg{padding:8px 12px;margin:5px;border-radius:10px;max-width:70%}.msg.mine{background:#1877f2;color:#fff;margin-left:auto}.msg.other{background:#e4e6eb}#chatBox{height:300px;overflow-y:auto;border:1px solid #eee;padding:10px;margin:10px 0}.hidden{display:none}</style></head><body><div class="header"><div class="logo">📖 NoorBook</div><div class="nav"><button onclick="showTab('home')" id="btn-home" class="active">🏠 الرئيسية</button><button onclick="showTab('chat')" id="btn-chat">💬 NoorChat</button><button onclick="showTab('profile')" id="btn-profile">👤 بروفايل</button><span id="notifCount"></span></div></div><div class="container"><div id="authCard" class="card"><h3>تسجيل الدخول / إنشاء حساب</h3><input id="authUsername" placeholder="اسم المستخدم (للتسجيل)"><input id="authEmail" placeholder="البريد الإلكتروني"><input id="authPassword" type="password" placeholder="كلمة السر"><button class="btn" onclick="doLogin()">دخول</button><button class="btn" style="background:#42b72a;margin-top:8px" onclick="doRegister()">إنشاء حساب جديد</button><p id="authMsg"></p></div><div id="homeTab"><div class="card"><h4>انشر شيئاً جديداً</h4><textarea id="postContent" rows="3" placeholder="بم تفكر؟"></textarea><button class="btn" onclick="createPost()">نشر</button></div><div id="postsList"></div></div><div id="chatTab" class="hidden"><div class="card"><h3>💬 NoorChat</h3><div id="usersList"></div><div id="chatArea" class="hidden"><h4 id="chatWith"></h4><div id="chatBox"></div><input id="msgInput" placeholder="اكتب رسالتك..."><button class="btn" onclick="sendMsg()">إرسال</button></div></div></div><div id="profileTab" class="hidden"><div class="card"><h3>👤 بروفايلي</h3><p id="profileInfo"></p><textarea id="bioInput" placeholder="نبذة عنك"></textarea><button class="btn" onclick="updateBio()">حفظ البروفايل</button><button class="btn" style="background:#e74c3c;margin-top:8px" onclick="doLogout()">تسجيل خروج</button></div></div></div><script>let me=null,chatUser=null;async function api(u,m='GET',b=null){let r=await fetch(u,{method:m,headers:{'Content-Type':'application/json'},credentials:'include',body:b?JSON.stringify(b):null});return r.json()}async function loadMe(){let d=await api('/api/me');me=d.user;if(me){document.getElementById('authCard').style.display='none';document.getElementById('profileInfo').innerText=me.username+' - '+me.email;document.getElementById('bioInput').value=me.bio||''}loadPosts();loadUsers()}async function doRegister(){let d=await api('/api/register','POST',{username:authUsername.value,email:authEmail.value,password:authPassword.value});authMsg.innerText=d.error||d.message;if(!d.error)location.reload()}async function doLogin(){let d=await api('/api/login','POST',{email:authEmail.value,password:authPassword.value});authMsg.innerText=d.error||d.message;if(!d.error)location.reload()}async function doLogout(){await api('/api/logout','POST');location.reload()}async function loadPosts(){let p=await api('/api/posts');postsList.innerHTML=p.map(x=>`<div class="card"><div class="post-user">👤 ${x.user.username}</div><div class="post-time">${new Date(x.created_at).toLocaleString('ar')}</div><p style="margin:10px 0">${x.content}</p><button onclick="likePost(${x.id})">❤️ ${x.likes}</button></div>`).join('')||'<div class="card">لا توجد منشورات بعد</div>'}async function createPost(){if(!me)return alert('سجل دخول أولاً');await api('/api/posts','POST',{content:postContent.value});postContent.value='';loadPosts()}async function likePost(id){await api('/api/posts/'+id+'/like','POST');loadPosts()}async function loadUsers(){let u=await api('/api/users');usersList.innerHTML=u.map(x=>`<div class="user-item"><span>👤 ${x.username} - ${x.bio||''}</span><button onclick="openChat(${x.id},'${x.username}')">محادثة</button></div>`).join('')||'لا يوجد مستخدمين'}async function openChat(id,name){chatUser=id;chatWith.innerText='محادثة مع '+name;chatArea.classList.remove('hidden');loadMsgs()}async function loadMsgs(){if(!chatUser)return;let m=await api('/api/messages/'+chatUser);chatBox.innerHTML=m.map(x=>`<div class="msg ${x.sender_id==me.id?'mine':'other'}">${x.content}</div>`).join('');chatBox.scrollTop=chatBox.scrollHeight}async function sendMsg(){await api('/api/messages','POST',{receiver_id:chatUser,content:msgInput.value});msgInput.value='';loadMsgs()}async function updateBio(){await api('/api/profile','PUT',{bio:bioInput.value});alert('تم الحفظ')}function showTab(t){['home','chat','profile'].forEach(x=>{document.getElementById(x+'Tab').classList.toggle('hidden',x!==t);document.getElementById('btn-'+x).classList.toggle('active',x===t)})}loadMe();setInterval(()=>{if(chatUser)loadMsgs()},3000);</script></body></html>"""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
