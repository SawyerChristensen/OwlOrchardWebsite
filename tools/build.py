#!/usr/bin/env python3
"""Generate owlorchard.com.

Emits plain static HTML into public/. The deployed site has no build step; this exists
only so the shared header, footer, and page chrome stay identical across every page.
Run it from anywhere:  python3 tools/build.py

It rewrites every .html file in public/ plus robots.txt, sitemap.xml, and assets/owl.svg.
It never touches public/style.css or the images in public/assets/."""

import json, os, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "public"
SITE = "https://owlorchard.com"
EMAIL = "support@owlorchard.com"
GH = "https://github.com/SawyerChristensen"

# Exact geometry from the vector original, Documents/OwlOrchard/owlOrchardLogo.psd
# (live Photoshop shape layers, read straight off their vector masks): two tangent rings
# (r=375, stroke 100, centres 750 apart), two eyebrow bars flush with the ring tops, and
# a 200x200 square beak rotated 45 degrees. PSD coordinates less (200, 575), which puts
# the artwork's own bounding box at the origin. Uses currentColor so it inherits the theme.
OWL = (
    '<svg viewBox="0 0 1600 1083.17" aria-hidden="true" focusable="false">'
    '<g fill="currentColor">'
    '<rect width="425" height="100"/>'
    '<rect x="1175" width="425" height="100"/>'
    '<path d="M800 800.33 941.42 941.75 800 1083.17 658.58 941.75Z"/>'
    '</g>'
    '<g fill="none" stroke="currentColor" stroke-width="100">'
    '<circle cx="425" cy="425" r="375"/>'
    '<circle cx="1175" cy="425" r="375"/>'
    '</g>'
    "</svg>"
)

# ---------------------------------------------------------------- app catalog

APPS = [
    dict(
        key="hexchess", slug="hex-chess.html", theme="t-hexchess",
        name="Hex Chess", short="Hex Chess",
        tagline="Chess, one ring wider.",
        icon="/assets/hexchess-icon.png",
        sub="iPhone &amp; iPad", status="live",
        store="https://apps.apple.com/us/app/hex-chess/id6743667749",
        desc="Gli&#324;ski&rsquo;s 1936 hexagonal chess, with a CPU opponent, pass-and-play, "
             "and ranked online matches against friends.",
        pills=["Board game", "25 languages"],
        privacy="/privacy-hex-chess.html",
        meta_desc="Hex Chess brings Gli&#324;ski&rsquo;s hexagonal chess to iPhone and iPad — "
                  "a CPU opponent, pass-and-play, ranked online matches, and Game Center achievements. Free.",
        category="GameApplication", os="iOS 17.0 or later",
    ),
    dict(
        key="politica", slug="politica.html", theme="t-politica",
        name="Politica: Congress Tracker", short="Politica",
        tagline="Congress, made legible.",
        icon="/assets/politica-icon.png",
        sub="iPhone &amp; iPad", status="live",
        store="https://apps.apple.com/us/app/politica-congress-tracker/id6786447664",
        desc="Track your representatives, follow every bill and roll-call vote, and see the "
             "money moving behind the campaigns.",
        pills=["Reference", "English &amp; Spanish"],
        privacy="/privacy-politica.html",
        meta_desc="Politica tracks the U.S. Congress on your iPhone: your representatives, live bill "
                  "progress, roll-call votes, campaign finance, and an interactive district map. Free.",
        category="MobileApplication", os="iOS 18.0 or later",
    ),
    dict(
        key="prism", slug="prism.html", theme="t-prism",
        name="Prism &mdash; Music Visualizer", short="Prism",
        tagline="Your music, rendered.",
        icon="/assets/prism-icon.png",
        sub="Mac", status="live",
        store="https://apps.apple.com/us/app/prism-music-visualizer/id6798428433?mt=12",
        desc="Milkdrop visuals rendered live from whatever your Mac is playing, with a curated "
             "library of 2,500+ community presets.",
        pills=["Music", "22 languages"],
        privacy="/privacy-prism.html",
        meta_desc="Prism renders classic Milkdrop visuals live from any audio playing on your Mac — "
                  "2,500+ .milk presets, beat-synced album art, plus a Music plug-in and screen saver. Free.",
        category="MobileApplication", os="macOS 26.0 or later",
    ),
    dict(
        key="cardgames", slug="card-games-for-imessage.html", theme="t-cardgames",
        name="Card Games for iMessage", short="Card Games",
        tagline="Your seat at the table is ready.",
        icon="/assets/cardgames-icon.png",
        sub="iMessage app", status="live",
        store="https://apps.apple.com/us/app/card-games-for-imessage/id6757935828",
        desc="Gin Rummy, Crazy 8s, and Golf, played a turn at a time inside the text threads "
             "you are already in.",
        pills=["Card game", "18 languages"],
        privacy="/privacy-card-games.html",
        meta_desc="Gin Rummy, Crazy 8s, and Golf played turn by turn inside your iMessage threads. "
                  "Free, no ads, no accounts, no tracking.",
        category="GameApplication", os="iOS 17.0 or later",
    ),
    dict(
        key="poker", slug="poker-for-imessage.html", theme="t-poker",
        name="Poker for iMessage", short="Poker",
        tagline="Deal a hand into the group chat.",
        icon="/assets/poker-icon.png",
        sub="iMessage app", status="soon",
        store=None,
        desc="Texas Hold&rsquo;Em, Omaha, and 7 Card Stud, dealt straight into a conversation. "
             "No real money, ever.",
        pills=["Card game", "18 languages"],
        privacy="/privacy-poker.html",
        meta_desc="Texas Hold'Em, Omaha, and 7 Card Stud played turn by turn inside your iMessage "
                  "threads. Free to play, no ads, no real money. Coming soon.",
        category="GameApplication", os="iOS 17.0 or later",
    ),
]

BY = {a["key"]: a for a in APPS}

NAV = [("/#apps", "Apps"), ("/about.html", "About"), ("/support.html", "Support")]


def status_pill(app):
    if app["status"] == "live":
        return '<span class="pill pill-live">On the App Store</span>'
    return '<span class="pill pill-soon">Coming soon</span>'


# ---------------------------------------------------------------- page chrome

def head(title, desc, canonical, theme="", icon="/assets/owl.svg", jsonld=None):
    ld = ""
    if jsonld:
        ld = ('\n<script type="application/ld+json">'
              + json.dumps(jsonld, separators=(",", ":")) + "</script>")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{canonical}">
<link rel="stylesheet" href="/style.css">
<link rel="icon" href="{icon}" type="{'image/svg+xml' if icon.endswith('.svg') else 'image/png'}">
<link rel="apple-touch-icon" href="/assets/owl-192.png">
<meta name="theme-color" content="#fbfaf7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#12140f" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Owl Orchard">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}{canonical}">
<meta name="twitter:card" content="summary">{ld}
<script>document.documentElement.className += " js";</script>
</head>
<body{f' class="{theme}"' if theme else ''}>

<a class="skip" href="#main">Skip to content</a>
"""


def header(current):
    links = "".join(
        f'\n      <a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>'
        for href, label in NAV
    )
    return f"""
<header class="site">
  <div class="wrap">
    <a class="brand" href="/">{OWL}<span>Owl Orchard</span></a>
    <nav class="site" aria-label="Primary">{links}
    </nav>
  </div>
</header>
"""


def footer():
    apps = "".join(f'\n        <li><a href="/{a["slug"]}">{a["short"]}</a></li>' for a in APPS)
    return f"""
