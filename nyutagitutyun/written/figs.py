# The sketches used by the written answers, keyed by name.
from math import sin, pi
from sketch import Plot, raw, fig, cube


def tensile():
    p = Plot((0, 1), (0, 1.05), 'ε, %', 'σ')
    pts = [(0, 0), (0.14, 0.6), (0.16, 0.57), (0.18, 0.59), (0.2, 0.56), (0.22, 0.585), (0.26, 0.575)]
    pts += [(0.26 + 0.5 * i / 20, 0.575 + 0.375 * (1 - (1 - i / 20) ** 2)) for i in range(1, 21)]
    pts += [(0.76 + 0.2 * i / 10, 0.95 - 0.15 * (i / 10) ** 1.6) for i in range(1, 11)]
    p.line(pts).pt(0.14, 0.6, 'σ<tspan class="sub">տ</tspan>', -34, -2).pt(0.76, 0.95, 'σ<tspan class="sub">բ</tspan>', -6, -7).pt(0.96, 0.8, 'խզում', 4, -6)
    p.line([(0.04, 0), (0.04, 0.05)], 'dash').text(0.05, 0.08, 'α', 2, 0)
    p.text(0.3, 0.45, 'Հուկի օրենք՝ σ = E·ε', 0, 0, cls='sm')
    return fig(p.svg(), 'Ձգման դիագրամ. ուղղագիծ մաս (Հուկ, E = tg α), հոսունության հարթակ (σ<sub>տ</sub>), առավելագույն լարում (σ<sub>բ</sub>), վզիկ և խզում։')


def cooling():
    p = Plot((0, 1), (0, 1), 'τ (ժամանակ)', 'T')
    p.line([(0.02, 0.95), (0.25, 0.6), (0.6, 0.6), (0.95, 0.15)]).text(0.32, 0.6, 'հարթակ T<tspan class="sub">կ</tspan>', 0, -6, cls='sm')
    p.fn(lambda t: 0.9 * (1 - t) ** 1.6 + 0.05, 0.02, 0.98, 'cv2').text(0.6, 0.14, 'ամորֆ', 0, -4, cls='sm').text(0.08, 0.92, 'մետաղ', 6, 2, cls='sm')
    return fig(p.svg(), 'Սառեցման կորեր. բյուրեղային մետաղը պնդանում է հաստատուն T<sub>կ</sub>-ում (հարթակ), ամորֆը՝ աստիճանաբար։')


def cells():
    corners = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    bcc = corners + [(.5, .5, .5)]
    fcc = corners + [(.5, .5, 0), (.5, .5, 1), (.5, 0, .5), (.5, 1, .5), (0, .5, .5), (1, .5, .5)]
    return fig(raw(cube(30, 120, 70, bcc, 'К8 (ԾԿԽ)') + cube(150, 120, 70, fcc, 'К12 (ՆԿԽ)'), 260, 160),
               'Տարրական բջիջներ. К8՝ 8 գագաթ + 1 կենտրոնում, К12՝ 8 գագաթ + 6 նիստի կենտրոններում։')


def _grid(n=7, m=5, s=24, ox=30, oy=30, skip=(), extra=(), big=(), r=6):
    b = ''
    for j in range(m):
        for i in range(n):
            x, y = ox + i * s, oy + j * s
            if (i, j) in skip:
                b += f'<circle cx="{x}" cy="{y}" r="{r}" class="hole"/>'
            elif (i, j) in big:
                b += f'<circle cx="{x}" cy="{y}" r="{r+3}" class="atom2"/>'
            else:
                b += f'<circle cx="{x}" cy="{y}" r="{r}" class="atom"/>'
    for (i, j) in extra:
        b += f'<circle cx="{ox + i * s}" cy="{oy + j * s}" r="3.4" class="atom3"/>'
    return b


