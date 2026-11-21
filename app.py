import os, json, base64, random, string
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///app.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://','postgresql://',1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','b-2048-secret')
db = SQLAlchemy(app)

# ===== Helpers - مصلحة =====
def hash_pw(p): return generate_password_hash(p)
def check_pw(h,p): return check_password_hash(h,p)
def encrypt(t):
    try: return base64.b64encode(str(t).encode()).decode()
    except: return str(t)
def decrypt(t):
    try: return base64.b64decode(str(t).encode()).decode()
    except: return str(t)
def now(): return datetime.utcnow().isoformat()

# ===== Models =====
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True); email=db.Column(db.String(200),unique=True)
    password=db.Column(db.String(300)); name=db.Column(db.String(200),default='User')
    avatar=db.Column(db.Text,default=''); bio=db.Column(db.Text,default='')
    cover=db.Column(db.Text,default=''); username=db.Column(db.String(100),default='')
    phone=db.Column(db.String(50),default=''); verified=db.Column(db.Boolean,default=False)
    followers=db.Column(db.Integer,default=0); following=db.Column(db.Integer,default=0)
    balance=db.Column(db.Float,default=0); created=db.Column(db.String(50),default=now)
    def to_dict(self): return {"id":self.id,"email":self.email,"name":self.name,"avatar":self.avatar,"bio":self.bio,"cover":self.cover,"username":self.username,"phone":self.phone,"verified":self.verified,"followers":self.followers,"following":self.following,"balance":self.balance}
class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); user_name=db.Column(db.String(200))
    text=db.Column(db.Text,default=''); image=db.Column(db.Text,default=''); video=db.Column(db.Text,default='')
    link=db.Column(db.Text,default=''); likes=db.Column(db.Integer,default=0)
    comments=db.Column(db.Integer,default=0); shares=db.Column(db.Integer,default=0); created=db.Column(db.String(50),default=now)
    def to_dict(self): return {"id":self.id,"user_id":self.user_id,"user_name":self.user_name,"text":self.text,"image":self.image,"video":self.video,"link":self.link,"likes":self.likes,"comments":self.comments,"shares":self.shares,"created":self.created}
class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True); post_id=db.Column(db.Integer); user_id=db.Column(db.Integer)
    user_name=db.Column(db.String(200)); text=db.Column(db.Text); created=db.Column(db.String(50),default=now)
    def to_dict(self): return {"id":self.id,"post_id":self.post_id,"user_id":self.user_id,"user_name":self.user_name,"text":self.text,"created":self.created}
class Friend(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); friend_id=db.Column(db.Integer)
    friend_name=db.Column(db.String(200)); status=db.Column(db.String(50),default='accepted')
    def to_dict(self): return {"id":self.id,"user_id":self.user_id,"friend_id":self.friend_id,"friend_name":self.friend_name,"status":self.status}
class Chat(db.Model):
    id=db.Column(db.Integer,primary_key=True); user1=db.Column(db.Integer); user2=db.Column(db.Integer)
    name=db.Column(db.String(200)); last_msg=db.Column(db.Text,default='')
    def to_dict(self): return {"id":self.id,"user1":self.user1,"user2":self.user2,"name":self.name,"last_msg":self.last_msg}
class Message(db.Model):
    id=db.Column(db.Integer,primary_key=True); chat_id=db.Column(db.Integer); sender_id=db.Column(db.Integer)
    sender_name=db.Column(db.String(200)); text=db.Column(db.Text); image=db.Column(db.Text,default='')
    created=db.Column(db.String(50),default=now)
    def to_dict(self): return {"id":self.id,"chat_id":self.chat_id,"sender_id":self.sender_id,"sender_name":self.sender_name,"text":self.text,"image":self.image,"created":self.created}
class Page(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); name=db.Column(db.String(200))
    category=db.Column(db.String(100),default='Page'); likes=db.Column(db.Integer,default=0)
    def to_dict(self): return {"id":self.id,"user_id":self.user_id,"name":self.name,"category":self.category,"likes":self.likes}
class Reel(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); user_name=db.Column(db.String(200))
    video=db.Column(db.Text,default=''); caption=db.Column(db.Text,default=''); likes=db.Column(db.Integer,default=0)
    def to_dict(self): return {"id":self.id,"user_id":self.user_id,"user_name":self.user_name,"video":self.video,"caption":self.caption,"likes":self.likes}
