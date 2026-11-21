# Noor Super App - نور بوك + نور شات + نور قرام + نور ثريدز - كل شي في app.py واحد
from flask import Flask, request, jsonify
from flask_cors import CORS
import os, uuid, hashlib, math, random
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

app = Flask(__name__)
CORS(app)
USERS={}; POSTS=[]; CHATS={}; MESSAGES={}; SETTINGS={}; COMMENTS={}; FRIENDS=[]; GROUPS=[]; NOTIFS=[]; STORIES=[]; SAVED=[]

# ===== خوارزميات نور =====
@dataclass
class LoginContext:
    ip_country: str; last_country: str; hours_since_last_login: float; is_new_device: bool; failed_attempts: int
    ip_asn: str=""; last_asn: str=""; logins_last_10min: int=0; sensitive_actions_last_10min: int=0; distance_km: float=0.0; is_tor: bool=False; is_datacenter_ip: bool=False

class NoorAlgo:
    @staticmethod
    def feed_rank(posts, user_id="demo"):
        # خوارزمية الفيد زي فيسبوك: اصحابك + تفاعل + جديد
        def score(p):
            s=0
            if p.get("author_id") in [f["id"] for f in FRIENDS]: s+=50
            s+= p.get("likes_count",0)*2 + p.get("comments_count",0)*3 + p.get("shares_count",0)*4
            if p.get("media_type") in ["image","video"]: s+=10
            return s
        return sorted(posts, key=score, reverse=True)
    @staticmethod
    def suggest_friends():
        # خوارزمية اقتراح اصدقاء - اصدقاء مشتركين
        names=[("أحمد علي","عطبرة",5),("سارة محمد","الخرطوم",12),("نور الهدى","بورتسودان",3),("يوسف إبراهيم","عطبرة",8),("خديجة حسن","مدني",2),("محمد عثمان","كسلا",15)]
        return [{"id":str(uuid.uuid4()),"name":n,"city":c,"mutual":m,"avatar":f"https://i.pravatar.cc/150?u={n}"} for n,c,m in names]
    @staticmethod
    def privacy_score(s):
        score=100; recs=[]
        def pen(a,t,imp):
            nonlocal score; score-=a; recs.append({"title":t,"impact":imp})
        if not s.get("two_factor_enabled"): pen(30,"تفعيل المصادقة الثنائية","+30%")
        if s.get("default_post_audience")=="PUBLIC": pen(15,"تقييد المنشورات للأصدقاء","+15%")
        if s.get("app_lock_timeout",0)==0: pen(10,"تفعيل قفل نور شات","+10%")
        if s.get("active_status",True): pen(5,"إخفاء حالة النشاط","+5%")
        return {"privacy_score":max(0,score),"status":"ممتاز 🟢" if score>=85 else "جيد 🟡" if score>=70 else "يحتاج تحسين 🔴","total_issues":len(recs),"quick_fixes":recs}
    @staticmethod
    def ato_risk(ctx):
        travel=1.0 if ctx.ip_country!=ctx.last_country and ctx.hours_since_last_login<2 else 0.0
        z=(0.25*travel+0.2*(1 if ctx.is_new_device else 0))*4-1.5
        r=round(1/(1+math.exp(-z)),2)
        return {"risk_score":r,"action_required":"BIOMETRIC" if r>=0.75 else "ALLOW","message":"دخول آمن" if r<0.75 else "نشاط غير عادي"}

# بيانات اولية زي فيسبوك
for i,n in enumerate(["PRO FM 106.6","الحدث السوداني","نور نيوز","عطبرة اليوم"]):
    POSTS.append({"post_id":str(uuid.uuid4()),"author_id":f"page{i}","author_name":n,"author_avatar":f"https://i.pravatar.cc/150?u={n}","content":"من أرشيف بودكاست سودان بلس ... تابعونا للمزيد ❤️","media_url":"https://picsum.photos/600/400?random="+str(i),"media_type":"image","kind":"post","audience":"PUBLIC","likes_count":random.randint(50,1500),"comments_count":random.randint(5,80),"shares_count":random.randint(2,40),"liked":False,"is_page":True,"created_at":datetime.now().isoformat()}); COMMENTS[POSTS[-1]["post_id"]]=[{"author":"أزاهر","content":"كلام في محله.."}]
for n in ["عفاف محمد","سليمان ادم أحمد","Mechanical FX"]:
    STORIES.append({"id":str(uuid.uuid4()),"name":n,"img":f"https://i.pravatar.cc/300?u={n}"})
for n in ["مجموعة عطبرة","سوق السودان","ذكريات نهر النيل"]:
    GROUPS.append({"id":str(uuid.uuid4()),"name":n,"members":random.randint(1200,15000),"img":f"https://i.pravatar.cc/150?u={n}"})

