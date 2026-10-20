# pre-render each logo as a 256px square texture (no rounded mask; the 3D box supplies the corners) + side colour
import glob, io, json, os, re, sys
sys.argv=["x"]; src=open("scripts/compose.py").read().split("files=sorted(")[0]
exec(src); S=512   # reuses load(), dominant(), tile(); render tiles at 512px
out=[]
for f in sorted(glob.glob("raw/*")):
    try: im=load(f)
    except Exception as e: print("skip",f,e); continue
    t,d=tile(im)
    t=t.convert("RGBA"); 
    # undo the rounded mask so the texture reaches the box edges
    a=Image.new("L",t.size,255); t.putalpha(a)
    # fill any transparent/rounded corner area with the tile's edge colour
    name=os.path.basename(f).rsplit(".",1)[0]
    t.convert("RGB").resize((512,512),Image.LANCZOS).save(f"render/tiles/{name}.png")
    lum=0.299*d[0]+0.587*d[1]+0.114*d[2]
    out.append({"name":name,"side":"#%02x%02x%02x"%tuple(max(0,int(c*0.55)) for c in d)})
json.dump(out,open("render/tiles.json","w")); print(len(out),"tiles")
