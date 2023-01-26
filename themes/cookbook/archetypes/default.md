---
draft: false
title: "Title for your recipe"
recipe_image: {{ .Site.Params.front.defaultImage | default "images/defaultImage.png" }} #The image for your recipe
image_width: {{ .Site.Params.front.defaultImageWidth | default 512 }}
image_height: {{ .Site.Params.front.defaultImageHeight | default 512 }}
date: {{ .Date }}
lastmod: {{ .Date }}
servings: 4
prep_time: 15 #in minutes #can be BLANK

categorias: ["vegano", "principal"]
ingredientes: ["ajo", "cebolla", "arroz"]
---


## Ingredientes

#### Ingredientes sub apartado

- First Ingredient
- Second Ingredient [^1]
- Third Ingredient
- Fourth Ingredient
- Fifth Ingredient


## Preparación

1. Step One
   1. Sub Step One
2. Step Two
3. Step Three
4. Step Four
5. Step Five
6. Step Six

#### Notas al pie

[^1]: Footnote 1