<footer class="site">
  <div class="wrap">
    <div class="foot-grid">

      <div>
        <span class="foot-brand">{OWL}<span>Owl Orchard</span></span>
        <p>An independent software studio in Oregon, building native apps for
        Apple platforms. Free, quiet, and made to last.</p>
      </div>

      <div>
        <h4>Apps</h4>
        <ul>{apps}
        </ul>
      </div>

      <div>
        <h4>Studio</h4>
        <ul>
          <li><a href="/about.html">About</a></li>
          <li><a href="/support.html">Support</a></li>
          <li><a href="{GH}" rel="noopener">GitHub</a></li>
          <li><a href="mailto:{EMAIL}">Email</a></li>
        </ul>
      </div>

      <div>
        <h4>Legal</h4>
        <ul>
          <li><a href="/privacy.html">Privacy policies</a></li>
          <li><a href="/support.html#refunds">Refunds</a></li>
        </ul>
      </div>

    </div>

    <div class="foot-legal">
      <p>&copy; 2026 Owl Orchard LLC &mdash; Oregon, USA</p>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
  </div>
</footer>
"""


REVEAL_JS = """
<script>
(function () {
  var els = document.querySelectorAll(".reveal");
  if (!els.length) return;
  if (!("IntersectionObserver" in window) ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    for (var i = 0; i < els.length; i++) els[i].classList.add("in");
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
  els.forEach(function (el) { io.observe(el); });
})();

// The panorama only needs a "scroll sideways" hint when it actually overflows.
(function () {
  var panos = document.querySelectorAll(".pano");
  if (!panos.length) return;
  function sync() {
    for (var i = 0; i < panos.length; i++) {
      var p = panos[i], hint = p.nextElementSibling;
      if (!hint || !hint.classList.contains("pano-hint")) continue;
      hint.classList.toggle("is-scrollable", p.scrollWidth > p.clientWidth + 4);
    }
  }
  window.addEventListener("load", sync);
  window.addEventListener("resize", sync);
  sync();
})();
</script>
"""


def page(path, title, desc, body, current="", theme="", icon="/assets/owl.svg", jsonld=None):
    html = (head(title, desc, "/" + path if path != "index.html" else "/", theme, icon, jsonld)
            + header(current)
            + '\n<main id="main">\n' + body + "\n</main>\n"
            + footer() + REVEAL_JS + "\n</body>\n</html>\n")
    (OUT / path).write_text(html, encoding="utf-8")
    print(f"  {path:32s} {len(html):>6,} bytes")


def app_card(app):
    store_note = status_pill(app)
    pills = ""
    return f"""
      <a class="card {app['theme']} reveal" href="/{app['slug']}">
        <div class="card-top">
          <img class="icon" src="{app['icon']}" alt="" width="64" height="64" loading="lazy">
          <div>
            <h3>{app['name']}</h3>
            <p class="card-sub">{app['sub']} &middot; {app['pills'][0]}</p>
          </div>
        </div>
        <p class="desc">{app['desc']}</p>
        <div class="card-foot">
          {store_note}{pills}
          <span class="more" aria-hidden="true">View &rarr;</span>
        </div>
      </a>"""


def app_head(app, extra_pills=()):
    if app["store"]:
        cta = (f'<a class="btn btn-primary" href="{app["store"]}" rel="noopener">'
               "Download on the App Store</a>")
    else:
        cta = '<span class="btn" aria-disabled="true">Coming soon to the App Store</span>'
    pills = "".join(f'<span class="pill">{p}</span>' for p in extra_pills)
    return f"""
  <div class="app-head">
    <img src="{app['icon']}" alt="{app['short']} app icon" width="116" height="116">
    <div>
      <h1>{app['name']}</h1>
      <p class="tagline">{app['tagline']}</p>
      <div class="pills">{status_pill(app)}{pills}</div>
    </div>
  </div>

  <div class="hero-actions">{cta}
    <a class="btn btn-ghost" href="/support.html">Support</a>
  </div>"""


PANO = {
    "hexchess":  (2307, 1000),
    "politica":  (2773, 1000),
    "cardgames": (2773, 1000),
    "poker":     (2311, 1000),
    "prism":     (4800, 1000),
}


def pano(key, alt):
    w, h = PANO[key]
    return f"""
<div class="pano" role="group" aria-label="{alt}">
  <img src="/assets/pano/{key}.jpg" alt="{alt}" width="{w}" height="{h}" fetchpriority="high">
</div>
<p class="pano-hint"><span>Scroll sideways for the rest &rarr;</span></p>"""


def features(items):
    lis = "".join(f"\n    <li>\n      <h3>{t}</h3>\n      <p>{d}</p>\n    </li>" for t, d in items)
    return f'\n  <ul class="features reveal">{lis}\n  </ul>'


def deftable(rows):
    out = "".join(f"\n    <div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)
    return f'\n  <dl class="deftable">{out}\n  </dl>'


def app_jsonld(app):
    d = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": app["name"].replace("&mdash;", "—"),
        "applicationCategory": app["category"],
        "operatingSystem": app["os"],
        "url": f"{SITE}/{app['slug']}",
        "author": {"@type": "Organization", "name": "Owl Orchard LLC"},
        "publisher": {"@type": "Organization", "name": "Owl Orchard LLC"},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    if app["store"]:
        d["installUrl"] = app["store"]
    return d


# ================================================================== home

def build_home():
    cards = "".join(app_card(a) for a in APPS)
    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="prose">
      <span class="eyebrow">Independent studio &middot; Oregon, USA</span>
      <h1>Native apps, built one at a time.</h1>
      <p class="lede">Owl Orchard is an independent software studio in Oregon, building
      native apps for iPhone, iPad, and Mac. Five so far: hexagonal chess, card games that
      live inside iMessage, a tracker for the U.S. Congress, and a music visualizer for
      macOS.</p>
      <p>Every one of them is free. None of them show you an advertisement, and none of them
      ask you to make an account unless you actually want a ranked online match.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="#apps">See the apps</a>
        <a class="btn btn-ghost" href="/about.html">About the studio</a>
      </div>
    </div>

    <dl class="stats">
      <div class="stat"><dt>Apps</dt><dd>5</dd></div>
      <div class="stat"><dt>Platforms</dt><dd>iOS &middot; iPadOS &middot; macOS</dd></div>
      <div class="stat"><dt>Localized into</dt><dd>Up to 25 languages</dd></div>
      <div class="stat"><dt>Price</dt><dd>Free</dd></div>
    </dl>
  </div>
</section>

<section class="section" id="apps">
  <div class="wrap">
    <div class="prose" style="margin-bottom:34px">
      <h2>The apps</h2>
      <p>Four are on the App Store today. The fifth is finished and on its way.</p>
    </div>
    <div class="appgrid">{cards}
    </div>
  </div>
</section>

<section class="section band">
  <div class="wrap">
    <div class="prose" style="margin-bottom:8px">
      <h2>How the work gets done</h2>
      <p>Four things hold across every project, whether it is a chess engine or a
      congressional bill feed.</p>
    </div>
{features([
  ("Native, all the way down",
   "Swift and SwiftUI against Apple&rsquo;s own frameworks &mdash; SpriteKit, MapKit, "
   "WidgetKit, StoreKit, Metal. No web views wrapped in an app shell, and no "
   "cross-platform runtime standing between you and the hardware."),
  ("Free, and honest about it",
   "Every app is free to download and free to play. There is no advertising SDK in any of "
   "them, no subscription, and no feature held hostage. The only thing ever sold is a "
   "cosmetic card back, bought once."),
  ("Built for more than English",
   "Hex Chess ships in 25 languages, Prism in 22, the card game apps in 18. VoiceOver and "
   "Voice Control reach individual cards and board tiles; Dynamic Type and Reduce Motion "
   "are honored throughout."),
  ("Privacy as an architecture choice",
   "The iMessage apps contain no networking code at all. Politica resolves your location "
   "on device and never transmits it. Hex Chess only asks for an account if you want a "
   "ranked online game. Nothing is tracked, sold, or shared."),
])}
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="prose reveal">
      <span class="eyebrow">The studio</span>
      <h2>Made in Oregon, slowly.</h2>
      <p>Owl Orchard is small and independent, with no investors to answer to and no growth
      target to hit. That shows up in the work: fewer apps, released when they are actually
      finished, and kept working afterwards rather than replaced by the next thing.</p>
      <p>It also means nobody here is arguing for an analytics SDK, and no app in the
      catalogue needs anything from you beyond the time you choose to spend in it.</p>
      <div class="hero-actions">
        <a class="btn btn-ghost" href="/about.html">About the studio</a>
        <a class="btn btn-ghost" href="/support.html">Get in touch</a>
      </div>
    </div>
  </div>
</section>
"""
    ld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Owl Orchard LLC",
        "alternateName": "Owl Orchard",
        "url": SITE,
        "email": EMAIL,
        "address": {"@type": "PostalAddress", "addressRegion": "OR", "addressCountry": "US"},
        "sameAs": [GH],
    }
    page("index.html", "Owl Orchard — native apps for iPhone, iPad, and Mac",
         "Owl Orchard is an independent software studio in Oregon. "
         "Hex Chess, Politica, Prism, and card games for iMessage — all free, all native, none tracking you.",
         body, current="/#apps", jsonld=ld)