def point_defects():
    b = _grid(skip=[(1, 1)], extra=[(3.5, 2.5)], big=[(5, 3)])
    b += '<text x="54" y="150" text-anchor="middle" class="sm">վականսիա</text><text x="114" y="164" text-anchor="middle" class="sm">միջհանգուցային ատոմ</text><text x="180" y="150" text-anchor="middle" class="sm">խառնուկ</text>'
    return fig(raw(b, 220, 170), 'Կետային թերություններ. վականսիա (դատարկ հանգույց), միջհանգուցային ատոմ, խառնուկի ատոմ։')


def dislocation():
    b, s = '', 20
    for j in range(6):
        y = 20 + j * s
        if j < 3:
            xs = [20 + i * s * 0.9 for i in range(10)]
        else:
            xs = [20 + i * s for i in range(9)]
        b += ''.join(f'<circle cx="{x:.1f}" cy="{y}" r="5.5" class="atom{"2" if (j < 3 and i == 5) else ""}"/>' for i, x in enumerate(xs))
    b += '<path d="M110,64 V76 M100,76 H120" class="mark"/><text x="196" y="40" class="sm">ավելորդ</text><text x="196" y="54" class="sm">կիսահարթություն</text><path d="M194,46 L120,40" class="dash"/>'
    return fig(raw(b, 260, 135), 'Եզրային դիսլոկացիա. վերին մասում կա ավելորդ կիսահարթություն, դրա եզրը նշվում է ⊥։')


def strength_vs_disl():
    p = Plot((0, 1), (0, 1), 'դիսլոկացիաների խտություն', 'ամրություն')
    p.fn(lambda x: 0.9 * (1 - x / 0.18) ** 2 + 0.12 if x < 0.18 else 0.12 + 0.8 * ((x - 0.18) / 0.82) ** 1.3, 0.02, 0.98)
    p.text(0.08, 0.9, 'առանց թերությունների', 6, 4, cls='sm').text(0.2, 0.1, 'մաքուր թրծված մետաղ', 0, -6, cls='sm').text(0.98, 0.95, 'կոփված', -2, 14, 'end', 'sm')
    return fig(p.svg(), 'Ամրության կախումը թերությունների խտությունից (Օդինգի կոր). նվազագույնը իրական թրծված մետաղի համար է։')


def free_energy():
    p = Plot((0, 1), (0, 1), 'T', 'F')
    p.line([(0.05, 0.85), (0.95, 0.2)]).line([(0.05, 0.95), (0.95, 0.05)], 'cv2')
    p.text(0.95, 0.2, 'F<tspan class="sub">պ</tspan>', -6, -6, 'end').text(0.95, 0.05, 'F<tspan class="sub">հ</tspan>', -4, -6, 'end')
    xs = 0.41
    p.line([(xs, 0), (xs, 0.6)], 'dash').xtick(xs, 'T<tspan class="sub">ս</tspan>').line([(0.25, 0), (0.25, 0.71)], 'dash').xtick(0.25, 'T<tspan class="sub">կ</tspan>')
    p.text(0.33, 0.12, 'ΔT', 0, 0, 'middle', 'sm')
    return fig(p.svg(), 'Հեղուկի և պինդի ազատ էներգիաները. հատվում են T<sub>ս</sub>-ում. բյուրեղացումը սկսվում է գերսառեցված T<sub>կ</sub>-ում, ΔT = T<sub>ս</sub> − T<sub>կ</sub>։')


