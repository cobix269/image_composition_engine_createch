# Image Composition Engine

Projet du duo Romain Decrand Lardière et Zoé Desfretier.
Binôme de binôme : Raphael De Rouvre et Paco Tibherin.

## Lancement

Avec Python 3.14 et `uv`, depuis la racine du projet :

```sh
uv sync --locked
uv run image-composition-engine-createch
```

Le moteur lit `conf.yml`, applique les filtres de chaque calque, superpose les
calques et affiche le résultat. Dans VS Code, F5 (configuration « Image
Composition Engine ») et le bouton de Code Runner lancent la même commande.

## Organisation

```text
conf.yml                    # Composition à afficher
images/                     # Images utilisées par conf.yml
src/image_composition_engine_createch/
├── filters/
│   ├── __init__.py         # FILTERS : noms des filtres dans le YAML
│   ├── base.py             # Filter : contrat commun des filtres
│   ├── ours.py             # Nos filtres
│   └── imported.py         # Filtres de l'autre groupe, non retouchés
├── blends.py               # Modes de fusion et BLENDS : leurs noms dans le YAML
├── config.py               # Lecture et validation du YAML
├── layer.py                # Layer : couleurs, alpha, opacité et blend
├── composition.py          # Création des calques et composition
├── imageIO.py              # Lecture et affichage des images
└── main.py                 # Point d'entrée
```

Les dépendances vont dans un seul sens : `main` utilise `composition`, qui
utilise `config`, `layer` et `blends`, qui utilisent `filters`.

`main.py` enchaîne `readConfig()`, `createLayers()`, `compose()` puis
`showFromArray()`. Dans tout le moteur, une image est un tableau NumPy en
flottants entre 0 et 1 ; la conversion en 8 bits n'a lieu qu'à l'affichage.
Toutes les images d'entrée ont les mêmes dimensions.

## Configuration

```yaml
layers:                       # du fond vers le dessus
  - image: images/0_photo.jpg
    filters:
      - name: gaussianBlur
        params: {window: 5, sigma: 2.0}
  - image: images/1_pop_bike.png
    blend: multiply           # normal par défaut
    opacity: 0.5              # entre 0 et 1, 1 par défaut
```

Les chemins d'images sont relatifs au fichier YAML.
Le YAML est validé par Pydantic dès sa lecture : une clé inconnue, une opacité
hors de [0, 1], un nom de filtre ou de blend inconnu produisent une erreur qui
indique le numéro du calque. Les paramètres d'un filtre sont validés par sa
classe, au moment de créer le calque.

## Filtres

| Nom | Paramètres | Effet |
| --- | --- | --- |
| `normal` | | aucun |
| `grayscale` | | niveaux de gris |
| `swapBG` | | échange le bleu et le vert |
| `brightness` | `value` ≥ 0 | multiplie les couleurs : 0 donne du noir, 1 ne change rien |
| `contrast` | 0 < `value` ≤ 5 | écarte les couleurs du gris moyen (> 1) ou les en rapproche (< 1) |
| `blur` | `radius` ≥ 0 | flou moyen sur un carré de côté 2 × `radius` + 1 |
| `gaussianBlur` | `window` ≥ 1, `sigma` > 0 | flou gaussien |
| `blackBorder` | `thickness` ≥ 0, 10 par défaut | bordure noire |
| `invert` | | négatif |
| `sepia` | | sépia |
| `importedNormal`, `importedGrayscale`, `importedSepia` | | versions de l'autre groupe |
| `importedBlur` | `taille` ≥ 1, 5 par défaut | flou moyen de l'autre groupe |
| `importedGaussianBlur` | `window` ≥ 1, `sigma` > 0 | flou gaussien de l'autre groupe |
| `importedBlackBorder` | `border_size` ≥ 1 | bordure noire de l'autre groupe |

## Partager des filtres

Un filtre est une dataclass Pydantic qui hérite de `Filter`
(`filters/base.py`). Ses paramètres sont ses champs, avec leurs contraintes ;
`Filter` impose en plus des types stricts, des nombres finis et refuse les
paramètres inconnus.

`apply(image)` reçoit une image RGB de forme `(hauteur, largeur, 3)` en
flottants entre 0 et 1, et renvoie une image de même forme, entre 0 et 1. Elle
peut modifier l'image reçue. Un filtre ne voit jamais l'alpha : `Layer` le
conserve.

```python
import numpy as np
from pydantic import Field
from pydantic.dataclasses import dataclass

from .base import Filter


@dataclass
class Brightness(Filter):
    value: float = Field(ge=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        return np.clip(image * self.value, 0, 1)
```

Pour donner nos filtres à un autre groupe, `filters/base.py` et
`filters/ours.py` suffisent. Ils ne dépendent que de NumPy, SciPy et Pydantic.

Pour utiliser les filtres d'un autre groupe :

1. Copier leurs classes dans `filters/imported.py` sans les modifier ;
   seul l'import de `Filter` est à adapter.
2. Leur donner un nom préfixé par `imported` dans `FILTERS`, dans
   `filters/__init__.py`.
3. Utiliser ce nom dans le YAML, avec leurs paramètres dans `params`.

## Modes de fusion

Modes disponibles : `normal`, `darken`, `multiply`, `color_burn`,
`linear_burn`, `lighten`, `screen`, `color_dodge`, `linear_dodge`,
`overlay`, `soft_light`, `hard_light`, `vivid_light`, `linear_light`,
`pin_light`, `difference`, `exclusion`. Pour en ajouter un, écrire sa fonction
dans `blends.py` puis lui donner un nom dans `BLENDS`, en bas du même fichier.

Les formules viennent du [tableau Deep Sky Colors](https://www.deepskycolors.com/apps/formulas-for-photoshop-blending-modes/).
Certaines sont approximatives et ne reproduisent pas exactement Photoshop. En
particulier, `soft_light` utilise l'approximation de cette référence et
`vivid_light` reprend les branches de son tableau. Les divisions par zéro ont
un résultat borné.

En partant d'un fond noir, `compose(layers)` traite chaque calque ainsi :

1. `couleur = blend(fond, calque)`, bornée entre 0 et 1 ;
2. `alpha = opacity × alpha du pixel` ;
3. `fond = (1 - alpha) × fond + alpha × couleur`.

Un pixel transparent ou une opacité nulle laisse donc le fond intact. Les
calques ne sont pas modifiés.