# ================================================================== app pages

def build_hexchess():
    a = BY["hexchess"]
    body = f"""
<section class="hero {a['theme']}">
  <div class="wrap">
{app_head(a, ["iOS 17+", "Free", "Game Center"])}
  </div>
</section>

<section class="section-sm {a['theme']}" style="padding-bottom:0">
{pano("hexchess", "Hex Chess: the main menu, the hexagonal board mid-game, achievements, online play with friends, and a game running inside an iMessage thread")}
</section>

<section class="section {a['theme']}" style="padding-top:0">
  <div class="wrap">
    <div class="prose">
      <p class="lede">Hexagonal chess was invented in 1936 by the Polish engineer W&#322;adys&#322;aw
      Gli&#324;ski. It keeps every piece you already know and puts them on a board of 91 hexagons,
      where a bishop has three colours to work with, a pawn captures diagonally into a
      different geometry, and none of your memorized openings survive contact.</p>

      <p>That is the appeal. Hex Chess is as easy to learn as ordinary chess and levels the
      board between a grandmaster and a beginner, because on ninety-one hexes nobody has
      twenty years of pattern recognition to fall back on.</p>
    </div>
{features([
  ("Play the computer",
   "A CPU opponent for practice, on a board where the usual heuristics do not transfer. "
   "Good for learning how the three-colour bishops and hex-diagonal pawns actually behave."),
  ("Pass and play",
   "Hand the device back and forth for a game across one table &mdash; no account, no "
   "connection, no setup."),
  ("Ranked online matches",
   "Send a friend a game code and play over the network, with an Elo rating and a global "
   "leaderboard tracking where you land."),
  ("Game Center achievements",
   "Achievements and progress tracked through Apple&rsquo;s own Game Center, viewable straight "
   "from the main menu."),
  ("Live Activities",
   "An active game can surface on the Lock Screen and in the Dynamic Island, so you know "
   "when it is your move without opening the app."),
  ("Twenty-five languages",
   "Hex Chess ships localized in twenty-five languages, from Arabic and Armenian to "
   "Turkish and both written forms of Chinese."),
])}

    <div class="prose">
      <h2>Details</h2>
{deftable([
  ("Platforms", "iPhone and iPad, iOS 17.0 or later"),
  ("Price", "Free"),
  ("Category", "Board &middot; Strategy"),
  ("Languages", "25"),
  ("Accounts", "Optional &mdash; sign in with Apple, Google, or email only if you want "
               "online play, achievements, and the leaderboard"),
  ("Source", f'<a href="{GH}/Chexx" rel="noopener">github.com/SawyerChristensen/Chexx</a>'),
])}

      <h2>Privacy</h2>
      <p>Playing offline against the CPU or passing the device around collects nothing at all.
      If you sign in for online play, a display name and avatar are stored so opponents can
      see who they are playing; your email is used for authentication and never shown to
      anyone. Read the <a href="{a['privacy']}">full privacy policy</a>.</p>
    </div>
  </div>
</section>
"""
    page(a["slug"], f"Hex Chess — Owl Orchard", a["meta_desc"], body,
         theme=a["theme"], icon=a["icon"], jsonld=app_jsonld(a))


def build_politica():
    a = BY["politica"]
    body = f"""
<section class="hero {a['theme']}">
  <div class="wrap">
{app_head(a, ["iOS 18+", "Free", "No account"])}
  </div>
</section>

<section class="section-sm {a['theme']}" style="padding-bottom:0">
{pano("politica", "Politica: the recent bills feed, bill detail with roll-call votes, representative profiles, campaign funders, and the interactive congressional district map")}
</section>

<section class="section {a['theme']}" style="padding-top:0">
  <div class="wrap">
    <div class="prose">
      <p class="lede">Congress publishes almost everything it does. The problem was never
      secrecy &mdash; it is that the record is scattered across half a dozen government
      systems, none of which were built to be read on a phone.</p>

      <p>Politica pulls those sources into one app: who represents you, what they voted on,
      what they sponsored, who funds them, what they trade, and where the bill you care about
      currently sits on its way to becoming law.</p>
    </div>
{features([
  ("Know who represents you",
   "Your House member, both senators, and your state&rsquo;s governor &mdash; found from precise "
   "location, approximate location, or a ZIP code you type in. Location is resolved on "
   "device and never transmitted."),
  ("A feed that ranks by progress",
   "Recent bills weighted by how far each one got &mdash; introduced, in committee, passed a "
   "chamber, on the president&rsquo;s desk, enacted &mdash; and by recency, including the notable "
   "ones that failed. Searchable by title, subject, progress, and topic."),
  ("Roll calls, your reps first",
   "Full House and Senate vote tallies on every bill, with your own representatives&rsquo; votes "
   "surfaced at the top. Bookmark a bill and get a local notification when its status moves."),
  ("Follow the money",
   "Per-representative profiles covering committees, sponsored and cosponsored bills, "
   "contact details, complete voting history, and the top PACs and individual donors behind "
   "the campaign."),
  ("Trading disclosures",
   "A trading-activity indicator assembled from House Periodic Transaction Reports and the "
   "Senate&rsquo;s electronic filing portal &mdash; the stock trades members are required to "
   "disclose, parsed and surfaced."),
  ("Governors too",
   "Your state&rsquo;s governor gets a profile of their own, including a &ldquo;Laws Passed&rdquo; section "
   "pulled live from LegiScan for everything enacted this legislative session."),
  ("An interactive district map",
   "Every U.S. congressional district drawn as a coloured outline. It opens on yours; tap "
   "any other to see who represents it alongside population, primary industries, average "
   "income, and local universities. Zoom out and districts fade into states."),
  ("A widget, and offline",
   "A Home Screen widget surfacing the top bill in Congress, deep-linking into its detail "
   "screen. Bills, roll calls, your full delegation, and map boundaries are cached on "
   "device so they still read with no signal."),
])}

    <div class="prose">
      <h2>Where the data comes from</h2>
      <p>All of it is public, and all of it is cited. Politica reads directly from
      government and open-data sources rather than an intermediary of its own:</p>
      <ul>
        <li><strong>Congress.gov</strong> &mdash; bills, member records, House roll calls</li>
        <li><strong>senate.gov roll-call XML</strong> &mdash; Senate votes, which Congress.gov does not carry</li>
        <li><strong>LegiScan</strong> &mdash; state legislative sessions behind the governors&rsquo; &ldquo;Laws Passed&rdquo;</li>
        <li><strong>OpenFEC</strong> &mdash; campaign finance and top funders</li>
        <li><strong>House Clerk disclosures and the Senate eFD portal</strong> &mdash; trading activity</li>
        <li><strong>U.S. Census Bureau</strong> &mdash; district demographics, geocoding, and the cartographic
        boundary files the map is drawn from</li>
      </ul>

      <h2>Details</h2>
{deftable([
  ("Platforms", "iPhone and iPad, iOS 18.0 or later"),
  ("Price", "Free"),
  ("Category", "Reference &middot; News"),
  ("Languages", "English and Spanish"),
  ("Accounts", "None &mdash; there is nothing to sign in to"),
  ("Source", f'<a href="{GH}/EagleEye" rel="noopener">github.com/SawyerChristensen/EagleEye</a>'),
])}

      <h2>Privacy</h2>
      <p>Politica collects nothing. Your location is turned into a district entirely on your
      own device and is never sent anywhere &mdash; and typing a ZIP code works without granting
      location access at all. Read the <a href="{a['privacy']}">full privacy policy</a>.</p>
    </div>
  </div>
</section>
"""
    page(a["slug"], "Politica: Congress Tracker — Owl Orchard", a["meta_desc"], body,
         theme=a["theme"], icon=a["icon"], jsonld=app_jsonld(a))


