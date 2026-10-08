# Les images du profil

Toutes les images animées du README sortent d'ici. L'Action [Profil](../.github/workflows/profil.yml) les redessine chaque nuit.

## Ajouter un projet dans « ma boîte à trucs »

1. Sur la page du dépôt, clique sur la roue dentée à côté de **About**.
2. Dans **Topics**, ajoute `boite-a-trucs`.
3. La carte arrive cette nuit. Pour l'avoir tout de suite : **Actions > Profil > Run workflow**.

La carte reprend la description du dépôt, et devine la catégorie, les technos et l'icône d'après ses sujets.
Pour changer un texte ou mettre un dessin sur mesure, ajoute le dépôt dans [`projets.yml`](projets.yml).

- **Projet phare** (la grande carte du haut) : sujet `phare` sur le dépôt, ou `phare: true` dans `projets.yml`.
- **Retirer un projet** : enlève le sujet, ou mets `cacher: true` dans `projets.yml`.
- **La mise en page s'adapte** : le phare, puis des paires, et un trio de petites cartes si le compte est impair.

## Changer les outils

Modifie [`outils.yml`](outils.yml). L'image « avec quoi je bricole » se redessine dès que le fichier change.

## Le reste

| Fichier | Ce que c'est |
| --- | --- |
| `images/heros.svg` | Le terminal du haut. Le nombre de projets se met à jour tout seul. |
| `images/projets/` | Une carte par projet |
| `images/mode-d-emploi.svg` | Les cinq cartes du mode d'emploi |
| `images/outils.svg` | Les outils reliés au b |
| `images/on-se-parle.svg` | Le pied de page |
| `moteur/` | Le générateur, en Python. En local : `pip install fonttools pyyaml`, puis `python profil/moteur/generer.py` |

Police : Inter, sous licence [SIL Open Font License](moteur/polices/OFL.txt).
