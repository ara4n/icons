import re, sys, os, io, subprocess, requests, urllib.parse
from bs4 import BeautifulSoup
from PIL import Image
OUT="/Users/matthew/workspace/logos/raw"
S=requests.Session(); S.headers["User-Agent"]="Mozilla/5.0 (Macintosh) logo-collector"
def slug(n): return re.sub(r"[^a-z0-9]+","-",n.lower()).strip("-")
R=lambda u,p:("repo",u,p); W=lambda u:("site",u); M=lambda u:("readme",u)
SRC={
 "Element X": R("https://github.com/element-hq/element-x-android","appicon/element/src/main/ic_launcher-playstore.png"),
 "Element": R("https://github.com/element-hq/element-web","apps/web/res/themes/element/img/logos/element-app-logo.png"),
 "Element Call": R("https://github.com/element-hq/element-call","src/icons/LogoMark.svg"),
 "Fractal": R("https://gitlab.gnome.org/World/fractal","data/icons/org.gnome.Fractal.svg"),
 "FluffyChat": R("https://github.com/krille-chan/fluffychat","assets/logo/vector/logo.svg"),
 "Nheko": R("https://github.com/Nheko-Reborn/nheko","resources/nheko.svg"),
 "NeoChat": R("https://invent.kde.org/network/neochat","logo.png"),
 "Cinny": R("https://github.com/cinnyapp/cinny","public/res/svg/cinny.svg"),
 "SchildiChat": R("https://github.com/SchildiChat/schildichat-desktop","graphics/store_icon.svg"),
 "Quaternion": R("https://github.com/quotient-im/Quaternion","icons/quaternion/sources/sc-apps-quaternion.svg"),
 "Commet": R("https://github.com/commetchat/commet","commet/assets/images/app_icon/icon.svg"),
 "Acter": R("https://github.com/acterglobal/a3","app/assets/icon/acter-logo.svg"),
 "Circles": R("https://github.com/circles-project/circles-ios","Circles/Assets.xcassets/AppIcon.appiconset/Circles-app-icon-1024.png"),
 "Tesseract": R("https://github.com/surakin/tesseract","ui/icons/tesseract.svg"),
 "Ement.el": R("https://github.com/alphapapa/ement.el","images/logo.svg"),
 "iamb": R("https://github.com/ulyssa/iamb","docs/iamb.svg"),
 "gomuks": R("https://github.com/gomuks/gomuks","desktop/icon.png"),
 "Harmony": R("https://codeberg.org/catcraft/harmony","assets/harmony-logo.svg"),
 "Trixnity Messenger": R("https://gitlab.com/connect2x/trixnity-messenger/trixnity-messenger","trixnity-messenger-compose-app/src/jvmMain/resources/logo.png"),
 "Koushi": R("https://github.com/shinaoka/koushi-matrix","apps/desktop/src/assets/koushi-logo.svg"),
 "Relay": R("https://github.com/subpop/Relay","docs/logo-256@2x.png"),
 "SchildiChat Revenge": R("https://github.com/SchildiChat/schildi-revenge","graphics/ic_launcher.svg"),
 "Synapse": R("https://github.com/element-hq/synapse","docs/favicon.svg"),
 "conduwuit": R("https://github.com/girlbossceo/conduwuit","docs/assets/conduwuit_logo.svg"),
 "TARDIS": R("https://github.com/matrix-org/tardis","public/favicon.svg"),
 "matrix-rust-sdk": R("https://github.com/matrix-org/matrix-rust-sdk","contrib/logo.svg"),
 "Trixnity": R("https://gitlab.com/trixnity/trixnity","website/static/img/logo.png"),
 "libQuotient": R("https://github.com/quotient-im/libQuotient","logo.png"),
 "Elm SDK": R("https://github.com/noordstar/elm-matrix-sdk-beta","docs/logo.svg"),
 "Chatty": R("https://gitlab.gnome.org/World/Chatty","data/icons/hicolor/scalable/apps/sm.puri.Chatty.svg"),
 "maubot": R("https://github.com/maubot/maubot","maubot/management/frontend/public/favicon.png"),
 "matrix-hookshot": R("https://github.com/matrix-org/matrix-hookshot","logo.svg"),
 "Synapse Admin": R("https://github.com/etkecc/synapse-admin","public/images/logo.webp"),
 "NeoDateFix": R("https://github.com/nordeck/matrix-meetings","matrix-meetings-widget/public/logo_light.svg"),
 "NeoChoice": R("https://github.com/nordeck/matrix-poll","public/logo.svg"),
 "Matrix Wrench": R("https://gitlab.com/jaller94/matrix-wrench","static/icon.svg"),
 "baibot": R("https://github.com/etkecc/baibot","etc/assets/baibot.svg"),
 "mautrix-manager": R("https://github.com/mautrix/manager","icon.png"),
 "AlexGames": R("https://github.com/alexbarry/AlexGames","img/logo.png"),
 "vodozemac": M("https://github.com/matrix-org/vodozemac"),
 "Draupnir": W("https://the-draupnir-project.github.io/draupnir-documentation/"),
 "Tuwunel": M("https://github.com/matrix-construct/tuwunel"),
 "Ruma": W("https://ruma.dev"),
 "Dendrite": M("https://github.com/matrix-org/dendrite"),
 "Matrix Authentication Service": M("https://github.com/element-hq/matrix-authentication-service"),
 "matrix-nio": M("https://github.com/matrix-nio/matrix-nio"),
 "Matrix Dart SDK": M("https://github.com/famedly/matrix-dart-sdk"),
 "synadm": M("https://github.com/JOJ0/synadm"),
 "Meowlnir": M("https://github.com/maunium/meowlnir"),
 "matrix-docker-ansible-deploy": M("https://github.com/spantaleev/matrix-docker-ansible-deploy"),
 "policyserv": M("https://github.com/matrix-org/policyserv"),
 "NioBot": M("https://github.com/nexy7574/nio-bot"),
 "matrix-bot-sdk": M("https://github.com/turt2live/matrix-bot-sdk"),
 "matrix-media-repo": M("https://github.com/t2bot/matrix-media-repo"),
 "Complement": M("https://github.com/matrix-org/complement"),
 "Spam Police": M("https://github.com/jjj333-p/spam-police"),
 "Matrix Reminder Bot": M("https://github.com/anoadragon453/matrix-reminder-bot"),
 "Pok'em": M("https://github.com/arcuru/pokem"),
 "Chaz": M("https://github.com/arcuru/chaz"),
 "Halcyon": M("https://github.com/WesR/Halcyon"),
 "Element Admin": M("https://github.com/element-hq/element-admin"),
 "Element Server Suite": W("https://element.io/server-suite"),
 "Matrix Widget Toolkit": M("https://github.com/nordeck/matrix-widget-toolkit"),
 "NeoBoard": W("https://neoboard.io"),
 "Matrix Connectivity Tester": W("https://connectivity-tester.mtrnord.blog"),
 "MatrixRooms.info": W("https://matrixrooms.info/"),
 "etke.cc": W("https://etke.cc"),
 "mautrix": W("https://mau.fi"),
 "Matrix.org": W("https://matrix.org"),
 "Extera": W("https://extera.xyz"),
 "Tammy": W("https://tammy.connect2x.de"),
 "kazv": W("https://kazv.chat/"),
 "Nexus": W("https://nexus.federated.nexus"),
 "Moment": W("https://mx-moment.xyz"),
 "Matrixbird": W("https://matrixbird.com"),
 "Venator": W("https://timedout.codeberg.page/venator"),
 "Rabble": W("https://rabble.talk"),
 "Sable": W("https://app.sable.moe"),
 "Vommet": W("https://vommet.app"),
 "Venoom": W("https://venoom.net"),
 "theGrid": W("https://thegrid.vicr123.com/"),
 "Beeper": W("https://www.beeper.com"),
 "polycule": W("https://polycule.im"),
 "Pangea Chat": W("https://www.pangea.chat"),
 "Zendrite": W("https://zendrite.pat-s.me"),
 "eM Client": W("https://www.emclient.com"),
 "Rocket.Chat": W("https://rocket.chat"),
 "Conduit": W("https://conduit.rs"),
 "continuwuity": W("https://continuwuity.org/"),
 "Telodendria": W("https://telodendria.io"),
 "Fractal Networks": W("https://fractalnetworks.co"),
 "RemoteRails": W("https://remoterails.com"),
 "Nordeck": R("https://github.com/nordeck/matrix-neoboard","packages/react-sdk/src/components/ImageUpload/test_files/nordeck.svg"),
 "Famedly": W("https://famedly.com"),
 "Connect2x": W("https://connect2x.com"),
 "Tchap": W("https://tchap.gouv.fr"),
 "BundesMessenger": W("https://messenger.bwi.de"),
 "openDesk": W("https://opendesk.eu"),
 "Asgard.chat": W("https://asgard.chat"),
 "Alertrix": W("https://alertrix.net"),
 "Solidar": W("https://solidar.app"),
 "PubHubs": W("https://pubhubs.net"),
 "Polyjuice": W("https://polyjuice.gitlab.io/"),
 "Telodendria": W("https://telodendria.io"),
 "Matrix Client Tutorial": W("https://uhoreg.gitlab.io/matrix-tutorial/"),
}
def get(u):
    try:
        r=S.get(u,timeout=25); return r if r.ok else None
    except Exception: return None