def ingot():
    b = '<rect x="60" y="20" width="140" height="150" class="mold"/>'
    b += '<rect x="66" y="26" width="128" height="138" class="wall"/>'
    for y in range(32, 160, 7):
        b += f'<path d="M68,{y} h18 M174,{y} h18" class="thin"/>'
    for x in range(90, 172, 7):
        b += f'<path d="M{x},150 v12" class="thin"/>'
    import random
    rnd = random.Random(3)
    for _ in range(26):
        x, y = rnd.uniform(96, 164), rnd.uniform(44, 142)
        b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(4,7):.1f}" class="wall"/>'
    b += '<path d="M112,26 L130,58 L148,26" class="cavity"/>'
    b += '<text x="206" y="36" class="sm">կծկման խոռոչ</text><path d="M204,32 L136,40" class="dash"/>'
    b += '<text x="206" y="80" class="sm">1 մանրահատիկ կեղև</text><path d="M204,76 L194,76" class="dash"/>'
    b += '<text x="206" y="100" class="sm">2 սյունաձև բյուրեղներ</text><path d="M204,96 L184,96" class="dash"/>'
    b += '<text x="206" y="120" class="sm">3 հավասարառանցք</text><path d="M204,116 L160,116" class="dash"/>'
    return fig(raw(b, 330, 180), 'Պողպատե ձույլի կառուցվածքը (Չեռնով). երեք գոտի և կծկման խոռոչ։')


def stress_parts():
    b = '<path d="M40,130 L200,50" class="wall"/><text x="206" y="50" class="sm">սահքի հարթություն</text>'
    b += '<path d="M120,90 L120,20" class="arr"/><path d="M120,16 l-3,8 h6 z" class="axh"/><text x="126" y="24">S</text>'
    b += '<path d="M120,90 L150,30" class="arr2"/><text x="154" y="32">σ</text>'
    b += '<path d="M120,90 L168,114" class="arr2"/><text x="170" y="122">τ</text>'
    return fig(raw(b, 280, 150), 'Լարման բաժանումը նորմալ σ (ուղղահայաց հարթությանը) և շոշափող τ (հարթության երկայնքով) բաղադրիչների։')


def slip():
    b = ''
    for k, dx in enumerate((0, 22)):
        ox = 20 + k * 130
        b += f'<rect x="{ox}" y="70" width="90" height="40" class="wall"/><rect x="{ox+dx}" y="30" width="90" height="40" class="wall"/>'
    b += '<path d="M118,70 h26" class="arr"/><path d="M148,70 l-7,-3 v6 z" class="axh"/><text x="20" y="130" class="sm">մինչև դեֆորմացիան</text><text x="150" y="130" class="sm">սահքից հետո (աստիճան)</text>'
    b += '<path d="M220,48 h26" class="arr"/><path d="M250,48 l-7,-3 v6 z" class="axh"/><text x="226" y="42">τ</text>'
    return fig(raw(b, 270, 140), 'Պլաստիկ դեֆորմացիա սահքով. բյուրեղի մի մասը τ-ի ազդեցությամբ տեղաշարժվում է մյուսի նկատմամբ։')


def coldwork():
    p = Plot((0, 1), (0, 1), 'դեֆորմացիայի աստիճան, %', '')
    p.fn(lambda x: 0.3 + 0.6 * x ** 0.6, 0, 1).fn(lambda x: 0.85 - 0.75 * x ** 0.6, 0, 1, 'cv2')
    p.text(1, 0.9, 'σ<tspan class="sub">բ</tspan>, HB', -4, -6, 'end').text(1, 0.1, 'δ, ψ', -4, -6, 'end')
    return fig(p.svg(), 'Կոփում. դեֆորմացիայի աճով ամրությունն ու կարծրությունն աճում են, պլաստիկությունը նվազում է։')


def recryst():
    p = Plot((0, 1), (0, 1), 'տաքացման T', '')
    sig = lambda x: 0.85 - 0.04 * x if x < 0.4 else (0.85 - 0.016 - 0.5 * (1 - (1 - (x - 0.4) / 0.2) ** 2) if x < 0.6 else 0.33 - 0.05 * (x - 0.6))
    dl = lambda x: 0.15 + 0.03 * x if x < 0.4 else (0.162 + 0.5 * (1 - (1 - (x - 0.4) / 0.2) ** 2) if x < 0.6 else 0.66 - 0.1 * (x - 0.6))
    p.fn(sig, 0, 1).fn(dl, 0, 1, 'cv2').line([(0.4, 0), (0.4, 1)], 'dash').line([(0.6, 0), (0.6, 1)], 'dash')
    p.text(0.02, 0.85, 'σ<tspan class="sub">բ</tspan>, HB', 2, -6).text(0.02, 0.15, 'δ', 2, -6).xtick(0.4, 'T<tspan class="sub">վ</tspan>')
    p.text(0.2, 1, 'վերադարձ', 0, 8, 'middle', 'sm').text(0.5, 1, 'վերաբյուր.', 0, 8, 'middle', 'sm').text(0.8, 1, 'հատիկի աճ', 0, 8, 'middle', 'sm')
    return fig(p.svg(), 'Կոփված մետաղի տաքացում. T<sub>վ</sub>-ից բարձր կարծրությունը կտրուկ նվազում է, պլաստիկությունը վերականգնվում է։')


