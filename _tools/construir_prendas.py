# -*- coding: utf-8 -*-
"""Construye una pagina propia para cada prenda, desde _data/catalogo.json

POR QUE EXISTE
    Hasta hoy las 49 prendas vivian en UNA sola direccion (/coleccion/). Para
    un buscador, una pagina que habla de 49 cosas es una pagina que no habla de
    ninguna: no hay long-tail, no hay Google Shopping (exige una direccion por
    producto con precio), y las estrellas de resenia no tienen donde colgarse.
    Ademas Monica no tenia un enlace que mandar por WhatsApp para UNA prenda.

QUE GENERA
    prendas/<id>.html  ->  se sirve como /prendas/<id> (sin .html, como el
    resto del sitio; asi lo resuelven Cloudflare Pages y GitHub Pages).

QUE NO INVENTA
    Tela, corte, caida, ocasion y cuidado NO se escriben aca. Este generador
    solo publica lo que el catalogo sabe de verdad: nombre, precio, tallas,
    categoria, colores y fotos. Lo demas queda como un hueco marcado que se
    llena cuando lleguen las descripciones de Monica (campo "descripcion" en
    catalogo.json). Inventarle la tela a una prenda es exactamente como se
    pierde la confianza de una clienta que la recibe y no era.

Uso:
    python _tools/construir_prendas.py --revisar   (dice que haria)
    python _tools/construir_prendas.py
"""
import io, os, sys, json, re, shutil
from urllib.parse import quote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(ROOT, '_data', 'catalogo.json')
SALIDA = os.path.join(ROOT, 'prendas')
SITIO = 'https://bolemsv.com'
WA = '50368590899'

SVG_WA = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967'
          '-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463'
          '-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149'
          '-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5'
          '-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462'
          ' 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195'
          ' 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347'
          'm-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0'
          ' 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893'
          ' 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335'
          '.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554'
          ' 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>')

SVG_IG = ('<svg fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.163c3.204 0 3.584.012'
          ' 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069'
          ' 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07'
          '-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149'
          '-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072'
          ' 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78'
          ' 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98'
          '.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668'
          '.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4'
          ' 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>')

WA_GENERAL = ('https://wa.me/%s?text=Hola%%2C%%20vi%%20la%%20p%%C3%%A1gina%%20de%%20BOLEM'
              '%%20y%%20quiero%%20saber%%20m%%C3%%A1s' % WA)

FUENTES = ('https://fonts.googleapis.com/css2?family=Inconsolata:wght@300;400;500;600'
           '&family=Outfit:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400'
           '&display=swap')


# --- existencias --------------------------------------------------------------
# Una prenda se marca agotada con `"agotada": true` en catalogo.json. El campo es
# OPCIONAL: si no esta, la prenda esta disponible, asi que las 49 entradas viejas
# siguen valiendo sin tocarlas.
#
# Tres reglas, cada una con su razon:
#   1. Una prenda agotada SIGUE VISIBLE, con su pagina y su direccion. Borrarla
#      tira el SEO que ya gano y le quita a Monica la chance de anotar a quien la
#      queria.
#   2. SI cuenta en "N estilos": ese numero describe lo que hay en pantalla, y la
#      tarjeta esta en pantalla.
#   3. NO cuenta en el RANGO DE PRECIOS: ese describe lo que se puede pagar hoy.
#      Es exactamente el caso de las dos prendas de $22 que sostienen el reclamo
#      "$22-$85" en tres archivos. Si se agotaron, el precio de entrada miente.


def disponible(p):
    """True si la prenda se puede comprar hoy."""
    return not p.get('agotada')


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def var(foto, ancho):
    return foto[:-5] + ('-%d' % ancho) + '.webp' if ancho else foto


def srcset(foto):
    return ('../assets/productos/%s 480w, ../assets/productos/%s 800w, ../assets/productos/%s 1200w'
            % (var(foto, 480), var(foto, 800), foto))


def wa_prenda(p):
    if not disponible(p):
        return 'https://wa.me/%s?text=%s' % (WA, quote(
            'Hola, vi que el %s aparece agotado. Me avisan cuando vuelva?' % p['nombre'],
            safe=''))
    t = 'Hola, quiero apartar el %s ($%s). Mi talla es: ' % (p['nombre'], precio_txt(p))
    if p.get('colores', 1) > 1:
        t += ' y lo quiero en color: '
    return 'https://wa.me/%s?text=%s' % (WA, quote(t, safe=''))


