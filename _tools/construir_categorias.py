# -*- coding: utf-8 -*-
"""Una direccion propia por categoria: /coleccion/<slug>.

POR QUE EXISTE
Las cuatro categorias existian solo como filtro dentro de `coleccion/`, y el
filtro vive en `coleccion/#vestido`. Un fragmento no es una direccion: Google
no lo indexa aparte, asi que «vestidos plus size el salvador» no tenia a donde
llegar aunque el catalogo tuviera 14 vestidos. Medido el 2026-08-17: 61 URLs
en el sitemap, ninguna de categoria.

QUE NO ES
No son paginas por ciudad. BOLEM despacha a todo el pais desde un solo lugar
y no tiene presencia en Santa Ana ni en San Miguel; una pagina por ciudad
seria una doorway page — el patron que Google penaliza por nombre propio — y
el riesgo cae sobre el dominio entero. Estas paginas corresponden a inventario
real: cada una lista prendas que existen.

TODO LO QUE DICEN SALE DEL CATALOGO. El conteo, el rango de precios, que
tallas cubre y cuantas llegan a 4XL se calculan de `_data/catalogo.json`, asi
que siguen siendo ciertas cuando entren o salgan prendas. Nada escrito a mano
que pueda quedar viejo.

Uso:  python _tools/construir_categorias.py  [--revisar]
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from construir_prendas import (DATOS, SITIO, WA_GENERAL, SVG_WA, esc, footer,
                               nav, precio_txt, srcset, var)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(ROOT, 'coleccion')
COLECCION = os.path.join(SALIDA, 'index.html')

FUENTES = ('https://fonts.googleapis.com/css2?family=Inconsolata:wght@300;400;500;600'
           '&family=Outfit:wght@300;400;500;600'
           '&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400&display=swap')

# slug y titular por categoria. El slug lleva la palabra que la gente busca.
SLUGS = {
    'vestido':  ('vestidos-plus-size',           'Vestidos'),
    'blusa':    ('blusas-plus-size',             'Blusas'),
    'pantalon': ('jeans-y-pantalones-plus-size', 'Jeans y pantalones'),
    'conjunto': ('conjuntos-plus-size',          'Conjuntos'),
}


def plural(n, uno, varios):
    return uno if n == 1 else varios


def intro(items, todos):
    """El parrafo de la categoria, calculado. Ni una cifra escrita a mano."""
    n = len(items)
    # Solo lo disponible: un rango de precios describe lo que se puede pagar
    # hoy, no lo que hubo. Si no queda nada, se cae al catalogo completo para
    # no escribir un rango vacio.
    _hay = [x for x in items if not x.get('agotada')] or items
    precios = sorted(float(x['precio']) for x in _hay)
    etiquetas = set()
    for x in items:
        etiquetas.update(x['tallas'])
    cuatro = [x for x in items if '4XL' in x['tallas']]
    cruzan = [x for x in items if 'XL' in x['tallas'] and '1XL' in x['tallas']]
    orden = [t for t in ['L', 'XL', '1XL', '2XL', '3XL', '4XL'] if t in etiquetas]

    f = []
    if precios[0] == precios[-1]:
        f.append('%d %s, %s a <strong>$%.2f</strong>.'
                 % (n, plural(n, 'pieza', 'piezas'), plural(n, 'esta', 'todas'), precios[0]))
    else:
        f.append('%d %s, de <strong>$%.2f</strong> a <strong>$%.2f</strong>.'
                 % (n, plural(n, 'pieza', 'piezas'), precios[0], precios[-1]))
    if orden:
        f.append('Entre todas cubren de la <strong>%s</strong> a la <strong>%s</strong>.'
                 % (orden[0], orden[-1]))
    if cuatro:
        f.append('%d %s hasta <strong>4XL</strong>.'
                 % (len(cuatro), plural(len(cuatro), 'llega', 'llegan')))
    if cruzan:
        f.append('En %d de %s, la <strong>XL</strong> y la <strong>1XL</strong> aparecen '
                 'como tallas distintas de la misma pieza — porque lo son: '
                 '<a href="../blog/tallas-xl-1xl-plus-size">te lo explicamos acá</a>.'
                 % (len(cruzan), plural(n, 'la única', 'las %d' % n)))
    f.append('Pagás al recibir y el envío es $5 a todo el país.')
    return ' '.join(f)


def tarjetas(items):
    out = []
    for p in items:
        out.append('        <a class="prenda-mini" href="../prendas/%s">'
                   '<img src="../assets/productos/%s" srcset="%s" '
                   'sizes="(max-width: 700px) 45vw, 200px" alt="%s" width="480" height="720" '
                   'loading="lazy" decoding="async">'
                   '<strong>%s</strong><span>$%s</span></a>'
                   % (p['id'], var(p['fotos'][0], 480), srcset(p['fotos'][0]),
                      esc(p['alt']), esc(p['nombre']), precio_txt(p)))
    return '\n'.join(out)


def json_ld(cat, slug, titular, items, meta):
    url = '%s/coleccion/%s' % (SITIO, slug)
    bloques = [
        {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
         'itemListElement': [
             {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': SITIO + '/'},
             {'@type': 'ListItem', 'position': 2, 'name': 'Colección',
              'item': SITIO + '/coleccion'},
             {'@type': 'ListItem', 'position': 3, 'name': titular, 'item': url},
         ]},
        {'@context': 'https://schema.org', '@type': 'CollectionPage',
         '@id': url + '#pagina', 'url': url,
         'name': '%s plus size en El Salvador' % titular,
         'description': meta,
         'isPartOf': {'@id': SITIO + '/#sitio'},
         'mainEntity': {
             '@type': 'ItemList',
             'numberOfItems': len(items),
             'itemListElement': [
                 {'@type': 'ListItem', 'position': i + 1,
                  'url': '%s/prendas/%s' % (SITIO, p['id']), 'name': p['nombre']}
                 for i, p in enumerate(items)],
         }},
    ]
    return '\n'.join('    <script type="application/ld+json">\n%s\n    </script>'
                     % json.dumps(b, ensure_ascii=False, indent=2) for b in bloques)


def pagina(cat, slug, titular, items, cats_todas, todos):
    url = '%s/coleccion/%s' % (SITIO, slug)
    titulo = '%s Plus Size El Salvador — BOLEM' % titular
    # Solo lo disponible: un rango de precios describe lo que se puede pagar
    # hoy, no lo que hubo. Si no queda nada, se cae al catalogo completo para
    # no escribir un rango vacio.
    _hay = [x for x in items if not x.get('agotada')] or items
    precios = sorted(float(x['precio']) for x in _hay)
    meta = ('%d %s plus size en El Salvador, de $%.2f a $%.2f. Tallas XL a 4XL, '
            'envío a todo el país y pagás al recibir.'
            % (len(items), titular.lower(), precios[0], precios[-1]))
    if len(meta) > 160:
        meta = meta[:157].rsplit(' ', 1)[0] + '...'

    otras = []
    for c, (s, t) in SLUGS.items():
        if c == cat:
            continue
        n = len([x for x in todos if x['categoria'] == c])
        if n:
            otras.append('<a href="%s">%s (%d)</a>' % (s, t, n))

    return """<!DOCTYPE html>