def build_prism():
    a = BY["prism"]
    body = f"""
<section class="hero {a['theme']}">
  <div class="wrap">
{app_head(a, ["macOS 26+", "Free", "Apple Silicon"])}
  </div>
</section>

<section class="section-sm {a['theme']}" style="padding-bottom:0">
{pano("prism", "Prism: Milkdrop presets rendering full screen on a Mac, with beat-synced album art composited over the visuals")}
</section>

<section class="section {a['theme']}" style="padding-top:0">
  <div class="wrap">
    <div class="prose">
      <p class="lede">Point Prism at any audio playing on your Mac &mdash; Spotify, Apple Music, a
      browser tab, anything &mdash; and it renders classic Milkdrop-style visuals in real time.
      Every colour, ripple, and kaleidoscoping shape reacts as the music happens.</p>

      <p>Prism runs genuine <code>.milk</code> preset files through a real, vendored build of the
      projectM engine: the same format that powered two decades of Winamp visuals, not a
      lookalike. Drop in your own preset packs, browse the curated built-in library of more
      than 2,500, or drag a single <code>.milk</code> file onto the window.</p>
    </div>
{features([
  ("Whatever is playing",
   "System audio is captured through Core Audio process taps, so Prism visualizes any app "
   "on the Mac rather than only the one music player it knows about."),
  ("2,500+ real presets",
   "A curated, frame-rate-benchmarked library ships in the app, and any folder of .milk "
   "files can be pointed at instead. NestDrop favourites lists are read if your pack has one."),
  ("Album art that moves",
   "When Spotify or Music is playing, Prism lifts the artwork&rsquo;s subject, pulls its colour "
   "palette, and composites it over the visuals with beat-synced parallax. Press &#8984;A to "
   "hide it and watch the preset alone."),
  ("Smart preset matching",
   "Prism reads a track&rsquo;s energy, mood, and tempo and picks a preset that suits it, instead "
   "of cycling at random."),
  ("Remembers where you were",
   "It reopens on the preset you left, keeps a session history you can step back through "
   "with the arrow keys, and keeps the previous session&rsquo;s log around too."),
  ("Three ways to run it",
   "Prism.app full screen or windowed; a plug-in that appears inside Music&rsquo;s own Visualizer "
   "menu; and a matching screen saver for when the Mac goes idle."),
])}

    <div class="prose">
      <h2>Built for the hardware</h2>
      <p>Prism is native to Apple Silicon. The projectM C++ engine is bridged into Metal
      through an ANGLE/EGL context, which keeps the original OpenGL preset semantics intact
      while rendering on Apple&rsquo;s modern graphics stack. On a current Mac it clears 800 frames
      per second.</p>

      <h2>Details</h2>
{deftable([
  ("Platform", "Mac, macOS 26.0 or later"),
  ("Price", "Free"),
  ("Category", "Music &middot; Graphics &amp; Design"),
  ("Languages", "22"),
  ("Ships as", "App, Music.app visualizer plug-in, and screen saver"),
  ("Permissions", "System audio capture; optionally Apple Events, to read now-playing "
                  "metadata from Spotify or Music"),
  ("Source", f'<a href="{GH}/Prism" rel="noopener">github.com/SawyerChristensen/Prism</a>'),
])}

      <h2>Privacy</h2>
      <p>Prism keeps no listening history and records nothing it captures. The one thing that
      leaves your Mac is the current track&rsquo;s title and artist, sent to a free public music-data
      API so preset matching knows the song&rsquo;s tempo and mood &mdash; with no account, device, or
      personal identifier attached. Read the
      <a href="{a['privacy']}">full privacy policy</a>.</p>
    </div>
  </div>
</section>
"""
    page(a["slug"], "Prism — Music Visualizer for macOS — Owl Orchard", a["meta_desc"], body,
         theme=a["theme"], icon=a["icon"], jsonld=app_jsonld(a))


def build_cardgames():
    a = BY["cardgames"]
    body = f"""
<section class="hero {a['theme']}">
  <div class="wrap">
{app_head(a, ["iOS 17+", "Free", "No account"])}
  </div>
</section>

<section class="section-sm {a['theme']}" style="padding-bottom:0">
{pano("cardgames", "Card Games for iMessage: Gin Rummy, Crazy 8s, and Golf played inside a text thread, with customizable card backs and group chat games")}
</section>

<section class="section {a['theme']}" style="padding-top:0">
  <div class="wrap">
    <div class="prose">
      <p class="lede">Three classic card games that live inside your text threads. Start one in
      a one-on-one conversation or a group chat, and everyone plays whenever they get to it.</p>

      <p>Card Games for iMessage is a standalone iMessage app &mdash; there is no separate app to
      open, no account to create, and no lobby to sit in. A game is a turn in a conversation,
      played at whatever pace suits the people in it, across any number of time zones.</p>

      <h2>The games</h2>
    </div>
{features([
  ("Gin Rummy",
   "Standard straight Gin at seven cards and in group games, with full deadwood calculation "
   "in one-on-one ten-card hands. Build your runs and sets and knock when you are ready."),
  ("Crazy 8s",
   "Shed your hand first. 8s are wild, 2s make the next player draw two, Queens skip, and "
   "Aces reverse the direction of play."),
  ("Golf",
   "Six cards in a grid, and the lowest score wins. Flip, swap, and decide how long to keep "
   "looking before you commit."),
])}

    <div class="prose">
      <h2>What it costs</h2>
      <p>All three games are free and there is no advertising anywhere in the app. The only
      in-app purchase is a card back &mdash; a cosmetic deck design, bought once through Apple&rsquo;s
      own purchase system. A card back bought here also unlocks in Poker for iMessage, and the
      other way round.</p>

      <h2>Accessibility and languages</h2>
      <p>The app ships fully localized in 18 languages and follows your device language
      automatically. It is built to Apple&rsquo;s accessibility standards: VoiceOver and Voice Control
      reach individual cards and game elements, Dynamic Type is supported throughout, and
      animations are reduced when Reduce Motion is on.</p>

      <h2>Details</h2>
{deftable([
  ("Platforms", "iPhone and iPad, iOS 17.0 or later"),
  ("Type", "Standalone iMessage app &mdash; no separate app to open"),
  ("Price", "Free, with optional cosmetic card backs"),
  ("Languages", "18"),
  ("Networking", "None &mdash; the app contains no networking code at all"),
  ("Source", f'<a href="{GH}/DeckedOut" rel="noopener">github.com/SawyerChristensen/DeckedOut</a>'),
])}

      <h2>Privacy</h2>
      <p>The app contains no analytics, no advertising frameworks, and no networking code.
      Nothing about you or your games is sent anywhere, because there is nowhere for it to go.
      Read the <a href="{a['privacy']}">full privacy policy</a>.</p>
    </div>
  </div>
</section>
"""
    page(a["slug"], "Card Games for iMessage — Owl Orchard", a["meta_desc"], body,
         theme=a["theme"], icon=a["icon"], jsonld=app_jsonld(a))