HTML = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>نور - Noor</title><style>*{box-sizing:border-box;margin:0;padding:0;font-family:system-ui}body{background:#f0f2f5;padding-bottom:85px}header{background:#fff;padding:10px 12px;display:flex;align-items:center;gap:10px;position:sticky;top:0;z-index:99;box-shadow:0 1px 5px #0001}.logo{width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#2563eb,#06b6d4,#a855f7);color:#fff;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:900}.hbtn{width:38px;height:38px;border-radius:50%;background:#f0f2f5;border:none;font-size:18px;cursor:pointer;position:relative}.hbtn b{position:absolute;top:-4px;left:-4px;background:#e11d48;color:#fff;font-size:10px;padding:2px 6px;border-radius:10px}.card{background:#fff;border-radius:16px;padding:14px;margin:10px;box-shadow:0 1px 3px #0001}.flex{display:flex;gap:10px;align-items:center}.avatar{width:42px;height:42px;border-radius:50%;object-fit:cover}input[type=text]{flex:1;background:#f0f2f5;border:none;padding:11px;border-radius:20px;outline:none}.btn{background:#2563eb;color:#fff;border:none;padding:10px 18px;border-radius:20px;font-weight:800;cursor:pointer}.post{line-height:1.6;font-size:15px;margin:10px 0}.post img,.post video{width:100%;border-radius:14px;margin-top:8px;max-height:420px;object-fit:cover}.actions{display:flex;gap:6px;border-top:1px solid #eee;padding-top:10px;margin-top:10px}.actions button{flex:1;padding:9px;border:none;border-radius:20px;background:#f0f2f5;font-weight:700;cursor:pointer}.actions button.active{background:#dbeafe;color:#2563eb}.stories{display:flex;gap:8px;overflow-x:auto;padding:0 10px}.story{min-width:105px;height:155px;border-radius:16px;position:relative;overflow:hidden;background:#ddd;cursor:pointer}.story img{width:100%;height:100%;object-fit:cover}.story span{position:absolute;bottom:8px;right:8px;color:#fff;font-weight:800;font-size:12px;text-shadow:0 1px 3px #000}.story .plus{position:absolute;top:8px;right:8px;width:28px;height:28px;background:#2563eb;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center}.chat-item{display:flex;gap:10px;align-items:center;padding:12px;background:#fff;border-radius:16px;margin:8px 10px;cursor:pointer}.msg{max-width:80%;padding:10px 14px;border-radius:18px;margin:6px 0;font-size:14px}.msg.me{background:#2563eb;color:#fff;margin-right:auto}.msg.other{background:#fff;box-shadow:0 1px 3px #0001}.toggle{width:48px;height:28px;border-radius:20px;background:#ccc;position:relative;cursor:pointer;flex-shrink:0}.toggle.on{background:#2563eb}.toggle::after{content:"";position:absolute;width:22px;height:22px;background:#fff;border-radius:50%;top:3px;right:3px}.toggle.on::after{right:23px}nav{position:fixed;bottom:0;right:0;left:0;max-width:600px;margin:auto;background:#fff;display:flex;border-top:1px solid #eee;z-index:99}nav button{flex:1;padding:11px 2px;border:none;background:none;font-weight:900;font-size:12px;cursor:pointer;color:#888}nav button.active{color:#2563eb;border-top:3px solid #2563eb}.circle{width:64px;height:64px;border-radius:50%;border:4px solid #22c55e;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:18px}.hidden{display:none}.menu-item{display:flex;justify-content:space-between;align-items:center;padding:12px;background:#fff;border-radius:14px;margin:6px 10px;cursor:pointer}.menu-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:0 10px}.menu-grid div{background:#fff;border-radius:14px;padding:14px;text-align:center;font-weight:800;font-size:13px;cursor:pointer}.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2px}.grid3 img{width:100%;aspect-ratio:1;object-fit:cover}.reel{height:520px;border-radius:18px;overflow:hidden;position:relative;background:#000;margin:10px}.reel video,.reel img{width:100%;height:100%;object-fit:cover}.reel-info{position:absolute;bottom:12px;right:12px;left:60px;color:#fff}.reel-actions{position:absolute;left:10px;bottom:20px;display:flex;flex-direction:column;gap:12px}.reel-actions button{width:48px;height:48px;border-radius:50%;border:none;background:#ffffffcc;font-size:20px}.comment-box{display:flex;gap:6px;margin-top:10px}.comment{padding:8px 10px;background:#f0f2f5;border-radius:14px;margin-top:6px;font-size:13px}.composer-btns{display:flex;gap:6px;margin-top:10px}.composer-btns label,.composer-btns button{flex:1;text-align:center;padding:9px;border-radius:20px;background:#f0f2f5;font-weight:700;font-size:13px;cursor:pointer;border:none}.badge{background:#e11d48;color:#fff;font-size:11px;padding:2px 7px;border-radius:10px}.section{padding:0 10px;font-weight:900;margin:14px 0 6px}</style></head><body>
<header><div class="logo">ن</div><div style="flex:1"><b style="font-size:20px">نور <span style="color:#2563eb">Noor</span></b><div style="font-size:11px;color:#888">نور بوك • نور شات • نور قرام</div></div><button class="hbtn" onclick="show('menu')">☰</button><button class="hbtn" onclick="show('chat')">💬<b>9+</b></button><button class="hbtn" onclick="show('notif')">🔔<b>3</b></button></header>

<!-- نور بوك -->
<div id="tab-book"><div class="card"><div class="flex"><img class="avatar" src="https://i.pravatar.cc/150?u=me"><input id="newPost" type="text" placeholder="بم تفكر؟..."><button class="btn" onclick="openComposer()">نشر</button></div><div id="composer" class="hidden"><div id="preview"></div><div class="composer-btns"><label>📷 صورة<input type="file" accept="image/*" hidden onchange="pickFile(this,'image')"></label><label>🎥 فيديو<input type="file" accept="video/*" hidden onchange="pickFile(this,'video')"></label><button onclick="setType('reel')">🎬 ريلز</button><button onclick="createPost()" style="background:#2563eb;color:#fff">نشر 🚀</button></div><div id="postType" style="font-size:12px;color:#2563eb;margin-top:6px">بوست عادي 📝</div><input id="mediaUrl" type="text" placeholder="أو الصق رابط صورة / فيديو" style="width:100%;margin-top:8px;padding:10px;border-radius:12px;border:1px solid #eee"></div></div>
<div class="section">القصص • Stories</div><div class="stories" id="stories"></div>
<div class="section">أشخاص قد تعرفهم • خوارزمية نور 🤖</div><div id="suggest" style="display:flex;gap:8px;overflow-x:auto;padding:0 10px"></div>
<div class="section">آخر المنشورات • خوارزمية الفيد ✨</div><div id="posts"></div><div class="card" style="text-align:center;color:#888" id="empty">لا منشورات</div>
<div class="section">المجموعات • Groups</div><div id="groups"></div></div>

<!-- نور قرام -->
<div id="tab-gram" class="hidden"><div class="card"><b>📸 نور قرام - NoorGram</b><p style="font-size:12px;color:#888">زي انستقرام - لكن حقك</p></div><div class="stories" id="stories2"></div><div style="display:flex;gap:6px;padding:0 10px"><button class="btn" style="flex:1" onclick="gramTab('grid')">▦ المنشورات</button><button class="btn" style="flex:1;background:#eee;color:#000" onclick="gramTab('reels')">🎬 ريلز</button><button class="btn" style="flex:1;background:#eee;color:#000" onclick="gramTab('explore')">🔍 استكشاف</button></div><div id="gramGrid" class="grid3" style="margin:10px"></div><div id="gramReels"></div></div>

<!-- ريلز -->
<div id="tab-reels" class="hidden"><div class="card"><b>🎬 ريلز - Reels</b></div><div id="reels"></div><div class="card"><input id="reelText" type="text" placeholder="وصف الريل..."><input id="reelMedia" type="text" placeholder="رابط صورة / فيديو" style="width:100%;margin-top:8px;padding:10px;border-radius:12px;border:1px solid #eee"><button class="btn" style="width:100%;margin-top:8px;background:#e11d48" onclick="createReel()">+ نشر ريلز 🎬</button></div></div>

<!-- نور شات -->
<div id="tab-chat" class="hidden"><div class="card"><b>💬 نور شات - NoorChat</b><p style="font-size:12px;color:#888">مشفر 🔒 E2EE • زي ماسنجر</p></div><div class="section">نشط الآن 🟢</div><div style="display:flex;gap:10px;overflow-x:auto;padding:0 10px" id="activeNow"></div><div id="chatList"></div><div class="card"><input id="newChatName" type="text" placeholder="اسم المحادثة..."><button class="btn" style="margin-top:8px;width:100%;background:#16a34a" onclick="createChat()">+ محادثة جديدة</button></div><div id="chatBox" class="card hidden"><button onclick="closeChat()">← رجوع</button><h3 id="chatTitle"></h3><div style="display:flex;gap:6px;margin:8px 0"><button class="btn" style="flex:1;background:#16a34a">📞 صوت</button><button class="btn" style="flex:1;background:#7c3aed">📹 فيديو</button></div><div id="msgs" style="height:300px;overflow-y:auto;background:#f0f2f5;padding:10px;border-radius:12px"></div><div class="flex" style="margin-top:10px"><input id="newMsg" type="text" placeholder="اكتب رسالة..."><button class="btn" onclick="sendMsg()">إرسال</button></div></div></div>

<!-- ثريدز -->
<div id="tab-threads" class="hidden"><div class="card"><b>🧵 نور ثريدز - NoorThreads</b><p style="font-size:12px;color:#888">بوستات قصيرة - زي ثريدز</p></div><div class="card"><input id="threadText" type="text" placeholder="اكتب ثريد..."><button class="btn" style="width:100%;margin-top:8px" onclick="createThread()">نشر ثريد</button></div><div id="threads"></div></div>

<!-- اشعارات -->
<div id="tab-notif" class="hidden"><div class="card"><b>🔔 الإشعارات</b></div><div id="notifs"></div></div>

<!-- القائمة - زي صورك -->
<div id="tab-menu" class="hidden"><div class="card"><div class="flex"><img class="avatar" src="https://i.pravatar.cc/150?u=me"><div><b>يوسف إبراهيم</b><div style="font-size:12px;color:#888">عرض ملفك الشخصي</div></div></div><button class="btn" style="width:100%;margin-top:10px">+ إنشاء صفحة على نور بوك</button></div>
<div class="menu-grid"><div onclick="show('book')">🕐<br>الذكريات</div><div onclick="show('book')">🔖<br>العناصر المحفوظة</div><div onclick="show('book')">👥<br>الأصدقاء</div><div onclick="show('book')">👨‍👩‍👧<br>المجموعات</div><div onclick="show('reels')">🎬<br>ريلز</div><div onclick="show('book')">📰<br>الأخبار</div><div onclick="show('book')">📅<br>المناسبات</div><div onclick="show('book')">🎮<br>الألعاب</div></div>
<button class="btn" style="width:calc(100% - 20px);margin:10px;background:#e5e7eb;color:#000" onclick="toggleMore()">عرض المزيد ▼</button>
<div id="moreMenu" class="hidden"><div class="section">الإعدادات والخصوصية ⚙️</div><div class="menu-item" onclick="show('settings')"><span>⚙️ الإعدادات</span><span>›</span></div><div class="menu-item" onclick="show('settings')"><span>🔒 مركز الخصوصية</span><span>›</span></div><div class="menu-item" onclick="show('settings')"><span>⏰ إدارة الوقت</span><span>›</span></div><div class="menu-item" onclick="show('settings')"><span>📱 طلبات الأجهزة</span><span>›</span></div><div class="menu-item" onclick="show('settings')"><span>📢 أحدث نشاط إعلاني</span><span>›</span></div><div class="menu-item" onclick="show('settings')"><span>💳 الطلبات وعمليات الدفع</span><span>›</span></div><div class="menu-item" onclick="show('settings')"><span>🔗 سجل الروابط</span><span>›</span></div><div class="section">المساعدة والدعم ❓</div><div class="menu-item"><span>❓ المساعدة والدعم</span><span>›</span></div>
<div class="section">الترقيات ✨</div><div class="card"><b>الحضور العام</b><p style="font-size:12px;color:#888">احصل على أدوات تساعدك على النمو...</p></div>
<div class="section">أيضًا من نور 🟣</div><div class="menu-item" onclick="show('gram')"><span>📸 نور قرام - NoorGram</span><span>›</span></div><div class="menu-item" onclick="show('threads')"><span>🧵 نور ثريدز</span><span>›</span></div><div class="menu-item" onclick="show('chat')"><span>💬 نور شات - NoorChat</span><span>›</span></div><div class="menu-item"><span>✏️ نور إيديتس - تحرير الفيديو</span><span>›</span></div><div class="menu-item"><span>🆓 نور بيسكس - إنترنت مجاني</span><span>›</span></div>
<button class="btn" style="width:calc(100% - 20px);margin:10px;background:#e5e7eb;color:#000">تسجيل الخروج</button></div></div>

<!-- الاعدادات -->
<div id="tab-settings" class="hidden"><div class="card" style="background:linear-gradient(135deg,#2563eb,#06b6d4,#a855f7);color:#fff"><b style="font-size:18px">مركز حسابات نور</b><p style="font-size:13px;opacity:.8">نور بوك + نور شات + نور قرام - مربوطين</p><div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px"><button style="padding:10px;border:none;border-radius:12px;background:#ffffff33;color:#fff;font-weight:800">البيانات 👤</button><button style="padding:10px;border:none;border-radius:12px;background:#ffffff33;color:#fff;font-weight:800">الأمان 🔒</button><button style="padding:10px;border:none;border-radius:12px;background:#ffffff33;color:#fff;font-weight:800">معلوماتك 📄</button><button style="padding:10px;border:none;border-radius:12px;background:#ffffff33;color:#fff;font-weight:800">الإعلانات 🎯</button></div></div><div class="card"><div style="display:flex;gap:12px;align-items:center"><div class="circle" id="scoreCircle">100%</div><div style="flex:1"><b id="scoreStatus">ممتاز 🟢</b><p style="font-size:12px;color:#888" id="scoreIssues">0 مشاكل</p></div><button class="btn" onclick="fixAll()">إصلاح الكل ✨</button></div><div id="fixes" style="margin-top:10px;font-size:13px"></div></div><div class="card"><div class="flex" style="justify-content:space-between;margin-bottom:14px"><span><b>حالة النشاط</b></span><div class="toggle on" onclick="toggle(this,'activeStatus')"></div></div><div class="flex" style="justify-content:space-between;margin-bottom:14px"><span><b>قفل الملف الشخصي</b></span><div class="toggle" onclick="toggle(this,'profileLocked')"></div></div><div class="flex" style="justify-content:space-between;margin-bottom:14px"><span><b>إخفاء عدد التفاعلات</b></span><div class="toggle" onclick="toggle(this,'hideReactionCounts')"></div></div><div class="flex" style="justify-content:space-between;margin-bottom:14px"><span><b>مؤشرات القراءة</b></span><div class="toggle on" onclick="toggle(this,'readReceipts')"></div></div><div class="flex" style="justify-content:space-between;margin-bottom:14px"><span><b>فقاعات الدردشة</b></span><div class="toggle on" onclick="toggle(this,'chatHeads')"></div></div><div style="margin-bottom:14px"><div style="display:flex;justify-content:space-between"><b>المزيد من الأصدقاء - خوارزمية الفيد</b><b id="feedVal" style="color:#2563eb">75%</b></div><input type="range" min="0" max="100" value="75" style="width:100%" oninput="document.getElementById('feedVal').innerText=this.value+'%';syncSetting('friendsFeedWeight',Number(this.value))"></div><div><b>قفل نور شات بالبصمة</b><br><select onchange="syncSetting('appLockTimeout',Number(this.value))" style="width:100%;margin-top:6px;padding:8px;border-radius:12px"><option value="0">معطل</option><option value="1" selected>فوري</option><option value="60">بعد دقيقة</option></select></div><div style="margin-top:12px"><b>إدارة الوقت ⏰</b><p style="font-size:12px;color:#888">تذكير بعد 30 دقيقة يومياً في نور</p></div></div></div>

<nav><button id="btn-book" class="active" onclick="show('book')">📘<br>نور بوك</button><button id="btn-gram" onclick="show('gram')">📸<br>نور قرام</button><button id="btn-reels" onclick="show('reels')">🎬<br>ريلز</button><button id="btn-chat" onclick="show('chat')">💬<br>نور شات</button><button id="btn-threads" onclick="show('threads')">🧵<br>ثريدز</button><button id="btn-menu" onclick="show('menu')">☰<br>القائمة</button></nav>
<script>const API=window.location.origin;let posts=[],chats=[],activeChat=null,mediaData='',mediaType='image',postKind='post',stories=[],groups=[],suggest=[];
function pickFile(inp,type){const f=inp.files[0];if(!f)return;const r=new FileReader();r.onload=e=>{mediaData=e.target.result;mediaType=type;document.getElementById('preview').innerHTML=type==='image'?`<img src="${mediaData}" style="width:100%;border-radius:12px;margin-top:8px">`:`<video src="${mediaData}" controls style="width:100%;border-radius:12px"></video>`;};r.readAsDataURL(f);}
function openComposer(){document.getElementById('composer').classList.remove('hidden');}
function setType(t){postKind=t;document.getElementById('postType').innerText=t==='reel'?'ريلز 🎬 - حيظهر في الريلز':'بوست عادي 📝';}
async function loadAll(){const r=await fetch(API+'/api/v1/posts');posts=await r.json();const r2=await fetch(API+'/api/v1/stories');stories=await r2.json();const r3=await fetch(API+'/api/v1/suggest');suggest=await r3.json();const r4=await fetch(API+'/api/v1/groups');groups=await r4.json();const r5=await fetch(API+'/api/v1/chats');chats=await r5.json();renderAll();}
function renderAll(){renderPosts();renderStories();renderSuggest();renderGroups();renderChats();renderGram();renderReels();renderThreads();renderNotifs();}
function renderPosts(){document.getElementById('posts').innerHTML=posts.filter(p=>p.kind!=='reel'&&p.kind!=='thread').map(p=>`<div class="card"><div class="flex"><img class="avatar" src="${p.author_avatar}"><div style="flex:1"><b>${p.author_name} ${p.is_page?'✓':''}</b><div style="font-size:11px;color:#888">${p.audience==='FRIENDS'?'الأصدقاء 👥':'عام 🌍'} • الآن</div></div><button style="border:none;background:none">•••</button></div><p class="post">${p.content}${p.media_url?(p.media_type==='video'?`<video src="${p.media_url}" controls></video>`:`<img src="${p.media_url}">`):''}</p><div style="display:flex;justify-content:space-between;font-size:12px;color:#888"><span>❤️ ${p.likes_count} • 💬 ${p.comments_count} • ↗️ ${p.shares_count||0}</span></div><div class="actions"><button class="${p.liked?'active':''}" onclick="likePost('${p.post_id}')">${p.liked?'❤️ أعجبني':'🤍 أعجبني'}</button><button onclick="toggleComments('${p.post_id}')">💬 تعليق</button><button onclick="sharePost('${p.post_id}')">↗️ شير</button><button onclick="savePost('${p.post_id}')">🔖 حفظ</button></div><div id="c-${p.post_id}" class="hidden"><div id="clist-${p.post_id}"></div><div class="comment-box"><input id="cin-${p.post_id}" type="text" placeholder="اكتب تعليق..."><button class="btn" onclick="addComment('${p.post_id}')">إرسال</button></div></div></div>`).join('');}
function renderStories(){const h=`<div class="story" style="background:linear-gradient(#2563eb,#06b6d4);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900">+ قصتي</div>`+stories.map(s=>`<div class="story"><img src="${s.img}"><span>${s.name}</span></div>`).join('');document.getElementById('stories').innerHTML=h;document.getElementById('stories2').innerHTML=h;}
function renderSuggest(){document.getElementById('suggest').innerHTML=suggest.map(s=>`<div class="card" style="min-width:160px;text-align:center"><img src="${s.avatar}" style="width:70px;height:70px;border-radius:50%"><br><b>${s.name}</b><div style="font-size:11px;color:#888">${s.mutual} صديق مشترك • ${s.city}</div><button class="btn" style="width:100%;margin-top:6px" onclick="addFriend(this)">+ إضافة صديق</button><button style="width:100%;margin-top:4px;padding:8px;border:none;border-radius:20px;background:#eee">إزالة</button></div>`).join('');}
function renderGroups(){document.getElementById('groups').innerHTML=groups.map(g=>`<div class="card"><div class="flex"><img class="avatar" src="${g.img}"><div style="flex:1"><b>${g.name}</b><div style="font-size:12px;color:#888">${g.members} عضو</div></div><button class="btn" onclick="alert('انضممت للمجموعة ✅')">انضمام</button></div></div>`).join('');}
function renderChats(){document.getElementById('chatList').innerHTML=chats.map(c=>`<div class="chat-item" onclick="openChat('${c.chat_id}','${c.name}')"><img class="avatar" src="${c.avatar}"><div style="flex:1"><b>${c.name}</b><div style="font-size:13px;color:#888">${c.last_message||'ابدأ المحادثة'}</div></div><span style="width:8px;height:8px;background:#22c55e;border-radius:50%"></span></div>`).join('')||'<div class="card" style="text-align:center;color:#888">لا محادثات - اعمل محادثة جديدة</div>';document.getElementById('activeNow').innerHTML=chats.slice(0,5).map(c=>`<div style="text-align:center"><img src="${c.avatar}" style="width:52px;height:52px;border-radius:50%;border:2px solid #22c55e"><div style="font-size:11px">${c.name.split(' ')[0]}</div></div>`).join('')||suggest.slice(0,4).map(s=>`<div style="text-align:center"><img src="${s.avatar}" style="width:52px;height:52px;border-radius:50%;border:2px solid #22c55e"><div style="font-size:11px">${s.name.split(' ')[0]}</div></div>`).join('');}
function renderGram(){document.getElementById('gramGrid').innerHTML=posts.filter(p=>p.media_url).map(p=>`<img src="${p.media_url}" onclick="show('book')">`).join('')||'<p style="padding:10px;color:#888">لا صور بعد</p>';}
function gramTab(t){if(t==='reels')show('reels');if(t==='explore')alert('استكشاف نور قرام 🔍 - كل صور نور');if(t==='grid')document.getElementById('gramGrid').scrollIntoView();}
function renderReels(){const reels=posts.filter(p=>p.kind==='reel');document.getElementById('reels').innerHTML=reels.length?reels.map(p=>`<div class="reel">${p.media_type==='video'?`<video src="${p.media_url}" controls></video>`:p.media_url?`<img src="${p.media_url}">`:`<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#fff;font-size:20px;padding:20px;text-align:center">${p.content}</div>`}<div class="reel-info"><b>${p.author_name}</b><p>${p.content}</p></div><div class="reel-actions"><button onclick="likePost('${p.post_id}')">❤️<div style="font-size:11px">${p.likes_count}</div></button><button>💬</button><button onclick="sharePost('${p.post_id}')">↗️</button></div></div>`).join(''):'<div class="card" style="text-align:center;color:#888">لا ريلز بعد</div>';document.getElementById('gramReels').innerHTML=document.getElementById('reels').innerHTML;}
function renderThreads(){document.getElementById('threads').innerHTML=posts.filter(p=>p.kind==='thread').map(p=>`<div class="card"><div class="flex"><img class="avatar" src="${p.author_avatar}"><b>${p.author_name}</b></div><p>${p.content}</p><div class="actions"><button onclick="likePost('${p.post_id}')">❤️ ${p.likes_count}</button><button>💬 ${p.comments_count}</button><button onclick="sharePost('${p.post_id}')">↗️</button></div></div>`).join('')||'<div class="card" style="text-align:center;color:#888">لا ثريدز بعد</div>';}
function renderNotifs(){document.getElementById('notifs').innerHTML=`<div class="card">❤️ أحمد أعجب بمنشورك</div><div class="card">💬 سارة علقت: كلام جميل</div><div class="card">👥 يوسف أرسل طلب صداقة</div>`;}
async function createPost(){const v=document.getElementById('newPost').value;const url=document.getElementById('mediaUrl')?.value||'';const fm=url||mediaData;if(!v.trim()&&!fm)return alert('اكتب شي أو اختار صورة');await fetch(API+'/api/v1/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author_name:'أنت - Noor User',author_avatar:'https://i.pravatar.cc/150?u=me',content:v||'منشور جديد',media_url:fm,media_type:fm?(mediaType==='video'||url.includes('.mp4')?'video':'image'):'text',kind:postKind})});document.getElementById('newPost').value='';mediaData='';loadAll();}
async function createReel(){const v=document.getElementById('reelText').value;const url=document.getElementById('reelMedia').value;await fetch(API+'/api/v1/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author_name:'أنت',author_avatar:'https://i.pravatar.cc/150?u=me',content:v||'ريلز جديد 🎬',media_url:url,media_type:'video',kind:'reel'})});loadAll();show('reels');}
async function createThread(){const v=document.getElementById('threadText').value;if(!v.trim())return;await fetch(API+'/api/v1/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author_name:'أنت',author_avatar:'https://i.pravatar.cc/150?u=me',content:v,kind:'thread'})});document.getElementById('threadText').value='';loadAll();}
async function likePost(id){const r=await fetch(API+`/api/v1/posts/${id}/like`,{method:'POST'});const p=await r.json();posts=posts.map(x=>x.post_id===id?p:x);renderAll();}
async function sharePost(id){await fetch(API+`/api/v1/posts/${id}/share`,{method:'POST'});alert('تم نسخ رابط المنشور ✅');loadAll();}
async function savePost(id){alert('تم الحفظ في العناصر المحفوظة 🔖 ✅');}
async function toggleComments(id){const el=document.getElementById('c-'+id);el.classList.toggle('hidden');const r=await fetch(API+`/api/v1/posts/${id}/comments`);const cs=await r.json();document.getElementById('clist-'+id).innerHTML=cs.map(c=>`<div class="comment"><b>${c.author}</b> ${c.content}</div>`).join('')||'<div style="font-size:12px;color:#888">لا تعليقات</div>';}
async function addComment(id){const v=document.getElementById('cin-'+id).value;if(!v.trim())return;await fetch(API+`/api/v1/posts/${id}/comment`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author:'أنت',content:v})});document.getElementById('cin-'+id).value='';loadAll();}
function addFriend(btn){btn.innerText='تم الإرسال ✅';btn.style.background='#16a34a';}
async function createChat(){const n=document.getElementById('newChatName').value||'محادثة جديدة';await fetch(API+'/api/v1/chats',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,avatar:'https://i.pravatar.cc/150?u='+n})});document.getElementById('newChatName').value='';loadAll();}
async function openChat(id,name){activeChat=id;document.getElementById('chatTitle').innerText=name;document.getElementById('chatBox').classList.remove('hidden');const r=await fetch(API+`/api/v1/chats/${id}/messages`);const msgs=await r.json();document.getElementById('msgs').innerHTML=msgs.map(m=>`<div class="msg ${m.sender_id==='me'?'me':'other'}">${m.content}</div>`).join('');}
function closeChat(){document.getElementById('chatBox').classList.add('hidden');activeChat=null;}
async function sendMsg(){const v=document.getElementById('newMsg').value;if(!v.trim()||!activeChat)return;await fetch(API+`/api/v1/chats/${activeChat}/messages`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sender_id:'me',content:v})});document.getElementById('newMsg').value='';openChat(activeChat,document.getElementById('chatTitle').innerText);loadAll();}
function show(t){['book','gram','reels','chat','threads','notif','menu','settings'].forEach(x=>{const e=document.getElementById('tab-'+x);if(e)e.classList.toggle('hidden',x!==t);const b=document.getElementById('btn-'+x);if(b)b.classList.toggle('active',x===t);});if(t==='settings')loadPrivacy();}
function toggleMore(){document.getElementById('moreMenu').classList.toggle('hidden');}
async function syncSetting(k,v){await fetch(API+'/api/v1/settings/sync',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({[k]:v,user_id:'demo'})});}
function toggle(el,k){el.classList.toggle('on');syncSetting(k,el.classList.contains('on'));}
async function loadPrivacy(){const r=await fetch(API+'/api/v1/security/privacy-score',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({two_factor_enabled:false,default_post_audience:'FRIENDS',app_lock_timeout:1,active_status:true})});const d=await r.json();document.getElementById('scoreCircle').innerText=d.privacy_score+'%';document.getElementById('scoreStatus').innerText=d.status;document.getElementById('scoreIssues').innerText=d.total_issues+' مشاكل';document.getElementById('fixes').innerHTML=d.quick_fixes.map(f=>'• '+f.title+' '+f.impact).join('<br>');}
function fixAll(){alert('تم إصلاح كل المشاكل ✅');loadPrivacy();}
loadAll();
</script></body></html>"""

@app.route('/')
def home(): return HTML
@app.route('/api/v1/posts', methods=['GET'])
def get_posts(): return jsonify(NoorAlgo.feed_rank(POSTS))
@app.route('/api/v1/posts', methods=['POST'])
def create_post():
    d=request.json or {}; p={"post_id":str(uuid.uuid4()),"author_id":d.get("author_id","demo"),"author_name":d.get("author_name","Noor User"),"author_avatar":d.get("author_avatar","https://i.pravatar.cc/150?u=me"),"content":d.get("content",""),"media_url":d.get("media_url",""),"media_type":d.get("media_type","text"),"kind":d.get("kind","post"),"audience":d.get("audience","FRIENDS"),"likes_count":0,"comments_count":0,"shares_count":0,"liked":False,"is_page":False,"created_at":datetime.now().isoformat()}; POSTS.append(p); COMMENTS[p["post_id"]]=[]; return jsonify(p)
@app.route('/api/v1/posts/<pid>/like', methods=['POST'])
def like_post(pid):
    for p in POSTS:
        if p["post_id"]==pid: p["liked"]=not p["liked"]; p["likes_count"]+=1 if p["liked"] else -1; return jsonify(p)
    return jsonify({"error":"not found"}),404
@app.route('/api/v1/posts/<pid>/share', methods=['POST'])
def share_post(pid):
    for p in POSTS:
        if p["post_id"]==pid: p["shares_count"]=p.get("shares_count",0)+1; return jsonify(p)
    return jsonify({"error":"not found"}),404
@app.route('/api/v1/posts/<pid>/comments', methods=['GET'])
def get_comments(pid): return jsonify(COMMENTS.get(pid,[]))
@app.route('/api/v1/posts/<pid>/comment', methods=['POST'])
def comment_post(pid):
    d=request.json or {}
    for p in POSTS:
        if p["post_id"]==pid: p["comments_count"]+=1; COMMENTS.setdefault(pid,[]).append({"author":d.get("author","أنت"),"content":d.get("content","")}); return jsonify({"ok":True})
    return jsonify({"error":"not found"}),404
@app.route('/api/v1/stories', methods=['GET'])
def get_stories(): return jsonify(STORIES)
@app.route('/api/v1/suggest', methods=['GET'])
def get_suggest(): return jsonify(NoorAlgo.suggest_friends())
@app.route('/api/v1/groups', methods=['GET'])
def get_groups(): return jsonify(GROUPS)
@app.route('/api/v1/settings/sync', methods=['PATCH'])
def sync_settings():
    d=request.json or {}; uid=d.get("user_id","demo"); SETTINGS.setdefault(uid,{}).update(d); return jsonify({"ok":True})
@app.route('/api/v1/chats', methods=['GET'])
def get_chats(): return jsonify(list(CHATS.values()))
@app.route('/api/v1/chats', methods=['POST'])
def create_chat():
    d=request.json or {}; cid=str(uuid.uuid4()); CHATS[cid]={"chat_id":cid,"name":d.get("name","محادثة"),"avatar":d.get("avatar",f"https://i.pravatar.cc/150?u={cid}"),"last_message":"","unread":0,"online":True}; return jsonify(CHATS[cid])
@app.route('/api/v1/chats/<cid>/messages', methods=['GET'])
def get_messages(cid): return jsonify(MESSAGES.get(cid,[]))
@app.route('/api/v1/chats/<cid>/messages', methods=['POST'])
def send_message(cid):
    d=request.json or {}; m={"message_id":str(uuid.uuid4()),"chat_id":cid,"sender_id":d.get("sender_id","me"),"content":d.get("content",""),"created_at":datetime.now().isoformat()}; MESSAGES.setdefault(cid,[]).append(m)
    if cid in CHATS: CHATS[cid]["last_message"]=d.get("content","")
    return jsonify(m)
@app.route('/api/v1/security/privacy-score', methods=['POST'])
def privacy_score(): return jsonify(NoorAlgo.privacy_score(request.json or {}))
@app.route('/api/v1/security/ato-check', methods=['POST'])
def ato_check():
    d=request.json or {}; ctx=LoginContext(ip_country=d.get("ip_country","SD"),last_country=d.get("last_country","SD"),hours_since_last_login=d.get("hours",24),is_new_device=d.get("is_new_device",False),failed_attempts=d.get("failed",0)); return jsonify(NoorAlgo.ato_risk(ctx))

if __name__=='__main__': app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