<html lang="es-SV">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%(titulo)s</title>
    <meta name="description" content="%(meta)s">
    <link rel="canonical" href="%(url)s">
    <meta property="og:title" content="%(titulo)s">
    <meta property="og:description" content="%(meta)s">
    <meta property="og:type" content="website">
    <meta property="og:url" content="%(url)s">
    <meta property="og:image" content="%(sitio)s/assets/productos/%(portada)s">
    <meta property="og:locale" content="es_SV">
    <meta property="og:site_name" content="BOLEM">
    <link rel="icon" href="../favicon.svg" type="image/svg+xml">

%(jsonld)s
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" as="style" href="%(fuentes)s" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="%(fuentes)s"></noscript>
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="../prenda.css">
</head>
<body>

%(nav)s

  <main class="prenda-wrap">
    <nav class="prenda-migas" aria-label="Dónde estás">
      <a href="../">Inicio</a> <span aria-hidden="true">/</span>
      <a href="./">Colección</a> <span aria-hidden="true">/</span>
      <span>%(titular)s</span>
    </nav>

    <h1 class="prenda-nombre">%(titular)s plus size en El Salvador</h1>
    <p class="prenda-nota">%(intro)s</p>

    <section class="prenda-relacionadas" style="margin-top:2rem">
      <div class="prenda-grid">
