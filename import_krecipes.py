import re
import sys
import sqlite3
from collections import defaultdict
from pprint import pprint
from typing import List
import os
import locale

locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")

SQL_RECIPES = """
SELECT r.*
FROM recipes r
"""

SQL_CATEGORIES = """
SELECT name from recipes r
    left outer join category_list cl on r.id = cl.recipe_id
    left outer join categories c on cl.category_id = c.id
where r.id = ? and name is not null;
"""

SQL_INGREDIENT_LIST = """
SELECT * from ingredient_list where recipe_id = ? order by order_index
"""

SQL_PREPARATIONS = """
select pm.name
from prep_method_list pml
    inner join prep_methods pm on pm.id = pml.prep_method_id
where ingredient_list_id = ?
order by pml.order_index;
"""

RE_RECIPE_TITLE = re.compile(r"(?:.?\d+\.-\s*)?(.*)")

TEMPLATE_CONTENT = """
---
draft: false
title: "{title}"
recipe_image: "images/defaultImage.png"
image_width: 512
image_height: 512
date: "{ctime}"
lastmod: "{mtime}"
servings: {servings}
prep_time: {prep_time}
categorias:
{categorias}
ingredientes:
{ingredientes}
---

## Ingredientes
{ingredientes_md}

## Preparación
{preparacion_md}
"""

CACHE = {
    'yield_types': {},
    'ingredients': {},
#    'prep_methods': {},
    'units': {}
}

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def setup_db(filename):
    print(f"Opening db file {filename}")
    db = sqlite3.connect(filename)
    db.row_factory = dict_factory

    print("Filling caches")
    for table in CACHE.keys():
        print(f"\tfilling {table}")
        for row in db.execute(f"SELECT * FROM {table}"):
            CACHE[table][row["id"]] = row

    return db

def read_recipes(db):
    for recipe in db.execute(SQL_RECIPES):
        recipe['title'] = RE_RECIPE_TITLE.match(recipe['title']).group(1)

        prep_hour, prep_minutes, prep_seconds = recipe['prep_time'].split(":")
        recipe['prep_time'] = (int(prep_hour) * 60 + int(prep_minutes)) or ""


        if recipe['yield_type_id'] in (5, 7, 8, 10, 11, 14, -1):
            recipe['servings'] = int(recipe['yield_amount'])
        else:
            yield_type_name = CACHE["yield_types"][recipe["yield_type_id"]]["name"]
            recipe['servings'] = f"{int(recipe['yield_amount'])} ({yield_type_name})"

        read_categorias(db, recipe)
        read_ingredientes(db, recipe)
        read_preparacion(db, recipe)

        slug = recipe['title'].lower().replace(" ", "_") + ".md"
        slug = slug.translate(str.maketrans("áéíóúñü /", "aeiounu_-"))

        print(f"Processing recipe {recipe['title']} ({slug})")
        with open(os.path.join("content", slug), "+w") as fout:
            fout.write(TEMPLATE_CONTENT.format(**recipe))

def read_categorias(db, recipe):
    categorias = ""
    for categoria in db.execute(SQL_CATEGORIES, (recipe['id'],)):
        categorias += f"  - {categoria['name']}\n"
    recipe['categorias'] = categorias

def get_preparations(db, ingredient_list_id) -> List[str]:
    preparations = []
    for row in db.execute(SQL_PREPARATIONS, (ingredient_list_id,)):
        preparations.append(row['name'])
    return " ".join(preparations)

def read_ingredientes(db, recipe):
    ingredientes = []
    ingredientes_md = []
    substitutos = defaultdict(list)  # Ingrediente: [substitutos]

    for ingrediente in db.execute(SQL_INGREDIENT_LIST, (recipe['id'],)):
        ingrediente_name = CACHE["ingredients"][ingrediente['ingredient_id']]['name'].strip()
        amount = ingrediente['amount']
        unit_row = CACHE['units'][ingrediente['unit_id']]
        if amount == 1:
            unit = unit_row['name']
        else:
            unit = unit_row['plural']
        preparations = get_preparations(db, ingrediente['id'])

        if amount:
            linea_ingrediente = f"- {amount:.3n} {unit} de {ingrediente_name}"
        else:
            linea_ingrediente = f"- {ingrediente_name}"

        if preparations:
            linea_ingrediente += " " + preparations

        if ingrediente["substitute_for"] in CACHE["ingredients"]:
            ingrediente_sustituido = CACHE["ingredients"][ingrediente["substitute_for"]]['name']
            substitutos[ingrediente_sustituido].append(linea_ingrediente)
        else:
            ingredientes.append(f"  - {ingrediente_name}")
            ingredientes_md.append(linea_ingrediente)

    recipe['ingredientes'] = "\n".join(ingredientes)
    recipe['ingredientes_md'] = "\n".join(ingredientes_md)

    if substitutos:
        for sustituido, sustitutos in substitutos.items():
            recipe['ingredientes_md'] += f"\n#### Sustitutos de {sustituido}\n"
            recipe['ingredientes_md'] += "\n".join(sustitutos)


def read_preparacion(db, recipe):
    recipe['preparacion_md'] = ""
    for instruction in recipe['instructions'].splitlines():
        recipe['preparacion_md'] += f"{instruction}\n\n"

if __name__ == '__main__':
    if len(sys.argv) == 1:
        dbfile = 'Krecipes.krecdb'
    else:
        dbfile = sys.argv[1]
    db = setup_db(dbfile)
    read_recipes(db)