def build_poker():
    a = BY["poker"]
    body = f"""
<section class="hero {a['theme']}">
  <div class="wrap">
{app_head(a, ["iOS 17+", "Free", "No real money"])}
  </div>
</section>

<section class="section-sm {a['theme']}" style="padding-bottom:0">
{pano("poker", "Poker for iMessage: Texas Hold&rsquo;Em, Omaha, and 7 Card Stud dealt into a text thread, with chips, betting rounds, and group chat tables")}
</section>

<section class="section {a['theme']}" style="padding-top:0">
  <div class="wrap">
    <div class="prose">
      <p class="lede">Three poker variants dealt straight into the conversations you are
      already having. Open a table in a group chat and everyone plays at their own pace.</p>

      <p>Like its sibling, Poker for iMessage is a standalone iMessage app &mdash; nothing separate
      to launch, no account, no lobby. Hands run turn by turn, so a game can play out over an
      afternoon or over a week without anyone needing to be online at the same moment.</p>

      <h2>The games</h2>
    </div>
{features([
  ("Texas Hold&rsquo;Em",
   "Two hole cards each and five community cards shared across the flop, turn, and river, "
   "with a betting round at every street."),
  ("Omaha",
   "Four hole cards each, and you must use exactly two of them plus three community cards "
   "to make your best five-card hand."),
  ("7 Card Stud",
   "No community cards at all. A mix of face-up and face-down cards across several betting "
   "rounds, with a bring-in and antes in place of blinds."),
])}

    <div class="prose">
      <h2>No real money, ever</h2>
      <p>Poker for iMessage is a simulated card game. Chips have no monetary value: they cannot
      be bought, cashed out, transferred, or exchanged for anything of value, and there is no
      wagering of real money or real-world items anywhere in the app.</p>

      <h2>What it costs</h2>
      <p>Every game is free and there is no advertising. The only in-app purchase is a
      cosmetic card back, bought once through Apple&rsquo;s own purchase system &mdash; and a design
      bought here also unlocks in Card Games for iMessage.</p>

      <h2>Accessibility and languages</h2>
      <p>Fully localized in 18 languages, with complete VoiceOver and Voice Control support
      down to individual cards, Dynamic Type throughout, and reduced animation when Reduce
      Motion is enabled.</p>

      <h2>Details</h2>
{deftable([
  ("Platforms", "iPhone and iPad, iOS 17.0 or later"),
  ("Type", "Standalone iMessage app &mdash; no separate app to open"),
  ("Price", "Free, with optional cosmetic card backs"),
  ("Languages", "18"),
  ("Networking", "None &mdash; the app contains no networking code at all"),
  ("Status", "Finished and on its way to the App Store"),
])}

      <div class="callout">
        <p><strong>Not on the App Store yet.</strong> Poker for iMessage is complete and going
        through review. This page will get a download button the moment it is live &mdash; in the
        meantime, <a href="/support.html">get in touch</a> if you have questions.</p>
      </div>

      <h2>Privacy</h2>
      <p>No analytics, no advertising frameworks, no networking code. Read the
      <a href="{a['privacy']}">full privacy policy</a>.</p>
    </div>
  </div>
</section>
"""
    page(a["slug"], "Poker for iMessage — Owl Orchard", a["meta_desc"], body,
         theme=a["theme"], icon=a["icon"], jsonld=app_jsonld(a))


# ================================================================== about

def build_about():
    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="prose">
      <span class="eyebrow">About</span>
      <h1>An independent studio in Oregon.</h1>
      <p class="lede">Owl Orchard LLC builds native applications for iPhone, iPad, and Mac.
      Five of them so far, and every one is free.</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:clamp(36px,5vw,52px)">
  <div class="wrap">
    <div class="prose">
      <p>The catalogue has nothing obvious in common. One app is a chess variant from 1936.
      One is a live feed of congressional roll-call votes. One turns whatever your Mac is
      playing into Milkdrop visuals. Two of them live inside iMessage and never open a window
      of their own.</p>

      <p>What they share is how they are built. Every app is written in Swift against Apple&rsquo;s
      own frameworks &mdash; no web views in a native wrapper, no cross-platform runtime between
      the app and the hardware. Every app is free to download and free to use. Every app is
      localized well past English, and built to work with VoiceOver, Voice Control, Dynamic
      Type, and Reduce Motion rather than around them.</p>

      <h2>Small on purpose</h2>
      <p>Owl Orchard is independent, with no investors and no growth target. That is a real
      constraint: releases are slower than a funded studio&rsquo;s, and there is no overnight
      support rotation.</p>
      <p>It buys something back, though. There is nobody here making the case for an
      analytics SDK, nobody who needs a retention metric to move, and no reason for any of
      these apps to want anything from you beyond the time you choose to spend in them. The
      two iMessage apps ship with no networking code whatsoever. The other three are specific,
      in writing, about the few things that leave your device.</p>

      <h2>Where it is</h2>
      <p>The studio is registered and run in Oregon, United States. Support email is answered
      from here, usually within a day or two.</p>

      <h2>The details</h2>
{deftable([
  ("Studio", "Owl Orchard LLC &mdash; Oregon, United States"),
  ("Platforms", "iOS, iPadOS, macOS"),
  ("Built with", "Swift and SwiftUI, plus SpriteKit, MapKit, WidgetKit, StoreKit, Metal, "
                 "and a vendored C++ rendering engine where a project calls for it"),
  ("Apps", '<a href="/hex-chess.html">Hex Chess</a>, <a href="/politica.html">Politica</a>, '
           '<a href="/prism.html">Prism</a>, '
           '<a href="/card-games-for-imessage.html">Card Games for iMessage</a>, and '
           '<a href="/poker-for-imessage.html">Poker for iMessage</a>'),
  ("Price", "Every app is free. The only in-app purchase anywhere is a cosmetic card back."),
  ("Contact", f'<a href="mailto:{EMAIL}">{EMAIL}</a>'),
])}

      <div class="hero-actions" style="margin-top:34px">
        <a class="btn btn-primary" href="/#apps">See the apps</a>
        <a class="btn btn-ghost" href="/support.html">Get in touch</a>
      </div>
    </div>
  </div>
