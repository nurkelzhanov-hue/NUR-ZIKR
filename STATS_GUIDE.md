# Mini app statistikası (tegin, karta kerek emes): Cloudflare Worker + D1

Nátiyje: botqa `/stats` jazsańız, mını kóresiz: házir onlayn, búgin kirgenler, jańa adamlar, ashılıwlar, 7/30 kún, jámi, bloklaǵanlar, hadisqa jazılǵanlar. Hár kúni 22:00 de ózi esabat jiberedi.

## 1. Tayarlıq
1. dash.cloudflare.com ta registraciya (tek e-mail, karta kerek emes).
2. nodejs.org tan Node.js (LTS) ornatıń.
3. VS Code ta usı `stats` papkasın ashıp, Terminal ashıń.

## 2. Ornatıw
```
npm install -g wrangler
wrangler login
wrangler d1 create nurzikr
```
Shıqqan `database_id` di kóshirip, `wrangler.toml` daǵı `BU_JERGE_wrangler_BERGEN_ID_JAZILADI` ornına qoyıń.

```
wrangler d1 execute nurzikr --remote --file=schema.sql
wrangler secret put BOT_TOKEN
wrangler secret put ADMIN_KEY
wrangler deploy
```
- `BOT_TOKEN`: botıńızdıń tokeni (soraǵanda jazıp Enter basıń, ekranda kórinbeydi).
- `ADMIN_KEY`: ózińiz oylap tapqan uzın qupıya sóz (mısalı 30 belgi).
- `wrangler deploy` dan keyin silteme shıǵadı: `https://nurzikr-stats.SIZ.workers.dev`

## 3. Appqa hám botqa ulaw
1. `index.html` daǵı `const STATS_URL="";` ge sol siltemeni jazıń, GitHub Pages ke qaytadan júkleń.
2. Bottıń `.env` ine qosıń:
```
STATS_URL=https://nurzikr-stats.SIZ.workers.dev
STATS_KEY=ADMIN_KEY ge jazǵan sóz
ADMIN_ID=ÓZ_TELEGRAM_ID_ŃIZ
```
3. Bottı qayta iske túsiriń. Botqa `/stats` jazıń.

## Qalay isleydi
- Mini app ashılǵanda hám ashıq turǵanda hár 2 minutta Telegram ID jiberedi (Worker ID di Telegramnıń imzası menen tekseredi, jalǵan sanlar kirmeydi).
- Saqlanatuǵını: Telegram ID hám waqıt. Atı, telefon, xabarları saqlanbaydı.
- "Házir onlayn": songı 5 minutta app ashıq bolǵan adamlar.
- Tegin limit: kúnine 100 000 sorawǵa shekem (Workers) hám 100 000 jazıwǵa shekem (D1). Bizge uzaq waqıt jetedi.
