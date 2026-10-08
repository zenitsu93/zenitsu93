"""Illustrations sur mesure des projets, dans le langage du logo : traits gris clair, un seul point orange. Repère 400 × 220."""
import math
import random

CLAIR, ORANGE, ARC, BULLE = "#E8ECEF", "#E08A2C", "#16273A", "#1E3148"


def fangup():
    return (f'<rect x="44" y="34" width="176" height="42" rx="21" stroke="{CLAIR}" stroke-width="2.5"></rect>'
            f'<path d="M66 55 H190" stroke="{CLAIR}" stroke-width="2.5" stroke-opacity=".35"></path>'
            f'<rect x="176" y="92" width="180" height="42" rx="21" fill="{BULLE}"></rect>'
            f'<path d="M198 113 H332" stroke="{CLAIR}" stroke-width="2.5" stroke-opacity=".55"></path>'
            f'<rect x="44" y="150" width="128" height="42" rx="21" stroke="{CLAIR}" stroke-width="2.5"></rect>'
            f'<path d="M66 171 H148" stroke="{CLAIR}" stroke-width="2.5" stroke-opacity=".35"></path>'
            f'<path d="M190 171 C 290 171, 352 168, 352 146" stroke="{CLAIR}" stroke-width="2" stroke-opacity=".4" stroke-dasharray="2 7"></path>'
            f'<circle cx="352" cy="92" r="9" fill="{ORANGE}" stroke="none"></circle>')


def anomalies():
    rnd = random.Random(7)
    pts = []
    for i in range(46):
        x = 44 + i * 7
        y = 182 - i * 2.9 + rnd.uniform(-13, 13)
        pts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{CLAIR}" fill-opacity=".55" stroke="none"></circle>')
    return ("".join(pts) + f'<path d="M36 196 H372 M36 196 V24" stroke="{CLAIR}" stroke-width="1.5" stroke-opacity=".3"></path>'
            f'<circle cx="262" cy="168" r="17" stroke="{ORANGE}" stroke-width="2" stroke-opacity=".55"></circle>'
            f'<circle cx="262" cy="168" r="7" fill="{ORANGE}" stroke="none"></circle>')


def learny():
    out = []
    for k, (x, y) in enumerate(((150, 50), (138, 40), (126, 30))):
        op = (".25", ".45", "1")[k]
        out.append(f'<rect x="{x}" y="{y}" width="150" height="160" rx="10" fill="#0E1D2C" stroke="{CLAIR}" stroke-width="2.5" stroke-opacity="{op}"></rect>')
    for i, wl in enumerate((96, 110, 70, 104, 84, 100)):
        y = 62 + i * 21
        hi = i == 2
        out.append(f'<path d="M150 {y} H{150 + wl}" stroke="{CLAIR}" stroke-width="{3 if hi else 2.5}" stroke-opacity="{1 if hi else .35}"></path>')
    out.append(f'<circle cx="140" cy="104" r="5.5" fill="{ORANGE}" stroke="none"></circle>')
    return "".join(out)


def encore():
    out = [f'<circle cx="200" cy="110" r="{r}" stroke="{CLAIR}" stroke-width="{2.5 if r in (92, 34) else 1.5}" stroke-opacity="{op}"></circle>'
           for r, op in ((92, 1), (78, .35), (64, .35), (50, .35), (34, .8))]
    out.append(f'<circle cx="200" cy="110" r="14" fill="{ORANGE}" stroke="none"></circle>')
    out.append(f'<path d="M330 30 L318 46 L262 118" stroke="{CLAIR}" stroke-width="3"></path><circle cx="330" cy="30" r="6" stroke="{CLAIR}" stroke-width="2.5"></circle>')
    return "".join(out)