</section>
"""
    page("about.html", "About — Owl Orchard",
         "Owl Orchard LLC is an independent software studio in Oregon building native Swift "
         "apps for iPhone, iPad, and Mac.", body, current="/about.html")


# ================================================================== support

def build_support():
    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="prose">
      <span class="eyebrow">Support</span>
      <h1>A real person answers this email.</h1>
      <p class="lede">Write to <a href="mailto:{EMAIL}">{EMAIL}</a> about any of the five apps.
      Owl Orchard is a small studio, so give it a day or two &mdash; but every message is read, and
      answered by someone who worked on the app you are writing about.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="mailto:{EMAIL}">Email support</a>
      </div>
    </div>
  </div>
</section>

<section class="section" style="padding-top:clamp(36px,5vw,52px)">
  <div class="wrap">
    <div class="prose">
      <h2>Reporting a bug</h2>
      <p>It helps enormously to include which app you were using, your iOS or macOS version,
      and what you were doing right before it went wrong. A screenshot is worth several
      paragraphs. For the iMessage apps, say whether it was a one-on-one thread or a group
      chat &mdash; that distinction is behind a surprising number of bugs.</p>
      <p>Bad translations count as bugs. If something reads badly to a native speaker, that is
      genuinely useful to hear and it will get fixed.</p>

      <h2 id="hex-chess">Hex Chess</h2>

      <h3>How do I see my achievements?</h3>
      <p>Sign in from the profile menu. Achievements and your Elo rating are tied to your
      account rather than the device, so they follow you to a new phone.</p>

      <h3>Can I play against a friend?</h3>
      <p>Yes. Create an online game, send your friend the game code it gives you, and they
      join from their own copy. You can also pass one device back and forth, or play the CPU.</p>

      <h3>Do I have to make an account?</h3>
      <p>Only for online play, achievements, and the leaderboard. Single player and pass-and-play
      work with no account at all.</p>

      <h2 id="politica">Politica</h2>

      <h3>Do I have to share my location?</h3>
      <p>No. Type any ZIP code &mdash; it does not have to be your own &mdash; and Politica loads that
      district&rsquo;s representatives. If you do grant location access, the lookup happens entirely
      on your device and the location is never transmitted.</p>

      <h3>Why is some data missing for a representative?</h3>
      <p>Politica reads from public government sources, and those sources have gaps and
      outages of their own. Campaign finance and trading disclosures in particular depend on
      what has actually been filed. When a section is empty it is usually because the upstream
      record is empty.</p>

      <h3>Can I follow a specific bill?</h3>
      <p>Bookmark it from its detail screen. You will get a local notification when its status
      changes &mdash; sent by your own device, not by a server.</p>

      <h2 id="prism">Prism</h2>

      <h3>Do I have to allow audio capture?</h3>
      <p>Yes &mdash; Prism cannot visualize what it cannot hear. Nothing captured is recorded, stored,
      or transmitted; the audio goes straight into the FFT and is gone.</p>

      <h3>Can I use my own presets?</h3>
      <p>Yes. Press <code>L</code> to point Prism at a folder of <code>.milk</code> files, or drag a
      single preset onto the window. It remembers the folder and reopens where you left off.</p>

      <h3>Where are the plug-in and screen saver?</h3>
      <p>Both ship alongside the app. The plug-in appears in Music&rsquo;s own Visualizer menu; the
      screen saver appears in System Settings once installed.</p>

      <h2 id="card-games">Card Games and Poker for iMessage</h2>

      <h3>I bought a card back in one app. Why don&rsquo;t I see it in the other?</h3>
      <p>You should &mdash; card backs are shared between both apps. If a design has not appeared
      yet, try these in order:</p>
      <ul>
        <li>Open the other app and let it finish loading its card back list once. A purchase
        made on the same device usually appears immediately.</li>
        <li>Check that both devices are signed into the same iCloud account with iCloud Drive
        enabled. Syncing can take a minute or two after a purchase.</li>
        <li>Use <strong>Restore Purchases</strong> in the card back menu.</li>
      </ul>
      <p>If it still has not shown up, email the name of the card back and which app you bought
      it in, and it will get sorted out.</p>

      <h3>I have a new iPhone. Do I have to buy my card backs again?</h3>
      <p>No. Sign in with the same Apple Account and use <strong>Restore Purchases</strong>.
      Purchases are tied to the account, not the device.</p>

      <h3>Does my friend need the app installed?</h3>
      <p>Both players do, to take turns. If someone in the thread does not have it, the
      message they receive includes a link to install it.</p>

      <h3>Is there real money in Poker for iMessage?</h3>
      <p>No. Chips have no monetary value and cannot be bought, cashed out, transferred, or
      exchanged for anything. It is a simulated card game with no wagering of any kind.</p>

      <h3>Does it work in a group chat?</h3>
      <p>Yes. Both apps support group games as well as one-on-one threads.</p>

      <h2 id="refunds">Refunds</h2>
      <p>In-app purchases are handled entirely by Apple, so refunds go through Apple rather
      than through Owl Orchard. Visit
      <a href="https://reportaproblem.apple.com" rel="noopener">reportaproblem.apple.com</a>,
      sign in with your Apple Account, and select the purchase.</p>

      <h2>Contact</h2>
      <p>
        Owl Orchard LLC<br>
        Oregon, United States<br>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
      </p>
    </div>
  </div>
</section>
"""
    page("support.html", "Support — Owl Orchard",
         "Support and frequently asked questions for Hex Chess, Politica, Prism, Card Games "
         "for iMessage, and Poker for iMessage.", body, current="/support.html")


# ================================================================== privacy

UPDATED = "August 31, 2026"

RIGHTS = f"""
      <h2>Your rights</h2>
      <p>Privacy laws including the GDPR and the CCPA give you the right to access, correct,
      delete, and port the personal information a company holds about you, and to opt out of
      its sale. There is nothing here to disclose, correct, delete, or port. Personal
      information has never been sold or shared, and it never will be.</p>

      <h2>Changes to this policy</h2>
      <p>If this policy changes, the updated version is posted on this page with a new date.
      Material changes are noted in the app&rsquo;s release notes.</p>

      <h2>Contact</h2>
      <p>
        Owl Orchard LLC<br>
        Oregon, United States<br>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
      </p>"""


def privacy_page(app, lede, inner, title=None):
    body = f"""
<section class="hero {app['theme']}" style="padding-bottom:clamp(28px,4vw,40px)">
  <div class="wrap">
    <div class="prose">
      <span class="eyebrow">Privacy policy</span>
      <h1>{app['name']}</h1>
      <p class="lede">{lede}</p>
      <p class="small">Last updated {UPDATED} &middot;
      <a href="/{app['slug']}">Back to {app['short']}</a> &middot;
      <a href="/privacy.html">All policies</a></p>
    </div>
  </div>
</section>

<section class="section {app['theme']}" style="padding-top:clamp(34px,5vw,50px)">
  <div class="wrap">
    <div class="prose">
{inner}
{RIGHTS}
    </div>
  </div>
</section>
"""
    page(app["privacy"].lstrip("/"),
         title or f"Privacy Policy — {app['short']} — Owl Orchard",
         f"Privacy policy for {app['short']}.", body,
         theme=app["theme"], icon=app["icon"])