def solutions():
    b = _grid(5, 5, 22, 20, 20, big=[(1, 1), (3, 2), (2, 4)]) + '<text x="64" y="138" text-anchor="middle" class="sm">տեղակալման</text>'
    b += _grid(5, 5, 22, 150, 20, extra=[(0.5, 0.5), (2.5, 1.5), (1.5, 3.5), (3.5, 2.5)]) + '<text x="194" y="138" text-anchor="middle" class="sm">ներդրման</text>'
    return fig(raw(b, 260, 148), 'Պինդ լուծույթներ. տեղակալման՝ B-ի ատոմները փոխարինում են A-ին հանգույցներում, ներդրման՝ փոքր ատոմները միջհանգույցներում։')


def _cuni():
    liq = lambda x: 1083 + 3.69 * x + 60 * sin(pi * x / 100)
    sol = lambda x: 1083 + 3.69 * x - 60 * sin(pi * x / 100)
    def inv(f, T):
        a, b = 0, 100
        for _ in range(60):
            m = (a + b) / 2
            a, b = (m, b) if f(m) < T else (a, m)
        return a
    return liq, sol, inv


def cuni(lever=False):
    liq, sol, inv = _cuni()
    p = Plot((0, 100), (1000, 1520), 'Ni, %', 'T, °C', w=270, x1=246)
    p.fn(liq, 0, 100).fn(sol, 0, 100, 'cv2')
    p.text(20, liq(20), 'լիկվիդուս', -2, -8, 'end', 'sm').text(70, sol(70), 'սոլիդուս', 4, 14, 'start', 'sm')
    p.text(35, 1470, 'Հ', 0, 0, 'middle').text(55, sol(55) + 25, 'Հ + α', 0, 4, 'middle', 'sm').text(60, 1080, 'α', 0, 0, 'middle')
    p.ytick(1083, '1083').ytick(1452, '1452').xtick(100, '100')
    if lever:
        T = 1290
        xl, xs = inv(liq, T), inv(sol, T)
        p.line([(xl, T), (xs, T)], 'tie').pt(xl, T).pt(xs, T).pt(40, T)
        for x, s in ((xl, 'x<tspan class="sub">հ</tspan>'), (40, 'x'), (xs, 'x<tspan class="sub">պ</tspan>')):
            p.line([(x, 1000), (x, T)], 'dash').xtick(x, s)
    cap = ('Կոնոդ (հորիզոնական) համաձուլվածքի կետով. ծայրերը տալիս են հեղուկի (x<sub>հ</sub>) և պինդի (x<sub>պ</sub>) բաղադրությունը։'
           if lever else 'Cu–Ni դիագրամ (անսահմանափակ լուծելիություն). լիկվիդուսից վեր՝ հեղուկ, սոլիդուսից ներքև՝ α պինդ լուծույթ։')
    return fig(p.svg(), cap)