def precio_txt(p):
    return ('%.2f' % float(p['precio'])).rstrip('0').rstrip('.') if False else '%.2f' % float(p['precio'])


def nav(activo=''):
    enlaces = [('../', 'Inicio'), ('../coleccion/', 'Colección'),
               ('../guia-de-tallas', 'Guía de tallas'), ('../nosotros', 'Nosotras'),
               ('../blog/', 'Blog')]
    esc_links = ''.join('\n    <a href="%s" class="nav-link">%s</a>' % (h, t) for h, t in enlaces)
    mob = ''.join('\n        <a href="%s" class="nav-mobile-link">%s</a>' % (h, t) for h, t in enlaces)
    return """  <nav class="site-nav">
    <a href="../" class="nav-logo" aria-label="BOLEM — inicio">BOL<span class="accent">E</span>M</a>
    <div class="nav-links">%s
    </div>
    <a href="%s" target="_blank" rel="noopener" class="nav-cta desktop-only">%s WhatsApp</a>
    <button id="menuBtn" class="nav-menu-btn" aria-label="Menú" aria-expanded="false" aria-controls="mobileMenu">
      <span id="menuLine1"></span>
      <span id="menuLine2"></span>
    </button>
    <div id="mobileMenu" class="nav-mobile">
      <div class="nav-mobile-inner">%s
        <a href="%s" target="_blank" rel="noopener" class="nav-mobile-link">WhatsApp</a>
      </div>
    </div>
  </nav>""" % (esc_links, WA_GENERAL, SVG_WA, mob, WA_GENERAL)


def footer():
    return """  <footer class="site-footer">
    <a href="../" class="footer-logo" aria-label="BOLEM — inicio">BOL<span class="accent">E</span>M</a>
    <div class="footer-links">
      <p class="footer-copy">&copy; 2026 BOLEM &mdash; Moda Plus Size &bull; El Salvador</p>
      <div class="footer-nav">
        <a href="../#faq">Preguntas frecuentes</a>
        <span>&bull;</span>
        <a href="../guia-de-tallas">Guía de tallas</a>
        <span>&bull;</span>
        <a href="../cambios">Cambios</a>
        <span>&bull;</span>
        <a href="../privacidad">Privacidad</a>
        <span>&bull;</span>
        <a href="../terminos">Términos</a>
      </div>
    </div>
    <div class="footer-social">
      <a href="https://instagram.com/bolem_sv" target="_blank" rel="noopener" aria-label="BOLEM en Instagram">%s</a>
      <a href="%s" target="_blank" rel="noopener" aria-label="Escribile a BOLEM por WhatsApp">%s</a>
    </div>
  </footer>""" % (SVG_IG, WA_GENERAL, SVG_WA)


def detalle_alt(p):
    """El trozo descriptivo del `alt`, sin el nombre ni la cola de SEO.

    Es la unica fuente de detalle fisico que el catalogo tiene escrita y
    revisada (color, corte, avios). Es distinta en las 49, y por eso es lo
    que hace que las 49 fichas no digan lo mismo. 7 prendas no traen nada:
    esas se quedan sin esa frase en vez de inventarsela.
    """
    a = p.get('alt') or ''
    a = re.sub(r'\s*—\s*BOLEM.*$', '', a)
    a = re.sub(r'\s*plus size,?\s*tallas[^,]*$', '', a).strip().rstrip(',')
    nom = p.get('nombre', '')
    if nom and a.lower().startswith(nom.lower()):
        a = a[len(nom):].strip()
    a = a.lstrip(',').strip()
    return a


def frase_tallas(p):
    """La corrida, dicha en terminos de la escala que ESTA prenda usa."""
    t = p['tallas']
    if len(t) == 1:
        return 'Nos queda solo en <strong>%s</strong>.' % t[0]
    cruza = ('XL' in t and '1XL' in t) or ('L' in t and ('XL' in t or '1XL' in t))
    base = 'Va de la <strong>%s</strong> a la <strong>%s</strong>' % (t[0], t[-1])
    if cruza:
        return base + ', o sea que cruza de la escala recta a la plus.'
    return base + '.'


