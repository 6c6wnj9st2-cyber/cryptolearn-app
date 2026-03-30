"""
CryptoLearn — App d'apprentissage du trading
Backend complet : leçons, quiz, progression, streaks, abonnement
"""
import os, sqlite3, hashlib, secrets, logging, json
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, request, jsonify, session, redirect
import requests as http
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger("cryptolearn")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
STRIPE_SECRET_KEY      = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET  = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_ID        = os.environ.get("STRIPE_PRICE_ID", "")
APP_URL                = os.environ.get("APP_URL", "http://localhost:5000")
DB_PATH = "cryptolearn.db"
# ══════════════════════════════════════════
#  CONTENU — Leçons et Quiz
# ══════════════════════════════════════════
MODULES = [
    {
        "id": 1, "name": "Les Bases", "emoji": "
        "level": "Débutant", "free": True,
",
        "desc": "Comprendre la bourse, les cryptos et les ETFs",
        "lessons": [
            {
            },
            {
                "id": 1, "title": "C'est quoi une action ?",
                "content": "Une action est une part de propriété d'une entreprise. Quand tu achètes une action Apple, tu deviens copropriétaire d'Apple ! Si l'entreprise grandit, ton action vaut plus. Si elle recule, ton action vaut moins.",
                "key_points": ["Une action = une part d'entreprise", "Le prix monte si l'entreprise performe bien", "Tu peux acheter/vendre en bourse"],
                "quiz": [
                    {"question": "Qu'est-ce qu'une action ?", "answers": ["Un billet de banque", "Une part de propriété d'une entreprise", "Un prêt à une entreprise", "Une monnaie numérique"], "correct": 1, "explanation": "Une action représente une part de propriété d'une entreprise cotée en bourse."},
                    {"question": "Si une entreprise fait de bons résultats, son action...", "answers": ["Reste stable", "Baisse généralement", "Monte généralement", "Disparaît"], "correct": 2, "explanation": "De bons résultats attirent les investisseurs, ce qui fait monter le prix de l'action."},
                ]
                "id": 2, "title": "C'est quoi une crypto ?",
                "content": "Une cryptomonnaie est une monnaie numérique décentralisée. Bitcoin (BTC) est la plus connue. Contrairement aux euros, personne ne contrôle les cryptos — elles fonctionnent sur une technologie appelée blockchain.",
                "key_points": ["Monnaie numérique décentralisée", "Blockchain = registre transparent", "Bitcoin = première crypto, créée en 2009"],
                "quiz": [
                    {"question": "Qui contrôle le Bitcoin ?", "answers": ["La banque centrale", "Satoshi Nakamoto", "Personne — c'est décentralisé", "Les États-Unis"], "correct": 2, "explanation": "Le Bitcoin est décentralisé — aucune banque ou gouvernement ne le contrôle."},
                    {"question": "Qu'est-ce que la blockchain ?", "answers": ["Un wallet crypto", "Un registre transparent et décentralisé", "Une bourse crypto", "Un type de crypto"], "correct": 1, "explanation": "La blockchain est un registre numérique transparent où toutes les transactions sont enregistrées."},
                ]
            },
            {
            },
        ]
    },
    {
                "id": 3, "title": "C'est quoi un ETF ?",
                "content": "Un ETF (Exchange Traded Fund) est un panier d'actifs. SPY est un ETF qui contient les 500 plus grandes entreprises américaines. Au lieu d'acheter 500 actions, tu achètes un seul ETF ! C'est simple et diversifié.",
                "key_points": ["ETF = panier d'actifs", "Diversification automatique", "SPY = S&P 500, QQQ = NASDAQ"],
                "quiz": [
                    {"question": "Quel est l'avantage principal d'un ETF ?", "answers": ["Des rendements garantis", "La diversification en un seul achat", "Il ne peut pas baisser", "Il est gratuit"], "correct": 1, "explanation": "Un ETF permet de s'exposer à de nombreux actifs en un seul achat, réduisant le risque."},
                ]
",
        "id": 2, "name": "Acheter & Vendre", "emoji": "
        "level": "Débutant", "free": True,
        "desc": "Types d'ordres, market cap, volume",
        "lessons": [
            {
                "id": 4, "title": "Les types d'ordres",
                "content": "Il existe 2 types d'ordres principaux. L'ordre MARKET s'exécute immédiatement au prix du marché. L'ordre LIMIT s'exécute seulement si le prix atteint ton objectif.",
                "key_points": ["Market order = achat/vente immédiat", "Limit order = achat/vente à un prix précis", "Stop loss = vente automatique si le prix baisse trop"],
                "quiz": [
                    {"question": "Quel ordre s'exécute immédiatement ?", "answers": ["Limit order", "Market order", "Stop order", "Take profit"], "correct": 1, "explanation": "Un market order s'exécute immédiatement au meilleur prix disponible sur le marché."},
                ]
            },
            {
                "id": 5, "title": "C'est quoi la market cap ?",
                "content": "La capitalisation boursière (market cap) = prix de l'action × nombre d'actions. Apple vaut 3 000 milliards de dollars ! Une grande market cap = entreprise établie. Une petite market cap = plus risqué mais plus de potentiel.",
                "key_points": ["Market cap = prix × quantité", "Large cap = stable", "Small cap = risqué mais potentiel"],
                "quiz": [
                    {"question": "Comment calcule-t-on la market cap ?", "answers": ["Prix + nombre d'actions", "Prix 
                ]
            },
        ]
    },
    {
        "id": 3, "name": "Analyse Technique", "emoji": " ",
        "level": "Intermédiaire", "free": False,
        "desc": "Chandeliers, supports, résistances",
        "lessons": [
            {
                "id": 6, "title": "Les chandeliers japonais",
                "content": "Un chandelier montre le mouvement du prix sur une période. Corps vert = prix a monté. Corps rouge = prix a baissé. Les mèches montrent les extrêmes atteints.",
                "key_points": ["Bougie verte = hausse", "Bougie rouge = baisse", "Mèche = extrême atteint"],
                "quiz": [
                    {"question": "Qu'indique une bougie verte ?", "answers": ["Le prix a baissé", "Le volume a augmenté", "Le prix a monté", "L'actif est surévalué"], "correct": 2, "explanation": "Une bougie verte signifie que le prix de clôture est supérieur au prix d'ouverture."},
                ]
            },
        ]
    },
    {
        "id": 4, "name": "Indicateurs IA", "emoji": "
        "level": "Avancé", "free": False,
        "desc": "RSI, MACD, Bollinger Bands",
        "lessons": [
            {
",
                "id": 7, "title": "Le RSI expliqué",
                "content": "Le RSI (Relative Strength Index) oscille entre 0 et 100. En dessous de 30 = l'actif est survendu (signal d'achat possible). Au-dessus de 70 = l'actif est suracheté (signal de vente possible).",
                "key_points": ["RSI < 30 = survendu = signal achat", "RSI > 70 = suracheté = signal vente", "RSI 50 = neutre"],
                "quiz": [
                    {"question": "Un RSI de 25 indique...", "answers": ["Suracheté = vendre", "Survendu = potentiel achat", "Prix stable", "Forte volatilité"], "correct": 1, "explanation": "RSI < 30 indique une zone de survente — le prix a peut-être trop baissé et pourrait remonter."},
                ]
            },
        ]
    },
    {
    },
]
        "id": 5, "name": "Stratégies", "emoji": " ",
        "level": "Expert", "free": False,
        "desc": "DCA, swing trading, gestion du risque",
        "lessons": [
            {
                "id": 8, "title": "Le DCA — Dollar Cost Averaging",
                "content": "Le DCA consiste à investir un montant fixe régulièrement (ex: 50€
                "key_points": ["Investir un montant fixe régulièrement", "Réduit l'impact de la volatilité", "Idéal pour les débutants"],
                "quiz": [
                    {"question": "Quel est l'avantage du DCA ?", "answers": ["Garantit des profits", "Réduit l'impact de la volatilité", "Évite toutes les pertes", "Nécessite peu de capital"], "correct": 1, "explanation": "Le DCA lisse le prix d'achat moyen et réduit l'impact des fluctuations de marché."},
                ]
            },
        ]
# ══════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT DEFAULT '',
        plan TEXT DEFAULT 'free',
        stripe_sub_id TEXT DEFAULT '',
        xp INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        last_lesson_date TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        lesson_id INTEGER NOT NULL,
        completed INTEGER DEFAULT 0,
        score INTEGER DEFAULT 0,
        completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, lesson_id)
    )""")
    conn.commit()
    conn.close()
    log.info("DB initialisee")
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
# ══════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════
def login_required(f):
    @wraps(f)
    def d(*a, **k):
        if "uid" not in session: return redirect("/login")
        return f(*a, **k)
    return d
# ══════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════
def read(f):
    return open(f, encoding="utf-8").read()
@app.route("/")
def index():
    return read("landing.html")
@app.route("/login")
def login_page():
    return read("login.html")
@app.route("/register")
def register_page():
    return read("register.html")
@app.route("/pricing")
@login_required
def pricing_page():
    return read("pricing.html").replace("__PK__", STRIPE_PUBLISHABLE_KEY)
@app.route("/app")
@login_required
def app_page():
    return read("app.html")
@app.route("/lesson/<int:lid>")
@login_required
def lesson_page(lid):
    return read("lesson.html")
@app.route("/payment-success")
@login_required
def payment_success():
    db = get_db()
    db.execute("UPDATE users SET plan='pro' WHERE id=?", (session["uid"],))
    db.commit()
    db.close()
    return redirect("/app")
# ══════════════════════════════════════════
#  API AUTH
# ══════════════════════════════════════════
@app.route("/api/register", methods=["POST"])
def api_register():
    d = request.get_json()
    email = d.get("email","").strip().lower()
    pw    = d.get("password","")
    name  = d.get("name","").strip()
    if not email or not pw or not name:
        return jsonify({"error": "Tous les champs sont requis"}), 400
    if len(pw) < 6:
        return jsonify({"error": "Mot de passe trop court"}), 400
    db = get_db()
    if db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
        db.close()
        return jsonify({"error": "Email deja utilise"}), 409
    db.execute("INSERT INTO users (email, password_hash, name) VALUES (?,?,?)",
               (email, hash_pw(pw), name))
    db.commit()
    u = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    db.close()
    session["uid"]   = u["id"]
    session["email"] = email
    session["name"]  = name
    return jsonify({"success": True, "redirect": "/app"})
@app.route("/api/login", methods=["POST"])
def api_login():
    d = request.get_json()
    email = d.get("email","").strip().lower()
    pw    = d.get("password","")
    db    = get_db()
    u     = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    db.close()
    if not u or u["password_hash"] != hash_pw(pw):
        return jsonify({"error": "Email ou mot de passe incorrect"}), 401
    session["uid"]   = u["id"]
    session["email"] = u["email"]
    session["name"]  = u["name"]
    return jsonify({"success": True, "redirect": "/app"})
@app.route("/api/logout")
def api_logout():
    session.clear()
    return redirect("/login")
@app.route("/api/me")
@login_required
def api_me():
    db = get_db()
    u  = db.execute("SELECT id,email,name,plan,xp,streak,last_lesson_date FROM users WHERE id=?",
                    (session["uid"],)).fetchone()
    db.close()
    if u is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(dict(u))
# ══════════════════════════════════════════
#  API STRIPE
# ══════════════════════════════════════════
@app.route("/api/create-checkout", methods=["POST"])
@login_required
def api_checkout():
    try:
        result = http.post(
            "https://api.stripe.com/v1/checkout/sessions",
            auth=(STRIPE_SECRET_KEY, ""),
            data={
                "payment_method_types[]": "card",
                "line_items[0][price]": STRIPE_PRICE_ID,
                "line_items[0][quantity]": "1",
                "mode": "subscription",
                "success_url": APP_URL + "/payment-success",
                "cancel_url": APP_URL + "/pricing",
                "customer_email": session["email"],
                "metadata[uid]": str(session["uid"]),
            }
        ).json()
        if "error" in result:
            return jsonify({"error": result["error"]["message"]}), 500
        return jsonify({"checkout_url": result["url"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/webhook", methods=["POST"])
def api_webhook():
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    payload = request.get_data()
    sig     = request.headers.get("Stripe-Signature","")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if event["type"] == "checkout.session.completed":
        obj = event["data"]["object"]
        uid = obj.get("metadata",{}).get("uid")
        sub = obj.get("subscription","")
        if uid:
            db = get_db()
            db.execute("UPDATE users SET plan='pro', stripe_sub_id=? WHERE id=?", (sub, uid))
            db.commit()
            db.close()
    return jsonify({"ok": True})
# ══════════════════════════════════════════
#  API LEARNING
# ══════════════════════════════════════════
@app.route("/api/modules")
@login_required
def api_modules():
    db = get_db()
    u  = db.execute("SELECT plan FROM users WHERE id=?", (session["uid"],)).fetchone()
    completed = db.execute("SELECT lesson_id FROM progress WHERE user_id=? AND completed=1",
                           (session["uid"],)).fetchall()
    db.close()
    completed_ids = {r["lesson_id"] for r in completed}
    is_pro = (u is not None and u["plan"] == "pro")
    result = []
    for m in MODULES:
        lessons_done = sum(1 for l in m["lessons"] if l["id"] in completed_ids)
        result.append({
            "id": m["id"], "name": m["name"], "emoji": m["emoji"],
            "level": m["level"], "free": m["free"], "desc": m["desc"],
            "total_lessons": len(m["lessons"]),
            "completed_lessons": lessons_done,
            "locked": not (m["free"] or is_pro),
            "pct": int(lessons_done / max(1, len(m["lessons"])) * 100),
        })
    return jsonify(result)
@app.route("/api/lesson/<int:lid>")
@login_required
def api_lesson(lid):
    db = get_db()
    u  = db.execute("SELECT plan FROM users WHERE id=?", (session["uid"],)).fetchone()
    db.close()
    is_pro = (u is not None and u["plan"] == "pro")
    for m in MODULES:
        for l in m["lessons"]:
            if l["id"] == lid:
                if not (m["free"] or is_pro):
                    return jsonify({"error": "Abonnement Pro requis"}), 403
                return jsonify({**l, "module_name": m["name"], "module_emoji": m["emoji"]})
    return jsonify({"error": "Leçon introuvable"}), 404
@app.route("/api/complete-lesson", methods=["POST"])
@login_required
def api_complete_lesson():
    d       = request.get_json()
    lid     = d.get("lesson_id")
    score   = d.get("score", 100)
    uid     = session["uid"]
    xp_gain = max(10, int(score / 100 * 50))
    db = get_db()
    # Enregistre la progression
    db.execute("""INSERT OR REPLACE INTO progress (user_id, lesson_id, completed, score, completed_at)
                  VALUES (?,?,1,?,?)""", (uid, lid, score, datetime.now().isoformat()))
    # Met à jour XP et streak
    u         = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    today     = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    last      = u["last_lesson_date"]
    new_streak = u["streak"]
    if last == today:
        new_streak = u["streak"]  # Déjà compté aujourd'hui
    elif last == yesterday:
        new_streak = u["streak"] + 1  # Streak continue
    else:
        new_streak = 1  # Streak cassé, repart à 1
    new_xp = u["xp"] + xp_gain
    db.execute("UPDATE users SET xp=?, streak=?, last_lesson_date=? WHERE id=?",
               (new_xp, new_streak, today, uid))
    db.commit()
    db.close()
    return jsonify({
        "success": True, "xp_gained": xp_gain,
        "new_xp": new_xp, "streak": new_streak,
    })
@app.route("/api/progress")
@login_required
def api_progress():
    db = get_db()
    rows = db.execute("SELECT * FROM progress WHERE user_id=? AND completed=1",
                      (session["uid"],)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])
@app.route("/api/leaderboard")
@login_required
def api_leaderboard():
    db = get_db()
    rows = db.execute("SELECT name, xp, streak FROM users ORDER BY xp DESC LIMIT 10").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])
# ══════════════════════════════════════════
with app.app_context():
    init_db()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
