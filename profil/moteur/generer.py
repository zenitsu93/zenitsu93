"""Génère les images animées du profil et la section « ma boîte à trucs » du README.

Lancé chaque nuit par l'Action « Profil ». En local : python profil/moteur/generer.py
Tout est en SVG animé (SMIL) avec les textes vectorisés : rien d'externe, rendu identique partout.
"""
import io
import json
import math
import os
import sys
import time
import urllib.request

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import forme as F  # noqa: E402
from icones import ICONS  # noqa: E402
from illustrations import ILLUS  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROFIL = os.path.join(RACINE, "profil")
IMAGES = os.path.join(PROFIL, "images")
UTILISATEUR = os.environ.get("PROFIL_USER", "zenitsu93")
SUJET, SUJET_PHARE = "boite-a-trucs", "phare"

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


TAGS = [({"llm", "rag", "chatbot", "gemini", "generative-ai", "nlp", "langchain", "openai"}, "IA"),
        ({"computer-vision", "object-detection", "yolov8", "cnn", "image-classification"}, "Vision"),
        ({"data-engineering", "etl", "elt", "airflow", "pipeline", "big-data", "spark", "apache-spark"}, "Data engineering"),
        ({"mlops", "model-monitoring"}, "MLOps"),
        ({"machine-learning", "deep-learning", "data-science", "classification", "regression"}, "Machine learning"),
        ({"optimization", "mathematical-modeling", "monte-carlo", "differential-equations", "stochastic-optimization", "graph-theory", "statistics"}, "Maths"),
        ({"web-development", "django", "nodejs", "react", "nextjs", "fastapi", "website"}, "Web"),
        ({"game", "music-quiz", "blind-test"}, "Jeu"),
        ({"automation", "web-scraping", "bot"}, "Automatisation"),
        ({"robotics"}, "Robotique"),
        ({"finance", "quantitative-finance", "credit-risk"}, "Finance"),
        ({"healthcare", "medical-imaging"}, "Santé")]
STACK = {"python": "Python", "typescript": "TypeScript", "javascript": "JavaScript", "nodejs": "Node.js", "django": "Django", "fastapi": "FastAPI",
         "react": "React", "nextjs": "Next.js", "docker": "Docker", "airflow": "Airflow", "snowflake": "Snowflake", "spark": "Spark", "apache-spark": "Spark",
         "pytorch": "PyTorch", "tensorflow": "TensorFlow", "scikit-learn": "scikit-learn", "langchain": "LangChain", "streamlit": "Streamlit",
         "gemini": "Gemini", "pandas": "pandas", "postgresql": "PostgreSQL", "supabase": "Supabase", "yolov8": "YOLOv8", "hadoop": "Hadoop",
         "xgboost": "XGBoost", "networkx": "NetworkX", "matlab": "MATLAB", "opencv": "OpenCV", "huggingface": "Hugging Face", "openai": "OpenAI",
         "telegram": "Telegram", "flask": "Flask", "vue": "Vue", "tailwindcss": "Tailwind", "mongodb": "MongoDB", "kubernetes": "Kubernetes"}
ICONES_AUTO = [({"llm", "chatbot", "rag", "gemini", "nlp", "generative-ai", "openai"}, "bulle"),
               ({"computer-vision", "object-detection", "yolov8", "medical-imaging", "cnn"}, "oeil"),
               ({"data-engineering", "etl", "elt", "pipeline", "airflow", "big-data", "spark", "apache-spark"}, "data"),
               ({"music", "music-quiz", "blind-test", "spotify"}, "note"),
               ({"sports-analytics", "football"}, "ballon"),
               ({"graph-theory", "graph-neural-networks", "network-analysis"}, "graphe"),
               ({"anomaly-detection"}, "loupe"),
               ({"path-planning", "robotics", "tsp"}, "route"),
               ({"3d", "threejs"}, "cube"),
               ({"optimization", "mathematical-modeling", "time-series", "monte-carlo", "statistics"}, "courbe"),
               ({"web-development", "django", "nodejs", "react", "nextjs", "website"}, "globe")]


def joli(nom):
    if any(c.isupper() for c in nom):
        return nom
    t = nom.replace("-", " ").replace("_", " ").strip()
    return t[:1].upper() + t[1:]


