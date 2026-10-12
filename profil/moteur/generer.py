"""Génère les images du profil : le terminal du haut, les outils et le pied de page.

Lancé chaque nuit par l'Action « Profil ». En local : python profil/moteur/generer.py
Tout est en SVG animé (SMIL) avec les textes vectorisés : rien d'externe, rendu identique partout.
"""
import io
import json
import math
import os
import subprocess
import sys
import time
import urllib.request

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import forme as F  # noqa: E402
from icones import ICONS  # noqa: E402
from logos import LOGOS  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROFIL = os.path.join(RACINE, "profil")
IMAGES = os.path.join(PROFIL, "images")
UTILISATEUR = os.environ.get("PROFIL_USER", "zenitsu93")

MAR, ARC, CL, OR, GT, SEC = "#0E1D2C", "#16273A", "#E8ECEF", "#E08A2C", "#8A97A6", "#5A6775"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


# ================= données =================
def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profil-badolo"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    for essai in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            if essai == 3:
                raise
            time.sleep(4)


def depots():
    out, page = [], 1
    while True:
        lot = api(f"https://api.github.com/users/{UTILISATEUR}/repos?per_page=100&type=owner&page={page}")
        out += lot
        if len(lot) < 100:
            return [d for d in out if not d.get("fork") and not d.get("private")]
        page += 1


def jeton():
    """Le jeton de l'Action, ou en local celui de la commande gh."""
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=30).stdout.strip() or None
    except Exception:
        return None


REQUETE_CHIFFRES = """query($login: String!) { user(login: $login) {
  followers { totalCount }
  contributionsCollection { totalCommitContributions contributionCalendar { totalContributions } }
  repositories(ownerAffiliations: OWNER, isFork: false, first: 100, privacy: PUBLIC) {
    totalCount
    nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
  }
} }"""
# exclus du décompte des langages : les notebooks (sorties et images compris) et le balisage
LANGAGES_EXCLUS = {"Jupyter Notebook", "HTML", "CSS"}


def chiffres():
    """Les chiffres publics du profil, tels qu'un visiteur les voit."""
    t = jeton()
    if not t:
        raise RuntimeError("pas de jeton GitHub")
    corps = json.dumps({"query": REQUETE_CHIFFRES, "variables": {"login": UTILISATEUR}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=corps,
                                 headers={"Authorization": "Bearer " + t, "User-Agent": "profil-badolo", "Content-Type": "application/json"})
    for essai in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                rep = json.load(r)
            break
        except Exception:
            if essai == 3:
                raise
            time.sleep(4)
    if rep.get("errors") or not rep.get("data", {}).get("user"):
        raise RuntimeError(str(rep.get("errors"))[:200])
    u = rep["data"]["user"]
    octets = {}
    for n in u["repositories"]["nodes"]:
        for e in n["languages"]["edges"]:
            if e["node"]["name"] not in LANGAGES_EXCLUS:
                octets[e["node"]["name"]] = octets.get(e["node"]["name"], 0) + e["size"]
    total = sum(octets.values()) or 1
    langs = sorted(((k, v * 100 / total) for k, v in octets.items()), key=lambda x: -x[1])
    reste = sum(p for _, p in langs[4:])
    langs = langs[:4] + ([("Autres", reste)] if reste > .05 else [])
    return dict(contributions=u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
                commits=u["contributionsCollection"]["totalCommitContributions"],
                depots=u["repositories"]["totalCount"], abonnes=u["followers"]["totalCount"]), langs


# ================= briques graphiques =================
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def f1(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def svg(w, h, corps, titre, defs="", rx=24, fond=MAR):
    rect = f'<rect width="{w}" height="{h}" fill="{fond}"/>' if fond else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(titre)}">'
            f'<title>{esc(titre)}</title><defs>{defs}<clipPath id="cadre"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath></defs>'
            f'<g clip-path="url(#cadre)">{rect}{corps}</g></svg>\n')


