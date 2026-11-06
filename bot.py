# NUR ZIKR Telegram boti: mini app + kúndelikli hadis eskertiwi
# Python 3.8+ ,  pip install requests
# Isletiw:  BOT_TOKEN=xxx WEBAPP_URL=https://siziń-sayt/index.html python3 bot.py
import json, os, time, datetime, requests

TOKEN = os.environ["BOT_TOKEN"]
WEBAPP = os.environ["WEBAPP_URL"]              # HTTPS siltemesi (mısalı GitHub Pages)
API = f"https://api.telegram.org/bot{TOKEN}"
SEND_HOUR, SEND_MIN = 7, 0                     # hadis jiberiw waqtı, Nókis waqtı (UTC+5)
HAD = json.load(open("hadislar.json", encoding="utf-8"))
SUBS = "subscribers.json"
BTN = {"inline_keyboard": [[{"text": "📿 NUR ZIKR ashıw", "web_app": {"url": WEBAPP}}]]}

def api(method, **kw):
    return requests.post(f"{API}/{method}", json=kw, timeout=30).json()

def load():
    try: return json.load(open(SUBS))
    except Exception: return {"chats": [], "last": ""}

def save(d): json.dump(d, open(SUBS, "w"))

def send(chat, text):
    api("sendMessage", chat_id=chat, text=text, reply_markup=BTN)

def today():
    n = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
    h = HAD[n.timetuple().tm_yday % len(HAD)]  # saytdaǵı menen birdey hadis
    return n, f"📖 Búgingi hadis\n\n{h['text']}\n\nSahıyh · {h['source']}"

# Chat túymesi (menyu) arqalı da ashılsın
api("setChatMenuButton", menu_button={"type": "web_app", "text": "NUR ZIKR", "web_app": {"url": WEBAPP}})
api("setMyCommands", commands=[
    {"command": "start", "description": "Baslaw hám hár kúngi hadisqa jazılıw"},
    {"command": "hadis", "description": "Búgingi hadis"},
    {"command": "stop", "description": "Hadis eskertiwin óshiriw"}])

offset = 0
while True:
    try:
        r = requests.get(f"{API}/getUpdates", params={"offset": offset, "timeout": 25}, timeout=35).json()
        d = load()
        for u in r.get("result", []):
            offset = u["update_id"] + 1
            m = u.get("message") or {}
            t, c = m.get("text", ""), m.get("chat", {}).get("id")
            if not c: continue
            if t.startswith("/start"):
                if c not in d["chats"]:
                    d["chats"].append(c); save(d)
                send(c, "Assalawma áleykum! NUR ZIKR: zikr tasbex, 99 at, salawat, duwalar, namaz waqıtları, hadis hám Islam kalendarı.\nHár kúni hadis jiberip turaman (toqtatıw: /stop).")
            elif t.startswith("/hadis"):
                send(c, today()[1])
            elif t.startswith("/stop") and c in d["chats"]:
                d["chats"].remove(c); save(d); send(c, "Eskertiw óshirildi.")
        n, msg = today()
        key = n.strftime("%Y-%m-%d")
        if (n.hour, n.minute) >= (SEND_HOUR, SEND_MIN) and d["last"] != key:
            for c in d["chats"]: send(c, msg)
            d["last"] = key; save(d)
    except Exception as e:
        print("qátelik:", e); time.sleep(5)