def carte(d, e):
    sujets = set(d.get("topics") or [])
    tags = []
    for cles, lab in TAGS:
        if sujets & cles and lab not in tags:
            tags.append(lab)
    stack = [STACK[s] for s in d.get("topics") or [] if s in STACK]
    stack = list(dict.fromkeys(stack))[:3] or ([d["language"]] if d.get("language") else [])
    icone = next((ic for cles, ic in ICONES_AUTO if sujets & cles), "code")
    return dict(depot=d["name"], url=d["html_url"], fichier=d["name"].lower(),
                titre=e.get("titre") or joli(d["name"]),
                description=e.get("description") or d.get("description") or "",
                tag=e.get("tag") or " · ".join(tags[:2]) or (d.get("language") or "Projet"),
                stack=e.get("stack") or stack,
                illustration=e.get("illustration"), icone=e.get("icone") or icone,
                phare=bool(e.get("phare")) or SUJET_PHARE in sujets)


def projets(liste_api):
    conf = yaml.safe_load(io.open(os.path.join(PROFIL, "projets.yml"), encoding="utf-8")) or {}
    entrees = conf.get("projets") or []
    par_nom = {d["name"].lower(): d for d in liste_api}
    connus = {str(e["depot"]).lower() for e in entrees}
    nouveaux = sorted((d for d in liste_api if SUJET in (d.get("topics") or []) and d["name"].lower() not in connus),
                      key=lambda d: d.get("pushed_at") or "", reverse=True)
    suivis = []
    for e in entrees:
        if e.get("cacher"):
            continue
        d = par_nom.get(str(e["depot"]).lower())
        if d is None:
            print(f"  ! dépôt introuvable ou privé, ignoré : {e['depot']}")
            continue
        suivis.append(carte(d, e))
    tous = [carte(d, {}) for d in nouveaux] + suivis
    if not tous:
        return []
    phare = next((p for p in tous if p["phare"]), tous[0])
    return [phare] + [p for p in tous if p is not phare]


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


def pulse(cx, cy, r, dur=2.4, debut=0.0, couleur=OR, sw=2, grow=2.4, op=.8):
    return (f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="none" stroke="{couleur}" stroke-width="{sw}" stroke-opacity="0">'
            f'<animate attributeName="r" values="{f1(r)};{f1(r * grow)}" dur="{dur}s" begin="{debut}s" repeatCount="indefinite"/>'
            f'<animate attributeName="stroke-opacity" values="{op};0" dur="{dur}s" begin="{debut}s" repeatCount="indefinite"/></circle>')


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


def pastille(nom, r=26, fond=ARC):
    return f'<circle r="{r}" fill="{fond}" stroke="{CL}" stroke-opacity=".14"/>' + icone(nom, -r * .6, -r * .6, r * 1.2, sw=3.6)


def chips(x, y, labels, h=34, taille=15):
    out = []
    for lab in labels:
        w = F.largeur(lab, taille, "m") + 32
        out.append(f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{h}" rx="{h / 2}" fill="none" stroke="{CL}" stroke-opacity=".22"/>'
                   + F.texte(lab, x + 16, y + h / 2 + taille * .36, taille, CL, "m", extra=' fill-opacity=".9"'))
        x += w + 10
    return "".join(out)


def etiquette(s, x, y, taille=15):
    return F.texte(s.upper(), x, y, taille, GT, "sb", .14)


def titre(s, x, y, taille, couleur=CL, ancre="start"):
    return F.texte(s, x, y, taille, couleur, "xb", -.02, ancre)


# ---------- illustrations animées (repère 400 × 220) ----------
def _flux(d, dur=1.2, dash="2 7", per=9, op=.5, sw=2):
    return (f'<path d="{d}" stroke="{CL}" stroke-width="{sw}" stroke-opacity="{op}" stroke-dasharray="{dash}" fill="none">'
            f'<animate attributeName="stroke-dashoffset" values="0;-{per}" dur="{dur}s" repeatCount="indefinite"/></path>')


def _paquet(chemin, dur=2.4, debut=0, r=4.5):
    return (f'<circle r="{r}" fill="{CL}" opacity="0"><animateMotion path="{chemin}" dur="{dur}s" begin="{debut}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="{dur}s" begin="{debut}s" repeatCount="indefinite"/></circle>')


def _cloche(cx, s, h, base=186):
    return [(cx - 3 * s + i * 6 * s / 80, base - h * math.exp(-((cx - 3 * s + i * 6 * s / 80 - cx) ** 2) / (2 * s * s))) for i in range(81)]