PTS = f'<pattern id="pts" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.3" fill="{CL}" fill-opacity=".07"/></pattern>'
GLOW = '<radialGradient id="glow"><stop offset="0" stop-color="#1B3149"/><stop offset="1" stop-color="#1B3149" stop-opacity="0"/></radialGradient>'
FLOU = '<filter id="flou" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5"/></filter>'


def grille(x, y, w, h, rx=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#pts)"/>'


def lueur(cx, cy, rx, ry, op=1):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#glow)" opacity="{op}"/>'


MONO_W = 484 / 684


def monogramme(x, y, h, encre=CL):
    """Le b du kit, tel quel. (x, y) = coin haut gauche, h = hauteur."""
    s = h / 684
    return (f'<g transform="translate({f1(x - 306 * s)} {f1(y - 176 * s)}) scale({s:.5f})">'
            f'<rect x="306" y="176" width="112" height="684" fill="{encre}"/>'
            f'<path d="M362 618 A186 186 0 1 0 617.7 445.5" fill="none" stroke="{encre}" stroke-width="112"/>'
            f'<circle cx="617.7" cy="445.5" r="71.7" fill="{OR}"/></g>')


def rrect(x, y, w, h, r):
    return (f"M{f1(x + r)} {f1(y)} H{f1(x + w - r)} A{r} {r} 0 0 1 {f1(x + w)} {f1(y + r)} V{f1(y + h - r)} A{r} {r} 0 0 1 {f1(x + w - r)} {f1(y + h)} "
            f"H{f1(x + r)} A{r} {r} 0 0 1 {f1(x)} {f1(y + h - r)} V{f1(y + r)} A{r} {r} 0 0 1 {f1(x + r)} {f1(y)} Z")


def faisceau_bord(x, y, w, h, r, dur=7, sw=2.5):
    """Une lumière orange fait le tour du cadre, avec sa traîne."""
    d = rrect(x, y, w, h, r)
    out = [f'<path d="{d}" fill="none" stroke="{CL}" stroke-opacity=".10" stroke-width="1.5"/>']
    for L, op, flou in ((160, .35, True), (90, .55, False), (34, 1, False)):
        filtre = ' filter="url(#flou)"' if flou else ""
        out.append(f'<path d="{d}" fill="none" stroke="{OR}" stroke-width="{sw * (2.2 if flou else 1)}" stroke-opacity="{op}" stroke-linecap="round" '
                   f'pathLength="1000" stroke-dasharray="{L} {1000 - L}"{filtre}>'
                   f'<animate attributeName="stroke-dashoffset" values="{L};{L - 1000}" dur="{dur}s" repeatCount="indefinite"/></path>')
    return "".join(out)


def icone(nom, x, y, taille, encre=CL, sw=3.4):
    corps = ICONS[nom][1].replace("{ink}", encre).replace("{ac}", OR)
    return (f'<g transform="translate({f1(x)} {f1(y)}) scale({taille / 48:.4f})" fill="none" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{corps}</g>')


def titre(s, x, y, taille, couleur=CL, ancre="start"):
    return F.texte(s, x, y, taille, couleur, "xb", -.02, ancre)


# ================= héros : le terminal =================
CW = .6  # largeur d'une cellule à chasse fixe, en em


def mono(s, x, y, taille, couleur, op=1):
    xs = " ".join(f1(x + i * taille * CW) for i in range(len(s)))
    return (f'<text x="{xs}" y="{f1(y)}" font-family="{MONO}" font-size="{taille}" fill="{couleur}" fill-opacity="{op}" '
            f'xml:space="preserve" style="white-space:pre">{esc(s)}</text>')


class Scene:
    """Chronologie d'un terminal en boucle : chaque élément apparaît à son heure, puis tout repart."""
    def __init__(self, T):
        self.T, self.defs, self.corps, self.n = T, [], [], 0

    def kt(self, t):
        return f"{min(max(t / self.T, 0), 1):.4f}"

    def apparait(self, el, t):
        self.corps.append(f'<g opacity="0"><animate attributeName="opacity" dur="{self.T}s" repeatCount="indefinite" calcMode="discrete" '
                          f'keyTimes="0;{self.kt(t)};{self.kt(self.T - .6)}" values="0;1;0"/>{el}</g>')

    def tape(self, invite, cmd, x, y, taille, t, cps=11):
        cw = taille * CW
        self.apparait(mono(invite, x, y, taille, GT), t)
        x0 = x + len(invite) * cw
        self.n += 1
        temps = ["0"] + [self.kt(t + .25 + k / cps) for k in range(1, len(cmd) + 1)] + [self.kt(self.T - .6), "1"]
        vals = ["0"] + [f1(k * cw + 1) for k in range(1, len(cmd) + 1)] + ["0", "0"]
        self.defs.append(f'<clipPath id="tp{self.n}"><rect x="{f1(x0 - 1)}" y="{f1(y - taille)}" height="{f1(taille * 1.5)}" width="0">'
                         f'<animate attributeName="width" dur="{self.T}s" repeatCount="indefinite" calcMode="discrete" '
                         f'keyTimes="{";".join(temps)}" values="{";".join(vals)}"/></rect></clipPath>')
        self.corps.append(f'<g clip-path="url(#tp{self.n})">{mono(cmd, x0, y, taille, CL)}</g>')
        fin = t + .25 + len(cmd) / cps
        cx = [f1(x0 + k * cw) for k in range(len(cmd) + 1)]
        ct = ["0", self.kt(t)] + [self.kt(t + .25 + k / cps) for k in range(1, len(cmd) + 1)] + [self.kt(fin + .35), "1"]
        cv = [cx[0], cx[0]] + cx[1:] + [cx[-1], cx[-1]]
        self.corps.append(f'<rect y="{f1(y - taille * .82)}" width="{f1(cw * .9)}" height="{f1(taille * 1.02)}" fill="{OR}" opacity="0">'
                          f'<animate attributeName="x" dur="{self.T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{";".join(ct)}" values="{";".join(cv)}"/>'
                          f'<animate attributeName="opacity" dur="{self.T}s" repeatCount="indefinite" calcMode="discrete" '
                          f'keyTimes="0;{self.kt(t)};{self.kt(fin + .35)}" values="0;1;0"/></rect>')
        return fin

    def attente(self, invite, x, y, taille, t):
        cw = taille * CW
        self.apparait(mono(invite, x, y, taille, GT) +
                      f'<rect x="{f1(x + len(invite) * cw)}" y="{f1(y - taille * .82)}" width="{f1(cw * .9)}" height="{f1(taille * 1.02)}" fill="{OR}">'
                      f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/></rect>', t)


def fenetre(w, titre_barre, barre=52):
    return (f'<rect width="{w}" height="{barre}" fill="{ARC}"/><path d="M0 {barre} H{w}" stroke="{CL}" stroke-opacity=".08"/>'
            f'<circle cx="30" cy="{barre / 2}" r="7" fill="{SEC}"/><circle cx="54" cy="{barre / 2}" r="7" fill="{SEC}"/>'
            f'<circle cx="78" cy="{barre / 2}" r="7" fill="{OR}"/>' + F.texte(titre_barre, w / 2, barre / 2 + 5.5, 15, GT, "m", ancre="middle"))


def heros(nb_projets):
    W, H, T = 1200, 520, 17
    sc = Scene(T)
    x, tl = 48, 21
    t = sc.tape("~ $ ", "whoami", x, 108, tl, .4)
    nom, nw = F.trace("christian thomas badolo", x, 178, 60, "xb", -.02)
    sc.apparait(f'<path d="{nom}" fill="{CL}"/><circle cx="{f1(x + nw + 14)}" cy="171" r="8.5" fill="{OR}"/>', t + .5)
    t = sc.tape("~ $ ", "cat passions.txt", x, 236, tl, t + 1.3)
    sc.apparait(mono("data · ia · web · et des trucs pas toujours utiles", x, 272, tl, CL, .82), t + .4)
    t = sc.tape("~ $ ", "ls ~/projets | wc -l", x, 324, tl, t + 1.1)
    n = str(nb_projets)
    sc.apparait(mono(n, x, 360, tl, CL, .9) + mono("# et c’est pas fini", x + (len(n) + 3) * tl * CW, 360, tl, GT), t + .4)
    t = sc.tape("~ $ ", "./me-prouver-que-j-en-suis-capable", x, 412, tl, t + 1.1)
    sc.apparait(f'<path d="M{x + 2} 441 l6 6 l12 -13" stroke="{OR}" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                + mono("ça compile. on continue.", x + 30, 448, tl, CL, .9), t + .5)
    sc.attente("~ $ ", x, 492, tl, t + 1.2)
    corps = (lueur(1000, 260, 420, 300) + grille(0, 52, W, H) + fenetre(W, "christian@badolo : ~")
             + monogramme(W - 64 - 280 * MONO_W, 150, 280) + "".join(sc.corps))
    return svg(W, H, corps, f"Terminal : whoami, christian thomas badolo. {nb_projets} projets, et c’est pas fini.", PTS + GLOW + "".join(sc.defs), 20)


# ================= images transparentes, une version par thème GitHub =================
THEMES = {"clair": dict(texte=MAR, doux=SEC, discret=GT, trait=MAR),
          "sombre": dict(texte=CL, doux=GT, discret=GT, trait=CL)}


def svg_libre(w, h, corps, titre):
    """SVG sans fond : il prend la couleur de la page GitHub."""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(titre)}">'
            f'<title>{esc(titre)}</title>{corps}</svg>\n')


# ================= avec quoi je bricole =================
CYCLE_VAGUE = 16  # secondes


def vague(el, rang):
    """Chaque outil monte et apparaît à son tour, reste affiché, puis la vague repart."""
    t0 = .4 + rang * .07
    a, b, z = t0 / CYCLE_VAGUE, (t0 + .55) / CYCLE_VAGUE, (CYCLE_VAGUE - .5) / CYCLE_VAGUE
    return (f'<g><animate attributeName="opacity" dur="{CYCLE_VAGUE}s" repeatCount="indefinite" values="0;0;1;1;0" '
            f'keyTimes="0;{a:.4f};{b:.4f};{z:.4f};1"/>'
            f'<animateTransform attributeName="transform" type="translate" dur="{CYCLE_VAGUE}s" repeatCount="indefinite" '
            f'calcMode="spline" values="0 10;0 10;0 0;0 0" keyTimes="0;{a:.4f};{b:.4f};1" keySplines="0 0 1 1;.2 .8 .3 1;0 0 1 1"/>{el}</g>')


def categories():
    conf = yaml.safe_load(io.open(os.path.join(PROFIL, "outils.yml"), encoding="utf-8")) or {}
    return [(str(c["nom"]), [str(o) for o in c.get("outils") or []]) for c in (conf.get("categories") or [])]


def outils(theme):
    """Une ligne par catégorie : le nom à gauche, puis chaque outil avec son logo."""
    t = THEMES[theme]
    W, X0, L, TT, PAS, LIGNE = 1200, 250, 26, 19, 34, 58
    corps, y, rang = [], 8, 0
    cats = categories()
    for k, (nom, items) in enumerate(cats):
        # découpe en lignes selon la largeur disponible
        lignes, cur, x = [], [], X0
        for it in items:
            w = L + 10 + F.largeur(it, TT, "m")
            if cur and x + w > W:
                lignes.append(cur)
                cur, x = [], X0
            cur.append((it, x))
            x += w + PAS
        if cur:
            lignes.append(cur)
        cy0 = y + LIGNE / 2
        corps.append(f'<circle cx="5" cy="{f1(cy0)}" r="4.5" fill="{OR}"/>' + F.texte(nom.upper(), 22, cy0 + 5, 14, t["discret"], "sb", .14))
        for ligne in lignes:
            cy = y + LIGNE / 2
            for it, x in ligne:
                if it in LOGOS:
                    logo = f'<path transform="translate({f1(x)} {f1(cy - L / 2)}) scale({L / 24:.4f})" d="{LOGOS[it]}" fill="{t["texte"]}"/>'
                else:
                    logo = icone("data" if it.upper() == "SQL" else "code", x - 1, cy - L / 2 - 1, L + 2, encre=t["texte"], sw=3.6)
                corps.append(vague(logo + F.texte(it, x + L + 10, cy + TT * .36, TT, t["texte"], "m"), rang))
                rang += 1
            y += LIGNE
        if k < len(cats) - 1:
            corps.append(f'<path d="M0 {f1(y + 6)} H{W}" stroke="{t["trait"]}" stroke-opacity=".10"/>')
            y += 12
    titre_alt = "Mes outils. " + " ".join(f"{n} : {', '.join(i)}." for n, i in cats)
    return svg_libre(W, math.ceil(y + 8), "".join(corps), titre_alt)


# ================= en chiffres =================
# teintes du kit pour la barre des langages : l'orange pour le premier, puis du plus fort au plus discret
TEINTES = {"clair": [OR, MAR, SEC, GT, "#C5CDD5"], "sombre": [OR, CL, GT, SEC, "#2A3B4F"]}
LIGNE_TITRE = {"clair": "#D0D7DE", "sombre": "#30363D"}


def nb(n):
    return f"{n:,}".replace(",", " ")


def pct(p):
    return (f"{p:.1f}".replace(".", ",").replace(",0", "") + " %") if p >= 1 else "< 1 %"


CYCLE_TITRE = 12  # secondes
TITRES = [("salut", "salut"), ("mode-d-emploi", "mode d’emploi"), ("outils", "avec quoi je bricole"), ("en-chiffres", "en chiffres")]


def titre_section(texte, theme, decalage=0.0):
    """Titre de section au format des titres du kit (1760 × 144). Le texte reste fixe ;
    le trait se dessine de gauche à droite, puis le point orange apparaît avec un petit rebond."""
    d, w = F.trace(texte, 6, 104, 84.4, "xb", -.03)
    cx = 6 + w + 15.5
    x0, larg = cx + 54, 1756 - cx - 54
    kt = lambda s: f"{min(max((decalage + s) / CYCLE_TITRE, 0), 1):.4f}"
    trait = (f'<rect x="{f1(x0)}" y="70" width="{f1(larg)}" height="4" fill="{LIGNE_TITRE[theme]}">'
             f'<animate attributeName="width" dur="{CYCLE_TITRE}s" repeatCount="indefinite" calcMode="spline" '
             f'values="0;0;{f1(larg)};{f1(larg)}" keyTimes="0;{kt(.3)};{kt(1.6)};1" keySplines="0 0 1 1;.3 .7 .2 1;0 0 1 1"/></rect>')
    point = (f'<circle cx="{f1(cx)}" cy="93" r="9" fill="{OR}">'
             f'<animate attributeName="r" dur="{CYCLE_TITRE}s" repeatCount="indefinite" calcMode="spline" '
             f'values="9;9;0;12;8;9;9" keyTimes="0;{kt(.05)};{kt(.15)};{kt(.45)};{kt(.6)};{kt(.75)};1" '
             f'keySplines="0 0 1 1;.4 0 1 1;.2 .8 .3 1;.4 0 .6 1;.4 0 .6 1;0 0 1 1"/></circle>')
    corps = f'<path d="{d}" fill="{THEMES[theme]["texte"]}"/>{point}{trait}'
    return svg_libre(1760, 144, corps, texte)


# ================= boutons du haut =================
BOUTONS = [("linkedin", "LinkedIn", "profil"), ("ecrire", "M’écrire", "mail"), ("2nb", "2NB Digital", "globe")]


def bouton(cle, texte_b, nom_icone):
    """Pilule marine 460 × 112 du kit ; une lumière orange fait le tour du bouton « M’écrire »."""
    W, H = 460, 112
    tw = F.largeur(texte_b, 31, "sb")
    x = (W - (40 + 24 + tw)) / 2
    corps = [f'<rect width="{W}" height="{H}" rx="56" fill="{MAR}"/>', icone(nom_icone, x, H / 2 - 20, 40, sw=3.4),
             F.texte(texte_b, x + 64, H / 2 + 31 * .36, 31, CL, "sb")]
    defs = ""
    if cle == "ecrire":
        corps.append(faisceau_bord(2, 2, W - 4, H - 4, 54, 5, 3.4))
        defs = FLOU
    return svg(W, H, "".join(corps), texte_b, defs, 56, None)


CYCLE, ROULEMENT = 15, 1.7  # le compteur repart toutes les 15 s et défile pendant 1,7 s


def chiffres_svg(taille, couleur):
    """Les dix chiffres, définis une fois et réutilisés par les compteurs."""
    return "".join(f'<path id="g{n}" d="{F.trace(str(n), 0, 0, taille, "xb")[0]}" fill="{couleur}"/>' for n in range(10))


def compteur(s, x, y, taille, uid, decalage):
    """Nombre qui défile comme un compteur mécanique avant de s'arrêter sur sa valeur."""
    f = F.police("xb")
    pos, _ = f.composer(s)
    k, ls, pas = taille / f.upm, -.03, taille * 1.2
    clips, corps = [], []
    for i, ((g, gx), ch) in enumerate(zip(pos, s)):
        if not ch.isdigit():
            continue
        cx = x + gx * k + i * ls * taille
        fin = 10 + int(ch)
        clips.append(f'<clipPath id="k{uid}{i}"><rect x="{f1(cx - 2)}" y="{f1(y - taille * .8)}" width="{f1(f.hmtx[g][0] * k + 4)}" '
                     f'height="{f1(taille * .92)}"/></clipPath>')
        pile = "".join(f'<use href="#g{j % 10}" xlink:href="#g{j % 10}" y="{f1(j * pas)}"/>' for j in range(fin + 1))
        t1 = ROULEMENT / CYCLE
        corps.append(f'<g clip-path="url(#k{uid}{i})"><g transform="translate({f1(cx)} {f1(y)})"><g>'
                     f'<animateTransform attributeName="transform" type="translate" dur="{CYCLE}s" begin="{decalage + i * .06:.2f}s" '
                     f'repeatCount="indefinite" values="0 0;0 {f1(-fin * pas)};0 {f1(-fin * pas)}" keyTimes="0;{t1:.3f};1" '
                     f'calcMode="spline" keySplines=".2 .8 .2 1;0 0 1 1"/>{pile}</g></g></g>')
    return "".join(clips), "".join(corps)


def en_chiffres(theme, D, langs):
    """Quatre chiffres en grand qui défilent comme un compteur, puis une fine barre des langages."""
    t = THEMES[theme]
    W, c = 1200, []
    defs = [chiffres_svg(64, t["texte"])]
    blocs = [(nb(D["contributions"]), "contributions", "sur un an"), (nb(D["commits"]), "commits publics", "sur un an"),
             (nb(D["depots"]), "dépôts", "publics"), (nb(D["abonnes"]), "abonnés", "")]
    col = W / 4
    for i, (n, l1, l2) in enumerate(blocs):
        x = i * col + (0 if i == 0 else 28)
        if i:
            c.append(f'<path d="M{f1(i * col)} 14 V128" stroke="{t["trait"]}" stroke-opacity=".12"/>')
        _, w = F.trace(n, x, 78, 64, "xb", -.03)
        clips, corps = compteur(n, x, 78, 64, i, .3 + i * .15)
        defs.append(clips)
        c.append(corps + f'<circle cx="{f1(x + w + 10)}" cy="70" r="7" fill="{OR}"/>')
        c.append(F.texte(l1.upper(), x + 2, 112, 13, t["discret"], "sb", .14))
        if l2:
            c.append(F.texte(l2, x + 2, 134, 14, t["discret"], "m"))
    y, x, largeur = 188, 150, W - 150
    c.append(F.texte("LANGAGES", 2, y, 13, t["discret"], "sb", .14))
    teintes = TEINTES[theme]
    # la barre se remplit pendant que les chiffres défilent, et finit avec eux
    debut, fin = .3 / CYCLE, (.3 + ROULEMENT + .4) / CYCLE
    c.append(f'<clipPath id="barre"><rect x="{x}" y="{y - 11}" width="{largeur}" height="8" rx="4">'
             f'<animate attributeName="width" dur="{CYCLE}s" repeatCount="indefinite" calcMode="spline" '
             f'values="0;0;{largeur};{largeur}" keyTimes="0;{debut:.4f};{fin:.4f};1" keySplines="0 0 1 1;.25 .8 .25 1;0 0 1 1"/>'
             f'</rect></clipPath><g clip-path="url(#barre)">')
    for i, (k, p) in enumerate(langs):
        w = largeur * p / 100
        c.append(f'<rect x="{f1(x)}" y="{y - 11}" width="{f1(w + .5)}" height="8" fill="{teintes[i % 5]}"/>')
        x += w
    c.append("</g>")
    x = 150
    for i, (k, p) in enumerate(langs):
        s = f"{k} {pct(p)}"
        c.append(f'<circle cx="{x + 5}" cy="{y + 25}" r="5" fill="{teintes[i % 5]}"/>' + F.texte(s, x + 16, y + 31, 16, t["texte"], "m"))
        x += 16 + F.largeur(s, 16, "m") + 30
    # témoin « en direct » : un point qui respire
    c.append(f'<circle cx="7" cy="{y + 74}" r="5" fill="{OR}"><animate attributeName="opacity" values="1;.25;1" dur="2.4s" repeatCount="indefinite"/></circle>'
             + F.texte("Chiffres publics de GitHub, actualisés toutes les heures", 22, y + 79, 13, t["discret"], "m"))
    alt = (f"En chiffres : {nb(D['contributions'])} contributions sur un an, {D['commits']} commits publics, {D['depots']} dépôts publics, "
           f"{D['abonnes']} abonnés. Langages : " + ", ".join(f"{k} {pct(p)}" for k, p in langs) + ".")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {y + 92}" width="{W}" '
            f'height="{y + 92}" role="img" aria-label="{esc(alt)}"><title>{esc(alt)}</title><defs>{"".join(defs)}</defs>{"".join(c)}</svg>\n')


