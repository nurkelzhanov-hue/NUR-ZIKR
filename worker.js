// NUR ZIKR statistikası: Cloudflare Worker + D1 (tegin tarif, karta kerek emes)
const enc = new TextEncoder();
const hex = b => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, "0")).join("");
const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,X-Key", "Access-Control-Allow-Methods": "GET,POST,OPTIONS" };

async function hmac(key, msg) {
  const k = await crypto.subtle.importKey("raw", key, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return crypto.subtle.sign("HMAC", k, msg);
}

// Telegram initData tekseriw: jalǵan ID jiberiwdiń aldın aladı
async function verify(initData, token) {
  const p = new URLSearchParams(initData);
  const hash = p.get("hash");
  p.delete("hash");
  const str = [...p.entries()].sort((a, b) => (a[0] < b[0] ? -1 : 1)).map(([k, v]) => `${k}=${v}`).join("\n");
  const secret = await hmac(enc.encode("WebAppData"), enc.encode(token));
  if (hex(await hmac(secret, enc.encode(str))) !== hash) return null;
  if (Date.now() / 1000 - Number(p.get("auth_date")) > 2 * 86400) return null;
  try { return JSON.parse(p.get("user")).id; } catch { return null; }
}

export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
    const now = Math.floor(Date.now() / 1000);
    const today0 = Math.floor((now + 18000) / 86400) * 86400 - 18000;   // Nókis kúni (UTC+5)

    if (u.pathname === "/ping" && req.method === "POST") {
      let b;
      try { b = await req.json(); } catch { return new Response("bad", { status: 400, headers: CORS }); }
      const id = await verify(String(b.initData || ""), env.BOT_TOKEN);
      if (!id) return new Response("auth", { status: 401, headers: CORS });
      const st = [env.DB.prepare("INSERT INTO users(id,first_seen,last_seen) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET last_seen=excluded.last_seen").bind(id, now, now)];
      if (b.open) st.push(env.DB.prepare("INSERT INTO opens(day,n) VALUES(?,1) ON CONFLICT(day) DO UPDATE SET n=n+1").bind(today0));
      await env.DB.batch(st);
      return new Response("ok", { headers: CORS });
    }

    if (u.pathname === "/stats") {
      if (!env.ADMIN_KEY || req.headers.get("X-Key") !== env.ADMIN_KEY) return new Response("no", { status: 403, headers: CORS });
      const q = async (sql, a) => (await env.DB.prepare(sql).bind(...a).first()).c;
      const out = {
        total: await q("SELECT COUNT(*) c FROM users", []),
        online: await q("SELECT COUNT(*) c FROM users WHERE last_seen>=?", [now - 300]),
        today: await q("SELECT COUNT(*) c FROM users WHERE last_seen>=?", [today0]),
        new_today: await q("SELECT COUNT(*) c FROM users WHERE first_seen>=?", [today0]),
        d7: await q("SELECT COUNT(*) c FROM users WHERE last_seen>=?", [now - 7 * 86400]),
        d30: await q("SELECT COUNT(*) c FROM users WHERE last_seen>=?", [now - 30 * 86400]),
        opens_today: (await env.DB.prepare("SELECT n FROM opens WHERE day=?").bind(today0).first())?.n || 0,
      };
      return new Response(JSON.stringify(out), { headers: { ...CORS, "Content-Type": "application/json" } });
    }
    return new Response("NUR ZIKR stats", { headers: CORS });
  },
};
