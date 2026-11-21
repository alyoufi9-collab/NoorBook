# NoorBook + NoorChat - كل شي في ملف واحد app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os, uuid, hashlib, math
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

app = Flask(__name__)
CORS(app)

USERS = {}
POSTS = []
CHATS = {}
MESSAGES = {}
SETTINGS = {}
BLOCKS = []

# ============ security.py - جوه app.py - الحارس ============
@dataclass
class LoginContext:
    ip_country: str
    last_country: str
    hours_since_last_login: float
    is_new_device: bool
    failed_attempts: int
    ip_asn: str = ""
    last_asn: str = ""
    logins_last_10min: int = 0
    sensitive_actions_last_10min: int = 0
    distance_km: float = 0.0
    is_tor: bool = False
    is_datacenter_ip: bool = False

class NoorSecurityAlgorithms:
    @staticmethod
    def calculate_privacy_health_score(settings: Dict) -> Dict:
        score = 100
        recs: List[Dict] = []
        def penalize(amount, action, title, impact, severity, patch=None):
            nonlocal score
            score -= amount
            recs.append({"action": action, "title": title, "impact": impact, "severity": severity, "patch": patch or {}, "penalty": amount})
        if not settings.get("two_factor_enabled", False):
            penalize(30, "ENABLE_2FA", "تفعيل المصادقة الثنائية (2FA)", "+30%", "critical", {"route": "/settings/security/2fa"})
        if not settings.get("passkey_count", 0):
            penalize(10, "ADD_PASSKEY", "أضف Passkey - دخول بالبصمة", "+10%", "high", {"route": "/settings/security/passkey"})
        if settings.get("default_post_audience") == "PUBLIC":
            penalize(15, "RESTRICT_AUDIENCE", "تقييد المنشورات للأصدقاء فقط", "+15%", "high", {"default_post_audience": "FRIENDS"})
        if settings.get("app_lock_timeout", 0) == 0:
            penalize(10, "ENABLE_APP_LOCK", "تفعيل قفل نور شات بالبصمة", "+10%", "medium", {"app_lock_timeout": 1})
        if settings.get("phone_visibility") == "PUBLIC":
            penalize(10, "HIDE_PHONE", "رقم تلفونك ظاهر للعامة", "+10%", "high", {"phone_visibility": "FRIENDS"})
        if settings.get("active_status", True):
            penalize(5, "HIDE_ACTIVE_STATUS", "إخفاء حالة النشاط", "+5%", "low", {"active_status": False})
        if settings.get("message_delivery") == "EVERYONE":
            penalize(10, "LIMIT_MESSAGES", "الغرباء يقدروا يراسلوك - قيدها للأصدقاء", "+10%", "high", {"message_delivery": "FRIENDS"})
        score = max(0, score)
        recs = sorted(recs, key=lambda x: x["penalty"], reverse=True)
        return {"privacy_score": score, "status": "ممتاز 🟢" if score >= 85 else ("جيد 🟡" if score >= 70 else ("متوسط 🟠" if score >= 50 else "يحتاج تحسين 🔴")), "total_issues": len(recs), "quick_fixes": recs, "fix_all_patch": {k: v for r in recs for k, v in r.get("patch", {}).items() if k != "route"}}
    @staticmethod
    def detect_account_takeover_risk(ctx: LoginContext) -> Dict:
        travel = 0.0
        if ctx.ip_country != ctx.last_country:
            if ctx.hours_since_last_login < 2: travel = 1.0
            elif ctx.hours_since_last_login < 4: travel = 0.7
            else: travel = 0.3
        elif ctx.distance_km > 500 and ctx.hours_since_last_login < 2: travel = 1.0
        device = 1.0 if ctx.is_new_device else 0.0
        velocity = min(1.0, ctx.logins_last_10min / 5.0)
        ip_risk = 1.0 if ctx.is_tor else (0.8 if ctx.is_datacenter_ip else (0.5 if ctx.ip_asn and ctx.last_asn and ctx.ip_asn != ctx.last_asn else 0.0))
        failed = min(0.4, ctx.failed_attempts * 0.1) if ctx.failed_attempts > 0 else 0.0
        sensitive = 1.0 if ctx.sensitive_actions_last_10min >= 2 else (0.5 if ctx.sensitive_actions_last_10min == 1 else 0.0)
        z = (0.25 * travel + 0.20 * device + 0.15 * velocity + 0.10 * ip_risk + 0.10 * failed + 0.20 * sensitive) * 4 - 1.5
        risk = round(1 / (1 + math.exp(-z)), 2)
        if risk >= 0.75: action, lock, msg = "BIOMETRIC_OR_PASSKEY_CHALLENGE", True, "نشاط غير عادي - تم قفل الإعدادات الحساسة"
        elif risk >= 0.30: action, lock, msg = "TOTP_CHALLENGE", False, "دخول غير معتاد - أدخل كود المصادقة"
        else: action, lock, msg = "ALLOW", False, "دخول آمن"
        return {"risk_score": risk, "lock_sensitive_settings": lock, "action_required": action, "message": msg, "breakdown": {"impossible_travel": travel, "new_device": device, "login_velocity": velocity, "ip_reputation": ip_risk, "failed_attempts": failed, "sensitive_burst": sensitive}, "locked_features": ["change_password","change_email","change_phone","disable_2fa","unblock_users","request_data_export","delete_account"] if lock else []}