# ================= mode d'emploi =================
def mode_emploi(theme):
    """Même grammaire que les outils : le trait de caractère à gauche, la phrase à droite."""
    t = THEMES[theme]
    conf = yaml.safe_load(io.open(os.path.join(PROFIL, "mode-d-emploi.yml"), encoding="utf-8")) or {}
    lignes = [(str(l["titre"]), str(l["texte"])) for l in (conf.get("lignes") or [])]
    W, X0, TT, LIGNE, INTER = 1200, 250, 19, 58, 28
    corps, y = [], 8
    for k, (titre_l, texte_l) in enumerate(lignes):
        morceaux = F.couper(texte_l, TT, W - X0, "m")
        h = LIGNE + (len(morceaux) - 1) * INTER
        cy0 = y + LIGNE / 2
        corps.append(f'<circle cx="5" cy="{f1(cy0)}" r="4.5" fill="{OR}"/>' + F.texte(titre_l.upper(), 22, cy0 + 5, 14, t["discret"], "sb", .14))
        for j, m in enumerate(morceaux):
            corps.append(F.texte(m, X0, cy0 + TT * .36 + j * INTER, TT, t["texte"], "m"))
        y += h
        if k < len(lignes) - 1:
            corps.append(f'<path d="M0 {f1(y + 6)} H{W}" stroke="{t["trait"]}" stroke-opacity=".10"/>')
            y += 12
    alt = "Mode d’emploi. " + " ".join(f"{a} : {b}" for a, b in lignes)
    return svg_libre(W, math.ceil(y + 8), "".join(corps), alt)


