# Owl Orchard — owlorchard.com

Static marketing and support site for Owl Orchard LLC. No build step, no dependencies.
Every page is plain HTML sharing one stylesheet.

```
wrangler.jsonc                         Cloudflare Workers static-assets config
public/index.html                      Home
public/poker-for-imessage.html         Poker for iMessage
public/card-games-for-imessage.html    Card Games for iMessage
public/support.html                    Support + FAQ
public/privacy-poker.html              Privacy policy — Poker
public/privacy-card-games.html         Privacy policy — Card Games
public/404.html                        Not found
public/style.css                       Shared styles (light + dark)
public/assets/                         App icons
```

## Local preview

```
python3 -m http.server 8931 --directory public
```

Then open http://localhost:8931. Links use absolute paths (`/style.css`), so open it through
a server rather than double-clicking the files.

## Deploy (Cloudflare Workers — static assets)

Connected to this repo. Pushing to `main` deploys automatically.

- Build command: *(empty)*
- Deploy command: `npx wrangler deploy`

Everything else lives in `wrangler.jsonc`: it serves `./public` with no server code, and
falls back to `public/404.html` for unmatched paths.

## App Store Connect URLs

| Field | Poker for iMessage | Card Games for iMessage |
|---|---|---|
| Support URL | `https://owlorchard.com/support.html` | `https://owlorchard.com/support.html` |
| Marketing URL | `https://owlorchard.com/poker-for-imessage.html` | `https://owlorchard.com/card-games-for-imessage.html` |
| Privacy Policy URL | `https://owlorchard.com/privacy-poker.html` | `https://owlorchard.com/privacy-card-games.html` |

## Notes

- The privacy policies claim the apps have **no networking code, no analytics, and no third-party
  SDKs**. That is true as of this writing and was verified against both repos. If that ever
  changes, both policies must change with it.
- `support@owlorchard.com` needs to actually receive mail before the App Store review; set up
  Cloudflare Email Routing to forward it.
- Poker for iMessage is marked "Coming soon". Once it is live, add the App Store link to
  `poker-for-imessage.html` (use the same `.store-link` markup as the Card Games page) and swap
  the badge on `index.html`.
