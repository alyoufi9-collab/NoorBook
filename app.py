from flask import Flask, request, redirect, url_for, render_template_string
import datetime

app = Flask(__name__)

# تخزين مؤقت
users = {}
posts = []
chats = {} # (user1,user2) -> messages
stories = []
notifications = []
friends = {}

HTML = """
<!DOCTYPE html>
<html dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NoorBook - زي فيسبوك واحسن</title>
<style>
*{box-sizing:border-box} body{margin:0;font-family:system-ui;background:#f0f2f5}
.top{background:#fff;padding:10px 15px;display:flex;gap:10px;align-items:center;position:sticky;top:0;box-shadow:0 1px 5px #0002;z-index:10}
.logo{font-size:24px;font-weight:900;color:#1877f2} .logo span{color:#00b96f}
.top input{flex:1;padding:10px;border-radius:20px;border:0;background:#f0f2f5}
.tabs{display:flex;background:#fff} .tabs a{flex:1;text-align:center;padding:12px;text-decoration:none;color:#333;font-weight:700;border-bottom:3px solid transparent} .tabs a.active{color:#1877f2;border-color:#1877f2}
.wrap{max-width:600px;margin:auto;padding:10px}
.card{background:#fff;border-radius:12px;padding:12px;margin-bottom:12px;box-shadow:0 1px 3px #0001}
.stories{display:flex;gap:8px;overflow:auto;padding:5px} .story{min-width:110px;height:170px;border-radius:12px;background:linear-gradient(#1877f2,#00b96f);color:#fff;padding:10px;display:flex;align-items:flex-end;font-weight:700}
input,textarea,select{width:100%;padding:11px;border-radius:10px;border:1px solid #ddd;margin:5px 0}
.btn{background:#1877f2;color:#fff;border:0;padding:12px;border-radius:10px;font-weight:800;width:100%}
.btn2{background:#00b96f} .post-img{width:100%;border-radius:10px;margin-top:8px}
.actions{display:flex;gap:5px;margin-top:10px} .actions a{flex:1;text-align:center;background:#f0f2f5;padding:8px;border-radius:20px;text-decoration:none;color:#333}
.chatbox{height:300px;overflow:auto;background:#f9f9f9;padding:10px;border-radius:10px} .msg{background:#e4e6eb;padding:8px 12px;border-radius:15px;margin:5px 0;max-width:80%} .me{background:#1877f2;color:#fff;margin-left:auto}
.online{color:#00b96f;font-weight:700}
</style></head><body>
<div class="top"><div class="logo">Noor<span>Book</span></div><input placeholder="🔍 ابحث عن اصدقاء، منشورات..."><a href="/?user={{user}}">🏠</a><a href="/chat?user={{user}}">💬</a><a href="/noti?user={{user}}">🔔 {{noti_count}}</a></div>
<div class="tabs"><a href="/?user={{user}}" class="{{'active' if page=='home' else ''}}">🏠 فيسبوك</a><a href="/chat?user={{user}}" class="{{'active' if page=='chat' else ''}}">💬 ماسنجر</a><a href="/friends?user={{user}}">👥 اصدقاء</a><a href="/profile?user={{user}}">👤 بروفايلي</a></div>
<div class="wrap">
{% if page=='home' %}
<div class="card"><b>👋 اهلا {{user or 'ضيف'}}</b><form method="post" action="/login"><input name="name" placeholder="اكتب اسمك للدخول..." value="{{user}}"><button class="btn">دخول / انشاء حساب</button></form></div>
<div class="stories"><div class="story">+ قصتي</div>{% for s in stories %}<div class="story">{{s}}</div>{% endfor %}<div class="story">🔥 قصص الاصدقاء</div></div>
<div class="card"><form method="post" action="/post?user={{user}}"><textarea name="text" placeholder="شنو في بالك يا {{user}}؟" required></textarea><input name="img" placeholder="رابط صورة (اختياري)"><button class="btn btn2">انشر 📢</button></form></div>
{% for p in posts|reverse %}
<div class="card"><b>👤 {{p.user}}</b> <small>{{p.time}} • 🌍 عام</small><p>{{p.text}}</p>{% if p.img %}<img class="post-img" src="{{p.img}}">{% endif %}<div class="actions"><a href="/like/{{loop.index0}}?user={{user}}">❤️ لايك ({{p.likes}})</a><a href="/post/{{loop.index0}}?user={{user}}">💬 تعليق ({{p.comments|length}})</a><a href="/chat?user={{user}}&to={{p.user}}">💬 راسلو</a></div>{% for c in p.comments %}<div style="background:#f0f2f5;padding:8px;border-radius:10px;margin-top:5px"><b>{{c.user}}:</b> {{c.text}}</div>{% endfor %}<form method="post" action="/comment/{{loop.index0}}?user={{user}}"><input name="text" placeholder="اكتب تعليق..." required></form></div>
{% endfor %}
{% elif page=='chat' %}
<div class="card"><h3>💬 ماسنجر - NoorChat</h3><p class="online">● 12 صديق اونلاين الان</p><form><input name="to" placeholder="اكتب اسم الشخص الداير تراسلو..." value="{{to}}"><input type="hidden" name="user" value="{{user}}"><button class="btn">فتح الشات</button></form></div>
{% if to %}<div class="card"><b>💬 شات مع {{to}}</b><div class="chatbox">{% for m in msgs %}<div class="msg {{'me' if m.user==user else ''}}"><b>{{m.user}}:</b> {{m.text}}</div>{% endfor %}</div><form method="post" action="/send?user={{user}}&to={{to}}"><input name="text" placeholder="اكتب رسالة..." required><button class="btn btn2">ارسال ➤</button></form></div>{% endif %}
<div class="card"><b>محادثاتك الاخيرة</b><p>👤 احمد - اها وينك؟</p><p>👤 سارة - الصورة رهيبة 🔥</p><p>👤 قروب العائلة - 5 رسائل جديدة</p></div>
{% elif page=='friends' %}
<div class="card"><h3>👥 اقتراحات اصدقاء</h3>{% for f in ['احمد علي','سارة محمد','مصطفى نور','ريم عبدالله','خالد حسن'] %}<p>👤 {{f}} <a href="/addfriend?name={{f}}&user={{user}}">+ اضافة صديق</a></p>{% endfor %}</div>
<div class="card"><h3>اصدقائك: {{myfriends}}</h3></div>
{% elif page=='profile' %}
<div class="card" style="text-align:center"><div style="font-size:60px">👤</div><h2>{{user or 'زائر'}}</h2><p>📍 عطبرة - السودان | 🎓 NoorBook</p><p>👥 {{myfriends|length}} صديق | 📝 {{myposts}} منشور</p><button class="btn">تعديل البروفايل</button></div>
{% elif page=='noti' %}
<div class="card"><h3>🔔 الاشعارات</h3>{% for n in notifications %}<p>{{n}}</p>{% endfor %}<p>❤️ احمد عمل لايك لمنشورك</p><p>💬 سارة علقت: رهيب والله</p><p>👥 مصطفى قبل طلب صداقتك</p></div>
{% endif %}
</div></body></html>
"""

