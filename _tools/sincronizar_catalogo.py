# -*- coding: utf-8 -*-
"""Valida un CSV exportado de la hoja maestra y actualiza el catálogo.

Uso seguro:
    python _tools/sincronizar_catalogo.py inventario.csv --revisar
    python _tools/sincronizar_catalogo.py inventario.csv --aplicar

La eliminación de códigos existentes se bloquea salvo que se autorice con
--permitir-retirados. Los textos SEO se derivan de los datos comerciales para
que un cambio de precio o talla no deje descripciones desactualizadas.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
from pathlib import Path
import re
import sys
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CATALOGO = ROOT / "_data" / "catalogo.json"
FOTOS = ROOT / "assets" / "productos"

HEADERS = [
    "Código", "Nombre", "Categoría", "Precio USD", "Tallas", "Colores",
    "Estado", "Destacada", "Fotos", "Notas",
]
CATEGORIES = {
    "vestidos y faldas": "vestido",
    "blusas": "blusa",
    "jeans y pantalones": "pantalon",
    "conjuntos": "conjunto",
}
TRUE_VALUES = {"si", "sí", "s", "yes", "true", "1"}
FALSE_VALUES = {"no", "n", "false", "0"}


def plain(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    return "".join(c for c in value if not unicodedata.combining(c)).strip().lower()


def split_values(value: str, separator: str) -> list[str]:
    return [part.strip() for part in value.split(separator) if part.strip()]


def money(value: str, row_number: int) -> float | int:
    cleaned = value.replace("$", "").replace(",", "").strip()
    try:
        amount = round(float(cleaned), 2)
    except ValueError as exc:
        raise ValueError(f"fila {row_number}: Precio USD no es numérico") from exc
    if amount <= 0:
        raise ValueError(f"fila {row_number}: Precio USD debe ser mayor que cero")
    return int(amount) if amount.is_integer() else amount


def yes_no(value: str, row_number: int, field: str) -> bool:
    normalized = plain(value)
    if normalized in {plain(v) for v in TRUE_VALUES}:
        return True
    if normalized in {plain(v) for v in FALSE_VALUES}:
        return False
    raise ValueError(f"fila {row_number}: {field} debe ser Sí o No")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        actual = [name.strip() if name else "" for name in (reader.fieldnames or [])]
        if actual != HEADERS:
            raise ValueError(
                "Encabezados incorrectos. Se esperaba:\n  " + " | ".join(HEADERS)
                + "\nSe recibió:\n  " + " | ".join(actual)
            )
        return [row for row in reader if any((value or "").strip() for value in row.values())]


def validate_product(row: dict[str, str], row_number: int, allowed_sizes: set[str]) -> dict:
    product_id = row["Código"].strip()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", product_id):
        raise ValueError(f"fila {row_number}: Código inválido: {product_id!r}")
    name = row["Nombre"].strip()
    if not name:
        raise ValueError(f"fila {row_number}: falta Nombre")
    category_label = plain(row["Categoría"])
    if category_label not in CATEGORIES:
        raise ValueError(f"fila {row_number}: Categoría no reconocida: {row['Categoría']!r}")
    sizes = split_values(row["Tallas"], ",")
    if not sizes:
        raise ValueError(f"fila {row_number}: falta Tallas")
    unknown_sizes = [size for size in sizes if size not in allowed_sizes]
    if unknown_sizes:
        raise ValueError(f"fila {row_number}: tallas no reconocidas: {', '.join(unknown_sizes)}")
    try:
        colors = int(row["Colores"].strip())
    except ValueError as exc:
        raise ValueError(f"fila {row_number}: Colores debe ser un número entero") from exc
    if colors < 1:
        raise ValueError(f"fila {row_number}: Colores debe ser al menos 1")
    status = plain(row["Estado"])
    if status not in {"disponible", "agotada"}:
        raise ValueError(f"fila {row_number}: Estado debe ser Disponible o Agotada")
    photos = split_values(row["Fotos"], ";")
    if not photos:
        raise ValueError(f"fila {row_number}: falta Fotos")
    for photo in photos:
        if Path(photo).name != photo or not photo.lower().endswith(".webp"):
            raise ValueError(f"fila {row_number}: nombre de foto inválido: {photo!r}")
        stem = photo[:-5]
        for variant in (photo, f"{stem}-800.webp", f"{stem}-480.webp"):
            if not (FOTOS / variant).is_file():
                raise ValueError(f"fila {row_number}: falta assets/productos/{variant}")
    price = money(row["Precio USD"], row_number)
    price_text = f"{float(price):.2f}"
    product = {
        "id": product_id,
        "descripcion": (
            f"{name} de BOLEM en tallas {', '.join(sizes)}. "
            f"Precio ${price_text} USD. Consultá disponibilidad por WhatsApp."
        ),
        "nombre": name,
        "categoria": CATEGORIES[category_label],
        "precio": price,
        "tallas": sizes,
        "tallas_texto_original": "–".join(sizes),
        "colores": colors,
        "fotos": photos,
        "destacada": yes_no(row["Destacada"], row_number, "Destacada"),
        "alt": f"{name} — BOLEM El Salvador",
    }
    if status == "agotada":
        product["agotada"] = True
    return product


def changed_fields(before: dict, after: dict) -> list[str]:
    keys = sorted(set(before) | set(after))
    return [key for key in keys if before.get(key) != after.get(key)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza el catálogo BOLEM desde CSV")
    parser.add_argument("csv", type=Path, help="CSV de la pestaña Inventario")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--revisar", action="store_true", help="valida y muestra cambios sin escribir")
    mode.add_argument("--aplicar", action="store_true", help="actualiza _data/catalogo.json")
    parser.add_argument("--permitir-retirados", action="store_true", help="permite eliminar códigos existentes")
    args = parser.parse_args()

    if not args.csv.is_file():
        parser.error(f"no existe el archivo: {args.csv}")
    current = json.loads(CATALOGO.read_text(encoding="utf-8"))
    rows = read_rows(args.csv)
    products = []
    errors = []
    for index, row in enumerate(rows, start=2):
        try:
            products.append(validate_product(row, index, set(current["escala_tallas"])))
        except ValueError as exc:
            errors.append(str(exc))
    ids = [product["id"] for product in products]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append("Códigos duplicados: " + ", ".join(duplicates))
    if errors:
        print("NO SE APLICÓ NINGÚN CAMBIO")
        for error in errors:
            print("-", error)
        return 1

    old_by_id = {product["id"]: product for product in current["productos"]}
    new_by_id = {product["id"]: product for product in products}
    added = [item for item in ids if item not in old_by_id]
    removed = [item for item in old_by_id if item not in new_by_id]
    changed = {
        item: changed_fields(old_by_id[item], new_by_id[item])
        for item in ids if item in old_by_id and old_by_id[item] != new_by_id[item]
    }
    print(f"Productos: {len(old_by_id)} -> {len(new_by_id)}")
    print("Nuevos:", ", ".join(added) if added else "ninguno")
    print("Retirados:", ", ".join(removed) if removed else "ninguno")
    if changed:
        print("Modificados:")
        for item, fields in changed.items():
            print(f"- {item}: {', '.join(fields)}")
    else:
        print("Modificados: ninguno")
    if removed and not args.permitir_retirados:
        print("BLOQUEADO: use --permitir-retirados después de revisar redirecciones.")
        return 2
    if args.revisar:
        print("REVISIÓN COMPLETA: no se escribió ningún archivo.")
        return 0

    current["_nota"] = (
        "Fuente única del catálogo, sincronizada desde la hoja maestra BOLEM. "
        "Precios, tallas, estado y fotografías se validan antes de generar el sitio."
    )
    current["productos"] = products
    temp = CATALOGO.with_suffix(".json.tmp")
    temp.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, CATALOGO)
    print("APLICADO:", CATALOGO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
