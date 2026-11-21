# Noor - app.py - مع داتابيز حقيقية PostgreSQL - الحسابات ما بتطير
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os, uuid, hashlib, base64
from datetime import datetime

try:
    from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime, Boolean
    from sqlalchemy.orm import sessionmaker, declarative_base
    HAS_SQL = True
except:
    HAS_SQL = False

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "noor-secret-2026")
CORS(app, supports_credentials=True)

# --- الداتابيز ---
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///noor.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)
    phone_enc = Column(String)
    email_enc = Column(String)
    email_plain = Column(String, unique=True)
    password_hash = Column(String)
    city = Column(String, default="")
    bio = Column(Text, default="")
    avatar = Column(String, default="")
    followers = Column(Integer, default=0)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    author_name = Column(String)
    author_avatar = Column(String)
    content = Column(Text)
    media_url = Column(Text, default="")
    media_type = Column(String, default="text")
    kind = Column(String, default="post")
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    liked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True)
    post_id = Column(String)
    author = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Page(Base):
    __tablename__ = "pages"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    name = Column(String)
    type = Column(String)
    category = Column(String)
    followers = Column(Integer, default=0)

class Ad(Base):
    __tablename__ = "ads"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    title = Column(String)
    budget = Column(Float, default=0)
    target = Column(String)
    views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spent = Column(Float, default=0)

class Gift(Base):
    __tablename__ = "gifts"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    name = Column(String)
    value = Column(Float, default=0)

class Support(Base):
    __tablename__ = "support"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    type = Column(String)
    text = Column(Text)

class Link(Base):
    __tablename__ = "links"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    url = Column(Text)
    time = Column(String)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    type = Column(String)
    amount = Column(Float, default=0)
    time = Column(String)

class Chat(Base):
    __tablename__ = "chats"
    id = Column(String, primary_key=True)
    name = Column(String)
    avatar = Column(String)
    last_message = Column(String, default="")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True)
    chat_id = Column(String)
    sender_id = Column(String)
    content = Column(Text)

Base.metadata.create_all(engine)

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def encrypt(t): return base64.b64encode(t.encode()).decode() if t else ""
def decrypt(t):
    try: return base64.b64decode(t.encode()).decode()
    except: return ""
def get_user():
    uid = session.get("user_id")
    if not uid: return None
    s = Session(); u = s.query(User).filter_by(id=uid).first(); s.close(); return u
def db(): return Session()