def frase_precio(p, prods):
    """El precio situado contra la distribucion REAL del catalogo.

    No es adorno: a la clienta que llega por un enlace suelto, un numero sin
    referencia no le dice nada. Los cortes se calculan de los 49 precios, asi
    que la frase sigue siendo cierta cuando entren o salgan prendas.
    """
    precios = sorted(x['precio'] for x in prods)
    n = len(precios)
    if n < 4:
        return ''
    q1 = precios[n // 4]
    med = precios[n // 2]
    q3 = precios[(3 * n) // 4]
    v = p['precio']
    if v <= q1:
        donde = 'es de las más accesibles del catálogo'
    elif v <= med:
        donde = 'está en la mitad baja de precios'
    elif v <= q3:
        donde = 'está en la mitad alta'
    else:
        donde = 'es de las de precio más alto'
    return 'A <strong>$%s</strong> %s.' % (fmt_precio(v), donde)


def fmt_precio(v):
    return ('%.2f' % v)


def descripcion(p, cats, prods=None):
    """Lo que se puede decir con lo que el catalogo SABE. Nada inventado.

    Deliberadamente NO dice tela, calce ni ocasion: el catalogo no los tiene
    y son justo las cuatro cosas que la hoja de descripciones le pide a
    Monica por nota de voz. Inventarlas aca seria escribir en la ficha de
    producto —lo que Google cita como hecho— algo que nadie verifico.
    """
    if p.get('descripcion'):
        return '<p data-auto="0">%s</p>' % esc(p['descripcion'])
    prods = prods or [p]
    partes = []
    det = detalle_alt(p)
    if det:
        partes.append('<strong>%s</strong>, %s.' % (esc(p['nombre']), det))
    else:
        partes.append('<strong>%s</strong>.' % esc(p['nombre']))
    if p.get('colores', 1) > 1:
        partes.append('Viene en %d colores.' % p['colores'])
    partes.append(frase_tallas(p))
    pr = frase_precio(p, prods)
    if pr:
        partes.append(pr)
    cierre = (cats.get(p['categoria'], {}) or {}).get('editorial') or ''
    bloque = '<p data-auto="1">%s</p>' % ' '.join(partes)
    if cierre:
        bloque += '\n<p data-auto="1" class="prenda-desc-editorial">%s</p>' % cierre
    bloque += ('\n<p data-auto="1" class="prenda-desc-falta">La tela y cómo cae '
               'te los contamos por WhatsApp — <a href="%s" target="_blank" '
               'rel="noopener">preguntanos por esta pieza</a>.</p>' % p['wa'])
    return bloque


def escala_nota(p):
    """La nota de tallas se escribe segun lo que ESTA prenda usa de verdad."""
    t = set(p['tallas'])
    if 'L' in t and ('XL' in t or '1XL' in t):
        return ('Esta prenda cruza de la <strong>L</strong> a las tallas plus. '
                'La <strong>XL</strong> y la <strong>1XL</strong> no son lo mismo: '
                'XL viene de la escala recta y 1XL de la plus. '
                '<a href="../blog/tallas-xl-1xl-plus-size">Te lo explicamos acá</a>.')
    if 'XL' in t and '1XL' in t:
        return ('Ojo: <strong>XL</strong> y <strong>1XL</strong> no son la misma talla. '
                'XL viene de la escala recta y 1XL de la plus. '
                '<a href="../blog/tallas-xl-1xl-plus-size">Te lo explicamos acá</a>.')
    return ('¿Entre dos tallas? Escribinos y te decimos cuál te queda mejor en '
            '<em>esta</em> prenda. <a href="../guia-de-tallas">Guía de tallas</a>.')


def json_ld(p, cats):
    url = '%s/prendas/%s' % (SITIO, p['id'])
    cat = cats[p['categoria']]['etiqueta_larga']
    # El detalle del `alt` entra aca a proposito: `description` es lo que lee
    # Merchant Center y lo que puede salir en un resultado enriquecido. Con
    # solo nombre+tallas+precio las 49 se parecen entre si; el color y el
    # corte son lo unico que las distingue, y ya estan escritos y revisados.
    det = detalle_alt(p)
    desc = ('%s plus size%s. Tallas %s. $%s. BOLEM El Salvador.'
            % (p['nombre'], (', ' + det) if det else '',
               p['tallas_texto_original'], precio_txt(p)))
    prod = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        '@id': url + '#producto',
        'name': p['nombre'],
        'description': desc,
        'image': ['%s/assets/productos/%s' % (SITIO, f) for f in p['fotos']],
        'sku': p['id'],
        'category': cat,
        'size': p['tallas'],
        'brand': {'@type': 'Brand', '@id': SITIO + '/#marca-bolem', 'name': 'BOLEM'},
        'offers': {
            '@type': 'Offer',
            'url': url,
            'price': precio_txt(p),
            'priceCurrency': 'USD',
            'availability': ('https://schema.org/InStock' if disponible(p)
                             else 'https://schema.org/OutOfStock'),
            'itemCondition': 'https://schema.org/NewCondition',
            'seller': {'@type': 'ClothingStore', '@id': SITIO + '/#bolem', 'name': 'BOLEM'},
            'shippingDetails': {
                '@type': 'OfferShippingDetails',
                'shippingRate': {'@type': 'MonetaryAmount', 'value': '5.00', 'currency': 'USD'},
                'shippingDestination': {'@type': 'DefinedRegion', 'addressCountry': 'SV'},
                'deliveryTime': {'@type': 'ShippingDeliveryTime',
                                 'transitTime': {'@type': 'QuantitativeValue', 'minValue': 1,
                                                 'maxValue': 3, 'unitCode': 'DAY'}},
            },
            'hasMerchantReturnPolicy': {
                '@type': 'MerchantReturnPolicy',
                'applicableCountry': 'SV',
                'returnPolicyCategory': 'https://schema.org/MerchantReturnFiniteReturnWindow',
                'merchantReturnDays': 2,
                'returnMethod': 'https://schema.org/ReturnByMail',
                'returnFees': 'https://schema.org/FreeReturn',
            },
        },
    }
    migas = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': SITIO + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Colección', 'item': SITIO + '/coleccion'},
            {'@type': 'ListItem', 'position': 3, 'name': cat,
             'item': '%s/coleccion#%s' % (SITIO, p['categoria'])},
            {'@type': 'ListItem', 'position': 4, 'name': p['nombre'], 'item': url},
        ],
    }
    return ('    <script type="application/ld+json">\n%s\n    </script>\n'
            '    <script type="application/ld+json">\n%s\n    </script>'
            % (json.dumps(prod, ensure_ascii=False, indent=2),
               json.dumps(migas, ensure_ascii=False, indent=2)))