%(tarjetas)s
      </div>
    </section>

    <section class="prenda-relacionadas">
      <h2>Seguí viendo</h2>
      <p class="prenda-nota">%(otras)s &bull; <a href="./">Las %(total)d de la colección completa</a></p>
    </section>
  </main>

%(footer)s

  <script src="../nav.js" defer></script>
</body>
</html>
""" % dict(titulo=esc(titulo), meta=esc(meta), url=url, sitio=SITIO,
           portada=cats_todas[cat].get('portada') or items[0]['fotos'][0],
           jsonld=json_ld(cat, slug, titular, items, meta), fuentes=FUENTES,
           nav=nav(), titular=esc(titular), intro=intro(items, todos),
           tarjetas=tarjetas(items), otras=' &bull; '.join(otras),
           total=len(todos), footer=footer())


MARCA_INI = '<!-- BOLEM:CATLINKS -->'
MARCA_FIN = '<!-- /BOLEM:CATLINKS -->'


def enlazar_desde_coleccion(bloque):
    """Deja los cuatro enlaces dentro de coleccion/index.html.

    Sin esto las cuatro paginas nacen huerfanas: existirian en el sitemap y
    nadie llegaria a ellas navegando, que es la mitad de lo que Google mira.
    Se inserta una sola vez, entre marcas, para poder regenerarlo despues.
    """
    h = open(COLECCION, encoding='utf-8').read()
    nuevo = '%s\n%s\n%s' % (MARCA_INI, bloque, MARCA_FIN)
    if MARCA_INI in h:
        h2 = re.sub(re.escape(MARCA_INI) + r'.*?' + re.escape(MARCA_FIN),
                    lambda m: nuevo, h, flags=re.S)
    else:
        ancla = '<!-- /BOLEM:FILTROS -->'
        if ancla not in h:
            return False, 'no se encontro el ancla %s' % ancla
        h2 = h.replace(ancla, ancla + '\n' + nuevo, 1)
    if h2 == h:
        return False, 'sin cambio'
    open(COLECCION, 'w', encoding='utf-8').write(h2)
    return True, 'ok'


def main(revisar=False):
    d = json.load(open(DATOS, encoding='utf-8'))
    todos = d['productos']
    cats = d['categorias']

    escritas = igual = 0
    enlaces = []
    for cat, (slug, titular) in SLUGS.items():
        items = [p for p in todos if p['categoria'] == cat]
        if not items:
            print('   (sin prendas) %s' % cat)
            continue
        items.sort(key=lambda p: float(p['precio']))
        html = pagina(cat, slug, titular, items, cats, todos)
        destino = os.path.join(SALIDA, slug + '.html')
        viejo = open(destino, encoding='utf-8').read() if os.path.exists(destino) else None
        if viejo == html:
            igual += 1
        elif not revisar:
            open(destino, 'w', encoding='utf-8').write(html)
            escritas += 1
        else:
            escritas += 1
        enlaces.append('      <a class="filter-link" href="%s">%s (%d)</a>'
                       % (slug, titular, len(items)))
        print('   %-30s %2d prendas  ->  /coleccion/%s' % (titular, len(items), slug))

    bloque = ('      <p class="filter-links">Cada categoría tiene su página: '
              + ' '.join(e.strip() for e in enlaces) + '</p>')
    if not revisar:
        ok, msg = enlazar_desde_coleccion(bloque)
        print('   enlaces desde coleccion/index.html: %s' % msg)

    print('\npaginas de categoria: %d escritas · %d sin cambio' % (escritas, igual))
    if revisar:
        print('(--revisar: no se escribio nada)')
    return 0


if __name__ == '__main__':
    sys.exit(main('--revisar' in sys.argv))
