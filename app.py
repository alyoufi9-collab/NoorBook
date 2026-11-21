# NoorBook + NoorChat - app.py - النسخة النهائية
from flask import Flask, request, jsonify
from flask_cors import CORS
import os, uuid, hashlib
from datetime import datetime

app = Flask(__name__)
CORS(app)

USERS = {}
POSTS = []
CHATS = {}
MESSAGES = {}
SETTINGS = {}
BLOCKS = []

# --- 1. Noor ID - تسجيل و دخول ---
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

# --- 2. Settings - الإعدادات ---
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

# --- 3. NoorBook - Posts ---
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

@app.route('/api/v1/posts/<pid>/comment', methods=['POST'])
def comment_post(pid):
    d = request.json or {}
    for p in POSTS:
        if p["post_id"] == pid:
            p["comments_count"] += 1
            return jsonify({"ok": True, "comment": d.get("content"), "post": p})
    return jsonify({"error": "not found"}), 404

# --- 4. NoorChat - Chats ---
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

# --- 5. Blocks - حظر موحد ---
@app.route('/api/v1/blocks', methods=['POST'])
def block_user():
    d = request.json or {}
    BLOCKS.append({"blocker": d.get("blocker_id"), "blocked": d.get("blocked_id")})
    return jsonify({"ok": True, "message": "تم الحظر في NoorBook + NoorChat"})

@app.route('/api/v1/blocks/<uid>', methods=['GET'])
def get_blocks(uid):
    return jsonify([b for b in BLOCKS if b["blocker"] == uid])

# --- 6. Security - Privacy Score + ATO ---
@app.route('/api/v1/security/privacy-score', methods=['POST'])
def privacy_score():
    from security import NoorSecurityAlgorithms
    return jsonify(NoorSecurityAlgorithms.calculate_privacy_health_score(request.json or {}))

@app.route('/api/v1/security/ato-check', methods=['POST'])
def ato_check():
    from security import NoorSecurityAlgorithms, LoginContext
    d = request.json or {}
    ctx = LoginContext(ip_country=d.get("ip_country","SD"), last_country=d.get("last_country","SD"), hours_since_last_login=d.get("hours",24), is_new_device=d.get("is_new_device",False), failed_attempts=d.get("failed",0), ip_asn=d.get("asn",""), last_asn=d.get("last_asn",""), logins_last_10min=d.get("velocity",0), sensitive_actions_last_10min=d.get("sensitive",0), distance_km=d.get("distance",0))
    return jsonify(NoorSecurityAlgorithms.detect_account_takeover_risk(ctx))

# --- 7. Sessions - خروج من كل الأجهزة ---
@app.route('/api/v1/sessions/logout-others', methods=['POST'])
def logout_others():
    d = request.json or {}
    uid = d.get("user_id")
    if uid in USERS: USERS[uid]["token_version"] += 1
    return jsonify({"ok": True, "message": "تم الخروج من كل الأجهزة الأخرى"})

@app.route('/')
def home():
    return jsonify({"status": "NoorBook + NoorChat API Running ✅"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
