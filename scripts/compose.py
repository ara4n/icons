import glob, io, math, random, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import cairosvg
random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 7)
W,H=1280,720; S=108          # tile size pre-projection
def load(f):
    if f.endswith(".svg"):
        im=Image.open(io.BytesIO(cairosvg.svg2png(url=f,output_width=512,output_height=512) if False else cairosvg.svg2png(url=f,output_width=512,unsafe=True)))
    else:
        im=Image.open(f)
        if f.endswith(".ico"): im.size  # largest frame already
    im=im.convert("RGBA")
    # trim transparent / uniform border
    a=im.getchannel("A"); bbox=a.getbbox()
    if bbox and a.getextrema()[0]<250: im=im.crop(bbox)
    else:
        bg=Image.new("RGBA",im.size,im.getpixel((0,0))); diff=ImageChops.difference(im,bg).convert("L").point(lambda v:255 if v>12 else 0)
        if diff.getbbox(): im=im.crop(diff.getbbox())
    return im
def dominant(im):
    small=im.convert("RGBA").resize((32,32)); px=[p for p in small.getdata() if p[3]>128 and not (p[0]>235 and p[1]>235 and p[2]>235)]
    if not px: return (90,90,110)
    r=sum(p[0] for p in px)//len(px); g=sum(p[1] for p in px)//len(px); b=sum(p[2] for p in px)//len(px); return (r,g,b)
def tile(im):
    """normalise to an app-icon style rounded square S x S"""
    t=Image.new("RGBA",(S,S),(0,0,0,0)); d=dominant(im)
    opaque=sum(1 for p in im.resize((32,32)).getdata() if p[3]>200)/1024
    ratio=im.width/im.height
    if opaque>0.9 and 0.8<ratio<1.25:        # already an app icon: fill tile
        im2=im.resize((S,S),Image.LANCZOS); t.paste(im2,(0,0))
    else:
        lum=0.299*d[0]+0.587*d[1]+0.114*d[2]
        bg=tuple(int(c*0.35+8) for c in d) if lum>110 else tuple(min(255,int(c*0.25+225)) for c in d)  # dark tile for light logos, pale tile for dark logos
        t.paste(bg+(255,),(0,0,S,S))
        im2=im.copy(); im2.thumbnail((int(S*0.66),int(S*0.66)),Image.LANCZOS)
        t.alpha_composite(im2,((S-im2.width)//2,(S-im2.height)//2))
    mask=Image.new("L",(S,S),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,S-1,S-1),radius=S//5,fill=255)
    t.putalpha(ImageChops.multiply(t.getchannel("A"),mask))
    return t,d
def iso(t):
    r=t.rotate(45,expand=True,resample=Image.BICUBIC)
    return r.resize((r.width,int(r.height/math.sqrt(3))),Image.LANCZOS)
files=sorted(glob.glob("raw/*")); tiles=[]
for f in files:
    try: tiles.append(tile(load(f)))
    except Exception as e: print("skip",f,e)
random.shuffle(tiles)
canvas=Image.new("RGBA",(W,H),(0,0,0,255))
# background gradient
grad=Image.new("RGBA",(1,H)); 
for y in range(H): grad.putpixel((0,y),(14+int(10*y/H),10+int(8*y/H),28+int(22*y/H),255))
canvas=grad.resize((W,H)); 
dw=int(S*math.sqrt(2)); dh=int(dw/math.sqrt(3)); gap=12; depth=16
cw,ch=dw+gap,dh+gap
k=0; placements=[]
rows=int(H/(ch/2))+6; cols=int(W/cw)+3
for j in range(-2,rows):
    for i in range(-2,cols):
        x=i*cw+(j%2)*cw//2+20; y=j*ch//2-80
        placements.append((y,x))
placements=[(y,x) for y,x in placements if -dh<y<H and -dw<x<W]
vis=lambda yx: 0<=yx[1] and yx[1]+dw<=W and 0<=yx[0] and yx[0]+dh+depth<=H
placements.sort()
order=[q for q in placements if vis(q)]+[q for q in placements if not vis(q)]
assign={q:tiles[i%len(tiles)] for i,q in enumerate(order)}
print('fully visible slots',len([q for q in placements if vis(q)]))
for y,x in placements:
    t,d=assign[(y,x)]; k+=1
    it=iso(t); cx,cy=x+it.width//2,y+it.height//2
    T=(cx,y); R=(x+it.width,cy); B=(cx,y+it.height); L=(x,cy)
    side=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(side)
    dark=tuple(int(c*0.45) for c in d)+(255,); darker=tuple(int(c*0.3) for c in d)+(255,)
    sd.polygon([L,B,(B[0],B[1]+depth),(L[0],L[1]+depth)],fill=darker)
    sd.polygon([B,R,(R[0],R[1]+depth),(B[0],B[1]+depth)],fill=dark)
    # shadow
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).polygon([(T[0],T[1]+depth+10),(R[0]+6,R[1]+depth+10),(B[0],B[1]+depth+16),(L[0]-6,L[1]+depth+10)],fill=(0,0,0,140))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    canvas.alpha_composite(side); canvas.alpha_composite(it,(x,y))
# soft vignette so UI text stays readable
vig=Image.new("L",(W,H),0); ImageDraw.Draw(vig).ellipse((-W*0.3,-H*0.5,W*1.3,H*1.5),fill=255); vig=vig.filter(ImageFilter.GaussianBlur(220))
canvas=Image.composite(canvas,Image.new("RGBA",(W,H),(8,6,18,255)),vig.point(lambda v:120+v*135//255))
canvas.convert("RGB").save("matrix-montage-720p.png"); print("tiles used",k,"unique",len(tiles))