def pagina(p, prods, cats):
    url = '%s/prendas/%s' % (SITIO, p['id'])
    cat = cats[p['categoria']]
    titulo = '%s Plus Size %s — BOLEM' % (p['nombre'], p['tallas_texto_original'])
    if len(titulo) > 60:
        titulo = '%s Plus Size — BOLEM' % p['nombre']
    meta = ('%s plus size en tallas %s por $%s. Ropa curvy en El Salvador, '
            'apartala por WhatsApp y pagás al recibir.'
            % (p['nombre'], p['tallas_texto_original'], precio_txt(p)))
    if len(meta) > 160:
        meta = meta[:157].rsplit(' ', 1)[0] + '...'

    # --- galeria: todas las fotos en el DOM. Sin JavaScript se ven todas;
    #     con JavaScript la de arriba se cambia al tocar una. ---
    principal = p['fotos'][0]
    g = ['      <div class="prenda-foto-grande">',
         '        <img id="fotoPrincipal" src="../assets/productos/%s" srcset="%s"'
         ' sizes="(max-width: 860px) 100vw, 55vw" alt="%s" width="1200" height="1800"'
         ' fetchpriority="high" decoding="async">' % (principal, srcset(principal), esc(p['alt'])),
         '      </div>']
    if len(p['fotos']) > 1:
        g.append('      <div class="prenda-miniaturas" role="group" aria-label="Más fotos de %s">'
                 % esc(p['nombre']))
        for i, f in enumerate(p['fotos']):
            g.append('        <button type="button" data-foto="../assets/productos/%s"'
                     ' data-set="%s" aria-current="%s" aria-label="Ver foto %d de %d">'
                     '<img src="../assets/productos/%s" alt="" width="480" height="720"'
                     ' loading="lazy" decoding="async"></button>'
                     % (f, srcset(f), 'true' if i == 0 else 'false', i + 1,
                        len(p['fotos']), var(f, 480)))
        g.append('      </div>')
    galeria = '\n'.join(g)

    tallas = ''.join('<span class="prenda-talla">%s</span>' % t for t in p['tallas'])

    # --- seguí viendo: misma categoria, las mas cercanas de precio ---
    hermanas = [q for q in prods if q['categoria'] == p['categoria'] and q['id'] != p['id']]
    hermanas.sort(key=lambda q: abs(float(q['precio']) - float(p['precio'])))
    rel = []
    for q in hermanas[:4]:
        rel.append('        <a class="prenda-mini" href="%s">'
                   '<img src="../assets/productos/%s" alt="%s" width="480" height="720"'
                   ' loading="lazy" decoding="async">'
                   '<strong>%s</strong><span>$%s</span></a>'
                   % (q['id'], var(q['fotos'][0], 480), esc(q['alt']),
                      esc(q['nombre']), precio_txt(q)))
    relacionadas = ''
    if rel:
        relacionadas = ("""
    <section class="prenda-relacionadas">
      <h2>Seguí viendo en %s</h2>
      <div class="prenda-grid">
%s
      </div>
    </section>""" % (esc(cat['etiqueta_larga']), '\n'.join(rel)))

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
    <meta property="og:type" content="product">
    <meta property="og:url" content="%(url)s">
    <meta property="og:image" content="%(sitio)s/assets/productos/%(principal)s">
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
      <a href="../">Inicio</a><span aria-hidden="true">/</span>
      <a href="../coleccion/">Colección</a><span aria-hidden="true">/</span>
      <a href="../coleccion/#%(catid)s">%(catnombre)s</a><span aria-hidden="true">/</span>
      <span aria-current="page">%(nombre)s</span>
    </nav>

    <div class="prenda-top">
      <div class="prenda-fotos">
