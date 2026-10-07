# Image Composition Engine

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

Le calcul dans `utils.py` suit deux étapes :

1. `blend_colors(fond, dessus, mode)` calcule la couleur mélangée. Les pixels
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