class Thread(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); user_name=db.Column(db.String(200))
    text=db.Column(db.Text); likes=db.Column(db.Integer,default=0)
    def to_dict(self): return {"id":self.id,"user_id":self.user_id,"user_name":self.user_name,"text":self.text,"likes":self.likes}
class Gift(db.Model):
    id=db.Column(db.Integer,primary_key=True); sender_id=db.Column(db.Integer); receiver_id=db.Column(db.Integer)
    amount=db.Column(db.Float,default=0); message=db.Column(db.Text,default='')
    def to_dict(self): return {"id":self.id,"sender_id":self.sender_id,"receiver_id":self.receiver_id,"amount":self.amount,"message":self.message}
class Ad(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); title=db.Column(db.String(300))
    budget=db.Column(db.Float,default=0); status=db.Column(db.String(50),default='active')
    def to_dict(self): return {"id":self.id,"user_id":self.user_id,"title":self.title,"budget":self.budget,"status":self.status}
class Support(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); subject=db.Column(db.String(300))
    message=db.Column(db.Text); status=db.Column(db.String(50),default='open')
    def to_dict(self): return {"id":self.id,"user_id":self.user_id,"subject":self.subject,"message":self.message,"status":self.status}
class Link(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); url=db.Column(db.Text); title=db.Column(db.String(300),default='')
    def to_dict(self): return {"id":self.id,"user_id":self.user_id,"url":self.url,"title":self.title}
class Payment(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); amount=db.Column(db.Float,default=0)
    method=db.Column(db.String(100),default=''); status=db.Column(db.String(50),default='completed'); created=db.Column(db.String(50),default=now)
    def to_dict(self): return {"id":self.id,"user_id":self.user_id,"amount":self.amount,"method":self.method,"status":self.status,"created":self.created}
class Story(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer); user_name=db.Column(db.String(200)); image=db.Column(db.Text,default='')
    def to_dict(self): return {"id":self.id,"user_id":self.user_id,"user_name":self.user_name,"image":self.image}

with app.app_context(): db.create_all()

def get_user():
    h = request.headers.get('X-User-Id') or request.args.get('user_id') or (request.get_json(silent=True) or {}).get('user_id')
    if not h: return None
    try: return User.query.get(int(h))
    except: return None
def req_user():
    u=get_user()
    if not u: return None,(jsonify({"error":"login required"}),401)
    return u,None

# ===== Auth =====
@app.route('/api/v1/register',methods=['POST'])
def register():
    d=request.get_json(force=True); email=d.get('email','').strip().lower(); pw=d.get('password','')
    if not email or not pw: return jsonify({"error":"email and password required"}),400
    if User.query.filter_by(email=email).first(): return jsonify({"error":"email exists"}),400
    u=User(email=email,password=hash_pw(pw),name=d.get('name') or email.split('@')[0],username=d.get('name') or email.split('@')[0])
    db.session.add(u); db.session.commit(); return jsonify({"user":u.to_dict()})
@app.route('/api/v1/login',methods=['POST'])
def login():
    d=request.get_json(force=True); u=User.query.filter_by(email=d.get('email','').strip().lower()).first()
    if not u or not check_pw(u.password,d.get('password','')): return jsonify({"error":"invalid login"}),401
    return jsonify({"user":u.to_dict()})
@app.route('/api/v1/logout',methods=['POST'])
def logout(): return jsonify({"ok":True})

# ===== Profile / Pages / Money =====
@app.route('/api/v1/profile',methods=['GET','POST'])
def profile():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"user":u.to_dict()})
    d=request.get_json(force=True)
    for k in ['name','bio','avatar','cover','username','phone']:
        if k in d: setattr(u,k,d[k])
    db.session.commit(); return jsonify({"user":u.to_dict()})
@app.route('/api/v1/users',methods=['GET'])
def users():
    u,e=req_user()
    if e: return e
    return jsonify({"users":[x.to_dict() for x in User.query.filter(User.id!=u.id).all()]})
@app.route('/api/v1/pages',methods=['GET','POST'])
def pages():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"pages":[x.to_dict() for x in Page.query.all()]})
    d=request.get_json(force=True); p=Page(user_id=u.id,name=d.get('name','My Page'),category=d.get('category','Page'))
    db.session.add(p); db.session.commit(); return jsonify({"page":p.to_dict()})
