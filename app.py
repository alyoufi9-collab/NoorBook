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

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return "<h1>NoorBook شغال</h1><p>اذا شفت الصفحة دي معناها السيرفر اشتغل</p>"

@app.route("/api/register", methods=["POST"])
def register():
    d = request.get_json() or {}
    if User.query.filter_by(email=d.get("email")).first():
        return jsonify({"error": "الايميل موجود"}), 400
    u = User(username=d.get("username"), email=d.get("email"), password=generate_password_hash(d.get("password", "")))
    db.session.add(u)
    db.session.commit()
    return jsonify({"user": {"id": u.id, "username": u.username, "email": u.email}})

@app.route("/api/login", methods=["POST"])
def login():
    d = request.get_json() or {}
    u = User.query.filter_by(email=d.get("email")).first()
    if u and check_password_hash(u.password, d.get("password", "")):
        return jsonify({"user": {"id": u.id, "username": u.username, "email": u.email}})
    return jsonify({"error": "بيانات خاطئة"}), 401

@app.route("/api/posts", methods=["GET", "POST"])
def posts():
    if request.method == "POST":
        d = request.get_json() or {}
        p = Post(content=d.get("content"), user_id=d.get("user_id"))
        db.session.add(p)
        db.session.commit()
        return jsonify({"message": "تم النشر"})
    all_posts = Post.query.order_by(Post.created_at.desc()).all()
    out = [{"id": p.id, "content": p.content, "user_id": p.user_id} for p in all_posts]
    return jsonify({"posts": out})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