def imessage_privacy(app):
    other = "Card Games for iMessage" if app["key"] == "poker" else "Poker for iMessage"
    gambling = ""
    if app["key"] == "poker":
        gambling = """
      <h2>No real-money gambling</h2>
      <p>Poker for iMessage is a simulated card game. Chips have no monetary value, cannot be
      purchased, and cannot be cashed out, transferred, or exchanged for anything of value.
      The app involves no wagering of real money or real-world items, and it therefore collects
      none of the identity or financial information that real-money gaming would require.</p>
"""
    children = ("""
      <h2>Children</h2>
      <p>Poker for iMessage is not directed to children, and because it depicts simulated
      gambling it carries a mature age rating on the App Store. No information is knowingly
      collected from children &mdash; and in fact none is collected from anyone.</p>
""" if app["key"] == "poker" else f"""
      <h2>Children</h2>
      <p>{app['name']} does not knowingly collect information from children, and in fact
      collects none from anyone. There is no advertising, no user-generated content beyond the
      card moves players exchange in their own conversations, and no external links other than
      to Apple&rsquo;s own purchase and support pages.</p>
""")
    inner = f"""      <p>{app['name']} is published by Owl Orchard LLC, an Oregon limited liability company.
      This policy explains what the app does and does not do with information. The short
      version: it collects nothing, and there is no Owl Orchard server for anything to be
      collected to.</p>

      <h2>Information collected</h2>
      <p><strong>None.</strong> {app['name']} contains no analytics frameworks, no advertising
      frameworks, no crash-reporting services, no third-party software development kits, and no
      networking code of any kind. It does not transmit information to Owl Orchard LLC or to any
      third party, because it has no capability to do so.</p>
      <p>Your name, email address, phone number, contacts, location, device identifiers,
      advertising identifiers, and usage analytics are not collected. You are not tracked across
      apps or websites, and the app never asks for permission to do so because it never
      attempts it.</p>

      <h2>Information stored on your device</h2>
      <p>A small amount of data is stored locally so the app can remember your settings and
      what you own:</p>
      <ul>
        <li><strong>Game state and preferences</strong> &mdash; the games in progress in your
        conversations, and settings such as your selected card back.</li>
        <li><strong>Card back ownership</strong> &mdash; a list of product identifiers for the card
        backs you have purchased, for example <code>Theme.Koi</code>. This lives in a shared app
        group container so that {app['name']} and {other} both recognize a purchase made in
        either one.</li>
      </ul>
      <p>This data stays on your device. It is not transmitted anywhere and cannot be read by
      Owl Orchard.</p>

      <h2>iCloud</h2>
      <p>So that a card back bought on one device is available on your others, the same list of
      purchased card back identifiers is written to Apple&rsquo;s iCloud key-value storage. It contains
      product identifiers only &mdash; no personal information, no game content, no message content.</p>
      <p>That data lives in your own iCloud account, governed by
      <a href="https://www.apple.com/legal/privacy/" rel="noopener">Apple&rsquo;s privacy policy</a>.
      Owl Orchard LLC has no access to it. You can turn it off by disabling iCloud Drive for the
      app in your device settings; card backs then stay available on the device where you bought
      them, and Restore Purchases brings them back elsewhere.</p>

      <h2>Your conversations</h2>
      <p>{app['name']} is an iMessage app. Game moves travel as messages inside your own Messages
      conversation, handled entirely by Apple&rsquo;s Messages framework and subject to Apple&rsquo;s
      encryption and privacy practices. They go to the people in your conversation. They never
      pass through any Owl Orchard system, and there is no ability to read, store, or recover
      them.</p>
      <p>The app does not access your contacts or your message history. It can see only the
      conversation it was opened in, and only the game data within it.</p>

      <h2>Purchases</h2>
      <p>Card backs are optional one-time in-app purchases processed entirely by Apple through
      StoreKit. Your payment method, billing address, and Apple Account details are never seen or
      handled by Owl Orchard. Apple provides only aggregate, anonymized sales reporting &mdash; unit
      counts and totals by territory &mdash; which cannot identify any individual purchaser.</p>
      <p>Refunds are handled by Apple at
      <a href="https://reportaproblem.apple.com" rel="noopener">reportaproblem.apple.com</a>.</p>
{gambling}{children}
      <h2>Removing your data</h2>
      <p>To remove everything the app has stored on your device, delete the app.</p>"""
    privacy_page(app,
        "This app collects nothing. It contains no analytics, no advertising, and no "
        "networking code of any kind.", inner)


def build_privacy_hexchess():
    a = BY["hexchess"]
    inner = """      <p>Hex Chess is published by Owl Orchard. This policy explains what the app does and does
      not do with information.</p>
      <p>Playing offline &mdash; single player against the CPU, or passing one device back and forth
      &mdash; involves no account and collects nothing. Everything below applies only if you choose
      to sign in for online play.</p>

      <h2>Information collected when you sign in</h2>
      <p>Signing in is optional, and exists so that online multiplayer, achievements, and the
      leaderboard can work. Depending on how you sign in:</p>
      <ul>
        <li><strong>Sign in with Apple or Game Center</strong> &mdash; a first name, and your Game
        Center icon if you have one.</li>
        <li><strong>Sign in with Google</strong> &mdash; a display name, a profile image, and an email
        address used internally only.</li>
        <li><strong>Email and password</strong> &mdash; the email address you register with, used for
        authentication and account recovery.</li>
      </ul>
      <p>Only your display name and profile picture are ever shown to another player, and only
      during an online game you have chosen to join. Your email address is never shown to anyone
      and is used solely for authentication and support.</p>

      <h2>How that information is used</h2>
      <ul>
        <li>To enable online multiplayer between you and an opponent you have shared a game
        code with.</li>
        <li>To display a name and avatar during that game.</li>
        <li>To store your game progress, achievements, and Elo rating against your account.</li>
      </ul>
      <p>It is not used for advertising, it is not profiled, and it is never sold, rented, or
      shared with any third party.</p>

      <h2>Where it is stored</h2>
      <p>Account and match data is stored using Google&rsquo;s Firebase infrastructure, encrypted in
      transit and at rest, with access restricted to the studio. Achievements are also
      reported to Apple&rsquo;s Game Center, governed by
      <a href="https://www.apple.com/legal/privacy/" rel="noopener">Apple&rsquo;s privacy policy</a>.
      A local copy of your profile is cached on your device so the app still works without a
      connection.</p>

      <h2>What is never collected</h2>
      <p>Hex Chess contains no advertising frameworks and no third-party analytics or attribution
      SDKs. It does not collect your location, your contacts, or advertising identifiers, and it
      does not track you across other apps or websites.</p>

      <h2>Your choices</h2>
      <ul>
        <li>Play without signing in at all &mdash; single player and pass-and-play need no account.</li>
        <li>Change your display name at any time from the profile menu.</li>
        <li>Ask for your account and its sign-in data to be deleted by emailing the address
        below.</li>
      </ul>"""
    privacy_page(a,
        "Play offline and nothing is collected. Sign in for online play and a display name, "
        "avatar, and rating are stored so opponents can see who they are playing.", inner)


def build_privacy_politica():
    a = BY["politica"]
    inner = """      <p>Politica is published by Owl Orchard. This policy explains what the app does and does
      not do with information.</p>

      <h2>Information collected</h2>
      <p><strong>None.</strong> Politica has no account system, no analytics framework, no
      advertising framework, and no third-party tracking SDKs. Nothing about you or your use of
      the app is transmitted to Owl Orchard, because there is no Owl Orchard server involved at
      any point.</p>

      <h2>Your location</h2>
      <p>Politica can use your location to work out which congressional district you are in.
      That resolution happens entirely on your own device. Your coordinates are not transmitted,
      stored off-device, logged, or shared with anyone.</p>
      <p>Granting location access is optional. Typing a ZIP code &mdash; any ZIP code, not necessarily
      your own &mdash; gives you the same result without the app ever requesting location permission.</p>

      <h2>Public data the app requests</h2>
      <p>To show you bills, votes, representatives, funders, and district demographics, the app
      requests public records directly from government and open-data services: Congress.gov,
      senate.gov, LegiScan, OpenFEC, the House Clerk&rsquo;s disclosure index, the Senate&rsquo;s electronic
      financial disclosure portal, and the U.S. Census Bureau.</p>
      <p>These requests carry only what is needed to fetch the record &mdash; for example a bill
      number or a district identifier. No account, device identifier, advertising identifier, or
      personal information is attached to them, and no request tells any of these services who
      you are. Each service operates under its own privacy practices, which govern the ordinary
      server logs any web service keeps.</p>

      <h2>Information stored on your device</h2>
      <p>Bills, bill details and roll calls, your representative delegation, and map boundaries
      and demographics are cached locally so the app still works offline. Your bookmarked bills
      and any ZIP code you entered are also stored on device. All of it stays there, and deleting
      the app removes it.</p>

      <h2>Notifications</h2>
      <p>When a bookmarked bill changes status, the notification you receive is scheduled by your
      own device. There is no push server, and no notification is sent from outside your phone.</p>

      <h2>Children</h2>
      <p>Politica is a reference app about public legislative records and collects no information
      from anyone, children included.</p>"""
    privacy_page(a,
        "Politica collects nothing. Your location is turned into a district on your own device "
        "and never leaves it &mdash; and a ZIP code works without location access at all.", inner)


