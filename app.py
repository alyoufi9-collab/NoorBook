import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500), default="")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="posts")

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
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def ud(u):
    return {"id": u.id, "username": u.username, "email": u.email, "bio": u.bio or "", "avatar": u.avatar or ""}

@app.route("/")
def index():
    html = open("index.html", encoding="utf-8").read() if os.path.exists("index.html") else "<h1>NoorBook</h1>"
    return html

@app.route("/api/register", methods=["POST"])
def register():
    d = request.get_json() or {}
    if User.query.filter_by(username=d.get("username")).first():
        return jsonify({"error": "اسم المستخدم موجود"}), 400
    if User.query.filter_by(email=d.get("email")).first():
        return jsonify({"error": "الايميل موجود"}), 400
    u = User(username=d.get("username"), email=d.get("email"), password=generate_password_hash(d.get("password", "")))
    db.session.add(u)
    db.session.commit()
    return jsonify({"user": ud(u)})

@app.route("/api/login", methods=["POST"])
def login():
    d = request.get_json() or {}
    u = User.query.filter_by(email=d.get("email")).first()
    if u and check_password_hash(u.password, d.get("password", "")):
        return jsonify({"user": ud(u)})
    return jsonify({"error": "بيانات خاطئة"}), 401

@app.route("/api/users")
def users():
    all_users = User.query.all()
    out = [ud(u) for u in all_users]
    return jsonify({"users": out})

@app.route("/api/posts", methods=["GET", "POST"])
def posts():
    if request.method == "POST":
        d = request.get_json() or {}
        p = Post(content=d.get("content"), image=d.get("image", ""), user_id=d.get("user_id"))
        db.session.add(p)
        db.session.commit()
        return jsonify({"message": "تم النشر"})
    all_posts = Post.query.order_by(Post.created_at.desc()).all()
    out = []
    for p in all_posts:
        name = p.user.username if p.user else ""
        out.append({"id": p.id, "content": p.content, "image": p.image, "user_id": p.user_id, "username": name, "created_at": p.created_at.isoformat() if p.created_at else ""})
    return jsonify({"posts": out})

@app.route("/api/posts/<int:pid>", methods=["DELETE"])
def del_post(pid):
    p = Post.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "تم الحذف"})

@app.route("/api/messages", methods=["GET", "POST"])
def messages():
    if request.method == "POST":
        d = request.get_json() or {}
        m = Message(sender_id=d.get("sender_id"), receiver_id=d.get("receiver_id"), content=d.get("content"))
        db.session.add(m)
        sender = User.query.get(d.get("sender_id"))
        sname = sender.username if sender else ""
        n = Notification(user_id=d.get("receiver_id"), content="رسالة جديدة من " + sname)
        db.session.add(n)
        db.session.commit()
        return jsonify({"message": "تم"})
    uid = request.args.get("user_id", type=int)
    oid = request.args.get("other_id", type=int)
    msgs = Message.query.filter(((Message.sender_id == uid) & (Message.receiver_id == oid)) | ((Message.sender_id == oid) & (Message.receiver_id == uid))).order_by(Message.created_at.asc()).all()
    for m in msgs:
        if m.receiver_id == uid:
            m.is_read = True
    db.session.commit()
    out = [{"id": m.id, "sender_id": m.sender_id, "content": m.content, "created_at": m.created_at.isoformat() if m.created_at else ""} for m in msgs]
    return jsonify({"messages": out})

@app.route("/api/notifications/<int:uid>")
def notifs(uid):
    all_n = Notification.query.filter_by(user_id=uid).order_by(Notification.created_at.desc()).all()
    out = [{"id": n.id, "content": n.content, "is_read": n.is_read, "created_at": n.created_at.isoformat() if n.created_at else ""} for n in all_n]
    return jsonify({"notifications": out})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