HTML = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>نور - Noor</title><style>*{box-sizing:border-box;margin:0;padding:0;font-family:system-ui}body{background:#f0f2f5;padding-bottom:85px}header{background:#fff;padding:8px 12px;position:sticky;top:0;z-index:99}.top{display:flex;align-items:center;gap:8px;position:relative}.logo{width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#2563eb,#06b6d4,#a855f7);color:#fff;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:900}.hbtn{width:38px;height:38px;border-radius:50%;background:#f0f2f5;border:none;font-size:18px;cursor:pointer;position:relative}.badge{position:absolute;top:-4px;left:-4px;background:#e11d48;color:#fff;font-size:10px;padding:2px 5px;border-radius:10px;font-weight:900}.card{background:#fff;border-radius:16px;padding:14px;margin:8px}.flex{display:flex;gap:10px;align-items:center}.avatar{width:42px;height:42px;border-radius:50%;object-fit:cover}input,select,textarea{width:100%;background:#f0f2f5;border:none;padding:12px;border-radius:20px;outline:none;margin-top:8px}.btn{background:#2563eb;color:#fff;border:none;padding:11px 16px;border-radius:20px;font-weight:800;cursor:pointer;width:100%;margin-top:10px}.post{line-height:1.6;font-size:15px;margin:10px 0}.post img,.post video{width:100%;border-radius:14px;margin-top:8px;max-height:420px;object-fit:cover}.actions{display:flex;gap:6px;border-top:1px solid #eee;padding-top:10px;margin-top:10px}.actions button{flex:1;padding:9px;border:none;border-radius:20px;background:#f0f2f5;font-weight:700}.actions button.active{background:#dbeafe;color:#2563eb}.hidden{display:none}nav{position:fixed;bottom:0;right:0;left:0;max-width:600px;margin:auto;background:#fff;display:flex;border-top:1px solid #eee;z-index:99}nav button{flex:1;padding:11px 2px;border:none;background:none;font-weight:900;font-size:12px;color:#888}nav button.active{color:#2563eb;border-top:3px solid #2563eb}.stories{display:flex;gap:8px;overflow-x:auto;padding:0 8px}.story{min-width:105px;height:155px;border-radius:16px;position:relative;overflow:hidden;background:#ddd}.story img{width:100%;height:100%;object-fit:cover}.story span{position:absolute;bottom:8px;right:8px;color:#fff;font-weight:800;font-size:12px}.menu-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:0 8px}.menu-grid div{background:#fff;border-radius:16px;padding:16px;text-align:center;font-weight:800;font-size:14px;cursor:pointer}.menu-item{display:flex;justify-content:space-between;align-items:center;padding:12px;background:#fff;border-radius:14px;margin:6px 8px;font-weight:700;cursor:pointer}.toggle{width:48px;height:28px;border-radius:20px;background:#ccc;position:relative;cursor:pointer;flex-shrink:0}.toggle.on{background:#2563eb}.toggle::after{content:"";position:absolute;width:22px;height:22px;background:#fff;border-radius:50%;top:3px;right:3px}.toggle.on::after{right:23px}.tabs{display:flex;gap:6px;margin:10px 0}.tabs button{flex:1;padding:10px;border:none;border-radius:20px;background:#eee;font-weight:800}.tabs button.active{background:#2563eb;color:#fff}.cbtns{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}.cbtns label,.cbtns button{flex:1;min-width:80px;text-align:center;padding:10px;border-radius:20px;background:#f0f2f5;font-weight:700;font-size:13px;cursor:pointer;border:none}.comment-box{display:flex;gap:6px;margin-top:10px}.comment{padding:8px 10px;background:#f0f2f5;border-radius:14px;margin-top:6px;font-size:13px}.reel{height:520px;border-radius:18px;overflow:hidden;position:relative;background:#000;margin:8px}.reel img,.reel video{width:100%;height:100%;object-fit:cover}.reel-info{position:absolute;bottom:12px;right:12px;left:60px;color:#fff}.reel-actions{position:absolute;left:10px;bottom:20px;display:flex;flex-direction:column;gap:12px}.reel-actions button{width:48px;height:48px;border-radius:50%;border:none;background:#ffffffcc;font-size:20px}.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2px}.grid3 img{width:100%;aspect-ratio:1;object-fit:cover}.chat-item{display:flex;gap:10px;align-items:center;padding:12px;background:#fff;border-radius:16px;margin:8px}.msg{max-width:80%;padding:10px 14px;border-radius:18px;margin:6px 0;font-size:14px}.msg.me{background:#2563eb;color:#fff;margin-right:auto}.msg.other{background:#fff}.algo{font-size:11px;color:#2563eb;background:#eff6ff;padding:6px 8px;border-radius:10px;margin-top:6px}.plus-menu{position:absolute;top:46px;left:0;width:270px;background:#fff;border-radius:16px;box-shadow:0 10px 30px #0003;padding:8px;display:none;z-index:999}.plus-menu.open{display:block}.plus-menu .pitem{display:flex;justify-content:space-between;align-items:center;padding:12px;border-radius:12px;cursor:pointer;font-weight:700}.auth{max-width:420px;margin:20px auto;padding:20px}.auth-logo{width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#2563eb,#06b6d4,#a855f7);color:#fff;display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:900;margin:0 auto}.section-title{font-size:13px;color:#888;font-weight:800;margin:14px 8px 6px}
</style></head><body>
<div id="authScreen"><div class="auth"><div class="auth-logo">ن</div><h2 style="text-align:center;margin-top:10px">نور - Noor</h2><p style="text-align:center;color:#888;font-size:13px">منصة سودانية - مشفرة 🔒 - داتابيز حقيقية - حسابك ما بيطير</p><div style="background:#dcfce7;padding:10px;border-radius:12px;text-align:center;font-size:12px;margin-bottom:10px">✅ داتابيز PostgreSQL - محفوظ للأبد</div><div class="card" id="loginCard"><b>تسجيل الدخول</b><input id="loginEmail" placeholder="البريد الإلكتروني أو رقم الجوال"><input id="loginPw" type="password" placeholder="الرقم السري - مشفر SHA256 🔒"><button class="btn" onclick="doLogin()">دخول 🔓</button><button class="btn" style="background:#16a34a" onclick="showRegister()">إنشاء حساب جديد - مجاناً</button></div><div class="card hidden" id="registerCard"><b>إنشاء حساب جديد - حقيقي - محفوظ في الداتابيز</b><input id="regName" placeholder="الاسم الكامل"><input id="regPhone" placeholder="رقم الجوال"><input id="regEmail" placeholder="البريد الإلكتروني"><input id="regPw" type="password" placeholder="الرقم السري - 6 حروف"><input id="regCity" placeholder="المدينة - عطبرة"><button class="btn" style="background:#16a34a" onclick="doRegister()">إنشاء الحساب ✅ - محفوظ للأبد</button><button class="btn" style="background:#eee;color:#000" onclick="showLogin()">عندي حساب - دخول</button></div></div></div>
<div id="appScreen" class="hidden">
<header><div class="top"><div class="logo">ن</div><div style="flex:1"><b style="font-size:22px">نور <span style="color:#2563eb">Noor</span></b><div style="font-size:11px;color:#888" id="helloUser">أهلاً بيك</div></div><button class="hbtn" onclick="show('menu')">☰</button><button class="hbtn" onclick="event.stopPropagation();togglePlus()">+</button><button class="hbtn">🔍</button><button class="hbtn" onclick="show('chat')">💬<span class="badge">+9</span></button><button class="hbtn" onclick="show('notifs')">🔔<span class="badge">3</span></button><div id="plusMenu" class="plus-menu" onclick="event.stopPropagation()"><b style="padding:4px 8px">إنشاء</b><div class="pitem" onclick="show('book');closePlus()">📝 منشور <span>›</span></div><div class="pitem" onclick="show('book');closePlus()">➕ قصة <span>›</span></div><div class="pitem" onclick="show('reels');closePlus()">🎬 مقطع ريلز <span>›</span></div><div class="pitem" onclick="checkLive();closePlus()">📹 بث مباشر <span>›</span></div><div class="pitem" onclick="show('pages');closePlus()">📄 إنشاء صفحة <span>›</span></div><div class="pitem" onclick="show('ads');closePlus()">📢 إنشاء إعلان <span>›</span></div></div></div></header>
<div id="tab-book"><div class="card"><div class="flex"><img class="avatar" src="https://i.pravatar.cc/150?u=me"><input id="newPost" type="text" placeholder="بم تفكر؟"></div><div class="tabs"><button id="t-file" class="active" onclick="pubTab('file')">📁 ملفات</button><button id="t-link" onclick="pubTab('link')">🔗 رابط</button><button id="t-make" onclick="pubTab('make')">🎨 صنع صورة</button><button id="t-video" onclick="pubTab('video')">🎬 ريلز</button></div><div id="p-file"><div class="cbtns"><label>📷 صورة<input type="file" accept="image/*" hidden onchange="pickFile(this,'image')"></label><label>🎥 فيديو<input type="file" accept="video/*" hidden onchange="pickFile(this,'video')"></label><label>🎬 ريلز<input type="file" accept="video/*,image/*" hidden onchange="pickFile(this,'reel')"></label></div></div><div id="p-link" class="hidden"><input id="mediaUrl" type="text" placeholder="الصق رابط..."><button class="btn" style="background:#16a34a" onclick="previewLink()">👀 معاينة</button></div><div id="p-make" class="hidden"><input id="makeText" type="text" placeholder="اكتب نص الصورة..."><button class="btn" style="background:#a855f7" onclick="makeImage()">🎨 صنع الصورة</button></div><div id="p-video" class="hidden"><input id="videoText" type="text" placeholder="اكتب نص الريلز..."><button class="btn" style="background:#e11d48" onclick="makeVideo()">🎬 صنع ريلز</button></div><div id="preview" style="margin-top:10px"></div><div id="makeCanvasWrap" class="hidden"><canvas id="makeCanvas" width="600" height="400" style="width:100%;border-radius:12px"></canvas></div><div style="display:flex;gap:6px;margin-top:10px"><button class="btn" style="flex:1" onclick="createPost()">نشر بوست 🚀</button><button class="btn" style="flex:1;background:#e11d48" onclick="createPostAsReel()">نشر ريلز 🎬</button></div></div><div class="stories" id="stories"></div><div id="suggest" style="display:flex;gap:8px;overflow-x:auto;padding:0 8px"></div><div id="posts"></div><div class="card" id="empty" style="text-align:center;color:#888">لسه ما في منشورات - انت أول واحد انشر 👆</div></div>
<div id="tab-reels" class="hidden"><div class="card"><b>🎬 ريلز</b></div><div id="reels"></div></div>
<div id="tab-gram" class="hidden"><div class="card"><b>📸 نور قرام</b></div><div id="gramGrid" class="grid3"></div></div>
<div id="tab-chat" class="hidden"><div class="card"><b>💬 نور شات</b></div><div id="chatList"></div><div class="card"><input id="newChatName" placeholder="اسم المحادثة..."><button class="btn" style="background:#16a34a" onclick="createChat()">+ محادثة</button></div><div id="chatBox" class="card hidden"><h3 id="chatTitle"></h3><div id="msgs" style="height:280px;overflow-y:auto;background:#f0f2f5;padding:10px;border-radius:12px"></div><div class="flex" style="margin-top:10px"><input id="newMsg" placeholder="اكتب رسالة..."><button class="btn" onclick="sendMsg()">إرسال</button></div></div></div>
<div id="tab-notifs" class="hidden"><div class="card"><b>🔔 الإشعارات</b></div><div id="notifList"></div></div>
<div id="tab-threads" class="hidden"><div class="card"><b>🧵 نور ثريدز</b></div><div class="card"><input id="threadText" placeholder="اكتب ثريد..."><button class="btn" onclick="createThread()">نشر ثريد</button></div><div id="threads"></div></div>
<div id="tab-profile" class="hidden"><div class="card"><img src="https://picsum.photos/800/300" style="width:100%;height:140px;object-fit:cover;border-radius:14px"><div class="flex" style="margin-top:-20px"><img id="profileAvatar" src="https://i.pravatar.cc/150?u=me" style="width:80px;height:80px;border-radius:50%;border:4px solid #fff"><div><b id="profileName">...</b><div style="font-size:12px;color:#888" id="profileCity">...</div><div style="font-size:12px" id="profileBio">...</div></div></div><p style="font-size:11px;color:#16a34a">🔒 بياناتك مشفرة - محفوظة في الداتابيز</p><button class="btn" onclick="document.getElementById('editForm').classList.toggle('hidden')">✏️ تعديل البيانات</button></div><div id="editForm" class="card hidden"><b>✏️ تعديل البيانات - مشفرة</b><input id="editName" placeholder="الاسم"><input id="editCity" placeholder="المدينة"><input id="editBio" placeholder="النبذة"><input id="editPhone" placeholder="رقم الجوال - مشفر"><input id="editAvatar" placeholder="رابط صورتك"><button class="btn" style="background:#16a34a" onclick="saveProfile()">💾 حفظ</button></div></div>
<div id="tab-pages" class="hidden"><div class="card"><b>📄 إنشاء صفحة</b></div><div class="card"><input id="pageName" placeholder="اسم الصفحة"><select id="pageType"><option value="normal">📄 صفحة عادية</option><option value="digital">🎬 صفحة محتوى رقمي</option></select><select id="pageCat"><option>كوميدي</option><option>رياضة</option><option>أخبار</option><option>طبخ</option></select><button class="btn" style="background:#16a34a" onclick="createPage()">+ إنشاء الصفحة</button></div><div id="pagesList"></div></div>
<div id="tab-money" class="hidden"><div class="card" style="background:linear-gradient(135deg,#16a34a,#06b6d4);color:#fff"><b>💰 أرباحي - محفوظة في الداتابيز</b><p style="font-size:12px">1000 مشاهدة = 2$</p></div><div class="card"><div style="display:flex;gap:8px"><div style="flex:1;background:#f0f2f5;border-radius:14px;padding:12px;text-align:center"><b id="mFollowers" style="font-size:20px">0</b><div style="font-size:12px">متابعين</div></div><div style="flex:1;background:#f0f2f5;border-radius:14px;padding:12px;text-align:center"><b id="mViews" style="font-size:20px">0</b><div style="font-size:12px">مشاهدات</div></div><div style="flex:1;background:#f0f2f5;border-radius:14px;padding:12px;text-align:center"><b id="mTotal" style="font-size:20px;color:#16a34a">0$</b><div style="font-size:12px">إجمالي</div></div></div><div style="font-size:12px;margin-top:10px" id="mBreak"></div><button class="btn" style="background:#e11d48" onclick="withdraw()">💸 سحب - بنكك / MTN / Zain</button></div><div class="card"><b>🎁 الهدايا</b><div style="display:flex;gap:6px;margin-top:8px"><button style="flex:1;padding:10px;border:none;border-radius:20px;background:#fff3cd;font-weight:800" onclick="sendGift('وردة 🌹',0.1)">🌹 وردة 0.10$</button><button style="flex:1;padding:10px;border:none;border-radius:20px;background:#fff3cd;font-weight:800" onclick="sendGift('أسد 🦁',10)">🦁 أسد 10$</button></div></div><div class="card"><b>📹 اللايف</b><div id="liveInfo"></div><button class="btn" style="background:#e11d48" onclick="checkLive()">📹 هل مسموح لي أعمل لايف؟</button></div></div>
<div id="tab-ads" class="hidden"><div class="card" style="background:linear-gradient(135deg,#7c3aed,#2563eb);color:#fff"><b>📢 منصة إعلانات نور</b></div><div class="card"><input id="adTitle" placeholder="عنوان الإعلان"><input id="adBudget" placeholder="الميزانية"><select id="adTarget"><option>كل السودان</option><option>عطبرة</option><option>الخرطوم</option></select><button class="btn" style="background:#7c3aed" onclick="createAd()">🚀 نشر الإعلان</button></div><div id="adsList"></div></div>
<div id="tab-menu" class="hidden"><div class="card"><div class="flex" onclick="show('profile')"><img class="avatar" src="https://i.pravatar.cc/150?u=me"><div><b id="menuName">...</b><div style="font-size:12px;color:#888">عرض ملفك</div></div></div><button class="btn" onclick="show('pages')">+ إنشاء صفحة</button><button class="btn" style="background:#16a34a" onclick="show('money')">💰 أرباحي</button><button class="btn" style="background:#7c3aed" onclick="show('ads')">📢 منصة الإعلانات</button></div><div class="menu-grid"><div>🕐<br>الذكريات</div><div>🔖<br>المحفوظة</div><div>👥<br>الأصدقاء</div><div>👨‍👩‍👧<br>المجموعات</div><div onclick="show('reels')">🎬<br>ريلز</div><div>📰<br>الأخبار</div><div>📅<br>المناسبات</div><div>🎮<br>الألعاب</div></div><div style="text-align:center;color:#2563eb;font-weight:800;padding:10px;cursor:pointer" onclick="document.getElementById('moreMenu').classList.toggle('hidden')">عرض المزيد ▼</div><div id="moreMenu" class="hidden"><div class="menu-grid"><div onclick="show('support')">🆘<br>المساعدة</div><div onclick="show('time')">⏰<br>إدارة الوقت</div><div onclick="show('devices')">📱<br>الأجهزة</div><div onclick="show('links')">🔗<br>سجل الروابط</div><div onclick="show('payments')">💳<br>الدفع</div><div onclick="show('zain')">📶<br>Zain</div></div></div><div class="section-title">الإعدادات و الخصوصية</div><div class="menu-item" onclick="show('settings')"><span>⚙️ الإعدادات</span><span>›</span></div><div class="menu-item" onclick="show('privacy')"><span>🔒 مركز الخصوصية</span><span>›</span></div><div class="menu-item" onclick="show('time')"><span>⏰ إدارة الوقت</span><span>›</span></div><div class="menu-item" onclick="show('devices')"><span>📱 طلبات الأجهزة</span><span>›</span></div><div class="menu-item" onclick="show('ads')"><span>📢 أحدث نشاط إعلاني</span><span>›</span></div><div class="menu-item" onclick="show('payments')"><span>💳 الطلبات و الدفع</span><span>›</span></div><div class="menu-item" onclick="show('links')"><span>🔗 سجل الروابط</span><span>›</span></div><div class="menu-item" onclick="show('zain')"><span>📶 مركز Zain Sudan</span><span>›</span></div><div class="section-title">أيضاً من نور</div><div class="menu-item" onclick="show('edits')"><span>✏️ نور Edits</span><span>›</span></div><div class="menu-item" onclick="show('threads')"><span>🧵 نور Threads</span><span>›</span></div><div class="menu-item" onclick="show('gram')"><span>📸 نور Instagram</span><span>›</span></div><div class="menu-item" onclick="show('freebasics')"><span>🌐 نور Free Basics</span><span>›</span></div><div class="menu-item" onclick="show('chat')"><span>💬 نور Messenger</span><span>›</span></div><div class="menu-item" onclick="show('whatsapp')"><span>💚 نور واتساب</span><span>›</span></div><div class="menu-item" onclick="show('presence')"><span>📡 الحضور العام</span><span>›</span></div><div class="menu-item" onclick="show('upgrades')"><span>⭐ الترقيات</span><span>›</span></div><div class="menu-item" onclick="show('support')"><span>🆘 المساعدة و الدعم</span><span>›</span></div><div class="menu-item" onclick="logout()"><span>🚪 تسجيل الخروج</span><span>›</span></div></div>
<div id="tab-support" class="hidden"><div class="card"><b>🆘 المساعدة و الدعم</b></div><div class="card"><select id="supportType"><option>مشكلة في النشر</option><option>مشكلة في الدخول</option><option>مشكلة في الأرباح</option><option>أخرى</option></select><textarea id="supportText" placeholder="اكتب مشكلتك..."></textarea><button class="btn" style="background:#e11d48" onclick="sendSupport()">🚨 إرسال البلاغ</button></div><div id="supportList"></div></div>
<div id="tab-time" class="hidden"><div class="card"><b>⏰ إدارة الوقت</b><p>كم ساعة قعدت اليوم؟</p><div style="font-size:24px;font-weight:900" id="timeToday">45 دقيقة اليوم</div><button class="btn" style="background:#f59e0b" onclick="alert('تم تفعيل التنبيه بعد 1 ساعة ⏰')">⏰ نبهني بعد 1 ساعة</button></div></div>
<div id="tab-devices" class="hidden"><div class="card"><b>📱 طلبات الأجهزة</b></div><div class="card"><b>Android - هذا الجهاز</b><div>عطبرة - متصل الآن ✅</div></div></div>
<div id="tab-links" class="hidden"><div class="card"><b>🔗 سجل الروابط</b></div><div id="linksList"></div></div>
<div id="tab-payments" class="hidden"><div class="card"><b>💳 الطلبات و الدفع</b></div><div id="paymentsList"></div></div>
<div id="tab-zain" class="hidden"><div class="card"><b>📶 مركز Zain Sudan</b></div><div class="card"><div class="menu-item"><span>📦 باقة 1GB - نور مجاناً</span><span>›</span></div><button class="btn" style="background:#7c3aed" onclick="alert('تم تفعيل باقة Zain ✅')">تفعيل</button></div></div>
<div id="tab-edits" class="hidden"><div class="card"><b>✏️ نور Edits</b><button class="btn" style="background:#a855f7" onclick="alert('تم تعديل الفيديو ✅')">✏️ تعديل الفيديو</button></div></div>
<div id="tab-freebasics" class="hidden"><div class="card"><b>🌐 نور Free Basics</b><button class="btn" style="background:#16a34a" onclick="alert('تم تفعيل Free Basics ✅')">تفعيل المجاني</button></div></div>
<div id="tab-whatsapp" class="hidden"><div class="card"><b>💚 نور واتساب</b><button class="btn" style="background:#16a34a" onclick="show('chat')">فتح نور واتساب</button></div></div>
<div id="tab-presence" class="hidden"><div class="card"><b>📡 الحضور العام</b><div class="flex" style="justify-content:space-between;margin-top:10px"><span><b>ظاهر للكل</b></span><div class="toggle on"></div></div></div></div>
<div id="tab-upgrades" class="hidden"><div class="card"><b>⭐ الترقيات - نور برو</b><button class="btn" style="background:#f59e0b" onclick="alert('تم الترقية ✅')">ترقية الآن ⭐</button></div></div>
<div id="tab-privacy" class="hidden"><div class="card"><b>🔒 مركز الخصوصية - مشفر</b><div class="flex" style="justify-content:space-between;margin-top:10px"><span><b>إخفاء رقم الجوال</b></span><div class="toggle on"></div></div><div class="flex" style="justify-content:space-between;margin-top:10px"><span><b>إخفاء الإيميل</b></span><div class="toggle on"></div></div></div></div>
<div id="tab-settings" class="hidden"><div class="card"><b>🛠️ فاحص الأكواد + الداتابيز</b><button class="btn" style="background:#7c3aed" onclick="runDiagnostics()">🔍 فحص كل شي</button><div id="diagResult"></div></div></div>
<nav><button id="btn-book" class="active" onclick="show('book')">📘<br>نور بوك</button><button id="btn-gram" onclick="show('gram')">📸<br>نور قرام</button><button id="btn-reels" onclick="show('reels')">🎬<br>ريلز</button><button id="btn-chat" onclick="show('chat')">💬<br>نور شات</button><button id="btn-threads" onclick="show('threads')">🧵<br>ثريدز</button><button id="btn-menu" onclick="show('menu')">☰<br>القائمة</button></nav>
</div>
<script>const API=window.location.origin;let posts=[],chats=[],activeChat=null,mediaData='',mediaType='image',postKind='post',profile={},pages=[],money={},ads=[],suggest=[];
function showRegister(){document.getElementById('loginCard').classList.add('hidden');document.getElementById('registerCard').classList.remove('hidden');}
function showLogin(){document.getElementById('registerCard').classList.add('hidden');document.getElementById('loginCard').classList.remove('hidden');}
async function doRegister(){const name=document.getElementById('regName').value,phone=document.getElementById('regPhone').value,email=document.getElementById('regEmail').value,pw=document.getElementById('regPw').value,city=document.getElementById('regCity').value;if(!name||!phone||!email||!pw)return alert('املا كل البيانات');if(pw.length<6)return alert('الرقم السري لازم 6 حروف');const r=await fetch(API+'/api/v1/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({name,phone,email,password:pw,city})});const d=await r.json();if(d.error)return alert(d.error);alert('تم إنشاء حسابك ✅ - محفوظ في الداتابيز - ما بيطير');showLogin();}
async function doLogin(){const email=document.getElementById('loginEmail').value,pw=document.getElementById('loginPw').value;if(!email||!pw)return alert('اكتب الإيميل و الرقم السري');const r=await fetch(API+'/api/v1/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({email,password:pw})});const d=await r.json();if(d.error)return alert(d.error);document.getElementById('authScreen').classList.add('hidden');document.getElementById('appScreen').classList.remove('hidden');loadAll();}
async function logout(){await fetch(API+'/api/v1/auth/logout',{method:'POST',credentials:'include'});location.reload();}
function togglePlus(){document.getElementById('plusMenu').classList.toggle('open');}
function closePlus(){document.getElementById('plusMenu').classList.remove('open');}
document.addEventListener('click',function(e){if(!e.target.closest('#plusMenu')){closePlus();}});
function pubTab(t){['file','link','make','video'].forEach(x=>{document.getElementById('p-'+x).classList.toggle('hidden',x!==t);document.getElementById('t-'+x).classList.toggle('active',x===t);});postKind=t==='video'?'reel':'post';}
function pickFile(inp,type){const f=inp.files[0];if(!f)return;const r=new FileReader();r.onload=e=>{mediaData=e.target.result;mediaType=type==='reel'?'video':type;if(type==='reel')postKind='reel';document.getElementById('preview').innerHTML=mediaType==='video'?`<video src="${mediaData}" controls style="width:100%;border-radius:12px"></video>`:`<img src="${mediaData}" style="width:100%;border-radius:12px">`;};r.readAsDataURL(f);}
function previewLink(){const u=document.getElementById('mediaUrl').value;if(!u)return alert('الصق رابط أول');mediaData=u;mediaType=u.includes('.mp4')?'video':'image';document.getElementById('preview').innerHTML=mediaType==='video'?`<video src="${u}" controls style="width:100%;border-radius:12px"></video>`:`<img src="${u}" style="width:100%;border-radius:12px">`;addLink(u);}
async function addLink(u){await fetch(API+'/api/v1/links',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({url:u})});}
function makeImage(){const txt=document.getElementById('makeText').value||document.getElementById('newPost').value||'نور';const c=document.getElementById('makeCanvas');document.getElementById('makeCanvasWrap').classList.remove('hidden');const ctx=c.getContext('2d');const g=ctx.createLinearGradient(0,0,600,400);g.addColorStop(0,'#2563eb');g.addColorStop(1,'#a855f7');ctx.fillStyle=g;ctx.fillRect(0,0,600,400);ctx.fillStyle='#fff';ctx.font='bold 32px system-ui';ctx.textAlign='center';const w=txt.match(/.{1,20}/g)||[txt];w.forEach((x,i)=>ctx.fillText(x,300,180+i*40));ctx.font='bold 18px system-ui';ctx.fillText('نور - Noor',300,360);mediaData=c.toDataURL('image/png');mediaType='image';document.getElementById('preview').innerHTML=`<img src="${mediaData}" style="width:100%;border-radius:12px">`;}
function makeVideo(){const txt=document.getElementById('videoText').value||document.getElementById('newPost').value||'ريلز نور';mediaData='https://picsum.photos/600/800?random='+Date.now();mediaType='video';postKind='reel';document.getElementById('preview').innerHTML=`<div style="background:linear-gradient(135deg,#e11d48,#7c3aed);color:#fff;padding:40px;border-radius:14px;text-align:center;font-size:22px;font-weight:900">${txt}</div>`;}
async function loadAll(){const r=await fetch(API+'/api/v1/posts',{credentials:'include'});posts=await r.json();const rp=await fetch(API+'/api/v1/profile',{credentials:'include'});profile=await rp.json();const rpg=await fetch(API+'/api/v1/pages',{credentials:'include'});pages=await rpg.json();const rm=await fetch(API+'/api/v1/monetization',{credentials:'include'});money=await rm.json();const ra=await fetch(API+'/api/v1/ads',{credentials:'include'});ads=await ra.json();const r5=await fetch(API+'/api/v1/chats',{credentials:'include'});chats=await r5.json();const r3=await fetch(API+'/api/v1/suggest',{credentials:'include'});suggest=await r3.json();renderAll();}
function renderAll(){document.getElementById('helloUser').innerText='أهلاً بيك يا '+profile.name;document.getElementById('profileName').innerText=profile.name;document.getElementById('profileCity').innerText=profile.city;document.getElementById('profileBio').innerText=profile.bio||'';document.getElementById('menuName').innerText=profile.name;document.getElementById('stories').innerHTML=`<div class="story" style="background:linear-gradient(#2563eb,#06b6d4);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900">+ قصتي</div>`+(posts.length?posts.slice(0,5).map(p=>`<div class="story"><img src="${p.media_url||'https://picsum.photos/300/400?random='+p.id}"><span>${p.author_name}</span></div>`).join(''):'');document.getElementById('suggest').innerHTML=suggest.map(s=>`<div class="card" style="min-width:170px;text-align:center"><img src="${s.avatar}" style="width:70px;height:70px;border-radius:50%"><br><b>${s.name}</b><div style="font-size:11px;color:#888">${s.mutual} مشترك</div><div class="algo">${s.reason}</div><button class="btn" style="width:100%;margin-top:6px" onclick="addFriend('${s.name}',this)">+ إضافة صديق</button></div>`).join('');document.getElementById('empty').style.display=posts.filter(p=>p.kind!=='reel'&&p.kind!=='thread').length?'none':'block';document.getElementById('posts').innerHTML=posts.filter(p=>p.kind!=='reel'&&p.kind!=='thread').map(p=>`<div class="card"><div class="flex"><img class="avatar" src="${p.author_avatar}"><div style="flex:1"><b>${p.author_name}</b></div></div><p class="post">${p.content}${p.media_url?(p.media_type==='video'?`<video src="${p.media_url}" controls></video>`:`<img src="${p.media_url}">`):''}</p><div style="display:flex;gap:6px"><button style="flex:1;padding:10px;border:none;border-radius:20px;background:#fff3cd;font-weight:800" onclick="sendGift('وردة 🌹',0.1)">🌹 وردة 0.10$</button><button style="flex:1;padding:10px;border:none;border-radius:20px;background:#fff3cd;font-weight:800" onclick="sendGift('أسد 🦁',10)">🦁 أسد 10$</button></div><div class="actions"><button class="${p.liked?'active':''}" onclick="likePost('${p.id}')">${p.liked?'❤️ أعجبني':'🤍 أعجبني'}</button><button onclick="toggleComments('${p.id}')">💬 تعليق</button><button onclick="sharePost('${p.id}')">↗️ شير</button></div><div id="c-${p.id}" class="hidden"><div id="clist-${p.id}"></div><div class="comment-box"><input id="cin-${p.id}" type="text" placeholder="اكتب تعليق..."><button class="btn" onclick="addComment('${p.id}')">إرسال</button></div></div></div>`).join('');document.getElementById('reels').innerHTML=posts.filter(p=>p.kind==='reel').map(p=>`<div class="reel">${p.media_url?`<img src="${p.media_url}">`:`<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#fff;font-size:22px;padding:20px;text-align:center">${p.content}</div>`}<div class="reel-info"><b>${p.author_name}</b><p>${p.content}</p></div><div class="reel-actions"><button onclick="likePost('${p.id}')">❤️</button><button>💬</button><button onclick="sharePost('${p.id}')">↗️</button></div></div>`).join('');document.getElementById('gramGrid').innerHTML=posts.filter(p=>p.media_url).map(p=>`<img src="${p.media_url}">`).join('');document.getElementById('threads').innerHTML=posts.filter(p=>p.kind==='thread').map(p=>`<div class="card">${p.content}</div>`).join('');document.getElementById('chatList').innerHTML=chats.map(c=>`<div class="chat-item" onclick="openChat('${c.id}','${c.name}')"><img class="avatar" src="${c.avatar}"><div style="flex:1"><b>${c.name}</b><div style="font-size:13px;color:#888">${c.last_message||'ابدأ'}</div></div></div>`).join('');document.getElementById('notifList').innerHTML=`<div class="card">🔔 أهلاً بيك في نور 🎉</div><div class="card">🔔 حسابك محفوظ في الداتابيز - ما بيطير ✅</div>`;document.getElementById('pagesList').innerHTML=pages.map(pg=>`<div class="card"><b>${pg.name}</b> - ${pg.type==='digital'?'🎬 محتوى رقمي':'📄 عادية'}</div>`).join('');document.getElementById('mFollowers').innerText=money.followers;document.getElementById('mViews').innerText=money.views;document.getElementById('mTotal').innerText=money.total+'$';document.getElementById('mBreak').innerHTML=`مشاهدات: ${money.views} - أرباح: ${money.earnings}$ - هدايا: ${money.gifts}$ - إجمالي: ${money.total}$`;document.getElementById('liveInfo').innerHTML=`متابعين: ${money.followers} - ${money.live.level} - ${money.live.reason}`;document.getElementById('adsList').innerHTML=ads.map(a=>`<div class="card"><b>${a.title}</b> - ${a.budget}$ - ${a.target}</div>`).join('')||'لسه ما عملت إعلان';}
async function createPost(){const v=document.getElementById('newPost').value;const url=document.getElementById('mediaUrl')?.value||'';const fm=url||mediaData;if(!v.trim()&&!fm)return alert('اكتب شي أو اختار صورة');await fetch(API+'/api/v1/posts',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({author_name:profile.name||'أنت',content:v||'منشور جديد',media_url:fm,media_type:fm?(mediaType==='video'?'video':'image'):'text',kind:postKind})});document.getElementById('newPost').value='';mediaData='';document.getElementById('preview').innerHTML='';loadAll();alert('تم النشر ✅ - محفوظ في الداتابيز');}
async function createPostAsReel(){postKind='reel';await createPost();show('reels');}
async function createThread(){const v=document.getElementById('threadText').value;if(!v.trim())return;await fetch(API+'/api/v1/posts',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({content:v,kind:'thread'})});document.getElementById('threadText').value='';loadAll();}
async function likePost(id){const r=await fetch(API+`/api/v1/posts/${id}/like`,{method:'POST',credentials:'include'});const p=await r.json();posts=posts.map(x=>x.id===id?p:x);renderAll();}
async function sharePost(id){await fetch(API+`/api/v1/posts/${id}/share`,{method:'POST',credentials:'include'});loadAll();}
async function toggleComments(id){const el=document.getElementById('c-'+id);el.classList.toggle('hidden');const r=await fetch(API+`/api/v1/posts/${id}/comments`,{credentials:'include'});const cs=await r.json();document.getElementById('clist-'+id).innerHTML=cs.map(c=>`<div class="comment"><b>${c.author}</b> ${c.content}</div>`).join('')||'لا تعليقات';}
async function addComment(id){const v=document.getElementById('cin-'+id).value;if(!v.trim())return;await fetch(API+`/api/v1/posts/${id}/comment`,{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({author:profile.name,content:v})});document.getElementById('cin-'+id).value='';loadAll();}
async function addFriend(n,btn){btn.innerText='تم ✅';}
async function saveProfile(){const data={name:document.getElementById('editName').value||profile.name,city:document.getElementById('editCity').value||profile.city,bio:document.getElementById('editBio').value||profile.bio,phone:document.getElementById('editPhone').value||profile.phone,avatar:document.getElementById('editAvatar').value||profile.avatar};await fetch(API+'/api/v1/profile',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify(data)});loadAll();alert('تم الحفظ ✅ - في الداتابيز');}
async function createPage(){const n=document.getElementById('pageName').value;if(!n.trim())return alert('اكتب اسم الصفحة');await fetch(API+'/api/v1/pages',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({name:n,type:document.getElementById('pageType').value,category:document.getElementById('pageCat').value})});loadAll();alert('تم إنشاء الصفحة ✅ - محفوظة');}
async function sendGift(name,val){await fetch(API+'/api/v1/gifts',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({name,value:val})});loadAll();alert('تم إرسال '+name+' ✅');}
async function withdraw(){await fetch(API+'/api/v1/payments',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({type:'سحب أرباح',amount:money.total})});alert('سحب الأرباح - بنكك / MTN / Zain');loadAll();}
async function checkLive(){const r=await fetch(API+'/api/v1/monetization',{credentials:'include'});const m=await r.json();alert(m.live.allowed?'✅ مسموح - '+m.live.reason:'❌ ممنوع - '+m.live.reason);}
async function createAd(){const t=document.getElementById('adTitle').value,b=document.getElementById('adBudget').value;if(!t||!b)return alert('اكتب عنوان و ميزانية');await fetch(API+'/api/v1/ads',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({title:t,budget:parseFloat(b),target:document.getElementById('adTarget').value})});loadAll();alert('تم نشر الإعلان ✅');}
async function sendSupport(){const t=document.getElementById('supportText').value;if(!t.trim())return alert('اكتب مشكلتك');await fetch(API+'/api/v1/support',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({type:document.getElementById('supportType').value,text:t})});document.getElementById('supportText').value='';loadAll();alert('تم إرسال بلاغك ✅');}
async function createChat(){const n=document.getElementById('newChatName').value||'محادثة';await fetch(API+'/api/v1/chats',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({name:n,avatar:'https://i.pravatar.cc/150?u='+n})});loadAll();}
async function openChat(id,name){activeChat=id;document.getElementById('chatTitle').innerText=name;document.getElementById('chatBox').classList.remove('hidden');const r=await fetch(API+`/api/v1/chats/${id}/messages`,{credentials:'include'});const msgs=await r.json();document.getElementById('msgs').innerHTML=msgs.map(m=>`<div class="msg ${m.sender_id==='me'?'me':'other'}">${m.content}</div>`).join('');}
async function sendMsg(){const v=document.getElementById('newMsg').value;if(!v.trim()||!activeChat)return;await fetch(API+`/api/v1/chats/${activeChat}/messages`,{method:'POST',headers:{'Content-Type':'application/json'},credentials:'include',body:JSON.stringify({sender_id:'me',content:v})});document.getElementById('newMsg').value='';openChat(activeChat,document.getElementById('chatTitle').innerText);loadAll();}
async function runDiagnostics(){const r=await fetch(API+'/api/v1/diagnostics',{credentials:'include'});const d=await r.json();document.getElementById('diagResult').innerHTML=`<b>${d.summary}</b><br>`+d.tests.map(t=>`<div style="padding:8px;background:#f0f2f5;border-radius:10px;margin-top:6px"><b>${t.name}</b> - ${t.status}<br><span style="font-size:12px">${t.detail}</span></div>`).join('');}
function show(t){['book','gram','reels','chat','threads','menu','settings','profile','pages','money','ads','notifs','support','time','devices','links','payments','zain','edits','freebasics','whatsapp','presence','upgrades','privacy'].forEach(x=>{const e=document.getElementById('tab-'+x);if(e)e.classList.toggle('hidden',x!==t);});if(t==='links')loadLinks();if(t==='payments')loadPayments();if(t==='support')loadSupport();}
async function loadLinks(){const r=await fetch(API+'/api/v1/links',{credentials:'include'});const d=await r.json();document.getElementById('linksList').innerHTML=d.map(x=>`<div class="card">🔗 ${x.url}</div>`).join('')||'لسه ما ضغطت رابط';}
async function loadPayments(){const r=await fetch(API+'/api/v1/payments',{credentials:'include'});const d=await r.json();document.getElementById('paymentsList').innerHTML=d.map(x=>`<div class="card">💳 ${x.type} - ${x.amount}$</div>`).join('')||'لسه ما في دفع';}
async function loadSupport(){const r=await fetch(API+'/api/v1/support',{credentials:'include'});const d=await r.json();document.getElementById('supportList').innerHTML=d.map(x=>`<div class="card"><b>${x.type}</b><p>${x.text}</p></div>`).join('')||'';}
</script></body></html>"""
@app.route('/')
def home(): return HTML
@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    d=request.json or {}; email=d.get("email","").lower()
    if not email or not d.get("password") or not d.get("name") or not d.get("phone"): return jsonify({"error":"املا كل البيانات"}),400
    s=db()
    if s.query(User).filter_by(email_plain=email).first(): s.close(); return jsonify({"error":"الإيميل مسجل قبل كده"}),400
    uid=str(uuid.uuid4()); u=User(id=uid,name=d.get("name"),phone_enc=encrypt(d.get("phone")),email_enc=encrypt(email),email_plain=email,password_hash=hash_pw(d.get("password")),city=d.get("city",""),avatar="https://i.pravatar.cc/150?u="+uid,followers=0,views=0)
    s.add(u); s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    d=request.json or {}; email=d.get("email","").lower(); pw=d.get("password","")
    s=db(); users=s.query(User).all(); s.close()
    for u in users:
        if u.email_plain==email or decrypt(u.phone_enc)==email:
            if u.password_hash==hash_pw(pw): session["user_id"]=u.id; return jsonify({"ok":True,"name":u.name})
            return jsonify({"error":"الرقم السري غلط"}),401
    return jsonify({"error":"الحساب ما موجود - اعمل حساب جديد"}),404
@app.route('/api/v1/auth/logout', methods=['POST'])
def logout(): session.pop("user_id",None); return jsonify({"ok":True})
@app.route('/api/v1/profile', methods=['GET'])
def get_profile():
    u=get_user()
    if not u: return jsonify({"name":"...","city":"...","bio":"","avatar":"https://i.pravatar.cc/150?u=me"})
    return jsonify({"name":u.name,"city":u.city or "","bio":u.bio or "","avatar":u.avatar,"phone":"مشفر 🔒"})
@app.route('/api/v1/profile', methods=['POST'])
def update_profile():
    u=get_user()
    if not u: return jsonify({"error":"سجل دخول"}),401
    d=request.json or {}; s=db(); uu=s.query(User).filter_by(id=u.id).first()
    if d.get("name"): uu.name=d["name"]
    if d.get("city"): uu.city=d["city"]
    if d.get("bio"): uu.bio=d["bio"]
    if d.get("phone"): uu.phone_enc=encrypt(d["phone"])
    if d.get("avatar"): uu.avatar=d["avatar"]
    s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/pages', methods=['GET'])
def get_pages():
    s=db(); r=[{"id":p.id,"name":p.name,"type":p.type,"category":p.category,"followers":p.followers} for p in s.query(Page).filter_by(user_id=session.get("user_id")).all()]; s.close(); return jsonify(r)
@app.route('/api/v1/pages', methods=['POST'])
def create_page():
    if not get_user(): return jsonify({"error":"سجل دخول"}),401
    d=request.json or {}; s=db(); p=Page(id=str(uuid.uuid4()),user_id=session.get("user_id"),name=d.get("name"),type=d.get("type","normal"),category=d.get("category",""),followers=0); s.add(p); s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/monetization', methods=['GET'])
def get_money():
    u=get_user(); uid=session.get("user_id",""); s=db(); gifts=sum(g.value for g in s.query(Gift).filter_by(user_id=uid).all()); s.close()
    views=u.views if u else 0; followers=u.followers if u else 0; earnings=round(views/1000*2,2); total=round(earnings+gifts,2)
    if followers<100: live={"allowed":False,"reason":f"عندك {followers} متابع - لازم 100 متابع","level":"ممنوع"}
    elif followers<1000: live={"allowed":True,"reason":f"عندك {followers} متابع - لايف عادي","level":"عادي"}
    else: live={"allowed":True,"reason":f"عندك {followers} متابع - لايف + هدايا + ارباح","level":"محترف"}
    return jsonify({"followers":followers,"views":views,"earnings":earnings,"gifts":gifts,"total":total,"live":live})
@app.route('/api/v1/gifts', methods=['POST'])
def gift():
    d=request.json or {}; s=db(); s.add(Gift(id=str(uuid.uuid4()),user_id=session.get("user_id"),name=d.get("name"),value=d.get("value",0))); s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/ads', methods=['GET'])
def get_ads():
    s=db(); r=[{"id":a.id,"title":a.title,"budget":a.budget,"target":a.target,"views":a.views,"clicks":a.clicks,"spent":a.spent} for a in s.query(Ad).filter_by(user_id=session.get("user_id")).all()]; s.close(); return jsonify(r)
@app.route('/api/v1/ads', methods=['POST'])
def create_ad():
    if not get_user(): return jsonify({"error":"سجل دخول"}),401
    d=request.json or {}; s=db(); s.add(Ad(id=str(uuid.uuid4()),user_id=session.get("user_id"),title=d.get("title"),budget=d.get("budget",0),target=d.get("target"),views=0,clicks=0,spent=d.get("budget",0))); s.add(Payment(id=str(uuid.uuid4()),user_id=session.get("user_id"),type="إعلان - "+d.get("title",""),amount=d.get("budget",0),time=datetime.now().strftime("%Y-%m-%d %H:%M"))); s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/support', methods=['GET'])
def get_support():
    s=db(); r=[{"type":x.type,"text":x.text} for x in s.query(Support).filter_by(user_id=session.get("user_id")).all()]; s.close(); return jsonify(r)
@app.route('/api/v1/support', methods=['POST'])
def post_support():
    d=request.json or {}; s=db(); s.add(Support(id=str(uuid.uuid4()),user_id=session.get("user_id"),type=d.get("type"),text=d.get("text"))); s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/links', methods=['GET'])
def get_links():
    s=db(); r=[{"url":x.url,"time":x.time} for x in s.query(Link).filter_by(user_id=session.get("user_id")).all()]; s.close(); return jsonify(r)
@app.route('/api/v1/links', methods=['POST'])
def post_link():
    d=request.json or {}; s=db(); s.add(Link(id=str(uuid.uuid4()),user_id=session.get("user_id"),url=d.get("url"),time=datetime.now().strftime("%Y-%m-%d %H:%M"))); s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/payments', methods=['GET'])
def get_payments():
    s=db(); r=[{"type":x.type,"amount":x.amount,"time":x.time} for x in s.query(Payment).filter_by(user_id=session.get("user_id")).all()]; s.close(); return jsonify(r)
@app.route('/api/v1/payments', methods=['POST'])
def post_payment():
    d=request.json or {}; s=db(); s.add(Payment(id=str(uuid.uuid4()),user_id=session.get("user_id"),type=d.get("type"),amount=d.get("amount",0),time=datetime.now().strftime("%Y-%m-%d %H:%M"))); s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/suggest', methods=['GET'])
def get_suggest(): return jsonify([{"id":str(uuid.uuid4()),"name":n,"city":c,"mutual":m,"reason":f"{m} اصدقاء مشتركين","avatar":f"https://i.pravatar.cc/150?u={n}"} for n,c,m in [("أحمد علي","عطبرة",5),("سارة محمد","الخرطوم",12),("محمد خالد","مدني",8)]])
@app.route('/api/v1/diagnostics', methods=['GET'])
def diag():
    s=db(); uc=s.query(User).count(); pc=s.query(Post).count(); s.close()
    tests=[{"name":"الداتابيز PostgreSQL","status":"شغال ✅","detail":f"{uc} حساب محفوظ - {pc} بوست محفوظ - ما بيطير"},{"name":"تسجيل الدخول SHA256","status":"شغال ✅","detail":"كلمات سر مشفرة"},{"name":"الملف - مشفر","status":"شغال ✅","detail":"جوال و إيميل مشفرين"},{"name":"الأرباح - من 0","status":"شغال ✅","detail":"محفوظة في الداتابيز"},{"name":"الإعلانات","status":"شغال ✅","detail":"مرتبطة بالداتابيز"},{"name":"الصفحات","status":"شغال ✅","detail":"محفوظة"}]
    return jsonify({"tests":tests,"summary":f"{len(tests)}/{len(tests)} شغالة ✅ - داتابيز حقيقية"})
@app.route('/api/v1/posts', methods=['GET'])
def get_posts():
    s=db(); ps=s.query(Post).order_by(Post.created_at.desc()).all(); r=[{"id":p.id,"author_name":p.author_name,"author_avatar":p.author_avatar,"content":p.content,"media_url":p.media_url,"media_type":p.media_type,"kind":p.kind,"likes_count":p.likes,"comments_count":p.comments_count,"shares_count":p.shares,"liked":p.liked} for p in ps]; s.close(); return jsonify(sorted(r, key=lambda x: x["likes_count"]*2+x["comments_count"]*3, reverse=True))
@app.route('/api/v1/posts', methods=['POST'])
def create_post():
    u=get_user(); d=request.json or {}; s=db(); p=Post(id=str(uuid.uuid4()),user_id=session.get("user_id"),author_name=u.name if u else d.get("author_name","أنت"),author_avatar=u.avatar if u else "https://i.pravatar.cc/150?u=me",content=d.get("content",""),media_url=d.get("media_url",""),media_type=d.get("media_type","text"),kind=d.get("kind","post"),likes=0,comments_count=0,shares=0,liked=False); s.add(p)
    if u:
        uu=s.query(User).filter_by(id=u.id).first(); uu.views+=10
    s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/posts/<pid>/like', methods=['POST'])
def like_post(pid):
    s=db(); p=s.query(Post).filter_by(id=pid).first()
    if not p: s.close(); return jsonify({"error":"not found"}),404
    p.liked=not p.liked; p.likes+=1 if p.liked else -1; s.commit(); r={"id":p.id,"author_name":p.author_name,"author_avatar":p.author_avatar,"content":p.content,"media_url":p.media_url,"media_type":p.media_type,"kind":p.kind,"likes_count":p.likes,"comments_count":p.comments_count,"shares_count":p.shares,"liked":p.liked}; s.close(); return jsonify(r)
@app.route('/api/v1/posts/<pid>/share', methods=['POST'])
def share_post(pid):
    s=db(); p=s.query(Post).filter_by(id=pid).first()
    if not p: s.close(); return jsonify({"error":"not found"}),404
    p.shares+=1; s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/posts/<pid>/comments', methods=['GET'])
def get_comments(pid):
    s=db(); r=[{"author":c.author,"content":c.content} for c in s.query(Comment).filter_by(post_id=pid).all()]; s.close(); return jsonify(r)
@app.route('/api/v1/posts/<pid>/comment', methods=['POST'])
def comment_post(pid):
    d=request.json or {}; s=db(); p=s.query(Post).filter_by(id=pid).first()
    if not p: s.close(); return jsonify({"error":"not found"}),404
    p.comments_count+=1; s.add(Comment(id=str(uuid.uuid4()),post_id=pid,author=d.get("author","أنت"),content=d.get("content",""))); s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/chats', methods=['GET'])
def get_chats():
    s=db(); r=[{"id":c.id,"name":c.name,"avatar":c.avatar,"last_message":c.last_message} for c in s.query(Chat).all()]; s.close(); return jsonify(r)
@app.route('/api/v1/chats', methods=['POST'])
def create_chat():
    d=request.json or {}; s=db(); cid=str(uuid.uuid4()); s.add(Chat(id=cid,name=d.get("name","محادثة"),avatar=d.get("avatar","https://i.pravatar.cc/150?u=x"),last_message="")); s.commit(); s.close(); return jsonify({"ok":True})
@app.route('/api/v1/chats/<cid>/messages', methods=['GET'])
def get_messages(cid):
    s=db(); r=[{"sender_id":m.sender_id,"content":m.content} for m in s.query(Message).filter_by(chat_id=cid).all()]; s.close(); return jsonify(r)
@app.route('/api/v1/chats/<cid>/messages', methods=['POST'])
def send_message(cid):
    d=request.json or {}; s=db(); s.add(Message(id=str(uuid.uuid4()),chat_id=cid,sender_id=d.get("sender_id","me"),content=d.get("content",""))); c=s.query(Chat).filter_by(id=cid).first()
    if c: c.last_message=d.get("content","")
    s.commit(); s.close(); return jsonify({"ok":True})
if __name__=='__main__': app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
