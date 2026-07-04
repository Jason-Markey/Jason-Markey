# Put the Marketing Command Centre online with Cloudflare Tunnel

Goal: open the dashboard from your phone or any laptop at
**https://marketing.pricelinepf.com.au**, with ticks synced everywhere, protected by an
email login. The app keeps running on ONE always-on machine (the same PC that runs the
POS dashboard is perfect) — Cloudflare just tunnels traffic to it. Free.

**How the sync works:** there's only one copy of the app and one `marketing_state.json`,
on the shop PC. Your phone and laptop are just browser windows into it — so a tick made
anywhere shows up everywhere, instantly.

---

## Step 0 — Try it in 2 minutes (optional, no account needed)

On the PC running the app, in Command Prompt:

```
winget install --id Cloudflare.cloudflared
cloudflared tunnel --url http://localhost:8060
```

It prints a random `https://xxxx.trycloudflare.com` URL — open it on your phone. That's
the experience you're setting up. This trial URL is temporary and **has no login**, so
close it (Ctrl+C) when done and do the real setup below.

---

## Step 1 — Put pricelinepf.com.au on Cloudflare (one-time, ~15 min)

Skip if the domain is already on Cloudflare.

1. Sign up free at https://dash.cloudflare.com → **Add a domain** → `pricelinepf.com.au`
   → Free plan.
2. Cloudflare shows two nameservers. Log in to your domain registrar and replace the
   existing nameservers with those two.
3. Wait for Cloudflare to email "your site is active" (minutes to a few hours).
   Your email and website keep working — Cloudflare imports your existing DNS records;
   double-check the list it imports matches before confirming.

## Step 2 — Create the tunnel (on the shop PC)

```
cloudflared tunnel login
cloudflared tunnel create marketing
cloudflared tunnel route dns marketing marketing.pricelinepf.com.au
```

(The login command opens a browser — pick pricelinepf.com.au.)
Note the tunnel ID it prints (a long UUID). Then create the config file at
`C:\Users\<you>\.cloudflared\config.yml`:

```yaml
tunnel: <TUNNEL-ID>
credentials-file: C:\Users\<you>\.cloudflared\<TUNNEL-ID>.json

ingress:
  - hostname: marketing.pricelinepf.com.au
    service: http://localhost:8060
  - service: http_status:404
```

Install it as a Windows service so it survives reboots:

```
cloudflared service install
```

## Step 3 — Lock it behind a login (Cloudflare Access, free)

Right now the URL would be open to the internet — fix that before using it:

1. https://one.dash.cloudflare.com → **Access → Applications → Add an application**
   → Self-hosted.
2. Application domain: `marketing.pricelinepf.com.au`.
3. Add a policy → Action **Allow** → Include → **Emails** → add
   `jason@pricelinepf.com.au` (and any team emails).
4. Save. Login method: One-time PIN is on by default — you enter your email, get a
   code, you're in. Sessions last 24h by default (set longer in the app settings if
   you like).

**Belt and braces (optional):** the app also supports its own password. On the shop PC
set a user environment variable `MARKETING_PASSWORD` to a password of your choosing and
restart the app — browsers will then also ask for it (any username). Skip this if
Cloudflare Access feels like enough.

## Step 4 — Keep the app running on the shop PC

1. `pip install waitress` (one-time — makes the app run on a proper production server).
2. Put a shortcut to `start_hidden_marketing.vbs` in the Startup folder
   (Win+R → `shell:startup`), same as the POS dashboard.
3. Reboot once to confirm: the PC comes up, the app and tunnel auto-start, and
   https://marketing.pricelinepf.com.au works from your phone.

---

## Day-to-day

- Open **https://marketing.pricelinepf.com.au** anywhere, log in with your email PIN,
  tick things off. Everything stays in sync because it's all one app.
- On the shop PC itself you can keep using http://localhost:8060 (no login needed
  locally unless you set MARKETING_PASSWORD).
- If the site ever doesn't load: the shop PC is off, the app isn't running (rerun the
  .vbs), or the tunnel service stopped (`net start cloudflared`).

## Notes

- The POS dashboard (port 8050) stays private on the shop PC — this setup only exposes
  the marketing app. (You could tunnel the POS one the same way later; it holds
  business figures, so keep Access rules tight if you do.)
- Total cost: $0 (Cloudflare free plan + Access free for up to 50 users).
