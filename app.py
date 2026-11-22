import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

db_url = os.environ.get("DATABASE_URL", "").strip()
if not db_url or "://" not in db_url:
    db_url = "sqlite:///noorbook.db"
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text, default="")
    avatar = db.Column(db.String(500), default="")
    cover = db.Column(db.String(500), default="")
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500), default="")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="posts")

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, nullable=False)
    following_id = db.Column(db.Integer, nullable=False)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(500), default="")
    text = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    from_id = db.Column(db.Integer, default=0)
    type = db.Column(db.String(50), default="info")
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def ud(u):
    if not u: return {}
    followers = Follow.query.filter_by(following_id=u.id).count()
    following = Follow.query.filter_by(follower_id=u.id).count()
    posts_c = Post.query.filter_by(user_id=u.id).count()
    return {"id": u.id, "username": u.username, "email": u.email, "bio": u.bio or "", "avatar": u.avatar or "", "cover": u.cover or "", "is_online": u.is_online, "followers": followers, "following": following, "posts_count": posts_c}

def notify(uid, fid, typ, text):
    if uid == fid: return
    n = Notification(user_id=uid, from_id=fid, type=typ, content=text)
    db.session.add(n)
    db.session.commit()

@app.route("/")
def index():
    if os.path.exists("index.html"):
        return open("index.html", encoding="utf-8").read()
    return "<h1>NoorBook</h1>"

@app.route("/api/register", methods=["POST"])
def register():
    d = request.get_json() or {}
    if User.query.filter_by(username=d.get("username")).first():
        return jsonify({"error": "اسم المستخدم موجود"}), 400
    if User.query.filter_by(email=d.get("email")).first():
        return jsonify({"error": "الايميل موجود"}), 400
    u = User(username=d.get("username"), email=d.get("email"), password=generate_password_hash(d.get("password", "")), is_online=True)
    db.session.add(u); db.session.commit()
    return jsonify({"user": ud(u)})

@app.route("/api/login", methods=["POST"])
def login():
    d = request.get_json() or {}
    u = User.query.filter_by(email=d.get("email")).first()
    if u and check_password_hash(u.password, d.get("password", "")):
        u.is_online = True; u.last_seen = datetime.utcnow; db.session.commit()
        return jsonify({"user": ud(u)})
    return jsonify({"error": "بيانات خاطئة"}), 401

@app.route("/api/users")
def users():
    q = request.args.get("q", "")
    all_u = User.query.all()
    if q:
        all_u = [x for x in all_u if q.lower() in x.username.lower()]
    return jsonify({"users": [ud(x) for x in all_u]})

@app.route("/api/profile/<int:uid>", methods=["GET", "PUT"])
def profile(uid):
    u = User.query.get_or_404(uid)
    if request.method == "PUT":
        d = request.get_json() or {}
        u.bio = d.get("bio", u.bio); u.avatar = d.get("avatar", u.avatar); u.cover = d.get("cover", u.cover)
        db.session.commit()
    return jsonify(ud(u))

@app.route("/api/follow", methods=["POST"])
def follow():
    d = request.get_json() or {}
    fid = d.get("follower_id"); tid = d.get("following_id")
    ex = Follow.query.filter_by(follower_id=fid, following_id=tid).first()
    if ex:
        db.session.delete(ex); db.session.commit()
        return jsonify({"following": False})
    db.session.add(Follow(follower_id=fid, following_id=tid)); db.session.commit()
    fuser = User.query.get(fid)
    notify(tid, fid, "follow", "تابعك " + (fuser.username if fuser else ""))
    return jsonify({"following": True})

@app.route("/api/is_following")
def is_following():
    fid = request.args.get("follower_id", type=int); tid = request.args.get("following_id", type=int)
    ex = Follow.query.filter_by(follower_id=fid, following_id=tid).first()
    return jsonify({"following": bool(ex)})

@app.route("/api/posts", methods=["GET", "POST"])
def posts():
    if request.method == "POST":
        d = request.get_json() or {}
        p = Post(content=d.get("content"), image=d.get("image", ""), user_id=d.get("user_id"))
        db.session.add(p); db.session.commit()
        return jsonify({"message": "تم"})
    all_p = Post.query.all()
    scored = []
    for p in all_p:
        likes = Like.query.filter_by(post_id=p.id).count()
        comments = Comment.query.filter_by(post_id=p.id).count()
        age_hours = (datetime.utcnow() - (p.created_at or datetime.utcnow)).total_seconds() / 3600
        score = (likes * 3 + comments * 2) - (age_hours * 0.5)
        scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for score, p in scored:
        likes = Like.query.filter_by(post_id=p.id).count()
        comments = Comment.query.filter_by(post_id=p.id).count()
        out.append({"id": p.id, "content": p.content, "image": p.image, "user_id": p.user_id, "username": p.user.username if p.user else "", "avatar": p.user.avatar if p.user else "", "likes": likes, "comments": comments, "score": round(score, 1), "created_at": p.created_at.isoformat() if p.created_at else ""})
    return jsonify({"posts": out})

@app.route("/api/posts/<int:pid>", methods=["DELETE"])
def del_post(pid):
    p = Post.query.get_or_404(pid)
    db.session.delete(p); db.session.commit()
    return jsonify({"message": "تم"})

