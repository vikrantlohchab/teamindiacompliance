// Cloudflare Worker: receives a generated TCI report PDF from the website and sends it to the user's WhatsApp
// through the Meta WhatsApp Cloud API (template message with a PDF header). Stateless: nothing is stored.
// Secrets: WA_TOKEN, WA_PHONE_ID, TURNSTILE_SECRET.  Optional KV binding: RL (rate limits).

const BANDS = ["Critical Attention", "Needs Improvement", "Satisfactory", "Good", "Excellent"];
const MAX_PDF_B64 = 700000;

function json(body, status, cors) { return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", ...cors } }); }
const clean = (s, n) => String(s == null ? "" : s).replace(/[\r\n\t]+/g, " ").replace(/ {2,}/g, " ").trim().slice(0, n);

async function sha256(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}
async function hit(env, key, limit, ttl) {
  if (!env.RL) return true;
  const n = parseInt((await env.RL.get(key)) || "0", 10);
  if (n >= limit) return false;
  await env.RL.put(key, String(n + 1), { expirationTtl: ttl });
  return true;
}
async function turnstileOk(env, token, ip) {
  if (!env.TURNSTILE_SECRET) return true;      // captcha not configured
  if (!token) return false;
  const f = new FormData(); f.append("secret", env.TURNSTILE_SECRET); f.append("response", token); if (ip) f.append("remoteip", ip);
  const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: f });
  return !!(await r.json()).success;
}

export default {
  async fetch(req, env) {
    const allowed = (env.ALLOW_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
    const origin = req.headers.get("Origin") || "";
    const cors = allowed.includes(origin) ? { "Access-Control-Allow-Origin": origin, "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Vary": "Origin" } : {};
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (req.method !== "POST") return json({ ok: false, error: "method" }, 405, cors);
    if (!allowed.includes(origin)) return json({ ok: false, error: "origin" }, 403, cors);

    let b;
    try { b = await req.json(); } catch { return json({ ok: false, error: "bad_json" }, 400, cors); }
    const name = clean(b.name, 60), company = clean(b.company, 80), phone = String(b.phone || ""), score = Number(b.score), band = String(b.band || "");
    const pdf = String(b.pdf || "");
    if (!name || !company || !/^\d{11,15}$/.test(phone) || !Number.isInteger(score) || score < 0 || score > 100 || !BANDS.includes(band)) return json({ ok: false, error: "invalid" }, 400, cors);
    if (!pdf || pdf.length > MAX_PDF_B64 || !pdf.startsWith("JVBERi")) return json({ ok: false, error: "invalid_pdf" }, 400, cors);   // "JVBERi" = base64 of "%PDF"

    const ip = req.headers.get("CF-Connecting-IP") || "";
    if (!(await turnstileOk(env, b.token, ip))) return json({ ok: false, error: "captcha" }, 403, cors);
    const hour = Math.floor(Date.now() / 3600000), day = Math.floor(Date.now() / 86400000);
    if (!(await hit(env, `ip:${ip}:${hour}`, 5, 3700)) || !(await hit(env, `ph:${await sha256(phone)}:${day}`, 2, 90000))) return json({ ok: false, error: "rate_limited" }, 429, cors);

    const base = `https://graph.facebook.com/${env.GRAPH_VERSION || "v21.0"}/${env.WA_PHONE_ID}`;
    const auth = { Authorization: `Bearer ${env.WA_TOKEN}` };
    const filename = `TCI-Report-${company.replace(/[^\w]+/g, "-").slice(0, 40) || "report"}.pdf`;
    try {
      const bytes = Uint8Array.from(atob(pdf), (c) => c.charCodeAt(0));
      const form = new FormData();
      form.append("messaging_product", "whatsapp"); form.append("type", "application/pdf");
      form.append("file", new Blob([bytes], { type: "application/pdf" }), filename);
      const up = await fetch(`${base}/media`, { method: "POST", headers: auth, body: form });
      const upj = await up.json();
      if (!up.ok || !upj.id) return json({ ok: false, error: "upload_failed" }, 502, cors);

      const msg = await fetch(`${base}/messages`, {
        method: "POST", headers: { ...auth, "Content-Type": "application/json" },
        body: JSON.stringify({
          messaging_product: "whatsapp", to: phone, type: "template",
          template: {
            name: env.WA_TEMPLATE || "tci_report_delivery", language: { code: env.WA_LANG || "en" },
            components: [
              { type: "header", parameters: [{ type: "document", document: { id: upj.id, filename } }] },
              { type: "body", parameters: [name, company, String(score), band].map((t) => ({ type: "text", text: t })) }
            ]
          }
        })
      });
      const mj = await msg.json();
      if (!msg.ok) {
        const code = mj && mj.error && mj.error.code;
        return json({ ok: false, error: code === 131026 ? "not_on_whatsapp" : "send_failed" }, 502, cors);
      }
      return json({ ok: true }, 200, cors);
    } catch {
      return json({ ok: false, error: "server" }, 500, cors);
    }
  }
};