@app.route('/')
def home():
    user=request.args.get('user','')
    return render_template_string(HTML, user=user, page='home', posts=posts, stories=stories, noti_count=len(notifications), myfriends=[], myposts=0)
@app.route('/login', methods=['POST'])
def login():
    name=request.form.get('name','ضيف')
    users[name]=name
    return redirect(f'/?user={name}')
@app.route('/post', methods=['POST'])
def post():
    user=request.args.get('user','ضيف')
    posts.append({'user':user,'text':request.form.get('text',''),'img':request.form.get('img',''),'likes':0,'comments':[],'time':datetime.datetime.now().strftime('%H:%M')})
    notifications.append(f'{user} نشر منشور جديد')
    return redirect(f'/?user={user}')
@app.route('/like/<int:id>')
def like(id):
    user=request.args.get('user','')
    if 0 <= id < len(posts): posts[id]['likes']+=1
    return redirect(f'/?user={user}')
@app.route('/comment/<int:id>', methods=['POST'])
def comment(id):
    user=request.args.get('user','ضيف')
    if 0 <= id < len(posts): posts[id]['comments'].append({'user':user,'text':request.form.get('text','')})
    return redirect(f'/?user={user}')
@app.route('/post/<int:id>')
def view_post(id):
    return redirect(f"/?user={request.args.get('user','')}")
@app.route('/chat')
def chat():
    user=request.args.get('user',''); to=request.args.get('to','')
    key=tuple(sorted([user,to])) if to else ()
    msgs=chats.get(key,[])
    return render_template_string(HTML, user=user, page='chat', posts=[], stories=[], noti_count=0, to=to, msgs=msgs, myfriends=[], myposts=0)
@app.route('/send', methods=['POST'])
def send():
    user=request.args.get('user',''); to=request.args.get('to','')
    key=tuple(sorted([user,to]))
    chats.setdefault(key,[]).append({'user':user,'text':request.form.get('text','')})
    return redirect(f'/chat?user={user}&to={to}')
@app.route('/friends')
def friends_page():
    user=request.args.get('user','')
    return render_template_string(HTML, user=user, page='friends', posts=[], stories=[], noti_count=0, myfriends=friends.get(user,[]), myposts=0)
@app.route('/addfriend')
def addfriend():
    user=request.args.get('user',''); name=request.args.get('name','')
    friends.setdefault(user,[]).append(name)
    return redirect(f'/friends?user={user}')
@app.route('/profile')
def profile():
    user=request.args.get('user','')
    myposts=len([p for p in posts if p['user']==user])
    return render_template_string(HTML, user=user, page='profile', posts=[], stories=[], noti_count=0, myfriends=friends.get(user,[]), myposts=myposts)
@app.route('/noti')
def noti():
    user=request.args.get('user','')
    return render_template_string(HTML, user=user, page='noti', posts=[], stories=[], noti_count=0, notifications=notifications, myfriends=[], myposts=0)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=10000)
