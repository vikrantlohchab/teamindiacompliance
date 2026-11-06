# TCI report → WhatsApp (Cloudflare Worker)

Sends the generated TCI report PDF to the user's WhatsApp through the Meta WhatsApp Cloud API.
The website works without it: until `endpoint` is set in `window.TCI_CONFIG` (see `tools/build_pages.py`), the phone field is hidden and users just download or print the PDF.

## Flow
Browser builds the PDF (`score-pdf.js`) → POST JSON to this Worker → Worker checks origin, captcha and rate limits → uploads the PDF to WhatsApp media → sends an approved **template message with the PDF as its header** → returns `{ok:true}`. Nothing is stored.

## One-time setup
1. **Meta**: create a Meta Business account and complete business verification. In *WhatsApp Manager* create a WhatsApp Business Account and add the sending number.
   - A number already used in the WhatsApp Business app may stop working there when moved to the API. Check Meta's "coexistence" option, or use a new number.
2. **Access token**: Business Settings → System Users → create one → assign the WABA → generate a **permanent token** with `whatsapp_business_messaging` and `whatsapp_business_management`. Note the **Phone number ID**.
3. **Template** (WhatsApp Manager → Message templates), category **Utility**, language English, name `tci_report_delivery`:
   - Header: **Document** (upload any sample PDF)
   - Body: `Hello {{1}}, thank you for completing the TeamIndia Compliance Index self-assessment for {{2}}. Your report is attached. Preliminary score: {{3}}/100 ({{4}}). For a verified, in-depth analysis, reply to this message and our team will help you.`
   - Footer: `TeamIndia Compliance` · Button: Quick reply `Talk to an expert`
   - Keep it transactional (no offers). Meta may re-classify promotional wording as Marketing, which costs more.
4. **Cloudflare**: create a free account, then in this folder:
   ```bash
   npm i -g wrangler && wrangler login
   wrangler kv namespace create RL          # paste the id into wrangler.toml
   wrangler secret put WA_TOKEN             # permanent token
   wrangler secret put WA_PHONE_ID          # phone number ID
   wrangler secret put TURNSTILE_SECRET     # from step 5
   wrangler deploy                          # prints https://tci-whatsapp-report.<you>.workers.dev
   ```
5. **Captcha**: Cloudflare → Turnstile → add the site `teamindiacompliance.com` → copy the *site key* and *secret key*.
6. **Turn it on**: in `tools/build_pages.py` set `window.TCI_CONFIG = { endpoint: "<worker url>", turnstileSiteKey: "<site key>" }`, run `python3 tools/build_pages.py`, commit and push.
7. **Test with your own number** first, then check the lead email arrives at the Web3Forms inbox.

## Guards in the Worker
Allowed origins only · Turnstile captcha · 5 requests/hour per IP · 2 per phone number per day · PDF must be < ~500 KB and start with `%PDF` · input validation.

## Costs and rules
- Utility template messages are billed per message by Meta (rates are on Meta's WhatsApp pricing page; check the current India rate). Cloudflare Workers free tier is plenty at this volume.
- You may only message people who opted in. The form has an explicit consent checkbox and links to `/privacy-policy/`. Have the policy reviewed by counsel.
- Replies from users open a 24-hour window in which you can answer freely from the WhatsApp Business inbox.
