import re, pymupdf
from recrop import fix
SRC='/Users/aregkhachatryan/Desktop/UNI/gazodinamika/գազադինամիկա.pdf'
d=pymupdf.open(SRC)
for i,p in enumerate(d):
    rects=[pymupdf.Rect(r) for im in p.get_images(full=True) for r in p.get_image_rects(im[0]) if r.width>40 and r.height>30]
    try: rects+=[pymupdf.Rect(r) for r in p.cluster_drawings() if r.width>40 and r.height>30]
    except: pass
    if not rects: continue
    merged=[]
    for r in rects:
        for m in merged:
            if m.intersects(r): m|=r; break
        else: merged.append(r)
    longs=[]; shorts=[]
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            t=fix(''.join(s['text'] for s in l['spans'])).strip()
            if not t: continue
            if len(t)>10 or re.search(r'Р[иі]с',t): longs.append(pymupdf.Rect(l['bbox']))
            else: shorts.append(pymupdf.Rect(l['bbox']))
    for r in longs:
        if any(pymupdf.Rect(m.x0-3,m.y0-3,m.x1+3,m.y1+3).contains(r) for m in merged): continue
        p.draw_rect(r,color=None,fill=(1,1,1),overlay=True)
    for k,r0 in enumerate(merged):
        g=pymupdf.Rect(r0.x0-16,r0.y0-14,r0.x1+16,r0.y1+14); r=pymupdf.Rect(r0)
        for s in shorts:
            if g.contains(s): r|=s
        r=pymupdf.Rect(r.x0-4,r.y0-4,r.x1+4,r.y1+4)&p.rect
        p.get_pixmap(dpi=220,clip=r).save(f'figs/p{i+1:03d}_{k+1}.png')
print('ok')
