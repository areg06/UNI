"""A clean one-page sketch for discussing the reducer layout with the lecturer.

Run from anywhere: python3 'meqenamaseri tesutyun/source/eskiz_review.py'
Reads the same geometry as harmanadasum.py. After a model change, rebuild both.
This review sheet has a conditional scale; dimension labels remain actual mm.
"""
import math
import harmanadasum as L

NAME = 'eskiz_review'
PAGE = (297,210)
SHRINK = .66
TITLE = 'Ռեդուկտորի էսքիզ · դասախոսի հետ քննարկելու համար'


def position(p):
    return (.12+SHRINK*p[0],43+SHRINK*(p[1]-29))


def sketch():
    base=L.build_drawing();L.verify_geometry(base)
    dr=L.Drawing()
    layers={'housing','shafts','gears','supports','axes','dimensions'}
    labels={'I · Մուտք','III · Ելք','II','I · շեղատամ','II · ուղղատամ'}
    labels.update(bearing['code'] for bearing in L.BEARINGS.values())
    for layer,kind,args in base.items:
        if layer not in layers and not (layer=='labels' and
                (kind=='poly' or kind=='text' and args[2] in labels)):
            continue
        dr.layer=layer
        if kind=='line':
            a,b,color,width,dash=args
            dr.line(position(a),position(b),color,max(.12,width*SHRINK),
                    tuple(v*SHRINK for v in dash))
        elif kind=='rect':
            x,y,w,h,color,width,fill,dash=args
            x,y=position((x,y))
            dr.rect(x,y,w*SHRINK,h*SHRINK,color,max(.12,width*SHRINK),fill,
                    tuple(v*SHRINK for v in dash))
        elif kind=='poly':
            points,color,width,fill,closed=args
            dr.poly([position(p) for p in points],color,max(.12,width*SHRINK),fill,closed)
        else:
            x,y,text,size,color,anchor,rotate,mask=args
            x,y=position((x,y))
            dr.text(x,y,text,max(2.6,size*SHRINK),color,anchor,rotate,mask)

    dr.layer='review'
    dr.text(148.5,201,'ՌԵԴՈՒԿՏՈՐԻ ԷՍՔԻԶ',size=5.)
    dr.text(148.5,194,'Քննարկման համար · տարբերակ 1 · չափերը՝ իրական մմ-ով · էսքիզը՝ պայմանական մասշտաբով',size=2.65)
    dr.line((10,190),(287,190),'#AAB2B4',.2)
    dr.line((208,43),(208,186),'#AAB2B4',.2)
    notes=[
        (184,'Հիմնական տվյալներ',3.3),
        (177,'n₁ = 7950 · n₃ ≈ 490 պտ/ր',2.65),
        (172,'Հաշվարկային հզորություն՝ 12,88 կՎտ',2.4),
        (167,'I աստիճան · շեղատամ',3.),
        (160,'z₁ / z₂ = 37 / 156 · m<sub>n</sub> = 2',2.6),
        (154,'d₁ / d₂ = 76,68 / 323,32',2.6),
        (148,'b₁ / b₂ = 85 / 80 · β = 15,20°',2.6),
        (138,'II աստիճան · ուղղատամ',3.),
        (131,'z₁ / z₂ = 33 / 127 · m = 2,5',2.6),
        (125,'d₁ / d₂ = 82,5 / 317,5',2.6),
        (119,'b₁ / b₂ = 55 / 50',2.6),
        (107,'Առանցքակալներ · միջին սերիա',2.8),
        (100,'1՝ 36306 · 2՝ 36307 · 3՝ 308',2.6),
        (93,'1 և 2՝ շառավղա-հենարանային',2.45),
        (87,'3՝ շառավղային',2.45),
        (81,'Լիսեռների d = 25 / 30 / 35',2.4),
        (74,'Նախնական ընդունումներ',2.9),
        (67,'α₁ = α₂ = 12°',2.7),
        (60,'Հենարանների առանցքային դիրքերը',2.45),
        (54,'և ներքին հենարանների հանգույցը',2.45),
        (48,'պետք է ճշտել դասախոսի հետ։',2.45),
    ]
    for y,text,size in notes:
        dr.text(214,y,text,size=size,anchor='start')
    dr.line((10,37),(287,37),'#AAB2B4',.2)
    dr.text(12,30,'Կարելի՞ է այս դասավորությամբ սկսել A3 միլիմետրական թղթի վրա գծելը՝ M 1:2։',
            size=3.3,anchor='start')
    dr.text(12,22,'Խնդրում եմ ճշտել նաև ներքին հենարանների հանգույցը, առանցքային դիրքերը և 12° կոնտակտի անկյունը։',
            size=2.75,anchor='start')
    dr.text(12,11,'Դիտողություններ՝',size=2.8,anchor='start')
    dr.line((41,10),(287,10),'#AAB2B4',.15)
    return dr


def main():
    L.find_font();dr=sketch()
    # Check that the review retains the copybook's orientation.
    assert position((L.X1,0))[0]>position((L.X2,0))[0]
    for _,kind,args in dr.items:
        if kind=='text':
            x,y,text,size,_,anchor,rotate,_=args
            w=L.text_width(text,size)
            start={'start':0,'middle':-w/2,'end':-w}[anchor]
            a=math.radians(rotate)
            box=[(x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a))
                 for u in [start,start+w] for v in [-size*.62,size*.62]]
            assert all(6<=px<=291 and 6<=py<=205 for px,py in box),(text,box)
    svg=L.make_svg(dr,page_size=PAGE,grid_origin=(0,0),grid_height=210,
        title=TITLE,description='Քննարկման էսքիզ. մուտքն ու ելքն աջում են, միջանկյալ լիսեռը՝ ձախում։ Չափերը նշված են իրական միլիմետրերով։')
    (L.OUT/f'{NAME}.svg').write_text('<?xml version="1.0" encoding="utf-8"?>\n'+svg)
    L.make_pdf(dr,name=NAME,page_size=PAGE,grid_origin=(0,0),grid_height=210,title=TITLE)
    for ext in ['pdf','png','svg']:
        p=L.OUT/f'{NAME}.{ext}';print(p.relative_to(L.OUT.parent),p.stat().st_size,'bytes')


if __name__=='__main__':
    main()
