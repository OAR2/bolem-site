# -*- coding: utf-8 -*-
"""Extrae el catalogo a UNA fuente unica: _data/catalogo.json

Hoy los datos de cada prenda viven repetidos en el HTML: las tarjetas de la
coleccion, su JSON-LD, las bandas del home, los azulejos de categoria, los
conteos de los botones de filtro y el llms.txt. Agregar un producto obliga a
tocar unos diez lugares y el que se olvide queda mintiendo.

Este script lee lo que ya existe y lo normaliza. De aca en adelante se edita el
JSON y se reconstruye el HTML, no al reves.

Normaliza dos cosas que venian mezcladas en un solo texto:
  - el rango de tallas ("XL-2XL") -> lista explicita ["XL","1XL","2XL"]
  - el conteo de colores ("· 4 colores") -> se separa del rango
"""
import io, sys, os, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\othma\dev\projects\bolem-site"
COL = os.path.join(ROOT, "coleccion", "index.html")

# Escala de BOLEM, en orden. XL y 1XL se tratan como DISTINTAS porque asi vienen
# etiquetadas por los mayoristas y asi estan en el catalogo — que sean o no el
# mismo cuerpo es la decision que tiene que tomar Monica.
ESCALA = ["XL", "1XL", "2XL", "3XL", "4XL"]


def expandir(rango):
    """'XL-2XL' -> ['XL','1XL','2XL'] ; 'XL' -> ['XL']"""
    partes = [p.strip() for p in re.split(r'[–\-—]', rango) if p.strip()]
    if not partes:
        return []
    if len(partes) == 1:
        return [partes[0]] if partes[0] in ESCALA else []
    a, b = partes[0], partes[-1]
    if a not in ESCALA or b not in ESCALA:
        return []
    return ESCALA[ESCALA.index(a):ESCALA.index(b) + 1]


col = open(COL, encoding='utf-8').read()

# precios del JSON-LD: se parsea el bloque de verdad, no con regex
precios = {}
for bloque in re.findall(r'<script type="application/ld\+json">(.*?)</script>', col, re.S):
    try:
        datos = json.loads(bloque)
    except Exception:
        continue

    def recorrer(o):
        if isinstance(o, dict):
            if o.get('@type') == 'Product':
                of = o.get('offers') or {}
                if isinstance(of, list):
                    of = of[0] if of else {}
                pr = of.get('price')
                if o.get('name') and pr is not None:
                    precios[o['name'].strip()] = float(pr)
            for v2 in o.values():
                recorrer(v2)
        elif isinstance(o, list):
            for v2 in o:
                recorrer(v2)

    recorrer(datos)

productos = []
for trozo in re.split(r'(?=<div class="product-card)', col)[1:]:
    did = re.search(r'data-id="([^"]+)"', trozo)
    if not did:
        continue
    fin = trozo.find('</article>')
    trozo = trozo[:fin] if fin > 0 else trozo

    def tx(cls):
        m = re.search(r'class="%s"[^>]*>(.*?)<' % cls, trozo, re.S)
        return m.group(1).strip() if m else ''

    cat = re.search(r'data-category="([^"]+)"', trozo)
    imgs = re.search(r'data-images="([^"]+)"', trozo)
    img1 = re.search(r'<img src="([^"]+)"[^>]*class="product-img"', trozo)
    cta = re.search(r'<a href="(https://wa\.me/[^"]+)" class="product-cta"', trozo)
    destacada = 'product-card--large' in trozo

    crudo = tx('product-sizes')
    partes = [p.strip() for p in crudo.split('·')]
    rango = partes[0] if partes else ''
    colores = None
    for p in partes[1:]:
        m = re.match(r'(\d+)\s+colores?', p)
        if m:
            colores = int(m.group(1))

    fuente = imgs.group(1) if imgs else (img1.group(1) if img1 else '')
    fotos = [s.strip().replace('../assets/productos/', '')
             for s in fuente.split(',') if s.strip()]

    nombre = tx('product-name')
    tallas = expandir(rango)
    # el alt de la foto principal: varios traen matices que no se pueden
    # deducir del nombre ("en champagne"), asi que se guardan tal cual
    alt = re.search(r'class="product-img"', trozo)
    alt_txt = ''
    m_alt = re.search(r'<img[^>]*class="product-img"[^>]*>', trozo)
    if not m_alt:
        m_alt = re.search(r'<img[^>]*alt="([^"]*)"[^>]*class="product-img"', trozo)
    if m_alt:
        a = re.search(r'alt="([^"]*)"', m_alt.group(0))
        alt_txt = a.group(1) if a else ''
    if not alt_txt:
        m2 = re.search(r'alt="([^"]+)"[^>]*class="product-img"', trozo)
        alt_txt = m2.group(1) if m2 else ''
    productos.append({
        "id": did.group(1),
        "nombre": nombre,
        "categoria": cat.group(1) if cat else '',
        "precio": precios.get(nombre),
        "tallas": tallas,
        "tallas_texto_original": crudo,
        "colores": colores if colores else len(fotos),
        "fotos": fotos,
        "destacada": destacada,
        "alt": alt_txt,
        "wa": cta.group(1) if cta else '',
    })

# ── controles antes de escribir ───────────────────────────────────────────────
assert len(productos) == 33, "se esperaban 33 productos, hay %d" % len(productos)
problemas = []
for p in productos:
    if not p["tallas"]:
        problemas.append("%s: no se pudo interpretar el rango '%s'" % (p["id"], p["tallas_texto_original"]))
    if p["precio"] is None:
        problemas.append("%s: sin precio en el JSON-LD" % p["id"])
    if not p["fotos"]:
        problemas.append("%s: sin fotos" % p["id"])
    if not p["alt"]:
        problemas.append("%s: sin texto alternativo en la foto" % p["id"])
    if len(p["fotos"]) > 1 and p["colores"] and p["colores"] != len(p["fotos"]):
        problemas.append("%s: dice %d colores pero trae %d fotos" % (p["id"], p["colores"], len(p["fotos"])))

os.makedirs(os.path.join(ROOT, "_data"), exist_ok=True)
salida = {
    "_nota": ("Fuente unica del catalogo. Se edita ESTE archivo y se reconstruye "
              "el HTML con _tools/construir_catalogo.py — nunca al reves."),
    "escala_tallas": ESCALA,
    "productos": productos,
}
with open(os.path.join(ROOT, "_data", "catalogo.json"), "w", encoding="utf-8") as f:
    json.dump(salida, f, ensure_ascii=False, indent=2)

print("productos extraidos:", len(productos))
print("_data/catalogo.json escrito")

# ── radiografia de tallas, que es lo que Monica intento explicar ──────────────
import collections
cuenta = collections.Counter()
for p in productos:
    for t in p["tallas"]:
        cuenta[t] += 1
print("\n--- en cuantos productos aparece cada talla ---")
for t in ESCALA:
    print("  %-4s %2d de 33" % (t, cuenta[t]))

print("\n--- problemas de datos ---")
for x in problemas:
    print("  " + x)
if not problemas:
    print("  ninguno")