def eutectic():
    p = Plot((0, 100), (0, 1), 'B, %', 'T', w=270, x1=246)
    E, Te = (40, 0.4), 0.4
    p.line([(0, 0.85), E, (100, 0.75)]).line([(0, 0.85), (12, Te)], 'cv2').line([(100, 0.75), (86, Te)], 'cv2')
    p.line([(12, Te), (86, Te)], 'cv2').line([(12, Te), (6, 0.05)], 'cv2').line([(86, Te), (93, 0.05)], 'cv2')
    p.pt(*E, 'E', -3, 14).text(40, 0.85, 'Հ', 0, 0, 'middle').text(17, 0.55, 'Հ+α', 0, 0, 'middle', 'sm').text(72, 0.55, 'Հ+β', 0, 0, 'middle', 'sm')
    p.text(4, 0.25, 'α', 0, 0, 'middle').text(97, 0.25, 'β', 0, 0, 'middle').text(28, 0.22, 'α+(α+β)', 0, 0, 'middle', 'sm').text(64, 0.22, 'β+(α+β)', 0, 0, 'middle', 'sm')
    p.xtick(40, '')
    return fig(p.svg(), 'Էվտեկտիկայով դիագրամ (սահմանափակ լուծելիություն). E կետում Հ → α + β հաստատուն ջերմաստիճանում։')


