import cv2, numpy as np, json, sys
from pathlib import Path
E=Path("Fotos reais")
# centro aproximado e raio aproximado (px da foto)
APROX={"WhatsApp Image 2026-09-27 at 08.45.13(2).jpeg":(635,493,215),
       "WhatsApp Image 2026-09-27 at 08.45.13(3).jpeg":(587,360,270),
       "WhatsApp Image 2026-09-27 at 08.45.13.jpeg":(456,636,240),
       "WhatsApp Image 2026-09-27 at 08.45.13(1).jpeg":(493,448,165)}
def fit(nome,cx,cy,r):
    im=cv2.imread(str(E/nome)); g=cv2.GaussianBlur(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY),(5,5),0)
    ed=cv2.Canny(g,40,110)
    pts=[]
    for a in np.linspace(0,2*np.pi,720,endpoint=False):
        best=None
        for t in np.arange(0.55*r,1.45*r,1.0):
            x=int(cx+t*np.cos(a)); y=int(cy+t*np.sin(a)*0.8)
            if 0<=x<im.shape[1] and 0<=y<im.shape[0] and ed[y,x]: best=(x,y)
        if best: pts.append(best)
    pts=np.array(pts,np.float32)
    rng=np.random.default_rng(1); melhor=None; mv=0
    for _ in range(1500):
        s=pts[rng.choice(len(pts),6,replace=False)]
        try: el=cv2.fitEllipse(s)
        except: continue
        (ex,ey),(w,h),ang=el
        if not (0.6*r<w/2<1.6*r and 0.4*r<h/2<1.6*r): continue
        c,sn=np.cos(np.radians(ang)),np.sin(np.radians(ang))
        dx,dy=pts[:,0]-ex,pts[:,1]-ey; u=(dx*c+dy*sn)/(w/2); v=(-dx*sn+dy*c)/(h/2)
        d=np.abs(np.sqrt(u*u+v*v)-1)*min(w,h)/2
        inl=(d<3).sum()
        if inl>mv: mv,melhor=inl,el
    (ex,ey),(w,h),ang=melhor
    c,sn=np.cos(np.radians(ang)),np.sin(np.radians(ang))
    dx,dy=pts[:,0]-ex,pts[:,1]-ey; u=(dx*c+dy*sn)/(w/2); v=(-dx*sn+dy*c)/(h/2)
    inl=pts[np.abs(np.sqrt(u*u+v*v)-1)*min(w,h)/2<3]
    el=cv2.fitEllipse(inl)
    return im,el,len(inl),len(pts)
res={}
for k,(nome,(cx,cy,r)) in enumerate(APROX.items()):
    im,el,ni,nt=fit(nome,cx,cy,r); res[nome]=el
    v=im.copy(); cv2.ellipse(v,el,(0,0,255),2); cv2.imwrite(f"final/elipse_{k}.jpg",v)
    print(nome[-12:], [round(x,1) for x in (*el[0],*el[1],el[2])], f"{ni}/{nt} pontos")
json.dump({k:[list(v[0]),list(v[1]),v[2]] for k,v in res.items()},open("final/elipses.json","w"))