def ok_img(content,u):
    if len(content)<300: return None
    if content.lstrip()[:5].lower().startswith(b"<svg") or b"<svg" in content[:2000]: return "svg"
    try:
        im=Image.open(io.BytesIO(content))
        if min(im.size)<64: return None
        return {"PNG":"png","JPEG":"jpg","WEBP":"webp","ICO":"ico","GIF":"gif"}.get(im.format)
    except Exception: return None
def save(name,u):
    r=get(u)
    if not r: return None
    ext=ok_img(r.content,u)
    if not ext: return None
    p=f"{OUT}/{slug(name)}.{ext}"; open(p,"wb").write(r.content); return u
def default_branch(u):
    out=subprocess.run(["git","ls-remote","--symref",u,"HEAD"],capture_output=True,text=True,timeout=60).stdout
    m=re.search(r"ref: refs/heads/(\S+)",out); return m[1] if m else "main"
def raw_url(url,branch,path):
    if m:=re.match(r"https://github\.com/([^/]+)/([^/]+)",url): return f"https://raw.githubusercontent.com/{m[1]}/{m[2]}/{branch}/{path}"
    if m:=re.match(r"https://codeberg\.org/([^/]+)/([^/]+)",url): return f"https://codeberg.org/{m[1]}/{m[2]}/raw/branch/{branch}/{path}"
    if m:=re.match(r"https://([^/]+)/(.+?)/?$",url): return f"https://{m[1]}/{m[2]}/-/raw/{branch}/{path}"
