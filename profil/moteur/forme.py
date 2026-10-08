"""Texte vectoriel : chaque texte devient un tracé en Inter, pour un rendu identique partout sur GitHub."""
import os
import tempfile

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ICI = os.path.dirname(os.path.abspath(__file__))
VARIABLE = os.path.join(ICI, "polices", "Inter[opsz,wght].ttf")
# graisse : (taille optique, poids). Inter Display pour les titres, Inter pour le reste.
POIDS = dict(xb=(32, 800), b=(32, 700), sb=(14, 600), m=(14, 500), r=(14, 400))


def _deballer(lookup):
    if lookup.LookupType == 9:
        return [(st.ExtensionLookupType, st.ExtSubTable) for st in lookup.SubTable]
    return [(lookup.LookupType, st) for st in lookup.SubTable]


class Police:
    def __init__(self, chemin):
        f = TTFont(chemin)
        self.cmap = f.getBestCmap()
        self.gs = f.getGlyphSet()
        self.hmtx = f["hmtx"]
        self.upm = f["head"].unitsPerEm
        self.crenage = []
        gpos = f["GPOS"].table
        idx = set()
        for fr in gpos.FeatureList.FeatureRecord:
            if fr.FeatureTag == "kern":
                idx.update(fr.Feature.LookupListIndex)
        for li in sorted(idx):
            self.crenage += [st for typ, st in _deballer(gpos.LookupList.Lookup[li]) if typ == 2]

    def _paire(self, a, b):
        for st in self.crenage:
            if a not in st.Coverage.glyphs:
                continue
            if st.Format == 1:
                for pvr in st.PairSet[st.Coverage.glyphs.index(a)].PairValueRecord:
                    if pvr.SecondGlyph == b:
                        return getattr(pvr.Value1, "XAdvance", 0) or 0 if pvr.Value1 else 0
            else:
                v = st.Class1Record[st.ClassDef1.classDefs.get(a, 0)].Class2Record[st.ClassDef2.classDefs.get(b, 0)].Value1
                adv = getattr(v, "XAdvance", 0) if v else 0
                if adv:
                    return adv
        return 0

    def composer(self, texte):
        glyphes = [self.cmap.get(ord(c), self.cmap[ord("?")]) for c in texte]
        pos, x = [], 0
        for k, g in enumerate(glyphes):
            pos.append((g, x))
            x += self.hmtx[g][0]
            if k + 1 < len(glyphes):
                x += self._paire(g, glyphes[k + 1])
        return pos, x


_polices = {}


def police(w):
    if w not in _polices:
        opsz, wght = POIDS[w]
        chemin = os.path.join(tempfile.gettempdir(), f"profil-inter-{opsz}-{wght}.ttf")
        if not os.path.exists(chemin):
            instancer.instantiateVariableFont(TTFont(VARIABLE), dict(opsz=opsz, wght=wght)).save(chemin)
        _polices[w] = Police(chemin)
    return _polices[w]


def largeur(s, taille, w="r", ls=0.0):
    f = police(w)
    return f.composer(s)[1] * taille / f.upm + ls * taille * max(len(s) - 1, 0)


def trace(s, x, y, taille, w="r", ls=0.0, ancre="start"):
    """Données du tracé et largeur. ls = interlettrage en fraction de la taille."""
    f = police(w)
    pos, adv = f.composer(s)
    k = taille / f.upm
    total = adv * k + ls * taille * max(len(s) - 1, 0)
    if ancre == "middle":
        x -= total / 2
    elif ancre == "end":
        x -= total
    pen = SVGPathPen(f.gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    for i, (g, gx) in enumerate(pos):
        f.gs[g].draw(TransformPen(pen, (k, 0, 0, -k, x + gx * k + i * ls * taille, y)))
    return pen.getCommands(), total


def texte(s, x, y, taille, couleur, w="r", ls=0.0, ancre="start", extra=""):
    d, _ = trace(s, x, y, taille, w, ls, ancre)
    return f'<path d="{d}" fill="{couleur}"{extra}/>' if d else ""


def couper(s, taille, maxw, w="r"):
    lignes, cur = [], ""
    for mot in s.split():
        t = (cur + " " + mot).strip()
        if cur and largeur(t, taille, w) > maxw:
            lignes.append(cur)
            cur = mot
        else:
            cur = t
    if cur:
        lignes.append(cur)
    return lignes


def paragraphe(s, x, y, taille, couleur, maxw, w="r", interligne=1.45, max_lignes=None):
    lignes = couper(s, taille, maxw, w)
    if max_lignes and len(lignes) > max_lignes:
        lignes = lignes[:max_lignes]
        while lignes[-1] and largeur(lignes[-1] + "…", taille, w) > maxw:
            lignes[-1] = lignes[-1].rsplit(" ", 1)[0]
        lignes[-1] += "…"
    out = "".join(texte(l, x, y + i * taille * interligne, taille, couleur, w) for i, l in enumerate(lignes))
    return out, len(lignes)