@app.route('/api/v1/monetization',methods=['GET','POST'])
def monet():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"balance":u.balance,"earnings":u.balance})
    d=request.get_json(force=True); amt=float(d.get('amount',0) or 0)
    if amt<=0 or amt>u.balance: return jsonify({"error":"invalid amount - رصيدك ما كافي"}),400
    u.balance-=amt; db.session.add(Payment(user_id=u.id,amount=amt,method=d.get('method','withdraw'),status='completed')); db.session.commit(); return jsonify({"balance":u.balance})
@app.route('/api/v1/gifts',methods=['GET','POST'])
def gifts():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"gifts":[x.to_dict() for x in Gift.query.filter_by(receiver_id=u.id).all()]})
    d=request.get_json(force=True); amt=float(d.get('amount',0) or 0); recv=int(d.get('receiver_id',0) or 0)
    if amt<=0 or amt>u.balance: return jsonify({"error":"insufficient balance"}),400
    r=User.query.get(recv)
    if not r: return jsonify({"error":"receiver not found"}),404
    u.balance-=amt; r.balance+=amt; db.session.add(Gift(sender_id=u.id,receiver_id=recv,amount=amt,message=d.get('message',''))); db.session.commit(); return jsonify({"ok":True,"balance":u.balance})
@app.route('/api/v1/ads',methods=['GET','POST'])
def ads():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"ads":[x.to_dict() for x in Ad.query.filter_by(user_id=u.id).all()]})
    d=request.get_json(force=True); a=Ad(user_id=u.id,title=d.get('title','Ad'),budget=float(d.get('budget',0) or 0)); db.session.add(a); db.session.commit(); return jsonify({"ad":a.to_dict()})
@app.route('/api/v1/support',methods=['GET','POST'])
def support():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"tickets":[x.to_dict() for x in Support.query.filter_by(user_id=u.id).all()]})
    d=request.get_json(force=True); s=Support(user_id=u.id,subject=d.get('subject',''),message=d.get('message','')); db.session.add(s); db.session.commit(); return jsonify({"ticket":s.to_dict()})
@app.route('/api/v1/links',methods=['GET','POST'])
def links():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"links":[x.to_dict() for x in Link.query.filter_by(user_id=u.id).all()]})
    d=request.get_json(force=True); l=Link(user_id=u.id,url=d.get('url',''),title=d.get('title','')); db.session.add(l); db.session.commit(); return jsonify({"link":l.to_dict()})
@app.route('/api/v1/payments',methods=['GET','POST'])
def payments():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"payments":[x.to_dict() for x in Payment.query.filter_by(user_id=u.id).all()]})
    d=request.get_json(force=True); amt=float(d.get('amount',0) or 0); p=Payment(user_id=u.id,amount=amt,method=d.get('method','')); db.session.add(p); u.balance+=amt; db.session.commit(); return jsonify({"payment":p.to_dict()})
@app.route('/api/v1/suggest',methods=['GET'])
def suggest():
    u,e=req_user()
    if e: return e
    return jsonify({"suggestions":[x.to_dict() for x in User.query.filter(User.id!=u.id).limit(10).all()]})
@app.route('/api/v1/diagnostics',methods=['GET'])
def diag():
    u,e=req_user()
    if e: return e
    return jsonify({"ok":True,"users":User.query.count(),"posts":Post.query.count(),"chats":Chat.query.count(),"time":now()})
@app.route('/api/v1/avatar',methods=['POST'])
def avatar():
    u,e=req_user()
    if e: return e
    d=request.get_json(force=True); u.avatar=d.get('avatar',''); db.session.commit(); return jsonify({"user":u.to_dict()})

# ===== Posts / Reels / Threads / Stories =====
@app.route('/api/v1/posts',methods=['GET','POST'])
def posts():
    u,e=req_user()
    if e: return e
    if request.method=='GET':
        out=[]
        for p in Post.query.order_by(Post.id.desc()).all():
            d=p.to_dict(); d['comments_list']=[c.to_dict() for c in Comment.query.filter_by(post_id=p.id).all()]; out.append(d)
        return jsonify({"posts":out})
    d=request.get_json(force=True); p=Post(user_id=u.id,user_name=u.name,text=d.get('text',''),image=d.get('image',''),video=d.get('video',''),link=d.get('link','')); db.session.add(p); db.session.commit(); return jsonify({"post":p.to_dict()})
