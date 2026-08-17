# -*- coding: utf-8 -*-
"""Chequeo de salud del sitio, para correr despues de cualquier cambio.

Comprueba lo que ya se rompio alguna vez en este proyecto:
  - que todos los bloques JSON-LD parseen (si uno revienta, Google lo ignora entero)
  - que toda foto referenciada exista, en sus tres tamanos
  - que todo enlace interno resuelva a un archivo real
  - que cada pagina tenga exactamente un H1
  - que el catalogo y lo publicado digan lo mismo (cuenta de productos)

Uso:  python _tools/verificar.py
"""
import io, os, sys, re, json, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

fallos, avisos = [], []


def paginas():
    for p in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        if os.sep + '_' in p:
            continue
        yield p


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


# ---------- 1. JSON-LD ----------
print('1. JSON-LD')
tot = 0
for p in paginas():
    h = open(p, encoding='utf-8').read()
    bloques = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        h, re.S | re.I)
    for i, b in enumerate(bloques):
        tot += 1
        try:
            json.loads(b)
        except Exception as e:
            fallos.append('JSON-LD roto en %s (bloque %d): %s' % (rel(p), i + 1, e))
print('   %d bloques, %d rotos' % (tot, sum(1 for f in fallos if 'JSON-LD' in f)))

# ---------- 2. fotos ----------
print('2. Fotos')
refs, faltan = set(), set()
for p in paginas():
    h = open(p, encoding='utf-8').read()
    for m in re.findall(r'(?:src|href|srcset)="([^"]*assets/[^"]+)"', h):
        for parte in m.split(','):
            u = parte.strip().split(' ')[0]
            if not u or u.startswith('http'):
                continue
            u = u.lstrip('./')
            while u.startswith('../'):
                u = u[3:]
            refs.add(u)
            if not os.path.exists(os.path.join(ROOT, u)):
                faltan.add((rel(p), u))
for pag, u in sorted(faltan):
    fallos.append('foto que no existe: %s (en %s)' % (u, pag))
print('   %d fotos referenciadas, %d faltantes' % (len(refs), len(faltan)))

# tres tamanos por cada foto de producto
prods = os.path.join(ROOT, 'assets', 'productos')
sin_variantes = []
for f in sorted(os.listdir(prods)):
    if not f.endswith('.webp') or '-480.' in f or '-800.' in f:
        continue
    base = f[:-5]
    for suf in ('-800', '-480'):
        if not os.path.exists(os.path.join(prods, base + suf + '.webp')):
            sin_variantes.append(base + suf + '.webp')
for f in sin_variantes:
    fallos.append('falta la variante %s' % f)
print('   %d variantes faltantes' % len(sin_variantes))

# ---------- 3. enlaces internos ----------
print('3. Enlaces internos')
rotos = set()
n_links = 0
for p in paginas():
    h = open(p, encoding='utf-8').read()
    carpeta = os.path.dirname(p)
    for href in re.findall(r'href="([^"]+)"', h):
        if href.startswith(('http', 'mailto:', 'tel:', '#', 'data:')):
            continue
        n_links += 1
        limpio = href.split('#')[0].split('?')[0]
        if not limpio:
            continue
        destino = os.path.normpath(os.path.join(carpeta, limpio))
        if (os.path.exists(destino) or os.path.exists(destino + '.html')
                or os.path.exists(os.path.join(destino, 'index.html'))):
            continue
        rotos.add((rel(p), href))
for pag, href in sorted(rotos):
    fallos.append('enlace roto: %s (en %s)' % (href, pag))
print('   %d enlaces, %d rotos' % (n_links, len(rotos)))

# ---------- 4. un H1 por pagina ----------
print('4. Encabezados')
malos = 0
for p in paginas():
    h = open(p, encoding='utf-8').read()
    n = len(re.findall(r'<h1\b', h, re.I))
    if n != 1:
        malos += 1
        fallos.append('%s tiene %d H1 (debe tener 1)' % (rel(p), n))
print('   %d paginas fuera de norma' % malos)

