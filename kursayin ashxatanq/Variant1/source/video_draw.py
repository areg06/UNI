"""Precise, code-native animated teaching figures for Variant 1's video."""
from __future__ import annotations
import math
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import model as M
import calc as C

W, H = 1920, 1080
INK='#16233c'; MUTED='#5b6980'; GRID='#e8edf4'; BLUE='#1768c4'
COL={'AB':'#de581d','BC':'#22934e','CD':'#7953cb','DE':'#7953cb','CE':'#7953cb','EF':'#1978ca','F':'#ce377c'}
CHAPTERS={1:'Մեխանիզմի կառուցումը',2:'Արագությունների 8 պլանները',3:'Արագացումների պլանը',4:'Մոմենտ և աշխատանք',5:'Իներցիայի մոմենտ և ամփոփում'}

@lru_cache(None)
def font(size=28,bold=False):
    # Apple's Noto Sans Armenian TTC has only ~100 Armenian glyphs: using it
    # alone turns every Latin point name, digit and formula into a tofu box.
    # DejaVu covers Armenian, Latin, Greek, arrows and our modifier letters.
    roots=[Path('/usr/share/fonts/truetype/dejavu')]
    try:
        import matplotlib
        roots.insert(0,Path(matplotlib.get_data_path())/'fonts/ttf')
    except ImportError:
        pass
    for root in roots:
        path=root/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')
        if path.exists():return ImageFont.truetype(str(path),size)
    try:return ImageFont.truetype('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',size)
    except OSError:pass
    universal=Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
    if universal.exists():return ImageFont.truetype(str(universal),size)
    mac=Path('/System/Library/Fonts/NotoSansArmenian.ttc')
    if mac.exists():return ImageFont.truetype(str(mac),size,index=1 if bold else 6)
    for path in ['/usr/share/fonts/truetype/noto/NotoSansArmenian-Regular.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default(size=size)

@lru_cache(None)
def symbol_font(size=28):
    path=Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
    return ImageFont.truetype(str(path),size) if path.exists() else font(size)

def txt(d,xy,text,size=27,color=INK,bold=False,anchor=None):
    d.text(xy,str(text).replace('⟂','⊥'),font=font(size,bold),fill=color,anchor=anchor,stroke_width=0)

def wrap(text,size,width,bold=False):
    lines=[]
    for paragraph in str(text).replace('⟂','⊥').split('\n'):
        line=''
        for word in paragraph.split():
            candidate=(line+' '+word).strip()
            if line and font(size,bold).getlength(candidate)>width:lines.append(line);line=word
            else:line=candidate
        lines.append(line)
    return lines

def block(d,xy,text,size,width,color=INK,bold=False,gap=10):
    x,y=xy
    for line in wrap(text,size,width,bold):txt(d,(x,y),line,size,color,bold);y+=size+gap
    return y

def line(d,a,b,color=INK,width=3,progress=1,dash=False):
    b=(a[0]+(b[0]-a[0])*progress,a[1]+(b[1]-a[1])*progress)
    if dash:
        length=math.dist(a,b)
        if length<.01:return
        for t in range(0,int(length),16):
            t1=t/length;t2=min((t+8)/length,1)
            d.line((a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1,a[0]+(b[0]-a[0])*t2,a[1]+(b[1]-a[1])*t2),fill=color,width=width)
    else:d.line((*a,*b),fill=color,width=width)

def arrow(d,a,b,color=BLUE,width=5,progress=1):
    line(d,a,b,color,width,progress)
    b=(a[0]+(b[0]-a[0])*progress,a[1]+(b[1]-a[1])*progress)
    if math.dist(a,b)<10:return
    angle=math.atan2(b[1]-a[1],b[0]-a[0]);r=13
    d.polygon([b,(b[0]-r*math.cos(angle-.45),b[1]-r*math.sin(angle-.45)),(b[0]-r*math.cos(angle+.45),b[1]-r*math.sin(angle+.45))],fill=color)

def point(d,p,name,color=INK,offset=(10,-32),size=24):
    d.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill=color,outline='white',width=1)
    if name:txt(d,(p[0]+offset[0],p[1]+offset[1]),name,size,color,True)

def poly(d,points,color=BLUE,width=4,progress=1):
    n=max(1,int((len(points)-1)*progress)+1)
    if n>1:d.line(points[:n],fill=color,width=width,joint='curve')

