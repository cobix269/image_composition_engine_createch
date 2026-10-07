# Image Composition Engine

## Lancement

Avec Python 3.14 et `uv`, depuis la racine du projet :

```sh
uv sync --locked
uv run image-composition-engine-createch
```

Le moteur lit `conf.yml` et affiche la composition. Les chemins d'images du
YAML sont relatifs à `src/image_composition_engine_createch`.

## Organisation et utilitaires

- `main.py` orchestre le chargement, les filtres dans l'ordre et la composition.
- `parseYaml.py` lit le YAML et valide la configuration.
- `classes.py` contient `Layer`, les registres de filtres et les modèles de validation.
- `filters.py` contient les traitements des pixels ; `blend.py` contient les modes de fusion.
- `utils.py` regroupe les opérations communes ci-dessous.

| Fonction de `utils.py` | Utilisation |
| --- | --- |
| `array_from_file` | `Layer` charge son image en RGBA. |
| `compose` | `main` superpose les calques. |
| `show_from_array` | `main` affiche le résultat. |
| `array_to_image` | `show_from_array` convertit le tableau pour Pillow. |

## Échanger un filtre

Le contrat actuel est simple : une fonction reçoit le calque en premier argument,
travaille sur `layer.pixels` et renvoie le calque. Les pixels sont un tableau NumPy
RGBA de forme `(hauteur, largeur, 4)`, en `uint8` entre 0 et 255. Les filtres de
couleur conservent l'alpha, les dimensions, l'opacité et le mode de blend.
Un filtre peut modifier les pixels en place ou renvoyer un nouveau calque respectant
ce contrat ; le moteur récupère toujours sa valeur de retour.

Pour importer un filtre d'un autre groupe :

1. Copier son fichier dans `src/image_composition_engine_createch/`.
2. Dans `classes.py`, ajouter par exemple `from .filtres_groupe import mon_filtre`,
   puis l'entrée `"mon_filtre": mon_filtre` dans `Layer.FILTERS`.
3. Utiliser `name: mon_filtre` dans le YAML, avec ses paramètres dans `params`.

Il n'est pas nécessaire d'ajouter une méthode à `Layer` ou de changer le moteur.
L'ajout dans `Layer.FILTER_PARAMS` est facultatif : sans modèle Pydantic, les
paramètres du YAML sont transmis tels quels. Les filtres du projet gardent leur
validation stricte.

Le moteur utilise `fonction(layer, **params)` : l'ordre des paramètres nommés
n'a pas d'importance. Le YAML doit simplement reprendre les noms attendus par
la fonction importée. Une signature différente peut être adaptée lors de l'exercice.
Un filtre n'a pas besoin d'importer notre classe `Layer` à l'exécution : il suffit
qu'il utilise les attributs du contrat. Cela évite aussi les imports circulaires.
Les dépendances Python de son fichier doivent être disponibles.
Notre `filters.py` n'importe à l'exécution que NumPy et SciPy ; il peut donc
être copié dans un autre groupe respectant le même contrat de calque.

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

1. `blendColors(fond, dessus, mode)`, dans `blend.py`, calcule la couleur mélangée. Les pixels
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
