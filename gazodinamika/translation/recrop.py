import sys, re, pymupdf
d=pymupdf.open('/Users/aregkhachatryan/Desktop/UNI/gazodinamika/գազադինամիկա.pdf')
def fix(s): return ''.join(bytes([ord(c)]).decode('cp1251') if 0xC0<=ord(c)<=0xFF else c for c in s)
def crop(pg,name,x0,y0,x1,y1,minlen=10):
    p=d[int(pg)-1]; clip=pymupdf.Rect(x0,y0,x1,y1)
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            if not pymupdf.Rect(l['bbox']).intersects(clip): continue
            t=fix(''.join(s['text'] for s in l['spans'])).strip()
            if len(t)>minlen or re.search(r'Р[иі]с',t):
                for s in l['spans']:
                    p.draw_rect(pymupdf.Rect(s['bbox']),color=None,fill=(1,1,1),overlay=True)
    p.get_pixmap(dpi=220,clip=clip).save('figs/'+name)
if __name__=='__main__':
    a=sys.argv[1:]; crop(int(a[0]),a[1],*map(float,a[2:6]),*( [int(a[6])] if len(a)>6 else []))