@app.route('/api/v1/posts/<int:pid>/like',methods=['POST'])
def like(pid):
    u,e=req_user()
    if e: return e
    p=Post.query.get(pid)
    if not p: return jsonify({"error":"not found"}),404
    p.likes+=1; db.session.commit(); return jsonify({"likes":p.likes})
@app.route('/api/v1/posts/<int:pid>/share',methods=['POST'])
def share(pid):
    u,e=req_user()
    if e: return e
    p=Post.query.get(pid)
    if not p: return jsonify({"error":"not found"}),404
    p.shares+=1; db.session.commit(); return jsonify({"shares":p.shares})
@app.route('/api/v1/posts/<int:pid>/comments',methods=['GET','POST'])
def comments(pid):
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"comments":[c.to_dict() for c in Comment.query.filter_by(post_id=pid).all()]})
    d=request.get_json(force=True); c=Comment(post_id=pid,user_id=u.id,user_name=u.name,text=d.get('text','')); db.session.add(c)
    p=Post.query.get(pid)
    if p: p.comments+=1
    db.session.commit(); return jsonify({"comment":c.to_dict()})
@app.route('/api/v1/reels',methods=['GET','POST'])
def reels():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"reels":[x.to_dict() for x in Reel.query.order_by(Reel.id.desc()).all()]})
    d=request.get_json(force=True); r=Reel(user_id=u.id,user_name=u.name,video=d.get('video',''),caption=d.get('caption','')); db.session.add(r); db.session.commit(); return jsonify({"reel":r.to_dict()})
@app.route('/api/v1/threads',methods=['GET','POST'])
def threads():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"threads":[x.to_dict() for x in Thread.query.order_by(Thread.id.desc()).all()]})
    d=request.get_json(force=True); t=Thread(user_id=u.id,user_name=u.name,text=d.get('text','')); db.session.add(t); db.session.commit(); return jsonify({"thread":t.to_dict()})
@app.route('/api/v1/stories',methods=['GET','POST'])
def stories():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"stories":[x.to_dict() for x in Story.query.order_by(Story.id.desc()).all()]})
    d=request.get_json(force=True); s=Story(user_id=u.id,user_name=u.name,image=d.get('image','')); db.session.add(s); db.session.commit(); return jsonify({"story":s.to_dict()})

# ===== Friends / Chats - مصلح: ما بيعمل شات مكرر =====
@app.route('/api/v1/friends',methods=['GET','POST'])
def friends():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"friends":[x.to_dict() for x in Friend.query.filter_by(user_id=u.id).all()]})
    d=request.get_json(force=True); fid=int(d.get('friend_id',0) or 0); f=User.query.get(fid)
    if not f: return jsonify({"error":"user not found"}),404
    if Friend.query.filter_by(user_id=u.id,friend_id=fid).first(): return jsonify({"ok":True})
    db.session.add(Friend(user_id=u.id,friend_id=fid,friend_name=f.name)); db.session.add(Friend(user_id=fid,friend_id=u.id,friend_name=u.name)); db.session.commit(); return jsonify({"ok":True})
@app.route('/api/v1/chats',methods=['GET','POST'])
def chats():
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"chats":[x.to_dict() for x in Chat.query.filter((Chat.user1==u.id)|(Chat.user2==u.id)).all()]})
    d=request.get_json(force=True); other=int(d.get('user_id',0) or d.get('friend_id',0) or 0); o=User.query.get(other)
    if not o: return jsonify({"error":"user not found"}),404
    ex=Chat.query.filter(((Chat.user1==u.id)&(Chat.user2==other))|((Chat.user1==other)&(Chat.user2==u.id))).first()
    if ex: return jsonify({"chat":ex.to_dict()})
    c=Chat(user1=u.id,user2=other,name=o.name); db.session.add(c); db.session.commit(); return jsonify({"chat":c.to_dict()})
@app.route('/api/v1/chats/<int:cid>/messages',methods=['GET','POST'])
def msgs(cid):
    u,e=req_user()
    if e: return e
    if request.method=='GET': return jsonify({"messages":[x.to_dict() for x in Message.query.filter_by(chat_id=cid).all()]})
    d=request.get_json(force=True); m=Message(chat_id=cid,sender_id=u.id,sender_name=u.name,text=d.get('text',''),image=d.get('image','')); db.session.add(m)
    ch=Chat.query.get(cid)
    if ch: ch.last_msg=d.get('text','')
    db.session.commit(); return jsonify({"message":m.to_dict()})