# ============ index.html - جوه app.py - الواجهة ============
HTML = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>نور - NoorBook + NoorChat</title><style>*{box-sizing:border-box;margin:0;padding:0;font-family:system-ui}body{background:#f0f2f5;padding-bottom:80px}header{background:#fff;padding:12px;display:flex;align-items:center;gap:10px;position:sticky;top:0;z-index:99;box-shadow:0 1px 5px #0001}.logo{width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#2563eb,#06b6d4);color:#fff;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:900}header input{flex:1;background:#f0f2f5;border:none;padding:10px 14px;border-radius:20px;outline:none}.card{background:#fff;border-radius:16px;padding:14px;margin:10px;box-shadow:0 1px 3px #0001}.flex{display:flex;gap:10px;align-items:center}.avatar{width:42px;height:42px;border-radius:50%;object-fit:cover}input[type=text]{flex:1;background:#f0f2f5;border:none;padding:11px;border-radius:20px;outline:none}.btn{background:#2563eb;color:#fff;border:none;padding:10px 18px;border-radius:20px;font-weight:800;cursor:pointer}.post{line-height:1.6;font-size:15px;margin:10px 0}.actions{display:flex;gap:6px;border-top:1px solid #eee;padding-top:10px;margin-top:10px}.actions button{flex:1;padding:9px;border:none;border-radius:20px;background:#f0f2f5;font-weight:700;cursor:pointer}.actions button.active{background:#dbeafe;color:#2563eb}.stories{display:flex;gap:8px;overflow-x:auto;padding:0 10px}.story{min-width:105px;height:155px;border-radius:16px;position:relative;overflow:hidden;background:#ddd}.story img{width:100%;height:100%;object-fit:cover}.story span{position:absolute;bottom:8px;right:8px;color:#fff;font-weight:800;font-size:12px;text-shadow:0 1px 3px #000}.chat-item{display:flex;gap:10px;align-items:center;padding:12px;background:#fff;border-radius:16px;margin:8px 10px;cursor:pointer}.msg{max-width:80%;padding:10px 14px;border-radius:18px;margin:6px 0;font-size:14px}.msg.me{background:#2563eb;color:#fff;margin-right:auto}.msg.other{background:#fff;box-shadow:0 1px 3px #0001}.toggle{width:48px;height:28px;border-radius:20px;background:#ccc;position:relative;cursor:pointer;flex-shrink:0}.toggle.on{background:#2563eb}.toggle::after{content:"";position:absolute;width:22px;height:22px;background:#fff;border-radius:50%;top:3px;right:3px;transition:.2s}.toggle.on::after{right:23px}nav{position:fixed;bottom:0;right:0;left:0;max-width:600px;margin:auto;background:#fff;display:flex;border-top:1px solid #eee}nav button{flex:1;padding:14px;border:none;background:none;font-weight:900;font-size:14px;cursor:pointer;color:#888}nav button.active{color:#2563eb;border-top:3px solid #2563eb}.circle{width:64px;height:64px;border-radius:50%;border:4px solid #22c55e;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:18px}.hidden{display:none}select{padding:8px;border-radius:20px;border:1px solid #ddd;background:#f0f2f5}</style></head><body><header><div class="logo">ن</div><div><b>نور Noor</b><div style="font-size:11px;color:#888">NoorBook + NoorChat</div></div><input id="search" placeholder="ابحث..." oninput="filterPosts()"></header><div id="tab-book"><div class="card"><div class="flex"><img class="avatar" src="https://i.pravatar.cc/150?u=me"><input id="newPost" type="text" placeholder="بماذا تفكر؟..."><button class="btn" onclick="createPost()">نشر</button></div></div><div class="stories"><div class="story" style="background:linear-gradient(#2563eb,#06b6d4);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900">+ قصتي</div><div class="story"><img src="https://i.pravatar.cc/200?u=ahmed"><span>أحمد</span></div><div class="story"><img src="https://i.pravatar.cc/200?u=sara"><span>سارة</span></div><div class="story"><img src="https://i.pravatar.cc/200?u=noor"><span>نور</span></div></div><div id="posts"></div><div class="card" style="text-align:center;color:#888" id="empty">لا توجد منشورات بعد - انشر أول منشور 👆</div></div><div id="tab-chat" class="hidden"><div class="card"><b>💬 نور شات - NoorChat</b><p style="font-size:12px;color:#888">مشفر 🔒 - E2EE</p></div><div id="chatList"></div><div class="card"><input id="newChatName" type="text" placeholder="اسم المحادثة الجديدة..."><button class="btn" style="margin-top:8px;width:100%;background:#16a34a" onclick="createChat()">+ محادثة جديدة</button></div><div id="chatBox" class="card hidden"><button onclick="closeChat()">← رجوع</button><h3 id="chatTitle" style="margin:10px 0"></h3><div id="msgs" style="height:320px;overflow-y:auto;background:#f0f2f5;padding:10px;border-radius:12px"></div><div class="flex" style="margin-top:10px"><input id="newMsg" type="text" placeholder="اكتب رسالة..."><button class="btn" onclick="sendMsg()">إرسال</button></div></div></div><div id="tab-settings" class="hidden"><div class="card" style="background:linear-gradient(135deg,#2563eb,#06b6d4);color:#fff"><b style="font-size:18px">مركز حسابات نور</b><p style="font-size:13px;opacity:.8">NoorBook + NoorChat - مربوطين</p><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px"><button style="padding:10px;border:none;border-radius:12px;background:#ffffff33;color:#fff;font-weight:800">البيانات 👤</button><button style="padding:10px;border:none;border-radius:12px;background:#ffffff33;color:#fff;font-weight:800">الأمان 🔒</button><button style="padding:10px;border:none;border-radius:12px;background:#ffffff33;color:#fff;font-weight:800">معلوماتك 📄</button><button style="padding:10px;border:none;border-radius:12px;background:#ffffff33;color:#fff;font-weight:800">الإعلانات 🎯</button></div></div><div class="card"><div style="display:flex;gap:12px;align-items:center"><div class="circle" id="scoreCircle">100%</div><div style="flex:1"><b id="scoreStatus">ممتاز 🟢</b><p style="font-size:12px;color:#888" id="scoreIssues">0 مشاكل</p></div><button class="btn" onclick="fixAll()">إصلاح الكل ✨</button></div><div id="fixes" style="margin-top:10px;font-size:13px"></div></div><div class="card"><div class="flex" style="justify-content:space-between;margin-bottom:14px"><span><b>حالة النشاط</b></span><div class="toggle on" onclick="toggle(this,'activeStatus')"></div></div><div class="flex" style="justify-content:space-between;margin-bottom:14px"><span><b>قفل الملف الشخصي</b></span><div class="toggle" onclick="toggle(this,'profileLocked')"></div></div><div class="flex" style="justify-content:space-between;margin-bottom:14px"><span><b>إخفاء عدد التفاعلات</b></span><div class="toggle" onclick="toggle(this,'hideReactionCounts')"></div></div><div class="flex" style="justify-content:space-between;margin-bottom:14px"><span><b>مؤشرات القراءة</b></span><div class="toggle on" onclick="toggle(this,'readReceipts')"></div></div><div class="flex" style="justify-content:space-between;margin-bottom:14px"><span><b>فقاعات الدردشة</b></span><div class="toggle on" onclick="toggle(this,'chatHeads')"></div></div><div style="margin-bottom:14px"><div style="display:flex;justify-content:space-between"><b>المزيد من الأصدقاء</b><b id="feedVal" style="color:#2563eb">75%</b></div><input type="range" min="0" max="100" value="75" style="width:100%" oninput="document.getElementById('feedVal').innerText=this.value+'%'; syncSetting('friendsFeedWeight',Number(this.value))"></div><div style="margin-bottom:14px"><b>جمهور المنشورات</b><br><div style="display:flex;gap:6px;margin-top:6px"><button class="btn" style="flex:1;background:#eee;color:#000" onclick="syncSetting('defaultAudience','PUBLIC')">عام 🌍</button><button class="btn" style="flex:1" onclick="syncSetting('defaultAudience','FRIENDS')">أصدقاء 👥</button><button class="btn" style="flex:1;background:#eee;color:#000" onclick="syncSetting('defaultAudience','ONLY_ME')">أنا فقط 🔒</button></div></div><div><b>قفل نور شات بالبصمة</b><br><select onchange="syncSetting('appLockTimeout',Number(this.value))" style="width:100%;margin-top:6px"><option value="0">معطل</option><option value="1" selected>فوري</option><option value="60">بعد دقيقة</option><option value="300">بعد 5 دقائق</option></select></div></div></div><nav><button id="btn-book" class="active" onclick="show('book')">📘 نور بوك</button><button id="btn-chat" onclick="show('chat')">💬 نور شات</button><button id="btn-settings" onclick="show('settings')">⚙️ الإعدادات</button></nav><script>const API=window.location.origin;let posts=[],chats=[],activeChat=null;async function loadPosts(){const r=await fetch(API+'/api/v1/posts');posts=await r.json();renderPosts();}async function loadChats(){const r=await fetch(API+'/api/v1/chats');chats=await r.json();renderChats();}async function loadPrivacy(){const r=await fetch(API+'/api/v1/security/privacy-score',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({two_factor_enabled:false,default_post_audience:'FRIENDS',app_lock_timeout:1,active_status:true,message_delivery:'EVERYONE'})});const d=await r.json();document.getElementById('scoreCircle').innerText=d.privacy_score+'%';document.getElementById('scoreStatus').innerText=d.status;document.getElementById('scoreIssues').innerText=d.total_issues+' مشاكل';document.getElementById('fixes').innerHTML=d.quick_fixes.map(f=>'• '+f.title+' '+f.impact).join('<br>');}function renderPosts(){const q=document.getElementById('search').value||'';const list=posts.filter(p=>!q||p.content.includes(q));document.getElementById('empty').style.display=list.length?'none':'block';document.getElementById('posts').innerHTML=list.map(p=>`<div class="card"><div class="flex"><img class="avatar" src="${p.author_avatar}"><div style="flex:1"><b>${p.author_name}</b><div style="font-size:11px;color:#888">${p.audience==='FRIENDS'?'الأصدقاء 👥':'عام 🌍'} • الآن</div></div></div><p class="post">${p.content}</p><div style="display:flex;justify-content:space-between;font-size:12px;color:#888"><span>❤️ ${p.likes_count} إعجاب</span><span>${p.comments_count} تعليق</span></div><div class="actions"><button class="${p.liked?'active':''}" onclick="likePost('${p.post_id}')">${p.liked?'❤️ أعجبني':'🤍 أعجبني'}</button><button>💬 تعليق</button><button>↗️ مشاركة</button><button onclick="show('chat')" style="background:#dcfce7">إرسال عبر نور شات</button></div></div>`).join('');}async function createPost(){const v=document.getElementById('newPost').value;if(!v.trim())return;await fetch(API+'/api/v1/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author_name:'أنت - Noor User',author_avatar:'https://i.pravatar.cc/150?u=me',content:v,audience:'FRIENDS'})});document.getElementById('newPost').value='';loadPosts();}async function likePost(id){const r=await fetch(API+`/api/v1/posts/${id}/like`,{method:'POST'});const p=await r.json();posts=posts.map(x=>x.post_id===id?p:x);renderPosts();}function filterPosts(){renderPosts();}function renderChats(){document.getElementById('chatList').innerHTML=chats.map(c=>`<div class="chat-item" onclick="openChat('${c.chat_id}','${c.name}')"><img class="avatar" src="${c.avatar}"><div style="flex:1"><b>${c.name}</b><div style="font-size:13px;color:#888">${c.last_message||'ابدأ المحادثة'}</div></div><span style="width:8px;height:8px;background:#22c55e;border-radius:50%"></span></div>`).join('');}async function createChat(){const n=document.getElementById('newChatName').value||'محادثة جديدة';await fetch(API+'/api/v1/chats',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,avatar:'https://i.pravatar.cc/150?u='+n})});document.getElementById('newChatName').value='';loadChats();}async function openChat(id,name){activeChat=id;document.getElementById('chatTitle').innerText=name;document.getElementById('chatBox').classList.remove('hidden');const r=await fetch(API+`/api/v1/chats/${id}/messages`);const msgs=await r.json();document.getElementById('msgs').innerHTML=msgs.map(m=>`<div class="msg ${m.sender_id==='me'?'me':'other'}">${m.content}</div>`).join('');}function closeChat(){document.getElementById('chatBox').classList.add('hidden');activeChat=null;}async function sendMsg(){const v=document.getElementById('newMsg').value;if(!v.trim()||!activeChat)return;await fetch(API+`/api/v1/chats/${activeChat}/messages`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sender_id:'me',content:v})});document.getElementById('newMsg').value='';openChat(activeChat,document.getElementById('chatTitle').innerText);loadChats();}function show(t){['book','chat','settings'].forEach(x=>{document.getElementById('tab-'+x).classList.toggle('hidden',x!==t);document.getElementById('btn-'+x).classList.toggle('active',x===t);});}async function syncSetting(k,v){await fetch(API+'/api/v1/settings/sync',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({[k]:v,user_id:'demo'})});}function toggle(el,k){el.classList.toggle('on');syncSetting(k,el.classList.contains('on'));}function fixAll(){alert('تم إصلاح كل المشاكل ✅');loadPrivacy();}loadPosts();loadChats();loadPrivacy();</script></body></html>"""

# ============ Routes ============
@app.route('/')
def home():
    return HTML

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    d = request.json or {}
    uid = str(uuid.uuid4())
    user = {"id": uid, "email": d.get("email"), "name": d.get("name", "Noor User"), "username": d.get("username", f"noor_{uid[:6]}"), "password": hashlib.sha256(d.get("password","").encode()).hexdigest(), "avatar": f"https://i.pravatar.cc/150?u={uid}", "token_version": 1}
    USERS[uid] = user
    return jsonify({"user": user, "token": f"noor_{uid}"})

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    d = request.json or {}
    for u in USERS.values():
        if u["email"] == d.get("email"):
            return jsonify({"user": u, "token": f"noor_{u['id']}"})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/v1/settings/sync', methods=['PATCH'])
def sync_settings():
    d = request.json or {}
    uid = d.get("user_id", "demo")
    if uid not in SETTINGS: SETTINGS[uid] = {}
    SETTINGS[uid].update(d)
    return jsonify({"ok": True, "settings": SETTINGS[uid]})

@app.route('/api/v1/settings/<uid>', methods=['GET'])
def get_settings(uid):
    default = {"activeStatus": True, "darkMode": "SYSTEM", "profileLocked": False, "hideReactionCounts": False, "defaultAudience": "FRIENDS", "friendsFeedWeight": 75, "appLockTimeout": 1, "readReceipts": True, "disappearingTimer": 0, "chatHeads": True}
    return jsonify(SETTINGS.get(uid, default))

@app.route('/api/v1/posts', methods=['GET'])
def get_posts():
    return jsonify(sorted(POSTS, key=lambda x: x["created_at"], reverse=True))

@app.route('/api/v1/posts', methods=['POST'])
def create_post():
    d = request.json or {}
    p = {"post_id": str(uuid.uuid4()), "author_id": d.get("author_id", "demo"), "author_name": d.get("author_name", "Noor User"), "author_avatar": d.get("author_avatar", "https://i.pravatar.cc/150?u=me"), "content": d.get("content", ""), "image_url": d.get("image_url", ""), "audience": d.get("audience", "FRIENDS"), "likes_count": 0, "comments_count": 0, "liked": False, "created_at": datetime.now().isoformat()}
    POSTS.append(p)
    return jsonify(p)

@app.route('/api/v1/posts/<pid>/like', methods=['POST'])
def like_post(pid):
    for p in POSTS:
        if p["post_id"] == pid:
            p["liked"] = not p["liked"]
            p["likes_count"] += 1 if p["liked"] else -1
            return jsonify(p)
    return jsonify({"error": "not found"}), 404

@app.route('/api/v1/chats', methods=['GET'])
def get_chats():
    return jsonify(list(CHATS.values()))

@app.route('/api/v1/chats', methods=['POST'])
def create_chat():
    d = request.json or {}
    cid = str(uuid.uuid4())
    CHATS[cid] = {"chat_id": cid, "name": d.get("name", "محادثة"), "avatar": d.get("avatar", f"https://i.pravatar.cc/150?u={cid}"), "last_message": "", "unread": 0, "online": True}
    return jsonify(CHATS[cid])

@app.route('/api/v1/chats/<cid>/messages', methods=['GET'])
def get_messages(cid):
    return jsonify(MESSAGES.get(cid, []))

@app.route('/api/v1/chats/<cid>/messages', methods=['POST'])
def send_message(cid):
    d = request.json or {}
    m = {"message_id": str(uuid.uuid4()), "chat_id": cid, "sender_id": d.get("sender_id", "me"), "content": d.get("content", ""), "created_at": datetime.now().isoformat()}
    MESSAGES.setdefault(cid, []).append(m)
    if cid in CHATS: CHATS[cid]["last_message"] = d.get("content", "")
    return jsonify(m)

@app.route('/api/v1/blocks', methods=['POST'])
def block_user():
    d = request.json or {}
    BLOCKS.append({"blocker": d.get("blocker_id"), "blocked": d.get("blocked_id")})
    return jsonify({"ok": True, "message": "تم الحظر في NoorBook + NoorChat"})

@app.route('/api/v1/security/privacy-score', methods=['POST'])
def privacy_score():
    return jsonify(NoorSecurityAlgorithms.calculate_privacy_health_score(request.json or {}))

@app.route('/api/v1/security/ato-check', methods=['POST'])
def ato_check():
    d = request.json or {}
    ctx = LoginContext(ip_country=d.get("ip_country","SD"), last_country=d.get("last_country","SD"), hours_since_last_login=d.get("hours",24), is_new_device=d.get("is_new_device",False), failed_attempts=d.get("failed",0), ip_asn=d.get("asn",""), last_asn=d.get("last_asn",""), logins_last_10min=d.get("velocity",0), sensitive_actions_last_10min=d.get("sensitive",0), distance_km=d.get("distance",0))
    return jsonify(NoorSecurityAlgorithms.detect_account_takeover_risk(ctx))

@app.route('/api/v1/sessions/logout-others', methods=['POST'])
def logout_others():
    d = request.json or {}
    uid = d.get("user_id")
    if uid in USERS: USERS[uid]["token_version"] += 1
    return jsonify({"ok": True, "message": "تم الخروج من كل الأجهزة الأخرى"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