def site_icons(u):
    r=get(u); c=[]
    if r:
        soup=BeautifulSoup(r.text,"lxml")
        for l in soup.find_all("link",href=True):
            rel=" ".join(l.get("rel",[])).lower()
            if "icon" in rel and "mask" not in rel:
                nums=re.findall(r"\d+",l.get("sizes","") or ""); n=int(nums[0]) if nums else 0
                href=urllib.parse.urljoin(r.url,l["href"])
                c.append(((2000 if l["href"].lower().endswith(".svg") else n)+(100 if "apple" in rel else 0),href))
        for m in soup.find_all("meta"):
            if m.get("property")=="og:logo" and m.get("content"): c.append((1500,urllib.parse.urljoin(r.url,m["content"])))
    base=r.url if r else u
    c+= [(1,urllib.parse.urljoin(base,p)) for p in ("/apple-touch-icon.png","/favicon.svg","/icon.svg","/logo.svg","/favicon.png")]
    c.sort(reverse=True); return [x for _,x in c]
def readme_imgs(u):
    r=get(u); 
    if not r: return []
    soup=BeautifulSoup(r.text,"lxml"); art=soup.find("article") or soup; out=[]
    for img in art.find_all("img",src=True):
        src=img["src"]; alt=(img.get("alt") or "")
        if re.search(r"shields|badge|screenshot",src,re.I): continue
        if re.search(r"logo|icon|mascot|banner",src+alt,re.I): out.append(urllib.parse.urljoin(r.url,src))
    return out
only=sys.argv[1:]
for name,(kind,u,*rest) in SRC.items():
    if only and name not in only: continue
    if kind=="repo": c=[raw_url(u,default_branch(u),rest[0])]
    elif kind=="site": c=site_icons(u)
    else: c=readme_imgs(u)
    got=None
    for x in c:
        got=save(name,x)
        if got: break
    print(("OK  " if got else "--  ")+name+": "+(got or "none"),flush=True)
