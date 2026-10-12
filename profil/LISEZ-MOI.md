# Les images du profil

Les images du README sortent d'ici. L'Action [Profil](../.github/workflows/profil.yml) les redessine toutes les heures.

## Changer le mode d'emploi

Modifie [`mode-d-emploi.yml`](mode-d-emploi.yml) : une ligne par trait de caractère.

## Changer les outils

Modifie [`outils.yml`](outils.yml). L'image « avec quoi je bricole » se redessine dès que le fichier change, avec le logo de chaque outil quand il existe. Elle existe en version claire et sombre : GitHub affiche celle qui va avec le thème du visiteur.

## Le reste

| Fichier | Ce que c'est |
| --- | --- |
| `images/heros.svg` | Le terminal du haut. Le nombre de projets se met à jour tout seul. |
| `images/mode-d-emploi-clair.svg`, `images/mode-d-emploi-sombre.svg` | Le mode d'emploi |
| `images/outils-clair.svg`, `images/outils-sombre.svg` | Les outils et leurs logos |
| `images/en-chiffres-clair.svg`, `images/en-chiffres-sombre.svg` | Contributions, commits, dépôts, abonnés et langages, mis à jour toutes les heures (hors notebooks pour les langages) |
| `images/on-se-parle.svg` | Le pied de page |
| `moteur/` | Le générateur, en Python. En local : `pip install fonttools pyyaml`, puis `python profil/moteur/generer.py` |

Police : Inter, sous licence [SIL Open Font License](moteur/polices/OFL.txt). Logos : [Simple Icons](https://simpleicons.org), licence CC0.