# ================= on se parle ? =================
def pied():
    W, H = 1200, 440
    p, w = F.trace("badolo", 0, 0, 330, "xb", -.02)
    L = w + 140
    defs = (f'<g id="geant"><path d="{p}" fill="none" stroke="{CL}" stroke-opacity=".13" stroke-width="2"/>'
            f'<circle cx="{f1(w + 46)}" cy="-30" r="34" fill="none" stroke="{OR}" stroke-opacity=".35" stroke-width="2"/></g>')
    uses = "".join(f'<use xlink:href="#geant" href="#geant" x="{f1(k * L)}"/>' for k in range(3))
    b = [lueur(600, 200, 520, 240), grille(0, 0, W, H),
         f'<g transform="translate(-40 530)"><g><animateTransform attributeName="transform" type="translate" from="0 0" to="{f1(-L)} 0" '
         f'dur="38s" repeatCount="indefinite"/>{uses}</g></g>']
    _, w1 = F.trace("on se parle ", 0, 0, 86, "xb", -.02)
    _, w2 = F.trace("?", 0, 0, 86, "xb", -.02)
    x0 = (W - w1 - w2) / 2
    b.append(titre("on se parle ", x0, 168, 86) + titre("?", x0 + w1, 168, 86, OR))
    b.append(F.texte("Un projet, une idée bizarre, un merci : tout me va.", W / 2, 224, 24, GT, ancre="middle"))
    bw, bh = 250, 62
    bx, by = (W - bw) / 2, 268
    b.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="{ARC}"/>')
    b.append(faisceau_bord(bx, by, bw, bh, bh / 2, 4, 2.2))
    b.append(F.texte("m’écrire  →", W / 2, by + bh / 2 + 7.5, 21, CL, "sb", ancre="middle"))
    return svg(W, H, "".join(b), "on se parle ? Un projet, une idée bizarre, un merci : tout me va. M’écrire.", PTS + GLOW + FLOU + defs, 24)