# ===== Frontend - HTML + JS كامل مصلح =====
@app.route('/')
def index(): return HTML_PAGE
HTML_PAGE = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>B-2048</title><style>*{box-sizing:border-box}body{margin:0;font-family:system-ui;background:#0b1220;color:#fff}input,textarea{width:100%;padding:12px;border-radius:12px;border:1px solid #334155;background:#0f172a;color:#fff;margin:6px 0}button{padding:11px 14px;border:0;border-radius:12px;background:#1877f2;color:#fff;font-weight:700;cursor:pointer}.card{background:#111c33;border:1px solid #26314d;border-radius:16px;padding:14px;margin:10px}.top{position:sticky;top:0;background:#0b1220;padding:12px;display:flex;gap:8px;align-items:center}.tabs{display:flex;gap:6px;overflow:auto;padding:0 10px}.tabs button{background:#1e293b}.tabs button.on{background:#1877f2}.hidden{display:none}.post img{max-width:100%;border-radius:12px}.row{display:flex;gap:8px;align-items:center}.avatar{width:42px;height:42px;border-radius:50%;background:#334155;display:flex;align-items:center;justify-content:center;font-weight:800;overflow:hidden}.pill{background:#1e293b;padding:6px 10px;border-radius:20px;font-size:13px}</style></head><body>
<div id="authScreen"><div class="card" style="max-width:420px;margin:30px auto"><h1 style="text-align:center">B-2048 🌐</h1><p style="text-align:center;opacity:.8">فيسبوك + واتساب + ثريدز في تطبيق واحد</p><div id="loginCard"><input id="loginEmail" placeholder="الإيميل"><input id="loginPass" type="password" placeholder="كلمة السر"><button onclick="doLogin()" style="width:100%">دخول</button><button onclick="document.getElementById('loginCard').classList.add('hidden');document.getElementById('registerCard').classList.remove('hidden')" style="width:100%;background:#22c55e;margin-top:8px">إنشاء حساب جديد</button></div><div id="registerCard" class="hidden"><input id="regName" placeholder="الاسم"><input id="regEmail" placeholder="الإيميل"><input id="regPass" type="password" placeholder="كلمة السر"><button onclick="doRegister()" style="width:100%;background:#22c55e">تسجيل</button><button onclick="document.getElementById('registerCard').classList.add('hidden');document.getElementById('loginCard').classList.remove('hidden')" style="width:100%;background:#475569;margin-top:8px">عندي حساب</button></div><p id="authMsg" style="text-align:center;color:#fda4af"></p></div></div>
<div id="appScreen" class="hidden"><div class="top"><div class="avatar" id="myAvatar">B</div><b id="myName">User</b><span class="pill" id="myBalance">💰 0</span><button onclick="logout()" style="margin-inline-start:auto;background:#ef4444">خروج</button></div><div class="tabs" id="tabs"></div>
<div id="view-home"><div class="card"><textarea id="postText" placeholder="شنو في بالك؟"></textarea><input id="postImage" placeholder="رابط صورة (اختياري)"><input id="postLink" placeholder="رابط (اختياري)"><button onclick="createPost()">نشر 📝</button> <button onclick="togglePlus()" style="background:#22c55e">+ إضافة</button></div><div id="plusMenu" class="card hidden"><button onclick="addImage()">🖼️ صورة</button><button onclick="makeImage()">✨ توليد صورة</button><button onclick="previewLink()">🔗 معاينة رابط</button><button onclick="show('reels')">🎬 ريلز</button><button onclick="show('threads')">🧵 ثريدز</button></div><div id="stories"></div><div id="posts"></div></div>
<div id="view-reels" class="hidden"><div class="card"><input id="reelVideo" placeholder="رابط فيديو"><input id="reelCaption" placeholder="وصف الريلز"><button onclick="createReel()">نشر ريلز 🎬</button></div><div id="reels"></div></div>
<div id="view-threads" class="hidden"><div class="card"><textarea id="threadText" placeholder="اكتب ثريد..."></textarea><button onclick="createThread()">نشر ثريد 🧵</button></div><div id="threads"></div></div>
<div id="view-chats" class="hidden"><div class="card"><h3>💬 محادثاتي</h3><div id="chats"></div></div><div class="card"><h3>👥 كل المستخدمين</h3><div id="allUsers"></div></div><div class="card hidden" id="chatBox"><h3 id="chatTitle">محادثة</h3><div id="messages" style="max-height:300px;overflow:auto"></div><div class="row"><input id="msgText" placeholder="اكتب رسالة..."><button onclick="sendMsg()">إرسال</button></div></div></div>
<div id="view-friends" class="hidden"><div class="card"><h3>👥 أصدقائي</h3><div id="friends"></div></div><div class="card"><h3>✨ اقتراحات</h3><div id="suggest"></div></div></div>
<div id="view-profile" class="hidden"><div class="card"><input id="pName" placeholder="الاسم"><input id="pBio" placeholder="النبذة"><input id="pAvatar" placeholder="رابط الصورة"><input id="pPhone" placeholder="الهاتف"><button onclick="saveProfile()">حفظ الملف الشخصي ✅</button></div><div class="card"><h3>📄 صفحاتي</h3><input id="pageName" placeholder="اسم الصفحة"><button onclick="createPage()">إنشاء صفحة</button><div id="pages"></div></div></div>
<div id="view-money" class="hidden"><div class="card"><h3>💰 محفظتي</h3><p id="moneyBalance"></p><input id="payAmount" type="number" placeholder="المبلغ"><input id="payMethod" placeholder="الطريقة - زين / بنكك"><button onclick="addPayment()">شحن 💳</button><button onclick="withdraw()" style="background:#f59e0b">سحب</button></div><div class="card"><h3>🎁 إرسال هدية</h3><input id="giftTo" placeholder="ID المستلم"><input id="giftAmount" type="number" placeholder="المبلغ"><button onclick="sendGift()">إرسال هدية</button></div><div id="payments"></div></div>
<div id="view-ads" class="hidden"><div class="card"><h3>📢 إعلاناتي</h3><input id="adTitle" placeholder="عنوان الإعلان"><input id="adBudget" type="number" placeholder="الميزانية"><button onclick="createAd()">إنشاء إعلان</button><div id="ads"></div></div></div>
<div id="view-support" class="hidden"><div class="card"><h3>🛟 الدعم</h3><input id="supSubject" placeholder="الموضوع"><textarea id="supMsg" placeholder="رسالتك"></textarea><button onclick="sendSupport()">إرسال</button><div id="supports"></div></div></div>
<div id="view-links" class="hidden"><div class="card"><h3>🔗 روابطي</h3><input id="linkUrl" placeholder="الرابط"><input id="linkTitle" placeholder="العنوان"><button onclick="saveLink()">حفظ رابط</button><div id="links"></div></div></div>
<div id="view-menu" class="hidden"><div class="card"><h3>☰ القائمة - الإعدادات / الخصوصية / الأجهزة / زين / واتساب / Free Basics</h3><button onclick="loadDiagnostics()">🔍 تشخيص النظام</button><div id="diag"></div></div></div></div>
<script>
const API=location.origin+'/api/v1'; let ME=null, CUR_CHAT=null;
function hdr(){return {'Content-Type':'application/json','X-User-Id':ME?ME.id:''}}
async function api(p,m='GET',b=null){let r=await fetch(API+p,{method:m,headers:hdr(),body:b?JSON.stringify(b):null}); return r.json()}
async function doRegister(){let d=await api('/register','POST',{name:regName.value,email:regEmail.value,password:regPass.value}); if(d.error){authMsg.innerText=d.error;return} ME=d.user; enter()}
async function doLogin(){let d=await api('/login','POST',{email:loginEmail.value,password:loginPass.value}); if(d.error){authMsg.innerText=d.error;return} ME=d.user; enter()}
function logout(){ME=null; authScreen.classList.remove('hidden'); appScreen.classList.add('hidden')}
function enter(){authScreen.classList.add('hidden'); appScreen.classList.remove('hidden'); myName.innerText=ME.name; myBalance.innerText='💰 '+(ME.balance||0); buildTabs(); show('home'); loadAll()}
function buildTabs(){let t=[['home','🏠 الرئيسية'],['reels','🎬 ريلز'],['threads','🧵 ثريدز'],['chats','💬 محادثات'],['friends','👥 أصدقاء'],['profile','👤 بروفايل'],['money','💰 أموال'],['ads','📢 إعلانات'],['support','🛟 دعم'],['links','🔗 روابط'],['menu','☰ قائمة']]; tabs.innerHTML=t.map(x=>'<button onclick="show(\\''+x[0]+'\\')" id="tab-'+x[0]+'">'+x[1]+'</button>').join('')}
function show(v){document.querySelectorAll('[id^="view-"]').forEach(e=>e.classList.add('hidden')); let el=document.getElementById('view-'+v); if(el) el.classList.remove('hidden'); document.querySelectorAll('.tabs button').forEach(b=>b.classList.remove('on')); let tb=document.getElementById('tab-'+v); if(tb) tb.classList.add('on'); if(v=='chats') loadChats(); if(v=='friends') loadFriends(); if(v=='money') loadPayments(); if(v=='profile') loadPages(); if(v=='ads') loadAds(); if(v=='support') loadSupport(); if(v=='links') loadLinks()}
function togglePlus(){plusMenu.classList.toggle('hidden')}
function previewLink(){let l=postLink.value; if(!l) return alert('اكتب رابط'); postText.value+='\\n🔗 '+l}
function addImage(){let u=prompt('رابط الصورة:'); if(u) postImage.value=u}
function makeImage(){postImage.value='https://picsum.photos/600/400?random='+Math.floor(Math.random()*1000)}
async function loadAll(){let d=await api('/posts'); posts.innerHTML=(d.posts||[]).map(p=>'<div class="card post"><div class="row"><div class="avatar">'+(p.user_name||'U')[0]+'</div><b>'+p.user_name+'</b></div><p>'+(p.text||'')+'</p>'+(p.image?'<img src="'+p.image+'">':'')+(p.link?'<a href="'+p.link+'" target="_blank">'+p.link+'</a>':'')+'<div class="row"><button onclick="toggleLike('+p.id+')">❤️ '+p.likes+'</button><button onclick="toggleComments('+p.id+')">💬 '+p.comments+'</button><button onclick="sharePost('+p.id+')">↗️ '+p.shares+'</button></div><div id="c-'+p.id+'" class="hidden"><input id="ci-'+p.id+'" placeholder="اكتب تعليق..."><button onclick="addComment('+p.id+')">تعليق</button><div>'+(p.comments_list||[]).map(c=>'<p><b>'+c.user_name+':</b> '+c.text+'</p>').join('')+'</div></div></div>').join('')||'<div class="card">لا توجد منشورات بعد</div>'; let s=await api('/stories'); stories.innerHTML='<div class="card">📖 ستوريز: '+(s.stories||[]).length+'</div>'; let r=await api('/reels'); reels.innerHTML=(r.reels||[]).map(x=>'<div class="card">🎬 '+x.user_name+' - '+(x.caption||'')+'</div>').join(''); let th=await api('/threads'); threads.innerHTML=(th.threads||[]).map(x=>'<div class="card">🧵 <b>'+x.user_name+'</b><p>'+x.text+'</p></div>').join('')}
function renderAll(){loadAll()}
async function createPost(){await api('/posts','POST',{text:postText.value,image:postImage.value,link:postLink.value}); postText.value=''; postImage.value=''; postLink.value=''; loadAll()}
async function createThread(){await api('/threads','POST',{text:threadText.value}); threadText.value=''; loadAll()}
async function createReel(){await api('/reels','POST',{video:reelVideo.value,caption:reelCaption.value}); reelVideo.value=''; reelCaption.value=''; loadAll()}
function toggleComments(id){document.getElementById('c-'+id).classList.toggle('hidden')}
async function addComment(id){let v=document.getElementById('ci-'+id).value; if(!v) return; await api('/posts/'+id+'/comments','POST',{text:v}); loadAll()}
async function toggleLike(id){await api('/posts/'+id+'/like','POST',{}); loadAll()}
async function sharePost(id){await api('/posts/'+id+'/share','POST',{}); loadAll()}
async function loadFriends(){let d=await api('/friends'); friends.innerHTML=(d.friends||[]).map(f=>'<p>👤 '+f.friend_name+'</p>').join('')||'لا أصدقاء بعد'; let s=await api('/suggest'); suggest.innerHTML=(s.suggestions||[]).map(u=>'<div class="row"><span>'+u.name+'</span><button onclick="addFriend('+u.id+')">+ إضافة</button><button onclick="openChat('+u.id+',\\''+u.name+'\\')" style="background:#22c55e">💬 محادثة</button></div>').join('')}
async function addFriend(id){await api('/friends','POST',{friend_id:id}); loadFriends()}
async function loadChats(){let d=await api('/chats'); chats.innerHTML=(d.chats||[]).map(c=>'<div class="card" onclick="openChatById('+c.id+',\\''+c.name+'\\')">💬 '+c.name+' - '+(c.last_msg||'')+'</div>').join('')||'لا محادثات'; let u=await api('/users'); allUsers.innerHTML=(u.users||[]).map(x=>'<div class="row"><span>'+x.name+'</span><button onclick="openChat('+x.id+',\\''+x.name+'\\')">💬</button></div>').join('')}
async function openChat(uid,name){let d=await api('/chats','POST',{user_id:uid}); if(d.chat) openChatById(d.chat.id,name)}
function openChatById(id,name){CUR_CHAT=id; chatBox.classList.remove('hidden'); chatTitle.innerText='💬 '+name; loadMessages()}
async function loadMessages(){if(!CUR_CHAT) return; let d=await api('/chats/'+CUR_CHAT+'/messages'); messages.innerHTML=(d.messages||[]).map(m=>'<p><b>'+m.sender_name+':</b> '+m.text+'</p>').join('')}
async function sendMsg(){if(!CUR_CHAT) return alert('اختر محادثة'); let t=msgText.value; if(!t) return; await api('/chats/'+CUR_CHAT+'/messages','POST',{text:t}); msgText.value=''; loadMessages()}
async function saveProfile(){let d=await api('/profile','POST',{name:pName.value,bio:pBio.value,avatar:pAvatar.value,phone:pPhone.value}); if(d.user){ME=d.user; myName.innerText=ME.name; alert('تم الحفظ ✅')}}
async function loadPages(){let d=await api('/pages'); pages.innerHTML=(d.pages||[]).map(p=>'<p>📄 '+p.name+'</p>').join('')}
async function createPage(){await api('/pages','POST',{name:pageName.value}); pageName.value=''; loadPages()}
async function loadPayments(){let d=await api('/payments'); payments.innerHTML=(d.payments||[]).map(p=>'<div class="card">💳 '+p.amount+' - '+p.method+'</div>').join(''); let m=await api('/monetization'); moneyBalance.innerText='رصيدك: '+(m.balance||0)}
async function addPayment(){await api('/payments','POST',{amount:payAmount.value,method:payMethod.value}); loadPayments()}
async function withdraw(){let d=await api('/monetization','POST',{amount:payAmount.value,method:payMethod.value}); if(d.error) alert(d.error); else alert('تم السحب ✅'); loadPayments()}
async function sendGift(){let d=await api('/gifts','POST',{receiver_id:giftTo.value,amount:giftAmount.value}); if(d.error) alert(d.error); else alert('تم إرسال الهدية 🎁')}
async function loadAds(){let d=await api('/ads'); ads.innerHTML=(d.ads||[]).map(a=>'<p>📢 '+a.title+' - '+a.budget+'</p>').join('')}
async function createAd(){await api('/ads','POST',{title:adTitle.value,budget:adBudget.value}); loadAds()}
async function loadSupport(){let d=await api('/support'); supports.innerHTML=(d.tickets||[]).map(s=>'<p>🛟 '+s.subject+' - '+s.status+'</p>').join('')}
async function sendSupport(){await api('/support','POST',{subject:supSubject.value,message:supMsg.value}); loadSupport()}
async function loadLinks(){let d=await api('/links'); links.innerHTML=(d.links||[]).map(l=>'<p>🔗 <a href="'+l.url+'" target="_blank">'+l.title+'</a></p>').join('')}
async function saveLink(){await api('/links','POST',{url:linkUrl.value,title:linkTitle.value}); loadLinks()}
async function loadDiagnostics(){let d=await api('/diagnostics'); diag.innerHTML='<p>✅ النظام شغال - مستخدمين: '+d.users+' - منشورات: '+d.posts+'</p>'}
</script></body></html>"""

if __name__=='__main__':
    port=int(os.environ.get('PORT',5000)); app.run(host='0.0.0.0',port=port)
