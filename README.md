# Image Composition Engine

## Lancement

Avec Python 3.14 et `uv`, depuis la racine du projet :

```sh
uv sync --locked
uv run image-composition-engine-createch
```
Projet du duo : Romain Decrand Lardière et Zoé Desfretier 
Binôme de Binôme : Raphael De Rouvre et Paco Tibherin 

Le moteur lit `conf.yml` et affiche la composition. Les chemins d'images du
YAML sont relatifs à `src/image_composition_engine_createch`.

## Organisation

```text
src/image_composition_engine_createch/
├── classes/
│   ├── base.py             # Filter, Blend et règles Pydantic
│   ├── layer.py            # Layer et registres
│   ├── filters.py          # Nos filtres
│   ├── importedFilters.py  # Filtres de l'autre groupe
│   └── blends.py           # Modes de fusion et validation Pydantic
├── utils/
│   ├── imageIO.py          # Lecture, conversion et affichage des images
│   ├── parseYaml.py        # Lecture et validation du YAML
│   └── composition.py      # Création des calques et composition
└── main.py                 # Point d'entrée
```

`main.py` lit le YAML, appelle `createLayers()`, puis affiche `compose(layers)`.
Les registres `FILTERS` et `BLENDS` sont des dictionnaires explicites dans leurs
modules, accessibles via `Layer.FILTERS` et `Layer.BLENDS`. Les traitements
ne dépendent pas de `Layer`, et les imports n'ont aucun enregistrement caché.

## Échanger un filtre

Une classe de filtre reçoit ses paramètres au constructeur et expose
`apply(image)`. L'image reçue est un tableau NumPy RGB de forme
`(hauteur, largeur, 3)`, en flottants entre 0 et 1. La méthode renvoie une image
RGB de mêmes dimensions. `Layer.applyFilter()` gère la conversion avec nos
pixels uint8 de 0 à 255 et conserve l'alpha, l'opacité et le mode de blend.

Pour importer un filtre d'un autre groupe :

1. Ajouter la classe dans `classes/importedFilters.py`, au format ci-dessous.
2. Ajouter `"monFiltre": MonFiltre` dans le dictionnaire `FILTERS` de ce fichier.
3. Utiliser `name: monFiltre` dans le YAML, avec les arguments dans `params`.

Les paramètres sont des attributs de dataclass avec leurs contraintes Pydantic.
Le décorateur génère le constructeur et valide les arguments. La configuration
héritée de `Filter` impose des types stricts, des nombres finis et refuse les
paramètres inconnus. `parseYaml.py` transforme les erreurs en `ValueError` avec
le numéro du calque, le nom du filtre et le paramètre concerné.

```python
import numpy as np
from pydantic import Field
from pydantic.dataclasses import dataclass
from .base import Filter


@dataclass
class MonFiltre(Filter):
    value: float = Field(default=1.0, ge=0)

    def apply(self, image: np.ndarray) -> np.ndarray:
        return np.clip(image * self.value, 0, 1)
```

Le moteur utilise `ClasseFiltre(**params)`, puis `layer.applyFilter(instance)`.
Les classes n'ont pas besoin de connaître `Layer`, ce qui évite les imports
circulaires. Les filtres importés sont enregistrés sous des noms comme
`importedGaussianBlur` et `importedSepia`, sans adaptateur.

`blur` est le flou moyen et prend `radius`. `gaussianBlur` prend `window` et
`sigma`. Pour les classes importées, `importedBlur` prend `taille` (5 par défaut)
et `importedBlackBorder` prend `border_size`.

`brightness(value)` multiplie les couleurs : `0` donne du noir, `1` conserve
l'image, une valeur supérieure à `1` éclaircit. `contrast(value)` agit autour
du gris moyen. Les deux conservent la transparence.

## Blend des calques

Les calques sont composés dans l'ordre du YAML : le premier est au fond,
les suivants passent au-dessus. Toutes les images ont les mêmes dimensions.
Le résultat est RGB, sur un fond noir, comme dans la composition initiale.

```yaml
layers:
  - image: images/0_photo.jpg
  - image: images/1_pop_bike.png
    blend: multiply
    opacity: 0.5
```

`blend` vaut `normal` lorsqu'il est absent. L'opacité du YAML vaut `1.0`
lorsqu'elle est absente et doit être comprise entre 0 et 1.

Modes disponibles : `normal`, `darken`, `multiply`, `color_burn`,
`linear_burn`, `lighten`, `screen`, `color_dodge`, `linear_dodge`,
`overlay`, `soft_light`, `hard_light`, `vivid_light`, `linear_light`,
`pin_light`, `difference`, `exclusion`.

Les formules viennent du [tableau Deep Sky Colors](https://www.deepskycolors.com/apps/formulas-for-photoshop-blending-modes/).
Il s'agit des formules de cette référence, dont certaines sont approximatives,
et non d'une reproduction exacte de Photoshop. En particulier, `soft_light`
utilise son approximation et `vivid_light` reprend les branches de son tableau.
Les divisions par zéro ont un résultat borné ; les couleurs hors plage sont
bornées entre 0 et 1 avant l'application de l'opacité.

Le calcul suit deux étapes :

1. `blendColors(fond, dessus, mode)`, dans `utils/composition.py`, calcule la couleur mélangée. Les pixels
   sont convertis en flottants entre 0 et 1 pour les formules, puis remis entre
   0 et 255. Par exemple, `multiply` multiplie les deux couleurs normalisées ;
   `lighten` garde la plus grande valeur de chaque canal R, G et B.
2. `compose(layers)` dose cette couleur avec
   `alpha = opacity * alpha_du_pixel / 255` pour un calque RGBA, ou simplement
   `alpha = opacity` en RGB. Ensuite :
   `résultat = (1 - alpha) * fond + alpha * couleur_mélangée`.

Un pixel transparent ou une opacité nulle laisse donc le fond intact.
Les calques d'entrée ne sont pas modifiés et le résultat est arrondi une fois,
à la fin, en `uint8`. Un mode inconnu produit une erreur indiquant le numéro
du calque et les modes disponibles.