def kurnakov():
    b = ''
    shapes = [('մեխ. խառնուրդ', lambda x: 0.2 + 0.5 * x),
              ('անսահմ. պինդ լուծ.', lambda x: 0.2 + 0.4 * x + 0.9 * x * (1 - x)),
              ('սահմ. պինդ լուծ.', lambda x: 0.2 + 1.6 * x if x < 0.2 else (0.52 + 0.1 * (x - 0.2) / 0.6 if x < 0.8 else 0.62 + 0.9 * (x - 0.8))),
              ('քիմ. միացություն', lambda x: 0.2 + 1.2 * x if x < 0.5 else 0.8 - 0.8 * (x - 0.5))]
    for k, (lab, f) in enumerate(shapes):
        ox, oy, w, h = 14 + (k % 2) * 130, 14 + (k // 2) * 86, 104, 56
        b += f'<path d="M{ox},{oy} V{oy+h} H{ox+w}" class="ax"/>'
        b += '<path d="' + ' '.join(('M' if i == 0 else 'L') + f'{ox + w * i / 40:.1f},{oy + h - h * f(i / 40):.1f}' for i in range(41)) + '" class="cv"/>'
        b += f'<text x="{ox + w/2}" y="{oy+h+14}" text-anchor="middle" class="sm">{lab}</text>'
    return fig(raw(b, 260, 180), 'Կուռնակով. հատկության (օր․ կարծրության) կախումը բաղադրությունից՝ ըստ դիագրամի տեսակի։')


def fe_c():
    p = Plot((0, 6.67), (600, 1600), 'C, %', 'T, °C', w=330, h=240, x1=306, y0=208, y1=16)
    A, B, C, D = (0, 1539), (0.51, 1493), (4.3, 1147), (6.67, 1550)
    E, F, G, H, J, N = (2.14, 1147), (6.67, 1147), (0, 910), (0.1, 1493), (0.16, 1493), (0, 1401)
    P, S, K, Q = (0.02, 727), (0.8, 727), (6.67, 727), (0.006, 600)
    p.line([A, B, C, D]).line([A, H, B], 'cv2').line([J, E], 'cv2').line([E, F], 'cv2').line([N, H], 'thinc').line([N, J], 'thinc')
    p.line([G, S], 'thinc').line([G, P], 'thinc').line([P, Q], 'thinc').line([(2.14 - 1.34 * i / 10, 1147 - 420 * (i / 10) ** 0.8) for i in range(11)], 'thinc').line([P, K], 'cv2')
    for pt, lab, dx, dy in ((A, 'A', 4, -4), (B, 'B', 3, -5), (C, 'C', -3, -6), (D, 'D', -12, -4), (E, 'E', -10, -5), (F, 'F', -10, -5),
                            (G, 'G', 4, 3), (N, 'N', 4, 4), (P, 'P', 3, 12), (S, 'S', -2, -6), (K, 'K', -12, -5), (J, 'J', 3, 12)):
        p.pt(*pt, lab, dx, dy)
    for t in (1539, 1147, 910, 727):
        p.ytick(t, str(t))
    for x in (0.8, 2.14, 4.3):
        p.xtick(x, str(x).replace('.', ','))
    for x, y, s in ((3, 1420, 'Հ'), (1.3, 1330, 'Հ+Ա'), (5.4, 1270, 'Հ+ՑI'), (0.85, 1020, 'Ա'), (1.75, 900, 'Ա+ՑII'),
                    (3.3, 960, 'Ա+ՑII+Լ'), (5.5, 960, 'Լ+ՑI'), (0.33, 640, 'Ֆ+Պ'), (1.5, 640, 'Պ+ՑII'), (3.3, 640, 'Պ+ՑII+Լ′'), (5.5, 640, 'Լ′+ՑI'), (0.28, 840, 'Ֆ+Ա')):
        p.text(x, y, s, 0, 0, 'middle', 'sm')
    return fig(p.svg().replace('class="sk-svg"', 'class="sk-svg wide"'), 'Fe–Fe₃C դիագրամ. ABCD լիկվիդուս, AHJECF սոլիդուս, ECF էվտեկտիկա (1147°C), PSK էվտեկտոիդ (727°C), GS (A₃), SE (A<sub>cm</sub>)։')


def iron_cooling():
    p = Plot((0, 1), (500, 1650), 'τ', 'T, °C')
    pts = [(0, 1620), (0.1, 1539), (0.2, 1539), (0.3, 1401), (0.38, 1401), (0.5, 910), (0.58, 910), (0.66, 769), (0.72, 769), (0.85, 560)]
    p.line(pts)
    for t, s in ((1539, '1539 հալում'), (1401, '1401 Fe<tspan class="sub">δ</tspan>→Fe<tspan class="sub">γ</tspan>'), (910, '910 Fe<tspan class="sub">γ</tspan>→Fe<tspan class="sub">α</tspan>'), (769, '769 Կյուրի')):
        p.ytick(t, '').text(0.86, t, s, 0, 4, 'end', 'sm')
    return fig(p.svg(), 'Մաքուր երկաթի սառեցման կորը. հարթակներ 1539, 1401, 910 և 769°C-ում (769-ը՝ մագնիսական փոխակերպում)։')


def steel_c():
    p = Plot((0, 1.4), (0, 1), 'C, %', '')
    p.fn(lambda x: 0.15 + 0.55 * x, 0, 1.4).fn(lambda x: 0.25 + 0.7 * (x / 0.95) - 0.35 * (x / 0.95) ** 2 if x < 0.95 else 0.6 - 0.3 * (x - 0.95), 0, 1.4, 'cv3')
    p.fn(lambda x: 0.85 * 2.7 ** (-1.8 * x) + 0.03, 0, 1.4, 'cv2')
    p.text(1.4, 0.92, 'HB', -4, -2, 'end').text(1.05, 0.6, 'σ<tspan class="sub">բ</tspan>', 0, -8).text(0.25, 0.55, 'δ, a<tspan class="sub">Н</tspan>', 6, 0).xtick(0.8, '0,8')
    return fig(p.svg(), 'Ածխածնի ազդեցությունը. HB-ն աճում է, σ<sub>բ</sub>-ն աճում է մինչև ≈0,9% C, ապա նվազում (ցեմենտիտի ցանց), δ-ն և a<sub>Н</sub>-ն նվազում են։')


def _disc(cx, cy, r, body, cid):
    return (f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
            f'<g clip-path="url(#{cid})">{body}</g><circle cx="{cx}" cy="{cy}" r="{r}" class="wall"/>')


def graphite():
    import random
    rnd = random.Random(7)
    flakes = ''.join(f'<path d="M{x:.0f},{y:.0f} q{rnd.uniform(-6,6):.0f},{rnd.uniform(-8,8):.0f} {rnd.uniform(10,20):.0f},{rnd.uniform(-6,6):.0f}" class="gr"/>'
                     for x, y in [(rnd.uniform(14, 70), rnd.uniform(22, 92)) for _ in range(16)])
    balls = ''.join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(3,5):.1f}" class="grf"/>' for x, y in [(rnd.uniform(100, 164), rnd.uniform(24, 90)) for _ in range(12)])
    flk = ''
    for x, y in [(rnd.uniform(194, 256), rnd.uniform(26, 88)) for _ in range(8)]:
        flk += ''.join(f'<circle cx="{x + rnd.uniform(-4,4):.0f}" cy="{y + rnd.uniform(-4,4):.0f}" r="{rnd.uniform(1.6,3):.1f}" class="grf"/>' for _ in range(6))
    b = _disc(42, 57, 36, flakes, 'g1') + _disc(132, 57, 36, balls, 'g2') + _disc(225, 57, 36, flk, 'g3')
    for x, a, c in ((42, 'գորշ', 'թերթավոր'), (132, 'բարձրամուր', 'գնդաձև'), (225, 'կռելի', 'փաթիլաձև')):
        b += f'<text x="{x}" y="108" text-anchor="middle" class="sm">{a}</text><text x="{x}" y="120" text-anchor="middle" class="sm">{c}</text>'
    return fig(raw(b, 270, 126), 'Գրաֆիտի ձևերը չուգուններում (երևում են առանց խածատման)։')