# ---------- 5. catalogo vs publicado ----------
print('5. Catalogo')
d = json.load(open(os.path.join(ROOT, '_data', 'catalogo.json'), encoding='utf-8'))
n_cat = len(d['productos'])
col = open(os.path.join(ROOT, 'coleccion', 'index.html'), encoding='utf-8').read()
n_cards = len(re.findall(r'class="product-card', col))
n_ld = len(re.findall(r'"@type"\s*:\s*"Product"', col))
print('   catalogo %d · tarjetas %d · Product en JSON-LD %d' % (n_cat, n_cards, n_ld))
if n_cards != n_cat:
    fallos.append('la coleccion muestra %d tarjetas y el catalogo tiene %d' % (n_cards, n_cat))
if n_ld != n_cat:
    fallos.append('la coleccion declara %d Product y el catalogo tiene %d' % (n_ld, n_cat))

# fotos del catalogo que no existen
for p in d['productos']:
    for f in p['fotos']:
        if not os.path.exists(os.path.join(prods, f)):
            fallos.append('%s: la foto %s no existe' % (p['id'], f))

# ---------- 6. numeros escritos a mano que se quedan viejos ----------
# El H1 de la coleccion decia "33 Estilos" con 49 prendas publicadas, porque
# el parche del constructor buscaba un <h2> que el arreglo de SEO ya habia
# vuelto <h1>. Un numero que miente en la pagina que vende es caro; esto lo
# caza antes de publicar.
print('6. Numeros escritos a mano')
# Solo las frases que hablan del catalogo COMPLETO. Se probo un barrido de
# "\d+ estilos|prendas" en todo el sitio y gritaba en falso: los azulejos del
# home dicen "14 estilos" de Vestidos (correcto) y el articulo de tallas dice
# "21 prendas" refiriendose a un subconjunto (tambien correcto). Un chequeo que
# grita en falso se ignora, y entonces no sirve de nada.
FRASES = [
    (re.compile(r'(\d+) Estilos de Ropa'), 'H1 de la coleccion'),
    (re.compile(r'Coleccion 2026: (\d+) estilos'), 'resumen de llms.txt'),
    (re.compile(r'Catalogo \((\d+) piezas\)'), 'encabezado de catalogo'),
    (re.compile(r'coleccion de (\d+) estilos'), 'descripcion'),
]
malos_num = 0
for p in [os.path.join(ROOT, 'coleccion', 'index.html'),
          os.path.join(ROOT, 'index.html'),
          os.path.join(ROOT, 'llms.txt')]:
    if not os.path.exists(p):
        continue
    h = open(p, encoding='utf-8').read()
    for rx, donde in FRASES:
        for m in rx.finditer(h):
            if int(m.group(1)) != n_cat:
                malos_num += 1
                fallos.append('%s (%s) dice %s y el catalogo tiene %d'
                              % (rel(p), donde, m.group(1), n_cat))
print('   %d numeros desactualizados' % malos_num)

# El rango de tallas NO se chequea contra escala_tallas. Se intento y gritaba
# en falso: "tallas XL a 2XL" en una ficha es el rango de ESA prenda y esta
# bien, y el reclamo de marca "XL a 4XL" tampoco tiene por que seguir a la
# escala interna (la L existe en 2 de 49 prendas que cruzan hacia abajo; no es
# el rango que la marca anuncia). El rango publicado se declara a mano en
# catalogo.json -> rango_publicado, y se compara solo contra eso.
rango_pub = d.get('rango_publicado')
if rango_pub:
    for p in [os.path.join(ROOT, 'llms.txt'),
              os.path.join(ROOT, 'index.html'),
              os.path.join(ROOT, 'coleccion', 'index.html')]:
        if not os.path.exists(p):
            continue
        h = open(p, encoding='utf-8').read()
        for m in re.finditer(r'[Tt]allas ([A-Z0-9]{1,3} a [A-Z0-9]{1,3}) seg', h):
            if m.group(1) != rango_pub:
                fallos.append('%s anuncia "tallas %s segun la prenda" y el rango '
                              'publicado es %s' % (rel(p), m.group(1), rango_pub))

# ---------- resultado ----------
print('\n' + '=' * 66)
if fallos:
    print('FALLA — %d problema(s)' % len(fallos))
    for f in fallos:
        print('  x ' + f)
else:
    print('PASA — sin problemas')
for a in avisos:
    print('  ! ' + a)
print('=' * 66)
sys.exit(1 if fallos else 0)