def build_privacy_prism():
    a = BY["prism"]
    inner = """      <p>Prism is published by Owl Orchard. This policy explains what the app does and does not
      do with information.</p>

      <h2>Information collected</h2>
      <p><strong>None.</strong> Prism has no account system, no analytics framework, no advertising
      framework, and no third-party tracking SDKs. No listening history is collected, and nothing
      about you or your use of the app is transmitted to Owl Orchard.</p>

      <h2>The audio Prism captures</h2>
      <p>Prism captures your Mac&rsquo;s system audio in order to visualize it. That audio is analysed
      in memory, frame by frame, and discarded. It is never recorded to disk, never uploaded, and
      never retained after the frame it drew.</p>

      <h2>Now-playing metadata</h2>
      <p>If you grant the optional Apple Events permission, Prism reads the title and artist of
      the track currently playing in Spotify or Music, so it can show album art and match a preset
      to the song. This is read locally from the app that is already playing it.</p>

      <h2>The one network request</h2>
      <p>To power smart preset matching, the current track&rsquo;s title and artist are sent to the free
      public ReccoBeats API, which returns the song&rsquo;s tempo, energy, and mood. No account, device
      identifier, advertising identifier, or personal information is transmitted with that request,
      and the service is not told who is asking. Results are cached on your Mac so a replayed track
      makes no further request. If the service is unreachable, Prism simply falls back to picking
      presets in sequence.</p>
      <p>Aside from this lookup, Prism makes no network requests of its own.</p>

      <h2>Information stored on your Mac</h2>
      <p>Prism stores your preferences, your preset library location, per-preset ratings, session
      history, and the cached track lookups described above &mdash; all locally, in standard app
      storage. Deleting the app removes it.</p>

      <h2>Children</h2>
      <p>Prism is a music visualizer and collects no information from anyone, children
      included.</p>"""
    privacy_page(a,
        "Prism records nothing it hears and keeps no listening history. One request leaves your "
        "Mac &mdash; a song title and artist, with nothing attached that identifies you.", inner)


def build_privacy_index():
    rows = "".join(f"""
      <a class="card {a['theme']} reveal" href="{a['privacy']}">
        <div class="card-top">
          <img class="icon" src="{a['icon']}" alt="" width="64" height="64" loading="lazy">
          <div>
            <h3>{a['short']}</h3>
            <p class="card-sub">{a['sub']}</p>
          </div>
        </div>
        <p class="desc">{s}</p>
        <div class="card-foot">
          <span class="pill">Updated {UPDATED}</span>
          <span class="more" aria-hidden="true">Read &rarr;</span>
        </div>
      </a>""" for a, s in [
        (BY["hexchess"], "Nothing collected offline. Sign in for online play and a display "
                         "name, avatar, and rating are stored."),
        (BY["politica"], "Nothing collected. Location is resolved on device and never "
                         "transmitted."),
        (BY["prism"],    "Nothing collected, nothing recorded. One anonymous song lookup for "
                         "preset matching."),
        (BY["cardgames"],"Nothing collected. The app contains no networking code at all."),
        (BY["poker"],    "Nothing collected. The app contains no networking code at all."),
    ])
    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="prose">
      <span class="eyebrow">Legal</span>
      <h1>Privacy policies</h1>
      <p class="lede">One policy per app, because the apps genuinely differ. Two of them
      contain no networking code whatsoever; the others are specific about the few things that
      do leave your device.</p>
      <p>What is true across all five: no advertising frameworks, no third-party analytics, no
      tracking across apps or websites, and nothing sold or shared with anyone.</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:clamp(36px,5vw,52px)">
  <div class="wrap">
    <div class="appgrid">{rows}
    </div>
  </div>
</section>
"""
    page("privacy.html", "Privacy policies — Owl Orchard",
         "Privacy policies for Hex Chess, Politica, Prism, Card Games for iMessage, and Poker "
         "for iMessage. No advertising, no analytics, nothing sold or shared.",
         body)


def build_404():
    body = f"""
<section class="hero">
  <div class="wrap">
    <div class="prose">
      <span class="eyebrow">404</span>
      <h1>That page isn&rsquo;t here.</h1>
      <p class="lede">The link may be out of date, or something may have moved.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="/">Go to the home page</a>
        <a class="btn btn-ghost" href="/support.html">Support</a>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="prose">
      <h2>Or head straight to an app</h2>
      <ul>
        {"".join(f'<li><a href="/{a["slug"]}">{a["name"]}</a></li>' for a in APPS)}
      </ul>
      <p>If you followed a link from inside one of the apps and landed here, please say so at
      <a href="mailto:{EMAIL}">{EMAIL}</a> &mdash; that is a bug worth fixing.</p>
    </div>
  </div>
</section>
"""
    page("404.html", "Page not found — Owl Orchard",
         "That page could not be found.", body)


# ================================================================== extras

# Standalone favicon: same mark as the inline OWL above, on the brand tile.
# Colours are literal here — CSS custom properties do not resolve in a favicon context.
OWL_FILE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192">
  <rect width="192" height="192" rx="43" fill="#2f5d3f"/>
  <g transform="translate(26.88 49.2) scale(0.0864)">
    <g fill="#fbfaf7">
      <rect width="425" height="100"/>
      <rect x="1175" width="425" height="100"/>
      <path d="M800 800.33 941.42 941.75 800 1083.17 658.58 941.75Z"/>
    </g>
    <g fill="none" stroke="#fbfaf7" stroke-width="100">
      <circle cx="425" cy="425" r="375"/>
      <circle cx="1175" cy="425" r="375"/>
    </g>
  </g>
</svg>
"""

ROBOTS = f"""User-agent: *
Allow: /

Sitemap: {SITE}/sitemap.xml
"""


def build_extras():
    (OUT / "assets" / "owl.svg").write_text(OWL_FILE, encoding="utf-8")
    (OUT / "robots.txt").write_text(ROBOTS, encoding="utf-8")

    urls = ["/", "/about.html", "/support.html", "/privacy.html"]
    urls += ["/" + a["slug"] for a in APPS]
    urls += [a["privacy"] for a in APPS]
    entries = "".join(
        f"\n  <url><loc>{SITE}{u}</loc><lastmod>2026-08-31</lastmod>"
        f"<priority>{'1.0' if u == '/' else '0.8' if not u.startswith('/privacy') else '0.4'}</priority></url>"
        for u in urls
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + entries + "\n</urlset>\n", encoding="utf-8")
    print(f"  owl.svg, robots.txt, sitemap.xml ({len(urls)} urls)")


# ================================================================== main

if __name__ == "__main__":
    print("Building owlorchard.com ->", OUT)
    build_home()
    build_hexchess()
    build_politica()
    build_prism()
    build_cardgames()
    build_poker()
    build_about()
    build_support()
    build_privacy_index()
    build_privacy_hexchess()
    build_privacy_politica()
    build_privacy_prism()
    imessage_privacy(BY["cardgames"])
    imessage_privacy(BY["poker"])
    build_404()
    build_extras()
    print("done.")