# ================= écriture =================
def ecrire(chemin, contenu):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    ancien = io.open(chemin, encoding="utf-8").read() if os.path.exists(chemin) else None
    if ancien != contenu:
        io.open(chemin, "w", encoding="utf-8", newline="\n").write(contenu)
        return True
    return False


def main():
    liste_api = depots()
    changes = []
    images = {"heros.svg": heros(len(liste_api)), "on-se-parle.svg": pied()}
    gardes = set()
    for theme in THEMES:
        images[f"outils-{theme}.svg"] = outils(theme)
        images[f"mode-d-emploi-{theme}.svg"] = mode_emploi(theme)
        # titres en cascade : chacun démarre un peu après le précédent
        for k, (cle, texte) in enumerate(TITRES):
            images[f"titre-{cle}-{theme}.svg"] = titre_section(texte, theme, k * .5)
    for cle, texte_b, nom_icone in BOUTONS:
        images[f"bouton-{cle}.svg"] = bouton(cle, texte_b, nom_icone)
    try:
        D, langs = chiffres()
        for theme in THEMES:
            images[f"en-chiffres-{theme}.svg"] = en_chiffres(theme, D, langs)
    except Exception as e:
        # sans données fiables, on garde les chiffres de la veille plutôt que d'afficher des zéros
        print(f"  ! chiffres GitHub indisponibles, images de la veille conservées : {e}")
        gardes = {f"en-chiffres-{theme}.svg" for theme in THEMES}
    for nom, contenu in images.items():
        if ecrire(os.path.join(IMAGES, nom), contenu):
            changes.append(nom)
    # retire les images qui ne servent plus
    for racine, dossiers, fichiers in os.walk(IMAGES, topdown=False):
        for f in fichiers:
            rel = os.path.relpath(os.path.join(racine, f), IMAGES).replace(os.sep, "/")
            if f.endswith(".svg") and rel not in images and rel not in gardes:
                os.remove(os.path.join(racine, f))
                changes.append(f"{rel} (retiré)")
        if racine != IMAGES and not os.listdir(racine):
            os.rmdir(racine)
    print("modifié : " + (", ".join(changes) if changes else "rien"))


if __name__ == "__main__":
    main()