def anim(nom):
    if nom == "fangup":
        return _flux("M190 171 C 290 171, 352 168, 352 146", 1.1) + pulse(352, 92, 9)
    if nom == "anomalies":
        return pulse(262, 168, 7, grow=3.4)
    if nom == "learny":
        return pulse(140, 104, 5.5, grow=3)
    if nom == "encore":
        def tour(dur, r, a):
            ex, ey = 200 + r * math.sin(math.radians(a)), 110 - r * math.cos(math.radians(a))
            return (f'<g><animateTransform attributeName="transform" type="rotate" from="0 200 110" to="360 200 110" dur="{dur}s" repeatCount="indefinite"/>'
                    f'<path d="M200 {110 - r} A{r} {r} 0 0 1 {f1(ex)} {f1(ey)}" stroke="{CL}" stroke-width="3" fill="none"/></g>')
        return tour(3.2, 78, 55) + tour(2.2, 50, 70)
    if nom == "monitoring":
        return _flux("M30 92 H376", 1.4, "5 7", 12, .5, 1.5) + pulse(326, 62, 8)
    if nom == "elt":
        return _paquet("M88 110 H322", 2.6) + _paquet("M88 110 H322", 2.6, 1.3) + pulse(340, 110, 8)
    if nom == "gat":
        return _paquet("M110 60 L200 110", 1.8) + _paquet("M312 72 L200 110", 1.8, .9) + pulse(200, 110, 12)
    if nom == "maintenance":
        d = "M" + " L".join(f"{f1(x)} {f1(y)}" for x, y in _cloche(262, 40, 96))
        return _paquet(d, 4, 0, 4) + pulse(262, 90, 8)
    return ""


def illu_auto(nom_icone):
    """Pour un nouveau projet sans dessin sur mesure : l'icône du kit de sa catégorie, en grand."""
    anneaux = "".join(f'<circle cx="200" cy="110" r="{r}" fill="none" stroke="{CL}" stroke-opacity="{o}" stroke-width="1.5"/>'
                      for r, o in ((52, .16), (74, .1), (96, .06)))
    return anneaux + pulse(200, 110, 52, 3, 0, CL, 1.5, 1.9, .3) + icone(nom_icone, 152, 62, 96, sw=1.9)


def illustration(p, x, y, echelle):
    nom = p.get("illustration")
    corps = ILLUS[nom]() + anim(nom) if nom in ILLUS else illu_auto(p.get("icone") if p.get("icone") in ICONS else "code")
    return (f'<g transform="translate({f1(x)} {f1(y)}) scale({echelle:.4f})" fill="none" stroke-linecap="round" stroke-linejoin="round">{corps}</g>')


def alt(p):
    return f"{p['titre']} : {p['description']}" if p["description"] else p["titre"]


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


# ================= ma boîte à trucs =================
def carte_phare(p):
    W, H = 1200, 440
    b = [lueur(1000, 120, 420, 260), grille(0, 0, W, H)]
    px, py, pw, ph = 628, 36, 536, 368
    b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="18" fill="{MAR}" stroke="{CL}" stroke-opacity=".08"/>')
    ech = (pw - 24) / 400
    b.append(illustration(p, px + 12, py + (ph - 220 * ech) / 2, ech))
    b.append(etiquette("Projet phare · " + p["tag"], 56, 88, 15))
    taille = 84 if F.largeur(p["titre"], 84, "xb") < 540 else 60
    b.append(titre(p["titre"], 54, 176, taille))
    d, n = F.paragraphe(p["description"], 56, 230, 23, CL, 500, interligne=1.42, max_lignes=3)
    b.append(f'<g fill-opacity=".82">{d}</g>')
    b.append(chips(56, 300 if n <= 2 else 330, p["stack"][:4]))
    b.append(F.texte("Voir le projet", 56, 392, 18, CL, "sb") + F.texte("→", 56 + F.largeur("Voir le projet ", 18, "sb"), 392, 18, OR, "sb"))
    b.append(faisceau_bord(1, 1, W - 2, H - 2, 23))
    return svg(W, H, "".join(b), alt(p), PTS + GLOW + FLOU, 24)


