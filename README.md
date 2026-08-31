# Owl Orchard — owlorchard.com

Marketing and support site for Owl Orchard LLC, covering all five apps. The deployed site is
plain static HTML sharing one stylesheet — **no build step at deploy time, no dependencies, no
JavaScript required to read any page.**

```
wrangler.jsonc                          Cloudflare Workers static-assets config
tools/build.py                          Page generator (see "Editing" below)
public/
  index.html                            Home — studio intro + all five apps
  hex-chess.html                        Hex Chess
  politica.html                         Politica: Congress Tracker
  prism.html                            Prism — Music Visualizer
  card-games-for-imessage.html          Card Games for iMessage
  poker-for-imessage.html               Poker for iMessage
  about.html                            About the studio
  support.html                          Support + per-app FAQ
  privacy.html                          Index of all five privacy policies
  privacy-hex-chess.html                Privacy — Hex Chess
  privacy-politica.html                 Privacy — Politica
  privacy-prism.html                    Privacy — Prism
  privacy-card-games.html               Privacy — Card Games
  privacy-poker.html                    Privacy — Poker
  404.html                              Not found
  style.css                             Shared styles (light + dark, per-app accents)
  robots.txt, sitemap.xml
  assets/
    owl.svg, owl-192.png                Site mark / favicon / apple-touch-icon
    *-icon.png                          App icons, 512px, from each project's asset catalog
    pano/*.jpg                          Full App Store panorama banner per app
```

## Editing

Every page duplicates the same header and footer, because a static site has no includes.
`tools/build.py` is the single source of truth for that chrome and for page content — edit it and
re-run:

```
python3 tools/build.py
```

It rewrites every file in `public/` except `style.css` and `assets/`. **Hand-editing the HTML
works too, but the next `build.py` run overwrites it** — so put real changes in the generator.
`style.css` and everything in `assets/` are maintained by hand and are never touched by the
generator.

## Local preview

```
python3 -m http.server 8931 --directory public
```

Then open http://localhost:8931. Links use absolute paths (`/style.css`), so open it through a
server rather than double-clicking the files. `.claude/launch.json` runs the same command.

## Deploy (Cloudflare Workers — static assets)

Connected to this repo. Pushing to `main` deploys automatically.

- Build command: *(empty)*
- Deploy command: `npx wrangler deploy`

`wrangler.jsonc` serves `./public` with no server code and falls back to `public/404.html`.

## Design notes

- **Per-app accents.** `style.css` defines `--accent` per app via `.t-hexchess`, `.t-politica`,
  `.t-prism`, `.t-cardgames`, `.t-poker`. Put the class on a section (or card) and buttons,
  pills, rules, and hero tints pick it up. Both light and dark values are defined.
- **Panorama banners.** Each app page shows its full App Store panorama at a fixed height in a
  horizontally scrollable, full-bleed strip, rather than sliced screenshots. `pano/*.jpg` are
  1000px tall. The "scroll sideways" hint below each one is shown by script only when the
  banner actually overflows, so it never lies on a wide screen.
- **App icons** come from each project's own asset catalog (`AppIcon.appiconset`), not from the
  App Store CDN — the CDN serves the Liquid Glass renders, which have transparent margins.
- **Progressive enhancement.** The only JavaScript is a scroll-reveal animation and the pano
  hint. Both no-op without JS, and both respect `prefers-reduced-motion`.

## App Store Connect URLs

| App | Support URL | Marketing URL | Privacy Policy URL |
|---|---|---|---|
| Hex Chess | `/support.html#hex-chess` | `/hex-chess.html` | `/privacy-hex-chess.html` |
| Politica | `/support.html#politica` | `/politica.html` | `/privacy-politica.html` |
| Prism | `/support.html#prism` | `/prism.html` | `/privacy-prism.html` |
| Card Games | `/support.html#card-games` | `/card-games-for-imessage.html` | `/privacy-card-games.html` |
| Poker | `/support.html#card-games` | `/poker-for-imessage.html` | `/privacy-poker.html` |

All relative to `https://owlorchard.com`.

## Open items

- **`support@owlorchard.com` must receive mail** before these URLs go into App Store Connect.
  Set up Cloudflare Email Routing to forward it.
- **The old GitHub Pages micro-sites are now superseded** — `hexchess-support`,
  `PoliticaSupport`, `PrismSupport`, `PocketPokerSupport`, `DeckedOutSupport`,
  `PoliticaPrivacyPolicy`, `PrismPrivacyPolicy`, `PocketPokerPrivacyPolicy`. Their content was
  carried over and expanded here. Point App Store Connect at this site, then archive them.
- **App Store developer name is "Sawyer Christensen", not "Owl Orchard LLC".** The site treats
  Owl Orchard as the studio and names Sawyer as the developer, which is accurate either way —
  but if the App Store listings should read "Owl Orchard LLC", that is an App Store Connect
  change, and the three non-LLC privacy policies should be reworded to match.
- **Privacy claims are per-app, deliberately.** Only the two iMessage apps claim "no networking
  code." Hex Chess (Firebase), Politica (government APIs), and Prism (ReccoBeats) each describe
  what actually leaves the device. If any app's behaviour changes, its policy must change too.
- **Poker for iMessage** is marked "Coming soon". Once it is live, add its App Store URL to
  `APPS` in `tools/build.py` and re-run the generator — the button, badge, and structured data
  all update from that one field.