%(galeria)s
      </div>

      <div class="prenda-datos">
        <p class="prenda-eyebrow">%(catnombre)s</p>
        <h1 class="prenda-nombre">%(nombre)s</h1>
        <p class="prenda-precio">$%(precio)s</p>

        <div class="prenda-campo">
          <h2>Tallas disponibles</h2>
          <div class="prenda-tallas">%(tallas)s</div>
          <p class="prenda-nota">%(nota_tallas)s</p>
        </div>

        <a class="prenda-cta" href="%(wa)s" target="_blank" rel="noopener">%(svgwa)s Apartar por WhatsApp</a>

        <ul class="prenda-confianza">
          <li><span aria-hidden="true">&#10003;</span><span><b>Pagás al recibir</b> — no adelantás nada.</span></li>
          <li><span aria-hidden="true">&#10003;</span><span><b>Envío $5</b> a todo El Salvador, llega en 1 a 3 días.</span></li>
          <li><span aria-hidden="true">&#10003;</span><span><b>Cambios</b> dentro de los 2 días de recibido.</span></li>
        </ul>
      </div>
    </div>

    <section class="prenda-detalle">
      <div>
        <h2>Sobre esta pieza</h2>
        <!-- BOLEM:DESC:%(id)s -->
%(descripcion)s
        <!-- /BOLEM:DESC:%(id)s -->
      </div>
      <div class="prenda-caja">
        <h2>La ficha</h2>
        <dl>
          <dt>Precio</dt><dd>$%(precio)s</dd>
          <dt>Tallas</dt><dd>%(tallas_txt)s</dd>
          <dt>Categoría</dt><dd>%(catnombre)s</dd>
          <dt>Colores</dt><dd>%(colores)s</dd>
          <dt>Código</dt><dd>%(id)s</dd>
        </dl>
      </div>
    </section>
%(relacionadas)s

    <p class="prenda-volver"><a href="../coleccion/">Ver toda la colección</a></p>
  </main>