def _cells(cx, cy, r, hatch, cid, net=False):
    b = ''
    s = 16
    k = 0
    for j in range(-3, 4):
        for i in range(-3, 4):
            x, y = cx + i * s + (j % 2) * s / 2, cy + j * s * 0.87
            pts = ' '.join(f'{x + 9.2 * c:.1f},{y + 9.2 * d:.1f}' for c, d in ((0, -1), (.87, -.5), (.87, .5), (0, 1), (-.87, .5), (-.87, -.5)))
            cls = 'hatch' if hatch(k) else 'cell'
            b += f'<polygon points="{pts}" class="{cls}{" net" if net else ""}"/>'
            k += 1
    return _disc(cx, cy, r, b, cid)


def micro_steel():
    b = _cells(42, 52, 36, lambda k: k % 2 == 0, 'm1') + _cells(132, 52, 36, lambda k: True, 'm2') + _cells(222, 52, 36, lambda k: True, 'm3', True)
    for x, a, c in ((42, 'Ֆ + Պ', '≈0,4% C'), (132, 'Պ', '0,8% C'), (222, 'Պ + ՑII', '1,2% C')):
        b += f'<text x="{x}" y="104" text-anchor="middle" class="sm">{a}</text><text x="{x}" y="116" text-anchor="middle" class="sm">{c}</text>'
    return fig(raw(b, 270, 122), 'Պողպատների միկրոկառուցվածք. ֆերիտը՝ բաց, պեռլիտը՝ մուգ (գծավոր), երկրորդային ցեմենտիտը՝ բաց ցանց հատիկների շուրջ։')


def brinell():
    b = '<path d="M20,90 H120 M150,90 H250" class="wall"/>'
    b += '<circle cx="70" cy="66" r="28" class="wall"/><path d="M52,90 Q70,102 88,90" class="cavity"/><path d="M70,8 V34" class="arr"/><path d="M70,38 l-3,-7 h6 z" class="axh"/><text x="76" y="20">P</text>'
    b += '<path d="M42,66 H98" class="dash"/><text x="70" y="62" text-anchor="middle" class="sm">D</text><path d="M52,108 H88" class="dim"/><text x="70" y="122" text-anchor="middle" class="sm">d</text>'
    b += '<path d="M200,90 L186,62 L214,62 Z" class="wall"/><path d="M186,62 V40 H214 V62" class="wall"/><text x="200" y="104" text-anchor="middle" class="sm">h (խորություն)</text><text x="224" y="70" class="sm">120°</text>'
    b += '<text x="70" y="140" text-anchor="middle">Բրինել</text><text x="200" y="140" text-anchor="middle">Ռոկվել</text>'
    return fig(raw(b, 270, 150), 'Բրինել՝ D տրամագծով գնդիկ, չափում են դրոշմահետքի d-ն. Ռոկվել՝ 120° ալմաստե կոն, չափում են խրման h խորությունը։')