def carte_moyenne(p):
    W, H = 600, 520
    b = [grille(0, 0, W, 310), lueur(480, 40, 260, 160, .8), illustration(p, 40, 14, 1.3)]
    b.append(f'<path d="M0 310 H{W}" stroke="{CL}" stroke-opacity=".08"/>')
    b.append(etiquette(p["tag"], 32, 356, 14))
    taille = 36 if F.largeur(p["titre"], 36, "xb") < W - 64 else 28
    b.append(titre(p["titre"], 31, 400, taille))
    d, _ = F.paragraphe(p["description"], 32, 438, 18, CL, 536, interligne=1.38, max_lignes=2)
    b.append(f'<g fill-opacity=".78">{d}</g>')
    b.append(F.texte(" · ".join(p["stack"]), 32, 498, 14, GT, "m"))
    b.append(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="23" fill="none" stroke="{CL}" stroke-opacity=".10"/>')
    return svg(W, H, "".join(b), alt(p), PTS + GLOW, 24)


def carte_petite(p):
    W, H = 392, 420
    b = [grille(0, 0, W, 222), illustration(p, 4, 4, .96)]
    b.append(f'<path d="M0 222 H{W}" stroke="{CL}" stroke-opacity=".08"/>')
    b.append(etiquette(p["tag"], 26, 262, 13))
    taille = 28 if F.largeur(p["titre"], 28, "xb") < W - 52 else 22
    b.append(titre(p["titre"], 25, 300, taille))
    d, _ = F.paragraphe(p["description"], 26, 334, 16, CL, W - 52, interligne=1.38, max_lignes=2)
    b.append(f'<g fill-opacity=".75">{d}</g>')
    b.append(F.texte(" · ".join(p["stack"][:2]), 26, 396, 13, GT, "m"))
    b.append(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="21" fill="none" stroke="{CL}" stroke-opacity=".10"/>')
    return svg(W, H, "".join(b), alt(p), PTS, 22)


def disposition(n):
    """Après le phare : des paires, et un trio de petites cartes si le compte est impair."""
    if n <= 0:
        return []
    if n == 1:
        return ["moyenne"]
    if n % 2 == 0:
        return ["moyenne"] * n
    return ["moyenne"] * (n - 3) + ["petite"] * 3


# ================= mode d'emploi =================
MODE = [("Méthode", "ampoule", "Pas besoin de réinventer la roue. Je m’inspire, je trouve l’astuce, je gagne du temps."),
        ("Carburant", "coeur", "Un merci sincère, et une chanson dont les paroles me parlent."),
        ("Force", "eclair", "La vivacité. Je capte vite, je m’emballe encore plus vite."),
        ("Manie", "carre", "Que tout soit carré. Vraiment tout."),
        ("Point faible", "agenda", "Les plans à long terme. J’y travaille. D’où FangUp.")]


def icone_animee(nom, x, y, taille):
    s = taille / 48

    def g(inner):
        return (f'<g transform="translate({f1(x)} {f1(y)}) scale({s:.4f})" fill="none" stroke-width="3.4" '
                f'stroke-linecap="round" stroke-linejoin="round">{inner}</g>')
    base = lambda n: ICONS[n][1].replace("{ink}", CL).replace("{ac}", OR)
    if nom == "eclair":
        return g('<animate attributeName="opacity" values="1;1;.2;1;.2;1;1" keyTimes="0;.72;.76;.8;.84;.88;1" dur="3.4s" repeatCount="indefinite"/>' + base("eclair"))
    if nom == "ampoule":
        return g(f'<circle cx="24" cy="20" r="6" fill="{OR}" stroke="none" opacity=".35"><animate attributeName="r" values="5;13;5" dur="2.6s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".45;.08;.45" dur="2.6s" repeatCount="indefinite"/></circle>' + base("ampoule"))
    if nom == "carre":
        return g(f'<rect x="8" y="10" width="30" height="30" rx="3" stroke="{CL}"/>'
                 f'<path d="M15 25 L21 31 L31 19" stroke="{CL}" stroke-dasharray="30" stroke-dashoffset="30">'
                 f'<animate attributeName="stroke-dashoffset" values="30;30;0;0" keyTimes="0;.2;.45;1" dur="3s" repeatCount="indefinite"/></path>'
                 f'<circle cx="40" cy="8" r="3.4" fill="{OR}" stroke="none"/>')
    if nom == "agenda":
        pos = [(15, 26), (24, 26), (33, 26), (15, 34), (24, 34), (33, 34)]
        return g(f'<rect x="7" y="10" width="34" height="31" rx="5" stroke="{CL}"/><path d="M7 18 H41 M16 6 V13 M32 6 V13" stroke="{CL}"/>'
                 f'<circle r="3.6" fill="{OR}" stroke="none" cx="15" cy="26">'
                 f'<animate attributeName="cx" values="{";".join(str(p[0]) for p in pos)}" dur="4.8s" calcMode="discrete" repeatCount="indefinite"/>'
                 f'<animate attributeName="cy" values="{";".join(str(p[1]) for p in pos)}" dur="4.8s" calcMode="discrete" repeatCount="indefinite"/></circle>')
    if nom == "coeur":
        return (f'<g transform="translate({f1(x + 24 * s)} {f1(y + 24 * s)})"><g>'
                f'<animateTransform attributeName="transform" type="scale" values="1;1.13;1;1.08;1;1" keyTimes="0;.1;.2;.3;.42;1" dur="1.6s" repeatCount="indefinite"/>'
                f'<g transform="translate({f1(-24 * s)} {f1(-24 * s)}) scale({s:.4f})" fill="none" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">'
                + base("coeur") + "</g></g></g>")
    return icone(nom, x, y, taille)


def mode_emploi():
    W, H = 1200, 612
    tuiles = [(0, 0, 594, 296), (606, 0, 594, 296), (0, 308, 392, 304), (404, 308, 392, 304), (808, 308, 392, 304)]
    b = []
    for (x, y, w, h), (lab, ic, phrase) in zip(tuiles, MODE):
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{MAR}"/>'
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="url(#pts)"/>')
        b.append(icone_animee(ic, x + 30, y + 30, 64))
        b.append(etiquette(lab, x + 32, y + 138, 14))
        d, _ = F.paragraphe(phrase, x + 32, y + 182, 27 if w > 500 else 24, CL, w - 64, "b", interligne=1.3)
        b.append(d)
        b.append(f'<rect x="{x + .75}" y="{y + .75}" width="{w - 1.5}" height="{h - 1.5}" rx="21.5" fill="none" stroke="{CL}" stroke-opacity=".10"/>')
    return svg(W, H, "".join(b), "Mode d’emploi. " + " ".join(f"{a} : {c}" for a, _, c in MODE), PTS, 0, None)


# ================= avec quoi je bricole =================
def outils():
    conf = yaml.safe_load(io.open(os.path.join(PROFIL, "outils.yml"), encoding="utf-8")) or {}
    cats = [(c["nom"], c.get("icone") if c.get("icone") in ICONS else "code", [str(o) for o in c.get("outils") or []])
            for c in (conf.get("categories") or [])][:6]
    W, cw, R = 1200, 320, 82
    nl = math.ceil(len(cats) / 2)
    colonnes = [cats[:nl], cats[nl:]]

    def hauteur(items):
        return 104 + len(F.couper(" · ".join(items), 17, cw - 48, "m")) * 25.5 + 22
    hs = [[hauteur(i) for _, _, i in col] for col in colonnes]
    H = max(64 * 2 + sum(h) + 72 * (len(h) - 1) for h in hs if h)
    H = max(H, 420)
    cx, cy = W / 2, H / 2
    b = [lueur(cx, cy, 360, 260), grille(0, 0, W, H)]
    k = 0
    for c, (col, hc) in enumerate(zip(colonnes, hs)):
        total = sum(hc) + 72 * (len(hc) - 1)
        y = (H - total) / 2
        x = 56 if c == 0 else W - 56 - cw
        for (nom, ic, items), h in zip(col, hc):
            gauche = c == 0
            sx, sy = (x + cw, y + h / 2) if gauche else (x, y + h / 2)
            ey = cy + max(-30, min(30, (sy - cy) * .25))
            ex = cx - R - 4 if gauche else cx + R + 4
            c1, c2 = sx + (90 if gauche else -90), ex + (-90 if gauche else 90)
            d = f"M{f1(sx)} {f1(sy)} C{f1(c1)} {f1(sy)}, {f1(c2)} {f1(ey)}, {f1(ex)} {f1(ey)}"
            b.append(f'<path d="{d}" fill="none" stroke="{CL}" stroke-opacity=".14" stroke-width="2"/>')
            for L, op in ((34, .35), (14, 1)):
                b.append(f'<path d="{d}" fill="none" stroke="{OR}" stroke-width="3" stroke-opacity="{op}" stroke-linecap="round" pathLength="100" '
                         f'stroke-dasharray="{L} 130" stroke-dashoffset="{L}"><animate attributeName="stroke-dashoffset" values="{L};{L - 134}" '
                         f'dur="2.8s" begin="{k * .7:.1f}s" repeatCount="indefinite"/></path>')
            b.append(f'<rect x="{f1(x)}" y="{f1(y)}" width="{cw}" height="{f1(h)}" rx="18" fill="{MAR}" stroke="{CL}" stroke-opacity=".14"/>')
            b.append(f'<g transform="translate({f1(x + 44)} {f1(y + 46)})">{pastille(ic, 22)}</g>')
            b.append(F.texte(nom, x + 80, y + 54, 23, CL, "b"))
            t, _ = F.paragraphe(" · ".join(items), x + 24, y + 104, 17, CL, cw - 48, "m", interligne=1.5)
            b.append(f'<g fill-opacity=".78">{t}</g>')
            y += h + 72
            k += 1
    b.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{R}" fill="{ARC}" stroke="{CL}" stroke-opacity=".16"/>')
    b.append(pulse(cx, cy, R, 2.8, 0, CL, 1.5, 1.35, .35))
    b.append(monogramme(cx - 92 * MONO_W / 2, cy - 46, 92))
    texte_alt = "Mes outils. " + " ".join(f"{n} : {', '.join(i)}." for n, _, i in cats)
    return svg(W, math.ceil(H), "".join(b), texte_alt, PTS + GLOW, 24)


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


# ================= README =================
DEBUT, FIN = "<!-- boite-a-trucs:debut -->", "<!-- boite-a-trucs:fin -->"


def section_readme(liste):
    lien = lambda p, w: (f'  <a href="{p["url"]}"><img src="profil/images/projets/{p["fichier"]}.svg" '
                         f'alt="{esc(alt(p))}" width="{w}"></a>')
    lignes = ['<p align="center">', lien(liste[0], "100%")]
    for genre, p in zip(disposition(len(liste) - 1), liste[1:]):
        lignes.append(lien(p, "49%" if genre == "moyenne" else "32%"))
    lignes.append("</p>")
    return "\n".join(lignes)


def ecrire(chemin, contenu):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    ancien = io.open(chemin, encoding="utf-8").read() if os.path.exists(chemin) else None
    if ancien != contenu:
        io.open(chemin, "w", encoding="utf-8", newline="\n").write(contenu)
        return True
    return False


def main():
    liste_api = depots()
    liste = projets(liste_api)
    if not liste:
        sys.exit("Aucun projet trouvé : rien n'est modifié.")
    changes = []
    images = {"heros.svg": heros(len(liste_api)), "mode-d-emploi.svg": mode_emploi(), "outils.svg": outils(), "on-se-parle.svg": pied()}
    genres = ["phare"] + disposition(len(liste) - 1)
    dessin = dict(phare=carte_phare, moyenne=carte_moyenne, petite=carte_petite)
    for genre, p in zip(genres, liste):
        images[f"projets/{p['fichier']}.svg"] = dessin[genre](p)
    for nom, contenu in images.items():
        if ecrire(os.path.join(IMAGES, nom), contenu):
            changes.append(nom)
    gardes = {f"{p['fichier']}.svg" for p in liste}
    dossier = os.path.join(IMAGES, "projets")
    for f in sorted(os.listdir(dossier)):
        if f.endswith(".svg") and f not in gardes:
            os.remove(os.path.join(dossier, f))
            changes.append(f"projets/{f} (retiré)")
    readme = os.path.join(RACINE, "README.md")
    s = io.open(readme, encoding="utf-8").read()
    if DEBUT in s and FIN in s:
        i, j = s.index(DEBUT) + len(DEBUT), s.index(FIN)
        if ecrire(readme, s[:i] + "\n" + section_readme(liste) + "\n" + s[j:]):
            changes.append("README.md")
    else:
        print("  ! marqueurs boite-a-trucs absents du README : section non mise à jour")
    print(f"{len(liste)} projets ({', '.join(p['depot'] for p in liste)})")
    print("modifié : " + (", ".join(changes) if changes else "rien"))


if __name__ == "__main__":
    main()