def monitoring():
    rnd = random.Random(3)
    xs = list(range(34, 300, 12))
    pts = [(x, 150 + rnd.uniform(-9, 9)) for x in xs] + [(312, 120), (326, 62), (340, 132), (356, 150), (370, 146)]
    line = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    return (f'<path d="M30 92 H376" stroke="{CLAIR}" stroke-width="1.5" stroke-opacity=".5" stroke-dasharray="5 7"></path>'
            f'<polyline points="{line}" stroke="{CLAIR}" stroke-width="2.5"></polyline>'
            f'<path d="M30 196 H376" stroke="{CLAIR}" stroke-width="1.5" stroke-opacity=".3"></path>'
            f'<circle cx="326" cy="62" r="8" fill="{ORANGE}" stroke="none"></circle>')


def elt():
    xs = (70, 160, 250, 340)
    out = [f'<path d="M88 110 H142 M178 110 H232 M268 110 H322" stroke="{CLAIR}" stroke-width="2.5" stroke-dasharray="3 7"></path>']
    for i, x in enumerate(xs):
        if i < 3:
            out.append(f'<circle cx="{x}" cy="110" r="18" stroke="{CLAIR}" stroke-width="2.5"></circle>')
        else:
            out.append(f'<circle cx="{x}" cy="110" r="18" stroke="{CLAIR}" stroke-width="2.5"></circle><circle cx="{x}" cy="110" r="8" fill="{ORANGE}" stroke="none"></circle>')
    for x, lab in zip(xs, ("EXTRAIRE", "ORCHESTRER", "STOCKER", "ENTREPÔT")):
        out.append(f'<text x="{x}" y="160" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-weight="600" font-size="10" letter-spacing="1.4" fill="{CLAIR}" fill-opacity=".6" stroke="none">{lab}</text>')
    return "".join(out)


def gat():
    nodes = [(200, 110), (110, 60), (96, 150), (190, 196), (292, 176), (312, 72), (226, 30), (150, 118), (262, 120)]
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 7), (2, 7), (4, 8), (5, 8), (6, 5), (1, 6), (3, 4)]
    out = [f'<path d="M{nodes[a][0]} {nodes[a][1]} L{nodes[b][0]} {nodes[b][1]}" stroke="{CLAIR}" stroke-width="{3 if a == 0 and b in (1, 5) else 1.5}" stroke-opacity="{.9 if a == 0 and b in (1, 5) else .35}"></path>' for a, b in edges]
    for i, (x, y) in enumerate(nodes[1:], 1):
        out.append(f'<circle cx="{x}" cy="{y}" r="9" fill="#0E1D2C" stroke="{CLAIR}" stroke-width="2.5"></circle>')
    out.append(f'<circle cx="200" cy="110" r="12" fill="{ORANGE}" stroke="none"></circle>')
    return "".join(out)


def maintenance():
    def bell(cx, s, h, base=186):
        pts = []
        for i in range(81):
            x = cx - 3 * s + i * 6 * s / 80
            y = base - h * math.exp(-((x - cx) ** 2) / (2 * s * s))
            pts.append(f"{x:.1f},{y:.1f}")
        return " ".join(pts)
    return (f'<path d="M30 186 H376" stroke="{CLAIR}" stroke-width="1.5" stroke-opacity=".3"></path>'
            f'<polyline points="{bell(150, 34, 120)}" stroke="{CLAIR}" stroke-width="2.5"></polyline>'
            f'<polyline points="{bell(262, 40, 96)}" stroke="{CLAIR}" stroke-width="2.5" stroke-dasharray="4 6" stroke-opacity=".7"></polyline>'
            f'<path d="M168 56 C 200 40, 232 50, 252 78" stroke="{CLAIR}" stroke-width="1.8" stroke-opacity=".5"></path>'
            f'<circle cx="262" cy="90" r="8" fill="{ORANGE}" stroke="none"></circle>')


ILLUS = dict(fangup=fangup, anomalies=anomalies, learny=learny, encore=encore, monitoring=monitoring, elt=elt, gat=gat, maintenance=maintenance)