def chain():
    b = ''
    for k, s in enumerate(('բաղադրություն', 'տեխնոլոգիա', 'մշակում')):
        b += f'<rect x="6" y="{12 + k*40}" width="96" height="28" rx="6" class="wall"/><text x="54" y="{30 + k*40}" text-anchor="middle" class="sm">{s}</text><path d="M104,{26 + k*40} L134,66" class="arr"/>'
    b += '<rect x="136" y="52" width="82" height="28" rx="6" class="wall2"/><text x="177" y="70" text-anchor="middle" class="sm">ստրուկտուրա</text>'
    b += '<path d="M220,66 H236" class="arr"/><path d="M240,66 l-7,-3 v6 z" class="axh"/><text x="244" y="70" class="sm">հատկություններ</text>'
    return fig(raw(b, 330, 135), 'Նյութագիտության հիմնական կապը. բաղադրությունը, տեխնոլոգիան և մշակումը որոշում են ստրուկտուրան, իսկ ստրուկտուրան՝ հատկությունները։')


def impact():
    b = '<circle cx="130" cy="20" r="3" class="pt"/><path d="M130,20 L70,90" class="wall"/><circle cx="70" cy="90" r="10" class="atom"/>'
    b += '<path d="M130,20 L130,120" class="dash"/><path d="M130,20 L196,84" class="dash"/><circle cx="196" cy="84" r="10" class="hole"/>'
    b += '<rect x="122" y="118" width="16" height="10" class="wall2"/><text x="146" y="130" class="sm">նմուշ (կտրվածքով)</text>'
    b += '<path d="M40,90 H60 M40,48 H60" class="dim"/><text x="18" y="74" class="sm">h₁</text><path d="M206,84 H236" class="dim"/><text x="238" y="70" class="sm">h₂</text>'
    return fig(raw(b, 270, 140), 'Ճոճանակավոր կոպր. ճոճանակը h₁ բարձրությունից կոտրում է նմուշը և բարձրանում h₂. A = G(h₁ − h₂)։')


def malleable():
    p = Plot((0, 1), (0, 1100), 'τ, ժ', 'T, °C')
    p.line([(0, 20), (0.12, 950), (0.42, 950), (0.5, 760), (0.58, 720), (0.88, 720), (0.98, 300)])
    p.ytick(950, '950').ytick(720, '720').text(0.27, 950, 'I փուլ', 0, -6, 'middle', 'sm').text(0.73, 720, 'II փուլ', 0, -6, 'middle', 'sm')
    return fig(p.svg(), 'Կռելի չուգունի թրծաթողում. սպիտակ չուգունը երկար պահում են 900–1000°C-ում (I), ապա 720–760°C-ում (II)՝ ֆերիտային հիմքի համար։')


FIG = {k: v() if k not in ('cuni', 'lever') else None for k, v in {
    'tensile': tensile, 'cooling': cooling, 'cells': cells, 'point': point_defects, 'disl': dislocation, 'oding': strength_vs_disl,
    'free': free_energy, 'ingot': ingot, 'stress': stress_parts, 'slip': slip, 'coldwork': coldwork, 'recryst': recryst,
    'solutions': solutions, 'eutectic': eutectic, 'kurnakov': kurnakov, 'fec': fe_c, 'fecool': iron_cooling,
    'steelc': steel_c, 'graphite': graphite, 'microsteel': micro_steel, 'brinell': brinell, 'chain': chain,
    'impact': impact, 'malleable': malleable, 'cuni': None, 'lever': None}.items()}
FIG['cuni'], FIG['lever'] = cuni(), cuni(True)