@app.route("/api/like", methods=["POST"])
def like():
    d = request.get_json() or {}
    ex = Like.query.filter_by(user_id=d.get("user_id"), post_id=d.get("post_id")).first()
    p = Post.query.get(d.get("post_id"))
    if ex:
        db.session.delete(ex); db.session.commit()
        return jsonify({"liked": False, "likes": Like.query.filter_by(post_id=d.get("post_id")).count()})
    db.session.add(Like(user_id=d.get("user_id"), post_id=d.get("post_id"))); db.session.commit()
    if p:
        u = User.query.get(d.get("user_id"))
        notify(p.user_id, d.get("user_id"), "like", "اعجب بمنشورك " + (u.username if u else ""))
    return jsonify({"liked": True, "likes": Like.query.filter_by(post_id=d.get("post_id")).count()})

@app.route("/api/comments/<int:pid>", methods=["GET", "POST"])
def comments(pid):
    if request.method == "POST":
        d = request.get_json() or {}
        c = Comment(post_id=pid, user_id=d.get("user_id"), content=d.get("content"))
        db.session.add(c); db.session.commit()
        p = Post.query.get(pid)
        if p:
            u = User.query.get(d.get("user_id"))
            notify(p.user_id, d.get("user_id"), "comment", "علق على منشورك: " + d.get("content", "")[:30])
        return jsonify({"message": "تم"})
    all_c = Comment.query.filter_by(post_id=pid).order_by(Comment.created_at.asc()).all()
    out = []
    for c in all_c:
        u = User.query.get(c.user_id)
        out.append({"id": c.id, "content": c.content, "username": u.username if u else "", "avatar": u.avatar if u else "", "created_at": c.created_at.isoformat() if c.created_at else ""})
    return jsonify({"comments": out})

@app.route("/api/stories", methods=["GET", "POST"])
def stories():
    if request.method == "POST":
        d = request.get_json() or {}
        s = Story(user_id=d.get("user_id"), image=d.get("image", ""), text=d.get("text", ""))
        db.session.add(s); db.session.commit()
        return jsonify({"message": "تم"})
    cutoff = datetime.utcnow() - timedelta(hours=24)
    all_s = Story.query.filter(Story.created_at >= cutoff).order_by(Story.created_at.desc()).all()
    out = []
    for s in all_s:
        u = User.query.get(s.user_id)
        out.append({"id": s.id, "user_id": s.user_id, "username": u.username if u else "", "avatar": u.avatar if u else "", "image": s.image, "text": s.text})
    return jsonify({"stories": out})

@app.route("/api/messages", methods=["GET", "POST"])
def messages():
    if request.method == "POST":
        d = request.get_json() or {}
        m = Message(sender_id=d.get("sender_id"), receiver_id=d.get("receiver_id"), content=d.get("content"))
        db.session.add(m); db.session.commit()
        s = User.query.get(d.get("sender_id"))
        notify(d.get("receiver_id"), d.get("sender_id"), "message", "رسالة جديدة من " + (s.username if s else ""))
        return jsonify({"message": "تم"})
    uid = request.args.get("user_id", type=int); oid = request.args.get("other_id", type=int)
    msgs = Message.query.filter(((Message.sender_id == uid) & (Message.receiver_id == oid)) | ((Message.sender_id == oid) & (Message.receiver_id == uid))).order_by(Message.created_at.asc()).all()
    for m in msgs:
        if m.receiver_id == uid: m.is_read = True
    db.session.commit()
    out = [{"id": m.id, "sender_id": m.sender_id, "content": m.content, "created_at": m.created_at.isoformat() if m.created_at else ""} for m in msgs]
    return jsonify({"messages": out})

@app.route("/api/conversations/<int:uid>")
def convs(uid):
    msgs = Message.query.filter((Message.sender_id == uid) | (Message.receiver_id == uid)).order_by(Message.created_at.desc()).all()
    mp = {}
    for m in msgs:
        other = m.receiver_id if m.sender_id == uid else m.sender_id
        if other not in mp:
            u = User.query.get(other)
            mp[other] = {"user_id": other, "username": u.username if u else "", "avatar": u.avatar if u else "", "is_online": u.is_online if u else False, "last_message": m.content, "unread": 0, "created_at": m.created_at.isoformat() if m.created_at else ""}
        if m.receiver_id == uid and not m.is_read: mp[other]["unread"] += 1
    return jsonify({"conversations": list(mp.values())})

@app.route("/api/notifications/<int:uid>")
def notifs(uid):
    all_n = Notification.query.filter_by(user_id=uid).order_by(Notification.created_at.desc()).all()
    out = [{"id": n.id, "content": n.content, "type": n.type, "is_read": n.is_read, "created_at": n.created_at.isoformat() if n.created_at else ""} for n in all_n]
    return jsonify({"notifications": out})

@app.route("/api/notifications/<int:uid>/read", methods=["POST"])
def read_all(uid):
    for n in Notification.query.filter_by(user_id=uid).all(): n.is_read = True
    db.session.commit()
    return jsonify({"message": "تم"})

@app.route("/api/logout/<int:uid>", methods=["POST"])
def logout(uid):
    u = User.query.get(uid)
    if u: u.is_online = False; db.session.commit()
    return jsonify({"message": "تم"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