class Plot:
    def __init__(self,size=(1160,670),bounds=(-50,-245,235,20),padding=38,grid=False):
        self.im=Image.new('RGB',size,'white');self.d=ImageDraw.Draw(self.im);self.clip=None
        x0,y0,x1,y1=bounds;self.s=min((size[0]-padding*2)/(x1-x0),(size[1]-padding*2)/(y1-y0))
        self.ox=(size[0]-(x1-x0)*self.s)/2-x0*self.s
        self.oy=(size[1]-(y1-y0)*self.s)/2+y1*self.s
        if grid:
            for x in range(int(x0//10)*10,int(x1)+11,10):line(self.d,self.p((x,y0)),self.p((x,y1)),GRID,1)
            for y in range(int(y0//10)*10,int(y1)+11,10):line(self.d,self.p((x0,y)),self.p((x1,y)),GRID,1)
    def p(self,p):return(self.ox+p[0]*self.s,self.oy-p[1]*self.s)
    def ln(self,a,b,color=INK,width=3,progress=1,dash=False):line(self.d,self.p(a),self.p(b),color,width,progress,dash)
    def ar(self,a,b,color=BLUE,width=5,progress=1):arrow(self.d,self.p(a),self.p(b),color,width,progress)
    def pt(self,p,name,color=INK,offset=(9,-30),size=24):point(self.d,self.p(p),name,color,offset,size)
    def circle(self,c,r,color=MUTED,progress=1,start=0,end=360):
        pts=[self.p((c[0]+r*math.cos(math.radians(start+(end-start)*j/180)),c[1]+r*math.sin(math.radians(start+(end-start)*j/180)))) for j in range(181)]
        poly(self.d,pts,color,2,progress)
    def ray(self,a,v,color=BLUE,progress=1):
        length=M.mag(v)
        if length<1e-10:return
        # A construction line grows outwards from its known source point.
        # Clip it below the plot header and above its explanatory footer.
        u=M.scl(v,120/length*progress)
        aa=self.p(M.sub(a,u));bb=self.p(M.add(a,u))
        if self.clip:
            clipped=clip_segment(aa,bb,self.clip)
            if clipped is None:return
            aa,bb=clipped
        line(self.d,aa,bb,color,3,1,True)

def clip_segment(a,b,rect):
    """Liang–Barsky clipping in screen pixels."""
    x0,y0,x1,y1=rect;dx=b[0]-a[0];dy=b[1]-a[1];lo,hi=0.,1.
    for p,q in [(-dx,a[0]-x0),(dx,x1-a[0]),(-dy,a[1]-y0),(dy,y1-a[1])]:
        if abs(p)<1e-12:
            if q<0:return None
        else:
            r=q/p
            if p<0:lo=max(lo,r)
            else:hi=min(hi,r)
            if lo>hi:return None
    return ((a[0]+lo*dx,a[1]+lo*dy),(a[0]+hi*dx,a[1]+hi*dy))

def mechanism(plot,i=2,focus=(),opacity=False,labels=True,stage=9,progress=1,animate=()):
    P=M.POS[i];d=plot.d
    plot.ln((0,15),(0,-240),'#adbbcc',2,dash=True)
    links={'AB':(M.A,P['B']),'BC':(P['B'],P['C']),'CD':(M.D,P['C']),'DE':(M.D,P['E']),'CE':(P['C'],P['E']),'EF':(P['E'],P['F'])}
    for key,(a,b) in links.items():
        color='#d1d9e4' if opacity else COL[key]
        if focus and key not in focus and not opacity:color='#cbd3de'
        plot.ln(a,b,color,7 if key in focus else 4,progress if key in animate else 1)
    for name,p in [('A',M.A),('D',M.D),('B',P['B']),('C',P['C']),('E',P['E']),('F',P['F'])]:
        if labels:plot.pt(p,name,offset={'A':(10,2),'B':(9,-29),'D':(8,-28),'C':(-28,-26),'E':(-27,0),'F':(14,-9)}[name])
    f=plot.p(P['F']);d.rounded_rectangle((f[0]-14,f[1]-18,f[0]+14,f[1]+18),radius=3,outline=COL['F'] if not opacity else '#cbd3de',width=3)
    if labels:
        plot.pt(P['S2'],'S₂',COL['BC'],(7,7),21)
        txt(d,(20,18),f'Դիրք {i}  ·  φ = {i*45}°',26,INK,True)
        txt(d,(20,52),'↻  n₁ = 210 պտ/ր',22,MUTED)

def geometry(scene,t):
    st=scene.get('stage',0);i=scene.get('i',2);focus=scene.get('focus',[])
    p=Plot(grid=True);d=p.d;active=t
    if st>=11:return force_diagram(scene,t)
    p.ln((0,12),(0,-242),'#8999ad',2,dash=True)
    p.pt(M.D,'D');p.pt(M.A,'A',(INK), (10,0))
    p.ln(M.D,(M.A[0],0),'#c3cfdf',2,dash=True);p.ln((M.A[0],0),M.A,'#c3cfdf',2,dash=True)
    txt(d,(p.p((75,0))[0],p.p((75,0))[1]-32),'L₁* = 200 մմ',23,MUTED)
    txt(d,(p.p(M.A)[0]+25,p.p((0,-44))[1]),'L₂* = 85,71 մմ',22,MUTED)
    if st>=1:
        p.circle(M.D,M.ED,'#b9a5dc',active if st==1 else 1,-135,-80)
        p.ln(M.D,(0,-137),'#aab5c5',2,dash=True)
        p.circle(M.D,65,COL['DE'],1,-93,-90)
        p.ln(M.D,M.E0p,COL['DE'],5,active if st==1 else 1);p.pt(M.E0p,'E₀′',COL['DE'],(10,-9))
        txt(d,(20,18),'DE* = 120 մմ',23,COL['DE'],True)
        txt(d,(20,52),'β = 3°',23,COL['DE'],True)
    if st>=2:
        if st==2:p.circle(M.E0p,M.EF,COL['EF'],active,205,325)
        p.ln(M.E0p,M.F0p,COL['EF'],4);p.pt(M.F0p,'F₀′',COL['F'],(15,-10))
    if st>=3:
        p.ar(M.F0p,M.F0,COL['F'],5,active if st==3 else 1);p.pt(M.F0,'F₀',COL['F'],(-40,-23))
        a=p.p(M.F0);txt(d,(a[0]-170,a[1]+28),'H* = 40 մմ',24,COL['F'],True)
    if st>=4:
        if st==4:
            p.circle(M.D,M.ED,COL['DE'],active,195,275);p.circle(M.F0,M.EF,COL['EF'],active,60,150)
        p.ln(M.D,M.E0,COL['DE'],5);p.ln(M.E0,M.F0,COL['EF'],4);p.pt(M.E0,'E₀',COL['DE'],(-40,-13))
    if st>=5:
        p.circle(M.D,M.CD,'#b9a5dc',active if st==5 else 1,-80,-36)
        p.circle(M.D,52,COL['CD'],active if st==5 else 1,M.ang(M.E0p),M.ang(M.C0p))
        q=p.p((28,-47));txt(d,(q[0],q[1]),'50°',23,COL['CD'],True)
        for q,name in [(M.C0,'C₀'),(M.C0p,'C₀′')]:p.ln(M.D,q,COL['CD'],5,active if st==5 else 1);p.pt(q,name,COL['CD'])
        p.ln(M.E0,M.C0,COL['CD'],2,dash=True);p.ln(M.E0p,M.C0p,COL['CD'],2,dash=True)
        txt(d,(20,100),'CD* = 108 մմ',23,COL['CD'],True)
        txt(d,(20,134),'α = 50°',23,COL['CD'],True)
    if st>=6:
        p.ln(M.A,M.C0,'#b58218',4,active if st==6 else 1);p.ln(M.A,M.C0p,'#b58218',4,active if st==6 else 1)
        txt(d,(760,100),'AC₀ = 169,7 մմ',24,'#93650d',True);txt(d,(760,140),'AC₀′ = 121,6 մմ',24,'#93650d',True)
    if st>=7:
        p.circle(M.A,M.ABS,'#de581d',active if st==7 else 1)
        for q,b,n in [(M.C0,M.B0,'B₀'),(M.C0p,M.B0p,'B₀′')]:p.ln(M.A,b,COL['AB'],6);p.ln(b,q,COL['BC'],5);p.pt(b,n,COL['AB'],(8,-34))
    if st>=8:
        p=Plot(grid=True);d=p.d
        if st>=9:
            for k in range(max(1,math.ceil(8*t)) if st==9 else 8):mechanism(p,k,opacity=True,labels=False)
        animated=(('DE','EF') if 'EF' in focus else ('AB','BC','CD')) if st==8 else ()
        mechanism(p,i,focus=focus,progress=t,animate=animated)
        if st==8:
            q=M.POS[i]
            if 'EF' not in focus:
                p.circle(M.A,M.ABS,'#c4b29c')
                a=M.ang(M.sub(q['C'],q['B']));p.circle(q['B'],M.BCS,COL['BC'],t,a-13,a+13)
                a=M.ang(q['C']);p.circle(M.D,M.CD,COL['CD'],t,a-13,a+13)
            else:
                a=M.ang(q['E']);p.circle(M.D,M.ED,'#aa94d2',t,a-13,a+13)
                a=M.ang(M.sub(q['F'],q['E']));p.circle(q['E'],M.EF,COL['EF'],t,a-13,a+13)
                p.ln(M.D,q['E'],COL['DE'],5,t)
        if st==10:
            txt(d,(650,85),'Մասշտաբ՝ μₗ = 0,00175 մ/մմ',25,INK,True)
            txt(d,(650,128),'AB* = 24,05 մմ',26,COL['AB']);txt(d,(650,169),'BC* = 145,65 մմ',26,COL['BC'])
            p.ln(M.D,(200,0),'#8fa1b8',2,dash=True);p.ln((200,0),M.A,'#8fa1b8',2,dash=True)
            p.ar((0,10),(200,10),'#64768d',2);p.ar((200,10),(0,10),'#64768d',2)
            q=p.p((50,10));txt(d,(q[0],q[1]-30),'L₁* = 200 մմ',23,MUTED)
            p.ar((220,0),(220,M.A[1]),'#64768d',2);p.ar((220,M.A[1]),(220,0),'#64768d',2)
            q=p.p((190,-55));txt(d,(q[0]-15,q[1]),'L₂* = 85,71 մմ',22,MUTED)
            p.ar((-15,M.F0[1]),(-15,M.F0p[1]),COL['F'],2);p.ar((-15,M.F0p[1]),(-15,M.F0[1]),COL['F'],2)
            q=p.p((-15,(M.F0[1]+M.F0p[1])/2));txt(d,(q[0]-205,q[1]-10),'H_F* = 40 մմ',23,COL['F'],True)
        if st==9:
            for k in range(8):
                if k!=i:p.pt(M.POS[k]['B'],str(k),COL['AB'],(int(18*math.cos(k)),int(-28+15*math.sin(k))),19)
    return p.im

def vector_diagram(scene,t,acc=False):
    i=scene.get('i',2);st=scene.get('stage',0)
    board=Image.new('RGB',(1160,670),'white')
    source=Plot((520,650),(-85,-245,235,25),padding=30)
    mechanism(source,i,focus=scene.get('focus',[]))
    txt(source.d,(20,608),'ՈՒՂՂՈՒԹՅԱՆ ԱՂԲՅՈՒՐԸ',21,MUTED,True)
    board.paste(source.im,(0,0))
    raw=M.aplan(i) if acc else M.vplan(i)
    key='pi' if acc else 'p';v=dict(raw)
    # A common rescale retains all vector relations while displaying adopted pb=50 / πb=70.
    scale=(70 if acc else 50)/M.mag(v['b'])
    v={k:M.scl(a,scale) for k,a in v.items()}
    xs=[q[0] for q in v.values()];ys=[q[1] for q in v.values()]
    cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
    factor=3.5 if acc else 4.5
    plan=Plot((620,650),(cx-310/factor,cy-325/factor,cx+310/factor,cy+325/factor),padding=5)
    plan.clip=(14,105,606,579)
    d=plan.d;P=M.POS[i];zero=(0,0)
    txt(d,(24,18),'ԱՐԱԳԱՑՈՒՄՆԵՐԻ ՊԼԱՆ' if acc else 'ԱՐԱԳՈՒԹՅՈՒՆՆԵՐԻ ՊԼԱՆ',23,INK,True)
    txt(d,(24,54),'μₐ = 0,2909 (մ/վ²)/մմ' if acc else 'μᵥ = 0,01852 (մ/վ)/մմ',23,MUTED)
    def edge(a,b,col,stage,arrowed=True,dashed=False):
        if st>=stage:
            frac=t if st==stage else 1
            if arrowed:plan.ar(v[a],v[b],col,4,frac)
            else:plan.ln(v[a],v[b],col,3,frac,dashed)
    def ray(a,vec,col,stage):
        if not acc and i==0 and st>=9:return
        if st>=stage:plan.ray(v[a],vec,col,t if st==stage else 1)
    def tag(k,name=None,color=INK):
        offsets={'p':(-110,15),'pi':(-110,15),'c':(-30,-31),'n3':(16,7),'e':(-24,-32),'n4':(24,8),'f':(18,-37),'s2':(10,2)}
        if acc:offsets.update(b=(15,8),n2=(24,-34))
        plan.pt(v[k],name or k,color,offsets.get(k,(10,-28)),23)
    pole_name='π (a,d)' if acc else ('p (a,c,d,e,f)' if i==0 and st>=7 else ('p (a,c,d)' if i==0 and st>=4 else 'p (a,d)'))
    tag(key,pole_name)
    edge(key,'b',COL['AB'],1)
    if st>=1:tag('b',color=COL['AB'])
    if not acc:
        ray(key,(-P['C'][1],P['C'][0]),COL['CD'],2)
        cb=M.sub(P['C'],P['B']);ray('b',(-cb[1],cb[0]),COL['BC'],3)
        edge(key,'c',COL['CD'],4);edge('b','c',COL['BC'],4)
        if st>=4 and i!=0:tag('c',color=COL['CD'])
        edge(key,'e',COL['DE'],5);edge('c','e','#ad9bcf',5,False,True)
        if st>=5 and i!=0:tag('e',color=COL['DE'])
        ray(key,(0,1),COL['F'],6)
        fe=M.sub(P['F'],P['E']);ray('e',(-fe[1],fe[0]),COL['EF'],7)
        edge('e','f',COL['EF'],7);edge(key,'f',COL['F'],7)
        if st>=7 and i!=0:tag('f',color=COL['F'])
        edge(key,'s2','#344861',8)
        if st>=8:tag('s2','s₂',COL['BC']);txt(d,(24,598),'bs₂ = cs₂  ·  S₂-ը BC-ի մեջտեղում է',22,MUTED)
    else:
        edge('b','n2',COL['BC'],2)
        if st>=2:tag('n2','n₂',COL['BC'])
        cb=M.sub(P['C'],P['B']);ray('n2',(-cb[1],cb[0]),COL['BC'],3)
        edge(key,'n3',COL['CD'],4)
        if st>=4:tag('n3','n₃',COL['CD'])
        ray('n3',(-P['C'][1],P['C'][0]),COL['CD'],5)
        edge('n2','c',COL['BC'],5);edge('n3','c',COL['CD'],5);edge(key,'c','#46566f',5)
        if st>=5:tag('c',color=COL['CD'])
        edge(key,'e',COL['DE'],6)
        if st>=6:tag('e',color=COL['DE'])
        edge('e','n4',COL['EF'],7)
        if st>=7:tag('n4','n₄',COL['EF'])
        fe=M.sub(P['F'],P['E']);ray('n4',(-fe[1],fe[0]),COL['EF'],8)
        ray(key,(0,1),COL['F'],9);edge('n4','f',COL['EF'],9);edge(key,'f',COL['F'],9)
        if st>=9:tag('f',color=COL['F'])
        edge(key,'s2','#46566f',10)
        if st>=10:tag('s2','s₂',COL['BC'])
    board.paste(plan.im,(540,0));d=ImageDraw.Draw(board)
    arrow(d,(494,325),(548,325),'#94a7c0',3)
    return board

def force_diagram(scene,t):
    p=Plot((1160,670),(0,-2,45,45),padding=55,grid=True);d=p.d;st=scene.get('stage',12);i=scene.get('i',2)
    def q(fr,s):return p.p((fr,40-s))
    arrow(d,q(0,0),q(44,0),INK,3);arrow(d,q(0,0),q(0,43),INK,3)
    txt(d,(q(42,0)[0]-90,q(42,0)[1]-40),'Fᵣ →',25,INK,True)
    txt(d,(q(0,40)[0]-65,q(0,40)[1]-5),'S_F',24,INK,True)
    txt(d,(q(0,0)[0]+10,q(0,0)[1]-35),'0',23)
    txt(d,(45,24),'Առաջադրանքի ուժային կորը → գծագրի մասշտաբ',26,INK,True)
    # The slider stroke is drawn at the same vertical scale as the S_F axis.
    # This makes the horizontal reading line's geometric source visible.
    ytop=q(0,0)[1];ybot=q(0,40)[1];gx=145
    txt(d,(35,78),'Սողնակի ընթացքը',21,MUTED,True)
    line(d,(gx,ytop-10),(gx,ybot+10),'#7c8da5',3)
    for y,label in [(ytop,'F₀'),(ybot,'F₀′')]:
        line(d,(gx,y),(q(0,0)[0],y),'#acb8c9',2,dash=True)
        point(d,(gx,y),label,COL['F'],(-51,-14),24)
    txt(d,(35,(ytop+ybot)/2-18),'40 մմ',23,COL['F'],True)
    if st>=12:
        pts=[q(39*M.fre_shape(k/300),40*k/300) for k in range(301)]
        poly(d,pts,COL['F'],5,t if st==12 else 1)
        txt(d,(q(39,0)[0]-145,q(39,0)[1]+20),'39 մմ = 7800 Ն',25,COL['F'],True)
    if st>=13:
        s=M.POS[i]['sF']/M.H;fr=C.MP[i]['yF'];loc=q(fr,40*s)
        y=loc[1];d.rounded_rectangle((gx-11,y-15,gx+11,y+15),radius=3,fill='white',outline=COL['F'],width=3)
        txt(d,(gx-55,y-12),f'F{i}',23,COL['F'],True)
        line(d,(gx+12,y),q(0,40*s),'#93a6bf',3,1,True)
        line(d,q(0,40*s),loc,BLUE,4,t);line(d,loc,q(fr,0),BLUE,2,dash=True)
        point(d,loc,f'{fr:.1f}'.replace('.',',')+' մմ',BLUE,(12,-10),24)
        txt(d,(590,560),f'Դիրք {i}: Fᵣ = {C.MP[i]["Fr"]:.0f} Ն',30,BLUE,True)
    return p.im

def smooth_points(xs,ys,n=20):
    ms=M._pchip_slopes(xs,ys);pts=[]
    for k in range(len(xs)-1):
        h=xs[k+1]-xs[k]
        for a in range(n):
            t=a/n;y=(2*t**3-3*t*t+1)*ys[k]+(t**3-2*t*t+t)*h*ms[k]+(-2*t**3+3*t*t)*ys[k+1]+(t**3-t*t)*h*ms[k+1]
            pts.append((xs[k]+t*h,y))
    return pts+[(xs[-1],ys[-1])]

def force_sources(scene,t):
    """Show the actual application points and compare force/velocity signs."""
    i=scene.get('j',2)%8;P=M.POS[i]
    p=Plot((1160,670),(-120,-295,245,25),padding=45);d=p.d
    mechanism(p,i,focus=['BC','EF'])
    s=P['S2'];f=P['F']
    p.ar(s,M.add(s,(0,-55)),COL['BC'],6,t)
    q=p.p(M.add(s,(5,-56)));txt(d,q,'G₂ ↓',26,COL['BC'],True)
    vs=M.scl(P['K']['VS2'],42/M.mag(P['K']['VS2']))
    p.ar(s,M.add(s,vs),BLUE,6,t)
    q=p.p(M.add(s,vs));txt(d,(q[0]+10,q[1]-28),'Vₛ₂',25,BLUE,True)
    p.ar(f,M.add(f,(0,-55)),COL['AB'],6,t)
    q=p.p(M.add(f,(-7,-40)));txt(d,(q[0]-95,q[1]),'G₅ ↓',26,COL['AB'],True)
    p.ar(f,M.add(f,(0,57)),COL['F'],6,t)
    q=p.p(M.add(f,(-9,55)));txt(d,(q[0]-70,q[1]-30),'Fᵣ ↑',26,COL['F'],True)
    p.ar(M.add(f,(28,0)),M.add(f,(28,-43)),BLUE,5,t)
    q=p.p(M.add(f,(34,-29)));txt(d,q,'V_F ↓',25,BLUE,True)
    txt(d,(20,110),'G₅ · V_F > 0  →  «+»',25,COL['AB'],True)
    txt(d,(20,150),'Fᵣ · V_F < 0  →  «−»',25,COL['F'],True)
    txt(d,(20,190),'G₂ · Vₛ₂ < 0  →  «−»',25,COL['BC'],True)
    txt(d,(20,615),'Սլաքները ցույց են տալիս ուղղությունները, ոչ ուժերի մասշտաբը։',23,MUTED)
    return p.im

def projection_sources(scene,t):
    board=Image.new('RGB',(1160,670),'white')
    source=Plot((520,650),(-85,-245,235,25),padding=30)
    mechanism(source,2,focus=['BC'])
    s=M.POS[2]['S2'];vs=M.POS[2]['K']['VS2'];vs=M.scl(vs,42/M.mag(vs))
    source.ar(s,M.add(s,vs),BLUE,5,t)
    q=source.p(M.add(s,vs));txt(source.d,(q[0]+6,q[1]-24),'Vₛ₂',23,BLUE,True)
    source.ar(s,M.add(s,(0,-40)),COL['BC'],5,t)
    q=source.p(M.add(s,(0,-40)));txt(source.d,(q[0]+9,q[1]),'G₂ ↓',23,COL['BC'],True)
    board.paste(source.im,(0,0))
    p=Plot((620,650),(-20,-15,65,65),padding=35);d=p.d;v=M.vplan(2)
    txt(d,(15,16),'ԱՐԱԳՈՒԹՅԱՆ ՈՒՂՂԱՁԻԳ ՄԱՍԸ',22,INK,True)
    p.ln(v['b'],v['c'],'#b5c2d2',3);p.pt(v['b'],'b','#8fa1b7');p.pt(v['c'],'c','#8fa1b7')
    p.ar((0,0),v['s2'],BLUE,5,t)
    p.pt((0,0),'p',INK,(-28,12));p.pt(v['s2'],'s₂',COL['BC'],(12,-24))
    p.ln((0,-6),(0,45),'#8696ad',2,dash=True)
    end=(0,v['s2'][1]);p.ln(v['s2'],end,'#8696ad',3,t,True)
    p.ar((0,0),end,COL['F'],7,t)
    q=p.p(end);txt(d,(q[0]+14,q[1]-35),'−16,0 մմ',28,COL['F'],True)
    txt(d,(24,548),'p-ից վեր՝ «−» · կշիռը՝ ներքև',23,MUTED)
    txt(d,(24,592),'ps₂ = 49,9 մմ ≠ ուղղաձիգ պրոյեկցիա',22,BLUE,True)
    board.paste(p.im,(540,0));return board

def contribution_cards(inertia_model=False):
    """Show each numerical term beside its physical source, not unrelated axes."""
    board=Image.new('RGB',(1160,670),'white');d=ImageDraw.Draw(board)
    txt(d,(35,24),'Դիրք 2 · Երեք ֆիզիկական աղբյուր → երեք ներդրում',28,INK,True)
    if inertia_model:
        rows=[('Կենտրոնի համընթաց շարժում','m₂(Vₛ₂/ω₁)²','0,006726',COL['BC']),
              ('Շարժաթևի պտույտ','Iₛ₂(ω₂/ω₁)²','0,001852',COL['CD']),
              ('Սողնակի համընթաց շարժում','m₅(V_F/ω₁)²','0,019425',COL['F'])]
        final='Iₚ₂ ≈ 0,006726 + 0,001852 + 0,019425 = 0,02800 կգ·մ²'
        footer='Արագությունների հարաբերությունները քառակուսի են. նշանները վերանում են։'
    else:
        rows=[('Շարժաթևի կշիռ G₂','38 × (−16,0) × 0,0008422','−0,51 Ն·մ',COL['BC']),
              ('Սողնակի կշիռ G₅','175 × 39,5 × 0,0008422','+5,82 Ն·մ',COL['AB']),
              ('Օգտակար դիմադրություն Fᵣ','−6860 × 39,5 × 0,0008422','−228,21 Ն·մ',COL['F'])]
        final='Mₚ₂ = −0,51 + 5,82 − 228,21 = −222,9 Ն·մ'
        footer='μᵥ / ω₁ = 0,0008422 մ/մմ · նույն դիրքի չափումներն են միավորվում։'
    for k,(label,equation,value,col) in enumerate(rows):
        y=92+k*130
        d.rounded_rectangle((35,y,1125,y+112),radius=16,fill='#f2f6fc',outline='#d7e0eb',width=2)
        d.rectangle((35,y+13,42,y+99),fill=col)
        txt(d,(65,y+14),label,26,col,True)
        txt(d,(65,y+58),equation,26,INK)
        txt(d,(1094,y+56),value,31,col,True,anchor='ra')
    d.rounded_rectangle((35,504,1125,598),radius=16,fill='#eaf2ff')
    size=33
    while font(size,True).getlength(final)>1020:size-=1
    txt(d,(62,532),final,size,BLUE,True)
    txt(d,(35,624),footer,22,MUTED)
    return board

def dynamics(scene,t):
    mode=scene.get('mode')
    if mode=='forces':return force_sources(scene,t)
    if mode=='projection':return projection_sources(scene,t)
    if mode=='resistance':return force_diagram(dict(scene,stage=13,i=scene.get('j',2)%8),t)
    if mode=='calculation':return contribution_cards()
    if mode=='dead':
        board=vector_diagram(dict(scene,stage=9,i=0,focus=['BC']),t)
        txt(ImageDraw.Draw(board),(575,545),'V_F = 0 · Vₛ₂ = 0,463 մ/վ',23,BLUE,True)
        return board
    st=scene.get('stage',0);position=scene.get('j',2)%9;j=max(1,min(8,scene.get('j',2)))
    # Shared angle abscissas; top axis M, lower axis A separated for legibility.
    # The schematic uses y_A=-110? Use custom screen mappings to retain 150 mm separation.
    p=Plot((1160,670),(-48,-220,174,30),padding=30,grid=True);d=p.d
    xs=[20*k for k in range(9)];ym=[x['Mmm'] for x in C.MP];ay=-150
    p.ar((-44,0),(169,0),INK,3);p.ar((0,-95),(0,24),INK,3)
    p.ar((0,ay),(169,ay),INK,3);p.ar((0,ay-66),(0,ay+68),INK,3)
    p.pt((-40,0),'P',INK,(-25,-30));p.pt((0,0),'Oₘ',INK,(-35,5));p.pt((0,ay),'Oₐ',INK,(-37,6))
    txt(d,(45,12),'A4 · Mₚ(φ) → Aᵣ(φ), Aₘ(φ), ΔE(φ)',27,INK,True)
    for k in range(9):
        p.ln((20*k,4),(20*k,ay-65),'#c7d3e1',1,dash=True)
        screen=p.p((20*k,0));txt(d,(screen[0]-8,screen[1]-30),str(k),20,MUTED)
        screen=p.p((20*k,ay));txt(d,(screen[0]-8,screen[1]+10),str(k),20,MUTED)
    if st>=1:
        for k in range(9):
            p.ln((20*k,0),(20*k,ym[k]),'#98acc6',2);p.pt((20*k,ym[k]),'',BLUE)
    if st>=2:poly(d,[p.p(q) for q in smooth_points(xs,ym)],BLUE,5,t if st==2 else 1)
    if mode=='scale':
        p.ar((20*position,0),(20*position,ym[position]),'#df9513',6,t)
        q=p.p((20*position,ym[position]));txt(d,(q[0]+16,q[1]-26),f'y{position} = {C.n(ym[position])} մմ',24,'#95620a',True)
    if st>=3:
        xmid=20*j-10;y=C.YMID[j-1]
        p.ln((xmid,0),(xmid,y),'#df9513',4,t if st==3 else 1);p.pt((xmid,y),'', '#df9513')
        if st>=4:p.ln((xmid,y),(0,y),'#df9513',4,t if st==4 else 1,True);p.pt((0,y),'', '#df9513')
        if st>=5:p.ar((-40,0),(0,y),'#df9513',5,t if st==5 else 1)
        screen=p.p((xmid,y));txt(d,(screen[0]+10,screen[1]+10),f'yₘ={C.n(y)} մմ',22,'#95620a',True)
    if st>=6:
        count=j if st==6 else 8
        for k in range(1,count+1):
            p.ln((20*(k-1),ay+C.AR[k-1]),(20*k,ay+C.AR[k]),COL['BC'],5,t if st==6 and k==j else 1)
            p.pt((20*k,ay+C.AR[k]),f'{k}′',COL['BC'],(6,4),18)
        if st==6:
            a=(20*(j-1),ay+C.AR[j-1]);b=(20*j,ay+C.AR[j]);p.ar(a,b,'#df9513',6,t)
    if st>=7:
        p.ln((0,ay),(160,ay+C.AM[8]),COL['AB'],5,t if st==7 else 1)
        p.pt((160,ay+C.AM[8]),'8″',COL['AB'],(9,-26),23)
    if st>=8:
        poly(d,[p.p(q) for q in smooth_points(xs,[ay+x for x in C.DE])],COL['F'],5,t if st==8 else 1)
        x=20*(scene.get('j',3)%9);k=scene.get('j',3)%9
        p.ln((x,ay+C.AR[k]),(x,ay+C.DE[k]),COL['AB'],5)
        p.pt((x,ay+C.DE[k]),f'ΔE{k}',COL['F'],(8,-28),23)
    if st>=9:
        p.ar((-40,0),(0,C.YMM),COL['AB'],4,t);p.ln((0,C.YMM),(160,C.YMM),COL['AB'],4,t)
    if mode=='meaning':
        d.rounded_rectangle((22,335,305,553),radius=14,fill='#eef4ff',outline='#cedbf0',width=2)
        block(d,(38,350),'3 → 4 դիրքեր\n−27,2 → −27,0 մմ\n\nԵրկուսն էլ «−» են,\nբայց կա աճ՝\n+0,87 Ջ',22,252,BLUE,True,gap=9)
    # compact key, always anchored away from drawn curves
    for n,(s,col) in enumerate([('Mₚ',BLUE),('Aᵣ',COL['BC']),('Aₘ',COL['AB']),('ΔE',COL['F'])]):txt(d,(850,150+n*42),s,26,col,True)
    return p.im

def inertia(scene,t):
    st=scene.get('stage',0);j=scene.get('j',2)%9
    if scene.get('mode')=='calculation':return contribution_cards(True)
    p=Plot((1160,670),(0,0,380,270),padding=20,grid=True);d=p.d
    txt(d,(30,12),'A3 · Iₚ(φ) և ΔT(φ)',27,INK,True)
    if st<=1:
        q=Plot((620,650),(-45,-245,235,25),padding=36);mechanism(q,j%8,focus=['BC','EF']);p.im.paste(q.im,(5,0));d=ImageDraw.Draw(p.im)
        if scene.get('mode')=='units':
            block(d,(650,95),'G₂ = 38 Ն\nm₂ = 38 / 10 = 3,8 կգ\n\nG₅ = 175 Ն\nm₅ = 175 / 10 = 17,5 կգ',27,470,gap=13)
            block(d,(650,400),'Iₛ₂ = 350 × 10⁻³\n      = 0,35 կգ·մ²\n\ng = 10 մ/վ²',28,470,BLUE,True,gap=13)
        else:
            block(d,(650,155),'m₂ = 3,8 կգ\nm₅ = 17,5 կգ\nIₛ₂ = 0,35 կգ·մ²',30,470,gap=24)
            block(d,(650,380),f'Դիրք {j}\nIₚ = {C.n(C.IP[j]["I"],5)} կգ·մ²',31,470,BLUE,True,gap=22)
        return p.im
    p.ar((250,255),(345,255),INK,3);p.ar((250,255),(250,85),INK,3)
    txt(d,(p.p((330,255))[0],p.p((330,255))[1]-35),'Iₚ →',24,INK,True)
    vals=[x['Imm'] for x in C.IP]
    for k in range(9):
        y=255-20*k;p.ln((250,y),(335,y),'#c7d3e1',1,dash=True)
        loc=p.p((250,y));txt(d,(loc[0]-28,loc[1]-10),str(k),21,MUTED)
    if st>=3:
        count=8 if st>=4 else j
        for k in range(count+1):
            y=255-20*k;p.ln((250,y),(250+vals[k],y),BLUE,3,t if st==3 and k==j else 1);p.pt((250+vals[k],y),'',BLUE)
        if st>=4:
            pts=smooth_points([20*k for k in range(9)],vals)
            poly(d,[p.p((250+v,255-x)) for x,v in pts],BLUE,5,t if st==4 else 1)
    if st>=5:
        p.ar((30,75),(198,75),INK,3);p.ar((30,30),(30,100),INK,3)
        for k in range(9):
            x=30+20*k;p.ln((x,100),(x,35),'#c7d3e1',1,dash=True);q=p.p((x,75));txt(d,(q[0]-6,q[1]+8),str(k),20,MUTED)
        q=p.p((30,110));txt(d,q,'ΔT = ΔE',25,COL['F'],True)
    if st>=6:
        count=8 if st>=7 else j
        for k in range(count+1):
            x=30+20*k;p.ln((x,75),(x,75+C.DE[k]),COL['F'],4,t if st==6 and k==j else 1);p.pt((x,75+C.DE[k]),'',COL['F'])
        if st>=7:poly(d,[p.p((30+x,75+y)) for x,y in smooth_points([20*k for k in range(9)],C.DE)],COL['F'],5,t if st==7 else 1)
    if st>=8:
        a=p.p((210,67));b=p.p((370,10));d.rounded_rectangle((a[0],a[1],b[0],b[1]),radius=12,fill='#f3f6fb',outline='#c2cede',width=2)
        block(d,(a[0]+18,a[1]+18),'Ազատ տեղ՝ հաջորդ փուլի\nէներգիա–զանգված դիագրամի համար',23,b[0]-a[0]-36,MUTED)
    return p.im

@lru_cache(None)
def preview(number):
    import pymupdf
    names={1:'chertej_A3_1.pdf',2:'chertej_A3_2.pdf',3:'chertej_A4_graf.pdf',4:'chertej_A3_4.pdf'}
    doc=pymupdf.open(Path(__file__).resolve().parent.parent/names[number]);pix=doc[0].get_pixmap(matrix=pymupdf.Matrix(2,2),alpha=False)
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((1120,630),Image.Resampling.LANCZOS)
    canvas=Image.new('RGB',(1160,670),'#fff');canvas.paste(im,((1160-im.width)//2,(670-im.height)//2));return canvas

def overview(scene,t):
    board=Image.new('RGB',(1160,670),'white');d=ImageDraw.Draw(board)
    for k in range(4):
        im=preview(k+1).copy();im.thumbnail((535,290),Image.Resampling.LANCZOS)
        x=20+(k%2)*575;y=15+(k//2)*330
        d.rounded_rectangle((x,y,x+545,y+310),radius=16,outline='#d6dfeb',width=2,fill='#f8fafc')
        board.paste(im,(x+(545-im.width)//2,y+4))
        txt(d,(x+20,y+275),f'Թերթ {k+1} · '+('A4' if k==2 else 'A3'),24,BLUE,True)
    return board

def frame(scene,progress=1,global_progress=0):
    im=Image.new('RGB',(W,H),'#edf2f8');d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,118),fill=INK)
    chapter=scene.get('chapter',1)
    txt(d,(46,18),f'ՏԱՐԲԵՐԱԿ 1  /  {CHAPTERS.get(chapter,"Կառուցման ուղեցույց")}',24,'#b9ccec',True)
    title=scene.get('title','Կառուցենք՝ հասկանալով')
    size=43
    while font(size,True).getlength(title)>1810:size-=1
    txt(d,(46,54),title,size,'white',True)
    d.rounded_rectangle((25,142,1235,845),radius=20,fill='white',outline='#d4dfed',width=2)
    view=scene.get('view','overview');t=1-(1-min(1,max(0,progress)))**2
    if view=='mechanism':drawing=geometry(scene,t)
    elif view=='velocity':drawing=vector_diagram(scene,t)
    elif view=='acceleration':drawing=vector_diagram(scene,t,True)
    elif view=='dynamics':drawing=dynamics(scene,t)
    elif view=='inertia':drawing=inertia(scene,t)
    elif view=='sheet':drawing=preview(scene.get('sheet',1))
    else:drawing=overview(scene,t)
    im.paste(drawing,(50,160))
    d=ImageDraw.Draw(im)
    x=1270;right=1880
    d.rounded_rectangle((x,142,right,845),radius=20,fill='white',outline='#d4dfed',width=2)
    txt(d,(x+28,170),'ԻՆՉՈՒ՞ ԱՅՍ ՔԱՅԼԸ',24,BLUE,True)
    y=block(d,(x+28,218),scene.get('note','Յուրաքանչյուր գիծ կառուցում ենք հայտնի պայմանից։'),32,550,INK,True,gap=13)
    formula=scene.get('formula','')
    if formula:
        y=max(y+30,395)
        flines=wrap(formula,29,520)
        fh=min(230,40+len(flines)*43)
        d.rounded_rectangle((x+22,y,right-22,y+fh),radius=15,fill='#eaf2ff')
        block(d,(x+40,y+20),formula,29,520,BLUE,gap=14)
        y+=fh
    tip=scene.get('tip') or {1:'Նախ՝ բարակ օժանդակ գծեր։ Հետո՝ ստացված հոդերը և հիմնական օղակները։',2:'Գիծը տեղափոխում ենք նույն դիրքի մեխանիզմից։ Մյուս դիրքի ուղղությունը մի՛ պատճենիր։',3:'Նորմալ բաղադրիչը դեպի կենտրոն է, շոշափողը՝ շառավղին ուղղահայաց։',4:'Օրդինատները վերցնում ենք իրենց նշաններով։ Աշխատանքը կուտակվում է։',5:'Նույն դիրքի արժեքներն են կապում երկու գրաֆիկները։'}[chapter]
    if y<650:block(d,(x+28,690),tip,25,550,MUTED,gap=10)
    txt(d,(48,866),'ԳԾԻ ԱՂԲՅՈՒՐԸ → ԿԱՌՈՒՑՈՒՄԸ → ԱՐԴՅՈՒՆՔԻ ՍՏՈՒԳՈՒՄԸ',22,MUTED,True)
    d.rectangle((0,910,W,H),fill=INK)
    d.rectangle((0,910,int(W*global_progress),916),fill='#5bafff')
    txt(d,(45,1030),'ՄՄՏ · Առաջադրանք 2 · Տարբերակ 1',21,'#9eb4d4')
    txt(d,(1870,1030),'Դադարեցրու և փորձիր թղթի վրա',21,'#9eb4d4',anchor='ra')
    return im
