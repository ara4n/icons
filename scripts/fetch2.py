import re, sys, os, subprocess, tempfile, requests, shutil
sys.path.insert(0, os.path.dirname(__file__))
from manifest import PROJECTS
OUT="/Users/matthew/workspace/logos/raw"
S=requests.Session(); S.headers["User-Agent"]="Mozilla/5.0 logo-collector"
def slug(n): return re.sub(r"[^a-z0-9]+","-",n.lower()).strip("-")
BAD=re.compile(r"(node_modules|/test|fixtures|emoji|flag|badge|screenshot|banner|sticker|/fonts?/|thirdparty|third_party|vendor|wordmark|google|apple|github|gitlab|twitter|mastodon|discord|matrix-org|element-hq|/web/icons/Icon-maskable|notification|status|avatar|placeholder|background|splash|feature_graphic|\bpreview|slide|docs/images/|/i18n/|_dark|-dark|monochrome|foreground|/res/img/[a-z-]+\.svg$|/res/css|/ic_[a-z_]+(?<!launcher)\.(png|svg|xml)$)", re.I)
def score(p):
    pl=p.lower(); b=os.path.basename(pl); s=0
    if not re.search(r"\.(svg|png|webp)$",pl): return -1
    if BAD.search("/"+pl): return -1
    if "logo" in b: s+=50
    if re.search(r"ic_launcher(_round)?\.(png|webp)",b) and "xxxhdpi" in pl: s+=45
    if re.search(r"ic_launcher-playstore|playstore",b): s+=48
    if re.search(r"appicon|app_icon|app-icon|/icons?/",pl): s+=30
    if re.search(r"1024|512|256",b): s+=10
    if b.endswith(".svg"): s+=20
    if re.search(r"(^|[^0-9])(16|24|32|48)x?(16|24|32|48)?\.",b): s-=30
    if "icon" in b: s+=15
    if pl.count("/")>4: s-=5
    if b.startswith("favicon"): s+=5
    return s
def raw_url(url, branch, path):
    if m:=re.match(r"https://github\.com/([^/]+)/([^/]+)",url): return f"https://raw.githubusercontent.com/{m[1]}/{m[2]}/{branch}/{path}"
    if m:=re.match(r"https://codeberg\.org/([^/]+)/([^/]+)",url): return f"https://codeberg.org/{m[1]}/{m[2]}/raw/branch/{branch}/{path}"
    if m:=re.match(r"https://(gitlab\.com|gitlab\.gnome\.org|invent\.kde\.org|gitlab\.matrix\.org|lily-is\.land)/(.+?)/?$",url): return f"https://{m[1]}/{m[2]}/-/raw/{branch}/{path}"
only=sys.argv[1:]
for name,url in PROJECTS.items():
    if only and name not in only: continue
    if not re.match(r"https://(github\.com|codeberg\.org|gitlab\.com|gitlab\.gnome\.org|invent\.kde\.org|gitlab\.matrix\.org|lily-is\.land)/[^/]+/[^/]+",url): continue
    d=tempfile.mkdtemp()
    try:
        subprocess.run(["git","clone","-q","--depth","1","--filter=blob:none","--no-checkout",url.rstrip("/"),d],check=True,capture_output=True,timeout=120)
        branch=subprocess.run(["git","-C",d,"rev-parse","--abbrev-ref","HEAD"],capture_output=True,text=True).stdout.strip()
        files=subprocess.run(["git","-C",d,"ls-tree","-r","--name-only","HEAD"],capture_output=True,text=True).stdout.split("\n")
    except Exception as e:
        print("!! ",name,"clone failed",str(e)[:80]); shutil.rmtree(d,ignore_errors=True); continue
    shutil.rmtree(d,ignore_errors=True)
    c=sorted(((score(p),p) for p in files if score(p)>0),reverse=True)[:5]
    got=None
    for s,p in c:
        r=S.get(raw_url(url,branch,p),timeout=30)
        if r.ok and len(r.content)>300:
            ext=p.rsplit(".",1)[1]; open(f"{OUT}/{slug(name)}.{ext}","wb").write(r.content); got=p; break
    print(("OK  " if got else "--  ")+name+": "+(got or "no candidates")+("   | alt: "+", ".join(p for _,p in c[1:3]) if len(c)>1 else ""),flush=True)
