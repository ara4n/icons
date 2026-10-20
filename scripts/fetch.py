import re, sys, os, json, urllib.parse, requests
sys.path.insert(0, os.path.dirname(__file__))
from manifest import PROJECTS
from bs4 import BeautifulSoup

OUT = "/Users/matthew/workspace/logos/raw"
H = {"User-Agent": "Mozilla/5.0 (logo-collector; contact matthew@element.io)"}
S = requests.Session(); S.headers.update(H)
LOGO_RE = re.compile(r"(logo|icon|brand|mark)", re.I)

def get(url, **kw):
    try:
        r = S.get(url, timeout=20, allow_redirects=True, **kw)
        return r if r.ok else None
    except Exception:
        return None

def slug(n): return re.sub(r"[^a-z0-9]+", "-", n.lower()).strip("-")

def save(name, url):
    r = get(url)
    if not r or len(r.content) < 200: return None
    ct = r.headers.get("content-type", "")
    ext = "svg" if ("svg" in ct or url.endswith(".svg")) else "png" if "png" in ct else "jpg" if "jp" in ct else "ico" if "icon" in ct else "webp" if "webp" in ct else None
    if not ext: return None
    p = f"{OUT}/{slug(name)}.{ext}"
    open(p, "wb").write(r.content)
    return p

def website_icons(url):
    r = get(url)
    if not r: return []
    soup = BeautifulSoup(r.text, "lxml")
    cands = []
    for l in soup.find_all("link", href=True):
        rel = " ".join(l.get("rel", [])).lower()
        if "icon" in rel:
            sz = l.get("sizes", "0x0"); n = int(re.findall(r"\d+", sz)[0]) if re.findall(r"\d+", sz) else 0
            href = l["href"]
            score = (1000 if href.endswith(".svg") else n) + (50 if "apple" in rel else 0)
            cands.append((score, urllib.parse.urljoin(r.url, href)))
    for m in soup.find_all("meta"):
        if m.get("property") in ("og:image", "og:logo") and m.get("content"):
            cands.append((10, urllib.parse.urljoin(r.url, m["content"])))
    for img in soup.find_all("img", src=True):
        if LOGO_RE.search(img["src"]) or LOGO_RE.search(img.get("alt", "") or ""):
            cands.append((500 if img["src"].endswith(".svg") else 100, urllib.parse.urljoin(r.url, img["src"])))
    cands.sort(reverse=True)
    return [u for _, u in cands]

def github(url):
    m = re.match(r"https://github\.com/([^/]+)/([^/#?]+)", url)
    if not m: return []
    owner, repo = m.groups()
    r = get(f"https://github.com/{owner}/{repo}")
    if not r: return []
    soup = BeautifulSoup(r.text, "lxml")
    cands = []
    art = soup.find("article") or soup
    for img in art.find_all("img", src=True):
        src = img["src"]; alt = img.get("alt", "") or ""
        if "badge" in src or "shields" in src or "img.shields" in src: continue
        if LOGO_RE.search(src) or LOGO_RE.search(alt) or repo.lower() in src.lower():
            u = urllib.parse.urljoin(r.url, src)
            # camo/raw -> raw
            cands.append(u)
    # also try repo tree for well-known logo paths via file-finder (no API): guess raw paths
    for b in ("main", "master", "develop"):
        for p in ("logo.svg","logo.png","assets/logo.svg","assets/logo.png","docs/logo.svg","docs/logo.png","res/logo.svg","icon.svg","icon.png","assets/icon.png","img/logo.svg","images/logo.svg","images/logo.png", "docs/assets/logo.svg", ".github/logo.svg", ".github/logo.png", "art/logo.svg"):
            cands.append(f"https://raw.githubusercontent.com/{owner}/{repo}/{b}/{p}")
    return cands

def gitlab(url):
    m = re.match(r"https://(gitlab\.com|gitlab\.gnome\.org|invent\.kde\.org|gitlab\.matrix\.org)/(.+?)/?$", url)
    if not m: return []
    host, path = m.groups()
    r = get(f"https://{host}/api/v4/projects/{urllib.parse.quote(path.strip('/'), safe='')}")
    if r:
        try:
            av = r.json().get("avatar_url")
            if av: return [av]
        except Exception: pass
    return []

def codeberg(url):
    m = re.match(r"https://codeberg\.org/([^/]+)/([^/]+)", url)
    if not m: return []
    o, rp = m.groups()
    r = get(f"https://codeberg.org/api/v1/repos/{o}/{rp}")
    if r:
        try:
            av = r.json().get("avatar_url")
            if av: return [av]
        except Exception: pass
    return []

def candidates(url):
    c = github(url) + gitlab(url) + codeberg(url)
    if not c or not re.match(r"https://(github|gitlab|codeberg|invent)", url):
        c += website_icons(url)
    return c

res = {}
only = sys.argv[1:]
for name, url in PROJECTS.items():
    if only and name not in only: continue
    if not only and any(f.startswith(slug(name) + ".") for f in os.listdir(OUT)):
        continue
    got = None
    for u in candidates(url):
        got = save(name, u)
        if got: break
    res[name] = got
    print(f"{'OK ' if got else '-- '} {name}: {got or url}", flush=True)
print(sum(1 for v in res.values() if v), "/", len(res))
