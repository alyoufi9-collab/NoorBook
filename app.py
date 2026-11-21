from flask import Flask, request, redirect, render_template_string
app = Flask(__name__)
posts = []
chats = []

HTML = """
<!DOCTYPE html><html dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NoorBook</title><style>
body{font-family:sans-serif;background:#f0f2f5;margin:0;padding:10px}
.top{background:#1877f2;color:white;padding:15px;font-size:22px;font-weight:bold;text-align:center;border-radius:10px}
.box{background:white;padding:12px;border-radius:10px;margin:10px 0}
input,textarea{width:95%;padding:10px;margin:5px 0;border:1px solid #ddd;border-radius:8px}
button{background:#1877f2;color:white;border:0;padding:10px 20px;border-radius:8px}
.post{background:white;padding:12px;border-radius:10px;margin:10px 0}
.tabs{display:flex;gap:10px}.tabs a{flex:1;text-align:center;background:white;padding:12px;border-radius:10px;text-decoration:none;color:#1877f2;font-weight:bold}
</style></head><body>
<div class="top">NoorBook و NoorChat</div>
<div class="tabs"><a href="/">NoorBook</a><a href="/chat">NoorChat</a></div>
{% if page=='home' %}
<div class="box"><form method="post" action="/post">
<input name="name" placeholder="اسمك" required>
<textarea name="text" placeholder="اكتب شنو في بالك؟" required></textarea>
<button>انشر</button></form></div>
{% for p in posts %}<div class="post"><b>{{p[0]}}</b><br>{{p[1]}}</div>{% endfor %}
{% else %}
<div class="box"><form method="post" action="/send">
<input name="name" placeholder="اسمك" required>
<input name="text" placeholder="اكتب رسالة..." required>
<button>ارسال</button></form></div>
{% for c in chats %}<div class="post"><b>{{c[0]}}:</b> {{c[1]}}</div>{% endfor %}
{% endif %}
</body></html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, posts=reversed(posts), chats=[], page='home')

@app.route("/post", methods=["POST"])
def post():
    posts.append((request.form["name"], request.form["text"]))
    return redirect("/")

@app.route("/chat")
def chat():
    return render_template_string(HTML, posts=[], chats=reversed(chats), page='chat')

@app.route("/send", methods=["POST"])
def send():
    chats.append((request.form["name"], request.form["text"]))
    return redirect("/chat")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