%(footer)s

  <script src="../nav.js" defer></script>
  <script>
    // La galeria funciona sin esto: sin JavaScript se ven todas las fotos.
    // Esto solo sube al lugar grande la que se toca.
    (function () {
      var grande = document.getElementById('fotoPrincipal');
      var tira = document.querySelector('.prenda-miniaturas');
      if (!grande || !tira) return;
      tira.addEventListener('click', function (e) {
        var b = e.target.closest('button[data-foto]');
        if (!b) return;
        grande.src = b.dataset.foto;
        grande.srcset = b.dataset.set;
        tira.querySelectorAll('button').forEach(function (o) {
          o.setAttribute('aria-current', o === b ? 'true' : 'false');
        });
      });
    })();
  </script>
</body>
</html>
""" % dict(titulo=esc(titulo), meta=esc(meta), url=url, sitio=SITIO,
           principal=principal, jsonld=json_ld(p, cats), fuentes=FUENTES,
           nav=nav(), footer=footer(), galeria=galeria,
           catid=p['categoria'], catnombre=esc(cat['etiqueta_larga']),
           nombre=esc(p['nombre']), precio=precio_txt(p), tallas=tallas,
           tallas_txt=esc(p['tallas_texto_original']),
           nota_tallas=escala_nota(p), wa=esc(wa_prenda(p)), svgwa=SVG_WA,
           descripcion=descripcion(p, cats, prods), id=p['id'],
           colores=('%d colores' % p['colores']) if p.get('colores', 1) > 1 else 'Un color',
           relacionadas=relacionadas)


def main(revisar):
    d = json.load(open(DATOS, encoding='utf-8'))
    prods, cats = d['productos'], d['categorias']

    # rescatar descripciones ya escritas a mano dentro de las marcas
    previas = {}
    if os.path.isdir(SALIDA):
        for f in os.listdir(SALIDA):
            if not f.endswith('.html'):
                continue
            pid = f[:-5]
            h = open(os.path.join(SALIDA, f), encoding='utf-8').read()
            m = re.search(r'<!-- BOLEM:DESC:%s -->(.*?)<!-- /BOLEM:DESC:%s -->'
                          % (re.escape(pid), re.escape(pid)), h, re.S)
            if m and 'data-auto="1"' not in m.group(1):
                # Solo se conserva lo que NO genero este script. Sin esta
                # comprobacion el hueco conservaba su propia salida y el texto
                # quedaba congelado en la primera corrida: mejorar
                # descripcion() no cambiaba ni una ficha ya escrita.
                previas[pid] = m.group(1)

    os.makedirs(SALIDA, exist_ok=True)
    nuevas = cambiadas = iguales = 0
    for p in prods:
        html = pagina(p, prods, cats)
        if p['id'] in previas and not p.get('descripcion'):
            html = re.sub(r'(<!-- BOLEM:DESC:%s -->).*?(<!-- /BOLEM:DESC:%s -->)'
                          % (re.escape(p['id']), re.escape(p['id'])),
                          lambda m: m.group(1) + previas[p['id']] + m.group(2),
                          html, flags=re.S)
        destino = os.path.join(SALIDA, p['id'] + '.html')
        viejo = open(destino, encoding='utf-8').read() if os.path.exists(destino) else None
        if viejo is None:
            nuevas += 1
        elif viejo != html:
            cambiadas += 1
        else:
            iguales += 1
            continue
        if not revisar:
            open(destino, 'w', encoding='utf-8').write(html)

    # borrar paginas de prendas que ya no estan en el catalogo
    vivos = {p['id'] + '.html' for p in prods}
    sobran = [f for f in os.listdir(SALIDA) if f.endswith('.html') and f not in vivos] \
        if os.path.isdir(SALIDA) else []
    for f in sobran:
        print('  sobra (se borra): prendas/%s' % f)
        if not revisar:
            os.remove(os.path.join(SALIDA, f))

    print('paginas de prenda: %d nuevas · %d actualizadas · %d sin cambio · %d borradas'
          % (nuevas, cambiadas, iguales, len(sobran)))
    print('   destino: prendas/<id>.html   ->   se sirve como /prendas/<id>')
    if previas:
        print('   descripciones escritas a mano conservadas: %d' % len(previas))
    if revisar:
        print('\n(--revisar: no se escribio nada)')
    return 0


if __name__ == '__main__':
    sys.exit(main('--revisar' in sys.argv))
