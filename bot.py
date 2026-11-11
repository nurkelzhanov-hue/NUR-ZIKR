# NUR ZIKR Telegram boti (24/7 nusqa): mini app + kúndelikli hadis eskertiwi
# Python 3.8+ ,  pip install -r requirements.txt
# Sazlamalar .env faylında (env.example di .env dep kóshirip toltırıń) yamasa environment arqalı.
import json, os, sys, time, logging, datetime, requests

BASE = os.path.dirname(os.path.abspath(__file__))

def load_env(path):
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.join(BASE, ".env"))
TOKEN = os.environ.get("BOT_TOKEN", "")
WEBAPP = os.environ.get("WEBAPP_URL", "")
ADMIN = int(os.environ.get("ADMIN_ID", "0") or 0)           # óziń ushın /stats (ixtiyariy)
SEND_HOUR = int(os.environ.get("SEND_HOUR", "7"))           # hadis waqtı, Nókis (UTC+5)
SEND_MIN = int(os.environ.get("SEND_MIN", "0"))
STATS_URL = os.environ.get("STATS_URL", "").rstrip("/")      # Cloudflare Worker siltemesi (ixtiyariy)
STATS_KEY = os.environ.get("STATS_KEY", "")
DATA = os.environ.get("DATA_DIR", BASE)
SUBS = os.path.join(DATA, "subscribers.json")
USERS = os.path.join(DATA, "users.json")
API = f"https://api.telegram.org/bot{TOKEN}"
BTN = {"inline_keyboard": [[{"text": "📿 NUR ZIKR ashıw", "web_app": {"url": WEBAPP}}]]}
S = requests.Session()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("nurzikr")
HAD = json.load(open(os.path.join(BASE, "hadislar.json"), encoding="utf-8"))

def api(method, **kw):
    try:
        return S.post(f"{API}/{method}", json=kw, timeout=40).json()
    except Exception as e:
        log.warning("%s: %s", method, e)
        return {"ok": False}

def load():
    try:
        return json.load(open(SUBS))
    except Exception:
        return {"chats": [], "last": ""}

def save(d):
    tmp = SUBS + ".tmp"
    json.dump(d, open(tmp, "w"))
    os.replace(tmp, SUBS)

def load_users():
    try:
        return json.load(open(USERS))
    except Exception:
        return {}

def save_users(u):
    tmp = USERS + ".tmp"
    json.dump(u, open(tmp, "w"))
    os.replace(tmp, USERS)

def touch(u, chat, blocked=False):
    now = int(time.time())
    r = u.setdefault(str(chat), {"first": now})
    r["last"] = now
    r["blocked"] = blocked

def app_stats():
    if not STATS_URL:
        return ""
    try:
        r = S.get(f"{STATS_URL}/stats", headers={"X-Key": STATS_KEY}, timeout=15).json()
        return (f"\n\n📱 Mini app\nHázir onlayn: {r['online']}\n"
                f"Búgin kirgen: {r['today']} (jańa: {r['new_today']}), ashılıwlar: {r['opens_today']}\n"
                f"7 kún: {r['d7']} · 30 kún: {r['d30']} · Jámi: {r['total']}")
    except Exception as e:
        log.warning("app_stats: %s", e)
        return "\n\n📱 Mini app statistikası alınbadı"

def stats_text(u, d):
    now = time.time()
    act = lambda n: sum(1 for r in u.values() if now - r.get("last", 0) < n * 86400 and not r.get("blocked"))
    return (f"📊 NUR ZIKR statistikası\nJámi baslaǵan: {len(u)}\nHadisqa jazılǵan: {len(d['chats'])}\n"
            f"Botti bloklaǵan: {sum(1 for r in u.values() if r.get('blocked'))}\n"
            f"Aktiv (botqa jazǵan): búgin {act(1)} · 7 kún {act(7)} · 30 kún {act(30)}") + app_stats()

