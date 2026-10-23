# Small inline-SVG sketches for the written answers ("draw this on the paper").
# Colors come from the page tokens (currentColor, --accent, --heat ...), so they work in both themes and in print.

W, H = 260, 180
X0, Y0, X1, Y1 = 38, 150, 244, 16


class Plot:
    """Axes with data ranges; add curves, points and labels in data coordinates."""
    def __init__(self, xr, yr, xl='', yl='', w=W, h=H, x0=X0, y0=Y0, x1=X1, y1=Y1, origin='0'):
        self.xr, self.yr, self.w, self.h = xr, yr, w, h
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.b = [f'<path d="M{x0},{y0} H{x1+8} M{x0},{y0} V{y1-8}" class="ax"/>',
                  f'<path d="M{x1+8},{y0} l-7,-3 v6 z M{x0},{y1-8} l-3,7 h6 z" class="axh"/>',
                  f'<text x="{x1+6}" y="{y0+15}" text-anchor="end">{xl}</text>',
                  f'<text x="{x0+6}" y="{y1-2}">{yl}</text>']
        if origin:
            self.b.append(f'<text x="{x0-4}" y="{y0+13}" text-anchor="end">{origin}</text>')

    def X(self, x): return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * (self.x1 - self.x0)
    def Y(self, y): return self.y0 - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * (self.y0 - self.y1)

    def d(self, pts):
        return ' '.join(('M' if i == 0 else 'L') + f'{self.X(x):.1f},{self.Y(y):.1f}' for i, (x, y) in enumerate(pts))

    def line(self, pts, cls='cv'):
        self.b.append(f'<path d="{self.d(pts)}" class="{cls}"/>'); return self

    def fn(self, f, a, b, cls='cv', n=60):
        return self.line([(a + (b - a) * i / n, f(a + (b - a) * i / n)) for i in range(n + 1)], cls)

    def area(self, pts, cls='area'):
        self.b.append(f'<path d="{self.d(pts)} Z" class="{cls}"/>'); return self

    def pt(self, x, y, lab='', dx=5, dy=-5, anchor='start'):
        self.b.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="2.6" class="pt"/>')
        if lab: self.text(x, y, lab, dx, dy, anchor)
        return self

    def text(self, x, y, s, dx=0, dy=0, anchor='start', cls=''):
        c = f' class="{cls}"' if cls else ''
        self.b.append(f'<text x="{self.X(x)+dx:.1f}" y="{self.Y(y)+dy:.1f}" text-anchor="{anchor}"{c}>{s}</text>'); return self

    def xtick(self, x, s):
        self.b.append(f'<path d="M{self.X(x):.1f},{self.y0} v4" class="ax"/><text x="{self.X(x):.1f}" y="{self.y0+14}" text-anchor="middle" class="sm">{s}</text>'); return self

    def ytick(self, y, s):
        self.b.append(f'<path d="M{self.x0},{self.Y(y):.1f} h-4" class="ax"/><text x="{self.x0-6}" y="{self.Y(y)+4:.1f}" text-anchor="end" class="sm">{s}</text>'); return self

    def svg(self):
        return f'<svg class="sk-svg" viewBox="0 0 {self.w} {self.h}" aria-hidden="true">{"".join(self.b)}</svg>'


def raw(body, w=W, h=H):
    return f'<svg class="sk-svg" viewBox="0 0 {w} {h}" aria-hidden="true">{body}</svg>'


def fig(svg, cap):
    return f'<figure class="sk">{svg}<figcaption>✏ {cap}</figcaption></figure>'


def cube(ox, oy, a, dots, label):
    """Oblique-projection cube with atoms at the given fractional (x, y, z) positions."""
    k = 0.45
    P = lambda x, y, z: (ox + a * x + a * k * z * 0.8, oy - a * y - a * k * z * 0.6)
    V = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    E = [(p, q) for i, p in enumerate(V) for q in V[i + 1:] if sum(abs(p[j] - q[j]) for j in range(3)) == 1]
    b = ''.join(f'<path d="M{P(*p)[0]:.1f},{P(*p)[1]:.1f} L{P(*q)[0]:.1f},{P(*q)[1]:.1f}" class="{"dash" if (p[2]==1 and q[2]==1 and p[0]==0 and q[0]==0) or (p==(0,0,1) or q==(0,0,1)) else "wall"}"/>' for p, q in E)
    for d in sorted(dots, key=lambda t: -t[2]):
        x, y = P(*d)
        b += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" class="atom"/>'
    b += f'<text x="{ox + a*0.6:.1f}" y="{oy + 22}" text-anchor="middle">{label}</text>'
    return b