def send(chat, text):
    """True = jiberildi, None = bot bloklanǵan/chat joq (dizimnen óshiriw), False = waqıtsha qátelik"""
    for _ in range(3):
        r = api("sendMessage", chat_id=chat, text=text, reply_markup=BTN)
        if r.get("ok"):
            return True
        code = r.get("error_code")
        if code == 429:
            time.sleep(r.get("parameters", {}).get("retry_after", 5) + 1)
            continue
        if code in (400, 403):
            return None
        break
    return False

def today():
    n = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    h = HAD[n.timetuple().tm_yday % len(HAD)]   # saytdaǵı menen birdey hadis
    return n, f"📖 Búgingi hadis\n\n{h['text']}\n\nSahıyh · {h['source']}"

def broadcast(d, msg):
    for c in list(d["chats"]):
        if send(c, msg) is None:
            d["chats"].remove(c)
        time.sleep(0.05)                          # Telegram limitine (sekundına ~30) tiymew

def handle(m, d, U):
    t, c = m.get("text", ""), m.get("chat", {}).get("id")
    if not c:
        return
    touch(U, c)
    if t.startswith("/start"):
        if c not in d["chats"]:
            d["chats"].append(c); save(d)
        send(c, "Assalawma áleykum! NUR ZIKR: zikr tasbeh, 99 at, salawatlar, duwalar, namaz waqıtları, hadis hám Islam kalenderi.\nHár kúni hadis jiberip turaman (toqtatıw: /stop).")
    elif t.startswith("/hadis"):
        send(c, today()[1])
    elif t.startswith("/stop") and c in d["chats"]:
        d["chats"].remove(c); save(d); send(c, "Eskertiw óshirildi.")
    elif t.startswith("/stats") and c == ADMIN:
        send(c, stats_text(U, d))

def main():
    if not TOKEN or not WEBAPP:
        sys.exit("BOT_TOKEN hám WEBAPP_URL kerek (.env faylın tekseriń)")
    api("setChatMenuButton", menu_button={"type": "web_app", "text": "NUR ZIKR", "web_app": {"url": WEBAPP}})
    api("setMyCommands", commands=[
        {"command": "start", "description": "Baslaw hám hár kúngi hadisqa jazılıw"},
        {"command": "hadis", "description": "Búgingi hadis"},
        {"command": "stop", "description": "Hadis eskertiwin óshiriw"}])
    log.info("Bot iske tústi")
    offset = 0
    while True:
        try:
            r = api("getUpdates", offset=offset, timeout=25)
            if not r.get("ok"):
                if r.get("error_code") == 409:
                    log.error("Basqa bot nusqası islep tur (409). Birewin toqtatıń.")
                time.sleep(5); continue
            d = load()
            U = load_users()
            for c in d["chats"]:
                U.setdefault(str(c), {"first": int(time.time()), "last": 0})
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                handle(u.get("message") or {}, d, U)
                mc = u.get("my_chat_member")
                if mc and mc.get("chat", {}).get("type") == "private":
                    touch(U, mc["chat"]["id"], mc.get("new_chat_member", {}).get("status") in ("kicked", "left"))
            save_users(U)
            n, msg = today()
            key = n.strftime("%Y-%m-%d")
            if (n.hour, n.minute) >= (SEND_HOUR, SEND_MIN) and d["last"] != key:
                d["last"] = key; save(d)             # aldın belgileymiz, qaytalanbasın
                broadcast(d, msg); save(d)
                log.info("Hadis jiberildi: %d adam", len(d["chats"]))
            if ADMIN and (n.hour, n.minute) >= (22, 0) and d.get("rep") != key:
                d["rep"] = key; save(d)             # kúnlik esabat óziń ushın (22:00)
                send(ADMIN, "🗓 Kúnlik esabat\n" + stats_text(U, d))
        except Exception as e:
            log.exception("qátelik: %s", e); time.sleep(5)

if __name__ == "__main__":
    main()
