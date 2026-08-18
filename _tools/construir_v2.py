# -*- coding: utf-8 -*-
"""Construye BOLEM v2 entero desde v2/_data/bolem.json (que baja de la Hoja Madre).

LA TESIS DE v2
    El sitio actual es un folleto con SEO encima. Pero el negocio real es que
    Monica vende por WhatsApp, de a una conversacion, y el cuello de botella es
    contestar "¿me quedara?" cuarenta veces al dia.

    v2 no es un catalogo. Es la maquina que contesta esa pregunta ANTES de la
    conversacion, y que le da a Monica un enlace por prenda.

TRES COSAS QUE v2 HACE Y v1 NO
    1. Se filtra POR TALLA. La clienta no piensa "quiero una blusa": piensa
       "soy 3XL, que hay para mi". v1 solo filtra por categoria.
    2. Cada prenda dice cuanto mide la modelo y que talla lleva puesta, y como
       queda de verdad. Es lo que hace Universal Standard y lo que nadie hace aca.
    3. Monica edita una hoja de calculo y el sitio se reconstruye. Hoy no puede
       cambiar un precio sin mi.

REGLA QUE NO SE ROMPE
    Un dato que no existe NO se inventa y NO se calla: el sitio dice que falta
    y ofrece preguntarlo por WhatsApp. Es honesto, y ademas convierte — manda
    al chat justo en el momento de la duda.

Uso:
    python _tools/construir_v2.py --revisar
    python _tools/construir_v2.py
"""
import io, os, sys, json, re, html, shutil
from urllib.parse import quote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2 = os.path.join(ROOT, 'v2')
DATOS = os.path.join(V2, '_data', 'bolem.json')

SITIO = 'https://bolemsv.com/v2'          # mientras v2 no sea la raiz
WA = '50368590899'
IG = 'https://instagram.com/bolem_sv'
FUENTES = ('https://fonts.googleapis.com/css2?family=Inconsolata:wght@300;400;500;600'
           '&family=Outfit:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;1,400'
           '&display=swap')

CATS = {
    'vestido':  ('Vestidos', 'Vestidos'),
    'blusa':    ('Blusas', 'Blusas y chalecos'),
    'pantalon': ('Jeans y pantalones', 'Jeans y pantalones'),
    'conjunto': ('Conjuntos', 'Conjuntos'),
}
ORDEN_TALLAS = ['L', 'XL', '1XL', '2XL', '3XL', '4XL']

SVG_WA = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846'
          ' 5.059 2.284 7.034L.789 23.492a.5.5 0 00.611.611l4.458-1.495A11.943 11.943 0 0012 24c6.627 0'
          ' 12-5.373 12-12S18.627 0 12 0zm0 22c-2.347 0-4.518-.801-6.24-2.144l-.436-.348-3.17 1.063'
          ' 1.063-3.17-.348-.436A9.956 9.956 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10'
          ' 10z"/></svg>')


def e(s):
    return html.escape(str(s), quote=True) if s is not None else ''


def wa(texto):
    return 'https://wa.me/%s?text=%s' % (WA, quote(texto, safe=''))


def precio(v):
    return '%.2f' % float(v)


def ruta(prof, destino):
    """prof = cuantos niveles abajo de v2/ esta la pagina."""
    return ('../' * prof) + destino if prof else destino


def foto(nombre, ancho=None, prof=1):
    base = nombre[:-5] if nombre.endswith('.webp') else nombre
    suf = '-%d' % ancho if ancho else ''
    return ('../' * (prof + 1)) + 'assets/productos/%s%s.webp' % (base, suf)


def srcset(nombre, prof=1):
    return '%s 480w, %s 800w, %s 1200w' % (foto(nombre, 480, prof),
                                           foto(nombre, 800, prof),
                                           foto(nombre, None, prof))


def estrellas(n, total=5):
    p = []
    for i in range(1, total + 1):
        cls = 'llena' if i <= round(n) else 'vacia'
        p.append('<svg class="%s" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l2.9 6.3 6.9.8'
                 '-5.1 4.6 1.4 6.8L12 17.1 5.9 20.5l1.4-6.8L2.2 9.1l6.9-.8z"/></svg>' % cls)
    return '<span class="estrellas" role="img" aria-label="%s de 5">%s</span>' % (n, ''.join(p))


# ============================================================ armazon comun
def cabeza(prof, titulo, desc, url, og_img=None, jsonld=(), extra_css=''):
    ld = '\n'.join('  <script type="application/ld+json">\n%s\n  </script>'
                   % json.dumps(b, ensure_ascii=False, indent=2) for b in jsonld)
    og = ('\n  <meta property="og:image" content="%s">' % og_img) if og_img else ''
    return """<!DOCTYPE html>
<html lang="es-SV">
<head>
  <meta charset="UTF-8">
<meta name="robots" content="noindex, nofollow">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>%s</title>
  <meta name="description" content="%s">
  <link rel="canonical" href="%s">
  <meta property="og:title" content="%s">
  <meta property="og:description" content="%s">
  <meta property="og:url" content="%s">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="BOLEM">
  <meta property="og:locale" content="es_SV">%s
  <link rel="icon" href="%sfavicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" as="style" href="%s" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="%s"></noscript>
  <link rel="stylesheet" href="%sbolem.css">%s
%s
</head>
<body>
  <a class="saltar" href="#principal">Saltar al contenido</a>
""" % (e(titulo), e(desc), url, e(titulo), e(desc), url, og,
       ruta(prof, ''), FUENTES, FUENTES, ruta(prof, ''), extra_css, ld)


def nav(prof, activo=''):
    items = [('', 'Inicio'), ('coleccion', 'La colección'), ('tallas', 'Tu talla'),
             ('resenas', 'Lo que dicen'), ('nosotras', 'Nosotras')]
    links = ''.join(
        '<a href="%s"%s>%s</a>' % (ruta(prof, x or './'),
                                   ' aria-current="page"' if x == activo else '', t)
        for x, t in items)
    return """  <nav class="nav" id="nav">
    <div class="nav-in">
      <a class="logo" href="%s" aria-label="BOLEM — inicio">BOL<b>E</b>M</a>
      <div class="nav-links">%s</div>
      <a class="nav-wa" href="%s" target="_blank" rel="noopener">%s<span class="txt">Escribinos</span></a>
      <button class="nav-btn" id="navBtn" aria-label="Menú" aria-expanded="false">
        <span></span><span></span>
      </button>
    </div>
  </nav>
""" % (ruta(prof, './'), links,
       wa('Hola, vi la página de BOLEM y quiero saber más'), SVG_WA)


def pie(prof):
    return """  <footer class="pie">
    <div class="pie-in">
      <div>
        <h4>Comprar</h4>
        <ul>
          <li><a href="%(col)s">Toda la colección</a></li>
          <li><a href="%(col)s#vestido">Vestidos</a></li>
          <li><a href="%(col)s#blusa">Blusas y chalecos</a></li>
          <li><a href="%(col)s#pantalon">Jeans y pantalones</a></li>
          <li><a href="%(col)s#conjunto">Conjuntos</a></li>
        </ul>
      </div>
      <div>
        <h4>Comprar tranquila</h4>
        <ul>
          <li><a href="%(tal)s">Cómo elegir tu talla</a></li>
          <li><a href="%(res)s">Lo que dicen las clientas</a></li>
          <li><a href="%(wa)s" target="_blank" rel="noopener">Preguntar por WhatsApp</a></li>
        </ul>
      </div>
      <div>
        <h4>BOLEM</h4>
        <ul>
          <li><a href="%(nos)s">Nosotras</a></li>
          <li><a href="%(ig)s" target="_blank" rel="noopener">Instagram</a></li>
        </ul>
      </div>
    </div>
    <div class="pie-abajo">
      <span>&copy; 2026 BOLEM &mdash; moda plus size, El Salvador</span>
      <span>Pagás al recibir &bull; envío $5 &bull; cambios en 2 días</span>
    </div>
  </footer>
  <script src="%(js)s" defer></script>
</body>
</html>
""" % dict(col=ruta(prof, 'coleccion'), tal=ruta(prof, 'tallas'),
           res=ruta(prof, 'resenas'), nos=ruta(prof, 'nosotras'),
           ig=IG, js=ruta(prof, 'bolem.js'),
           wa=wa('Hola, tengo una duda sobre una prenda'))


# ============================================================== componentes
def tarjeta(p, prof=0):
    """Tarjeta de prenda. Enlace real, no div con role=button."""
    ins = ''
    if p.get('calce'):
        ins = '<span class="insignia insignia--calce">%s</span>' % e(p['calce'].split('(')[0].strip())
    elif p.get('modelo_talla'):
        ins = '<span class="insignia">La modelo lleva %s</span>' % e(p['modelo_talla'])
    rating = ''
    if p.get('rating'):
        rating = ' <span class="rating-linea">%s %s</span>' % (
            estrellas(p['rating']), p['n_resenas'])
    return """      <a class="pieza" href="%s">
        <div class="pieza-foto">
          <img src="%s" srcset="%s" sizes="(max-width:600px) 45vw, (max-width:1000px) 30vw, 15rem"
               alt="%s" width="480" height="720" loading="lazy" decoding="async">%s
        </div>
        <p class="pieza-nombre">%s</p>
        <p class="pieza-linea"><span class="pieza-precio">$%s</span><span>%s</span>%s</p>
      </a>
""" % (ruta(prof, 'prendas/%s' % p['id']), foto(p['fotos'][0], 480, prof),
       srcset(p['fotos'][0], prof),
       e('%s plus size, tallas %s — BOLEM El Salvador' % (p['nombre'], '/'.join(p['tallas']))),
       ins, e(p['nombre']), precio(p['precio']), e(' · '.join(p['tallas'])), rating)


def falta(texto, pregunta):
    return ('<p class="falta">%s <a href="%s" target="_blank" rel="noopener">'
            'Preguntar por WhatsApp &rarr;</a></p>' % (texto, wa(pregunta)))


# ================================================================== paginas
def pagina_prenda(p, todos):
    prof = 2
    url = '%s/prendas/%s' % (SITIO, p['id'])
    cat_corta, cat_larga = CATS.get(p['categoria'], (p['categoria'], p['categoria']))
    rango = '%s–%s' % (p['tallas'][0], p['tallas'][-1]) if len(p['tallas']) > 1 else p['tallas'][0]

    titulo = '%s plus size %s — BOLEM' % (p['nombre'], rango)
    if len(titulo) > 60:
        titulo = '%s plus size — BOLEM' % p['nombre']
    desc = ('%s en tallas %s, $%s. %sRopa curvy en El Salvador: apartala por '
            'WhatsApp y pagás al recibir.'
            % (p['nombre'], rango, precio(p['precio']),
               (p['calce'] + '. ') if p.get('calce') else ''))
    desc = desc[:157].rsplit(' ', 1)[0] + '…' if len(desc) > 160 else desc

    # ---- JSON-LD. aggregateRating SOLO si hay resenas de verdad ----
    prod_ld = {
        '@context': 'https://schema.org', '@type': 'Product',
        '@id': url + '#producto', 'name': p['nombre'],
        'description': desc, 'sku': p['id'], 'category': cat_larga,
        'image': ['%s/assets/productos/%s' % (SITIO.rsplit('/v2', 1)[0], f) for f in p['fotos']],
        'size': p['tallas'],
        'brand': {'@type': 'Brand', 'name': 'BOLEM'},
        'offers': {
            '@type': 'Offer', 'url': url, 'price': precio(p['precio']),
            'priceCurrency': 'USD', 'availability': 'https://schema.org/InStock',
            'itemCondition': 'https://schema.org/NewCondition',
            'seller': {'@type': 'ClothingStore', 'name': 'BOLEM'},
            'shippingDetails': {
                '@type': 'OfferShippingDetails',
                'shippingRate': {'@type': 'MonetaryAmount', 'value': '5.00', 'currency': 'USD'},
                'shippingDestination': {'@type': 'DefinedRegion', 'addressCountry': 'SV'},
                'deliveryTime': {'@type': 'ShippingDeliveryTime',
                                 'transitTime': {'@type': 'QuantitativeValue', 'minValue': 1,
                                                 'maxValue': 3, 'unitCode': 'DAY'}}},
            'hasMerchantReturnPolicy': {
                '@type': 'MerchantReturnPolicy', 'applicableCountry': 'SV',
                'returnPolicyCategory': 'https://schema.org/MerchantReturnFiniteReturnWindow',
                'merchantReturnDays': 2, 'returnMethod': 'https://schema.org/ReturnByMail',
                'returnFees': 'https://schema.org/FreeReturn'}},
    }
    if p.get('tela'):
        prod_ld['material'] = p['tela']
    if p.get('rating'):
        prod_ld['aggregateRating'] = {'@type': 'AggregateRating',
                                      'ratingValue': p['rating'],
                                      'reviewCount': p['n_resenas']}
        prod_ld['review'] = [{
            '@type': 'Review',
            'reviewRating': {'@type': 'Rating', 'ratingValue': r['estrellas'], 'bestRating': 5},
            'author': {'@type': 'Person', 'name': r['autora']},
            'datePublished': r['fecha'], 'reviewBody': r['texto'] or '',
        } for r in p['resenas'][:8]]

    migas_ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                'itemListElement': [
                    {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': SITIO + '/'},
                    {'@type': 'ListItem', 'position': 2, 'name': 'La colección',
                     'item': SITIO + '/coleccion'},
                    {'@type': 'ListItem', 'position': 3, 'name': cat_corta,
                     'item': '%s/coleccion#%s' % (SITIO, p['categoria'])},
                    {'@type': 'ListItem', 'position': 4, 'name': p['nombre'], 'item': url}]}

    # ---- galeria: todas las fotos en el DOM, se ven sin JavaScript ----
    g = ['<div class="gal-grande"><img id="galPrincipal" src="%s" srcset="%s"'
         ' sizes="(max-width:900px) 100vw, 50vw" alt="%s" width="1200" height="1800"'
         ' fetchpriority="high" decoding="async"></div>'
         % (foto(p['fotos'][0], 800, prof), srcset(p['fotos'][0], prof),
            e('%s plus size — BOLEM El Salvador' % p['nombre']))]
    if len(p['fotos']) > 1:
        tiras = ''.join(
            '<button type="button" data-src="%s" data-set="%s" aria-current="%s"'
            ' aria-label="Ver foto %d"><img src="%s" alt="" width="480" height="720"'
            ' loading="lazy" decoding="async"></button>'
            % (foto(f, 800, prof), srcset(f, prof), 'true' if i == 0 else 'false',
               i + 1, foto(f, 480, prof))
            for i, f in enumerate(p['fotos']))
        g.append('<div class="gal-tira" role="group" aria-label="Más fotos">%s</div>' % tiras)

    # ---- el bloque de calce: el corazon de v2 ----
    calce = []
    if p.get('calce'):
        calce.append('<p class="calce-veredicto">%s</p>' % e(p['calce']))
    if p.get('modelo_altura') or p.get('modelo_talla'):
        partes = []
        if p.get('modelo_altura'):
            partes.append('mide %s' % e(p['modelo_altura']))
        if p.get('modelo_talla'):
            partes.append('lleva talla <b>%s</b>' % e(p['modelo_talla']))
        calce.append('<p class="calce-modelo">La modelo de la foto %s.</p>' % ' y '.join(partes))
    if not calce:
        calce.append(falta(
            'Todavía no publicamos cómo queda esta prenda ni la talla que lleva la modelo. '
            'No lo vamos a adivinar.',
            'Hola, quiero saber cómo queda el %s y qué talla lleva la modelo' % p['nombre']))

    # ---- medidas en plano ----
    if p['medidas']:
        filas = ''.join(
            '<tr><td class="talla">%s</td>%s</tr>'
            % (e(m['talla']), ''.join('<td class="n">%s</td>' % (
                ('%g' % m[k]) if m.get(k) is not None else '—')
                for k in ('busto_cm', 'cintura_cm', 'cadera_cm', 'largo_cm')))
            for m in p['medidas'])
        medidas = ("""<div class="tabla-marco"><table class="datos">
          <thead><tr><th class="talla">Talla</th><th>Busto</th><th>Cintura</th><th>Cadera</th><th>Largo</th></tr></thead>
          <tbody>%s</tbody></table></div>
          <p class="nota-medida">Medidas de <strong>la prenda acostada</strong>, en centímetros —
          no de tu cuerpo. Es la forma honesta de compararla con algo que ya tenés y te queda bien.</p>""" % filas)
    else:
        medidas = falta(
            'Todavía no tenemos medida en plano de esta prenda. Estamos midiéndolas una por una '
            'y publicamos solo las que ya medimos.',
            'Hola, quiero las medidas exactas del %s' % p['nombre'])

    # ---- ficha tecnica: solo lo que existe ----
    dl = [('Precio', '$%s' % precio(p['precio'])),
          ('Tallas', ' · '.join(p['tallas'])),
          ('Categoría', cat_corta)]
    if p.get('colores', 1) > 1:
        dl.append(('Colores', '%d' % p['colores']))
    if p.get('tela'):
        dl.append(('Tela', p['tela']))
    if p.get('cuidado'):
        dl.append(('Cuidado', p['cuidado']))
    ficha = ''.join('<dt>%s</dt><dd>%s</dd>' % (e(k), e(v)) for k, v in dl)
    if not p.get('tela'):
        ficha_extra = falta('Falta la composición de la tela.',
                            'Hola, ¿de qué tela es el %s?' % p['nombre'])
    else:
        ficha_extra = ''

    # ---- por que la elegi (lo unico que nadie puede copiar) ----
    porque = ''
    if p.get('por_que_la_elegi'):
        porque = ("""    <section class="porque">
      <div class="marco">
        <p class="etiqueta">Por qué la elegí</p>
        <blockquote class="porque-cita">%s</blockquote>
        <p class="porque-firma">— Mónica, fundadora de BOLEM</p>
      </div>
    </section>
""" % e(p['por_que_la_elegi']))

    # ---- resenas ----
    if p['resenas']:
        items = ''.join("""        <li class="resena">
          <div class="resena-top">%s<span class="resena-autora">%s</span>%s</div>
          %s<p class="resena-texto">%s</p>%s
        </li>""" % (
            estrellas(r['estrellas']), e(r['autora']),
            '<span class="resena-verif">Compra verificada</span>' if r['verificada'] else '',
            ('<p class="resena-titulo">%s</p>' % e(r['titulo'])) if r['titulo'] else '',
            e(r['texto'] or ''),
            ('<p class="resena-calce">Pidió %s · le quedó %s</p>'
             % (e(r['talla_pedida'] or '—'), e(r['calce_real'])))
            if r.get('calce_real') else '')
            for r in p['resenas'])
        resenas = ('<div class="resena-cabeza">%s<span>%s de 5 · %d reseña%s</span></div>'
                   '<ul class="resena-lista">%s</ul>'
                   % (estrellas(p['rating']), p['rating'], p['n_resenas'],
                      's' if p['n_resenas'] != 1 else '', items))
    else:
        resenas = falta(
            'Esta prenda todavía no tiene reseñas. No inventamos ninguna: cuando una clienta '
            'nos cuente cómo le quedó y nos dé permiso, aparece acá con su nombre.',
            'Hola, compré el %s y quiero contarles cómo me quedó' % p['nombre'])

    # ---- seguí viendo ----
    hermanas = [q for q in todos if q['categoria'] == p['categoria'] and q['id'] != p['id']]
    hermanas.sort(key=lambda q: abs(q['precio'] - p['precio']))
    rel = ''.join(tarjeta(q, prof) for q in hermanas[:4])

    mensaje = 'Hola, quiero apartar el %s ($%s). Mi talla es: ' % (p['nombre'], precio(p['precio']))
    if p.get('colores', 1) > 1:
        mensaje += ' y lo quiero en color: '

    cuerpo = """  <main id="principal">
    <nav class="migas marco" aria-label="Dónde estás">
      <a href="../../">Inicio</a> <span aria-hidden="true">/</span>
      <a href="../../coleccion">La colección</a> <span aria-hidden="true">/</span>
      <a href="../../coleccion#%(cid)s">%(ccorta)s</a> <span aria-hidden="true">/</span>
      <span aria-current="page">%(nombre)s</span>
    </nav>

    <div class="prenda marco">
      <div class="prenda-gal">%(galeria)s</div>

      <div class="prenda-info">
        <p class="etiqueta">%(ccorta)s</p>
        <h1>%(nombre)s</h1>
        <p class="prenda-precio">$%(precio)s</p>
        %(rating_top)s

        <div class="bloque">
          <p class="etiqueta">Tallas</p>
          <div class="tallas-fila">%(tallas)s</div>
          %(nota_xl)s
        </div>

        <div class="bloque bloque--calce">
          <p class="etiqueta">Cómo queda</p>
          %(calce)s
        </div>

        <a class="btn btn--wa" href="%(wa)s" target="_blank" rel="noopener">%(svg)s Apartar por WhatsApp</a>

        <ul class="confianza">
          <li><b>Pagás al recibir.</b> No adelantás nada.</li>
          <li><b>Envío $5</b> a todo el país, llega en 1 a 3 días.</li>
          <li><b>Cambios</b> dentro de los 2 días.</li>
        </ul>
      </div>
    </div>

    <section class="marco bloque-ancho">
      <h2>Las medidas de esta prenda</h2>
      %(medidas)s
    </section>

    <section class="marco bloque-ancho ficha-tecnica">
      <h2>La ficha</h2>
      <dl class="ficha">%(ficha)s</dl>
      %(ficha_extra)s
    </section>
%(porque)s
    <section class="marco bloque-ancho">
      <h2>Lo que dicen de esta prenda</h2>
      %(resenas)s
    </section>

    <section class="marco bloque-ancho">
      <h2>Seguí viendo en %(ccorta)s</h2>
      <div class="rejilla">
%(rel)s      </div>
    </section>
  </main>
""" % dict(cid=p['categoria'], ccorta=e(cat_corta), nombre=e(p['nombre']),
           galeria=''.join(g), precio=precio(p['precio']),
           rating_top=('<p class="rating-linea">%s %s de 5 · %d reseñas</p>'
                       % (estrellas(p['rating']), p['rating'], p['n_resenas']))
           if p.get('rating') else '',
           tallas=''.join('<span class="talla-chip">%s</span>' % e(t) for t in p['tallas']),
           nota_xl=('<p class="nota-talla">XL y 1XL <strong>no son la misma talla</strong> — '
                    'vienen de dos escalas distintas. <a href="../../tallas">Te lo explicamos</a>.</p>')
           if ('XL' in p['tallas'] and '1XL' in p['tallas']) else
           '<p class="nota-talla"><a href="../../tallas">Cómo elegir tu talla</a></p>',
           calce='\n          '.join(calce), wa=e(wa(mensaje)), svg=SVG_WA,
           medidas=medidas, ficha=ficha, ficha_extra=ficha_extra,
           porque=porque, resenas=resenas, rel=rel)

    og = '%s/assets/productos/%s' % (SITIO.rsplit('/v2', 1)[0], p['fotos'][0])
    return cabeza(prof, titulo, desc, url, og, [prod_ld, migas_ld]) + nav(prof) + cuerpo + pie(prof)


def pagina_coleccion(prods):
    prof = 1
    url = SITIO + '/coleccion'
    por_cat = {}
    for p in prods:
        por_cat.setdefault(p['categoria'], []).append(p)

    # atajos por talla: cada uno lleva a su propia pagina, no a un filtro de JS
    cuenta_talla = {t: sum(1 for p in prods if t in p['tallas']) for t in ORDEN_TALLAS}
    chips_talla = ''.join(
        '<a class="chip" href="../talla/%s/">%s <small>%d</small></a>'
        % (t.lower(), t, cuenta_talla[t]) for t in ORDEN_TALLAS if cuenta_talla[t])

    chips_cat = ''.join(
        '<a class="chip" href="#%s">%s <small>%d</small></a>'
        % (k, CATS[k][0], len(por_cat.get(k, []))) for k in CATS if por_cat.get(k))

    bloques = []
    for k in CATS:
        g = por_cat.get(k)
        if not g:
            continue
        g = sorted(g, key=lambda p: p['precio'])
        bloques.append("""    <section class="cat-bloque" id="%s">
      <div class="marco">
        <div class="cat-cabeza">
          <h2>%s</h2>
          <p class="etiqueta">%d piezas · $%s a $%s</p>
        </div>
        <div class="rejilla">
%s        </div>
      </div>
    </section>
""" % (k, e(CATS[k][1]), len(g), precio(min(p['precio'] for p in g)),
       precio(max(p['precio'] for p in g)), ''.join(tarjeta(p, prof) for p in g)))

    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage',
          'name': 'La colección BOLEM', 'url': url,
          'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(prods),
                         'itemListElement': [
                             {'@type': 'ListItem', 'position': i + 1,
                              'url': '%s/prendas/%s' % (SITIO, p['id']),
                              'name': p['nombre']} for i, p in enumerate(prods)]}}

    titulo = '%d piezas plus size XL a 4XL — BOLEM El Salvador' % len(prods)
    desc = ('Las %d piezas de BOLEM en tallas XL a 4XL. Filtrá por tu talla, mirá las '
            'medidas de cada prenda y apartala por WhatsApp. Pagás al recibir.' % len(prods))

    cuerpo = """  <main id="principal">
    <header class="col-cabeza marco">
      <p class="etiqueta">Colección 2026 · El Salvador</p>
      <h1>%d piezas que sí te van a quedar</h1>
      <p class="col-bajada leer">Cada prenda dice su talla, sus medidas reales y cómo queda.
      Si algo no lo sabemos todavía, lo decimos — no lo adivinamos.</p>
    </header>

    <div class="filtros marco">
      <div class="filtro-grupo">
        <p class="etiqueta">Empezá por tu talla</p>
        <div class="chips">%s</div>
      </div>
      <div class="filtro-grupo">
        <p class="etiqueta">O por lo que buscás</p>
        <div class="chips">%s</div>
      </div>
    </div>

%s  </main>
""" % (len(prods), chips_talla, chips_cat, ''.join(bloques))
    return cabeza(prof, titulo, desc, url, None, [ld]) + nav(prof, 'coleccion') + cuerpo + pie(prof)


def pagina_talla(talla, prods):
    """Una pagina por talla. Sirve sin JavaScript, la sigue Google, y ataca
    justo lo que la clienta busca: 'ropa plus size talla 3XL'."""
    prof = 2
    g = sorted([p for p in prods if talla in p['tallas']], key=lambda p: p['precio'])
    url = '%s/talla/%s' % (SITIO, talla.lower())
    por_cat = {}
    for p in g:
        por_cat.setdefault(p['categoria'], []).append(p)
    resumen = ' · '.join('%d %s' % (len(v), CATS[k][0].lower()) for k, v in por_cat.items())

    titulo = 'Ropa plus size talla %s — %d piezas | BOLEM' % (talla, len(g))
    desc = ('%d piezas en talla %s: %s. Precios de $%s a $%s. Ropa curvy en El Salvador '
            'con las medidas de cada prenda publicadas.'
            % (len(g), talla, resumen, precio(min(p['precio'] for p in g)),
               precio(max(p['precio'] for p in g))))
    desc = desc[:157].rsplit(' ', 1)[0] + '…' if len(desc) > 160 else desc

    otras = ''.join('<a class="chip" href="../%s/">%s</a>' % (t.lower(), t)
                    for t in ORDEN_TALLAS if t != talla and any(t in p['tallas'] for p in prods))

    explica = ''
    if talla in ('XL', '1XL'):
        explica = ("""<div class="caja caja--ojo leer">
        <p><strong>Ojo con XL y 1XL:</strong> no son la misma talla. XL es la más grande de la
        escala recta y 1XL la más chica de la escala plus. <a href="../../tallas">Acá está la
        diferencia</a>, con la tabla de equivalencias.</p>
      </div>""")

    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage',
          'name': 'Ropa plus size talla %s' % talla, 'url': url,
          'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(g),
                         'itemListElement': [
                             {'@type': 'ListItem', 'position': i + 1,
                              'url': '%s/prendas/%s' % (SITIO, p['id']),
                              'name': p['nombre']} for i, p in enumerate(g)]}}
    migas = {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
             'itemListElement': [
                 {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': SITIO + '/'},
                 {'@type': 'ListItem', 'position': 2, 'name': 'La colección',
                  'item': SITIO + '/coleccion'},
                 {'@type': 'ListItem', 'position': 3, 'name': 'Talla %s' % talla, 'item': url}]}

    cuerpo = """  <main id="principal">
    <nav class="migas marco" aria-label="Dónde estás">
      <a href="../../">Inicio</a> <span aria-hidden="true">/</span>
      <a href="../../coleccion">La colección</a> <span aria-hidden="true">/</span>
      <span aria-current="page">Talla %(t)s</span>
    </nav>

    <header class="col-cabeza marco">
      <p class="etiqueta">Talla %(t)s</p>
      <h1>%(n)d piezas en talla %(t)s</h1>
      <p class="col-bajada leer">%(resumen)s. Todo lo que tenemos hoy en esta talla, de menor a
      mayor precio.</p>
      %(explica)s
    </header>

    <div class="filtros marco">
      <div class="filtro-grupo">
        <p class="etiqueta">Ver otra talla</p>
        <div class="chips">%(otras)s <a class="chip" href="../../coleccion">Todas</a></div>
      </div>
    </div>

    <section class="marco"><div class="rejilla">
%(cards)s    </div></section>
  </main>
""" % dict(t=talla, n=len(g), resumen=e(resumen.capitalize()), explica=explica,
           otras=otras, cards=''.join(tarjeta(p, prof) for p in g))
    return cabeza(prof, titulo, desc, url, None, [ld, migas]) + nav(prof, 'coleccion') + cuerpo + pie(prof)


def pagina_home(prods, resumen):
    prof = 0
    url = SITIO + '/'
    cuenta_talla = {t: sum(1 for p in prods if t in p['tallas']) for t in ORDEN_TALLAS}
    puertas = ''.join(
        """        <a class="puerta" href="talla/%s/">
          <span class="puerta-talla">%s</span>
          <span class="puerta-n">%d piezas</span>
        </a>""" % (t.lower(), t, cuenta_talla[t])
        for t in ORDEN_TALLAS if cuenta_talla[t])

    destacadas = [p for p in prods if p['destacada']]
    if len(destacadas) < 8:
        resto = [p for p in prods if not p['destacada']]
        resto.sort(key=lambda p: (-len(p['fotos']), -p['precio']))
        destacadas += resto[:8 - len(destacadas)]
    tarjetas = ''.join(tarjeta(p, prof) for p in destacadas[:8])

    con_medidas = resumen['n_con_medidas']
    todas_r = [(p, r) for p in prods for r in p.get('resenas', [])]
    todas_r.sort(key=lambda x: x[1]['fecha'] or '', reverse=True)
    if todas_r:
        voces = ''.join(
            '        <li class="voz">%s<p>%s</p><cite>%s &mdash; sobre %s</cite></li>'
            % (estrellas(r['estrellas']), e(r['texto'] or ''), e(r['autora']), e(p['nombre']))
            for p, r in todas_r[:3])
        bloque_voces = ('<ul class="voces">%s</ul>'
                        '<p><a href="resenas">Ver todas las rese&ntilde;as &rarr;</a></p>' % voces)
    else:
        bloque_voces = falta(
            'Todav&iacute;a no publicamos rese&ntilde;as. Estamos pregunt&aacute;ndoles a las '
            'clientas que ya compraron, y solo va a salir ac&aacute; lo que ellas escriban y nos '
            'den permiso de publicar. Ni una inventada.',
            'Hola, compre en BOLEM y quiero contarles como me fue')

    ld = {'@context': 'https://schema.org', '@type': 'ClothingStore', '@id': SITIO + '/#bolem',
          'name': 'BOLEM', 'url': SITIO + '/',
          'description': 'Ropa plus size en El Salvador, tallas XL a 4XL.',
          'address': {'@type': 'PostalAddress', 'addressCountry': 'SV'},
          'areaServed': {'@type': 'Country', 'name': 'El Salvador'},
          'paymentAccepted': 'Efectivo contra entrega',
          'currenciesAccepted': 'USD', 'sameAs': [IG]}

    FAQ = [
        ('¿Cómo sé qué talla pedir?',
         'Cada prenda tiene su propia página con las tallas disponibles y, cuando ya la '
         'medimos, las medidas de la prenda acostada. Compará esas medidas con algo que ya '
         'tenés y te queda bien: es más confiable que la etiqueta, porque cada marca '
         'corta distinto. Si tenés dudas, escribinos y te decimos la medida exacta de esa pieza.'),
        ('¿XL y 1XL son lo mismo?',
         'No. XL es la talla más grande de la escala recta y 1XL la más chica de la '
         'escala plus. Se tocan en el ancho pero están cortadas distinto. De hecho hay '
         'prendas nuestras que ofrecen las dos como opciones separadas.'),
        ('¿Cómo pago?',
         'Pagás al recibir. No adelantás nada. Apartás por WhatsApp, te llega, '
         'la ves, y ahí pagás.'),
        ('¿Cuánto cuesta el envío y cuánto tarda?',
         'Cinco dólares a todo El Salvador, y llega en uno a tres días.'),
        ('¿Puedo cambiarla si no me queda?',
         'Sí, dentro de los 2 días de recibida y sin usar. Escribinos por WhatsApp '
         'y coordinamos.'),
        ('¿Por qué no hay carrito de compras?',
         'Porque acá se compra hablando. Mónica te contesta ella misma, te dice si esa '
         'talla te va a quedar y te aparta la prenda. Un carrito no hace eso.'),
    ]
    faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage',
              'mainEntity': [{'@type': 'Question', 'name': q,
                              'acceptedAnswer': {'@type': 'Answer', 'text': a}}
                             for q, a in FAQ]}
    faq_html = ''.join(
        '<details class="faq"><summary>%s</summary><p>%s</p></details>' % (e(q), e(a))
        for q, a in FAQ)

    titulo = 'BOLEM — ropa plus size en El Salvador, tallas XL a 4XL'
    desc = ('Ropa plus size en El Salvador. %d piezas de la XL a la 4XL con las medidas de cada '
            'prenda publicadas. Apartás por WhatsApp y pagás al recibir.' % len(prods))

    cuerpo = """  <main id="principal">

    <header class="hero">
      <div class="marco hero-in">
        <p class="etiqueta">Moda plus size &bull; El Salvador</p>
        <h1>Aqu&iacute; tu talla no es la excepci&oacute;n.<br><span class="subrayado">Es la regla.</span></h1>
        <p class="hero-bajada leer">%(n)d piezas de la XL a la 4XL, elegidas una por una por M&oacute;nica.
        Cada una con sus medidas reales, para que sepas si te queda <em>antes</em> de comprarla.</p>
      </div>
    </header>

    <section class="puertas-sec">
      <div class="marco">
        <h2 class="puertas-titulo">Empez&aacute; por tu talla</h2>
        <p class="puertas-bajada leer">Porque nadie entra a una tienda pensando
        &laquo;quiero una blusa&raquo;. Se entra pensando &laquo;qu&eacute; hay para m&iacute;&raquo;.</p>
        <div class="puertas">
%(puertas)s
        </div>
      </div>
    </section>

    <section class="marco bloque-ancho">
      <div class="cat-cabeza">
        <h2>Algunas piezas</h2>
        <p class="etiqueta"><a href="coleccion">Ver las %(n)d &rarr;</a></p>
      </div>
      <div class="rejilla">
%(tarjetas)s      </div>
    </section>

    <section class="promesas">
      <div class="marco">
        <div class="promesa-grid">
          <div class="promesa">
            <p class="promesa-n">%(medidas)d de %(n)d</p>
            <h3>Prendas con sus medidas publicadas</h3>
            <p>Medimos la prenda acostada, talla por talla, y publicamos el n&uacute;mero. Las que
            todav&iacute;a no medimos lo dicen: preferimos que falte a que est&eacute; mal.</p>
          </div>
          <div class="promesa">
            <p class="promesa-n">Cero</p>
            <h3>Adelantado</h3>
            <p>Pag&aacute;s cuando la ten&eacute;s en la mano. Si no te convence al verla, no la pag&aacute;s.</p>
          </div>
          <div class="promesa">
            <p class="promesa-n">Una</p>
            <h3>Persona elige cada pieza</h3>
            <p>BOLEM no fabrica: M&oacute;nica busca entre marcas que s&iacute; cortan para cuerpos
            curvy, y trae solo lo que se pondr&iacute;a ella.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="marco bloque-ancho">
      <h2>Lo que dicen las clientas</h2>
      %(voces)s
    </section>

    <section class="marco bloque-ancho">
      <h2>Lo que siempre nos preguntan</h2>
      <div class="faq-lista leer">%(faq)s</div>
    </section>

    <section class="cierre">
      <div class="marco">
        <h2>&iquest;Viste algo que te gust&oacute;?</h2>
        <p class="leer">Escribile a M&oacute;nica. Te dice si esa talla te va a quedar, te la aparta,
        y la pag&aacute;s cuando llegue.</p>
        <a class="btn btn--wa cierre-btn" href="%(wa)s" target="_blank" rel="noopener">%(svg)s Escribir por WhatsApp</a>
      </div>
    </section>
  </main>
""" % dict(n=len(prods), puertas=puertas, tarjetas=tarjetas, medidas=con_medidas,
           voces=bloque_voces, faq=faq_html,
           wa=e(wa('Hola, vi la pagina de BOLEM y quiero preguntar por una prenda')), svg=SVG_WA)

    return cabeza(prof, titulo, desc, url, None, [ld, faq_ld]) + nav(prof, '') + cuerpo + pie(prof)


def pagina_resenas(prods):
    prof = 1
    url = SITIO + '/resenas'
    con = [p for p in prods if p.get('resenas')]
    total = sum(p['n_resenas'] for p in con)

    if con:
        prom = round(sum(p['rating'] * p['n_resenas'] for p in con) / total, 2)
        cabecera = ('<div class="res-resumen">%s<p class="res-prom">%s de 5</p>'
                    '<p class="etiqueta">%d rese&ntilde;as sobre %d prendas</p></div>'
                    % (estrellas(prom), prom, total, len(con)))
        cuerpo_res = ''.join(
            """    <section class="marco res-bloque">
      <div class="res-cabeza">
        <a href="../prendas/%s/"><img src="%s" alt="%s" width="480" height="720" loading="lazy"></a>
        <div>
          <h2><a href="../prendas/%s/">%s</a></h2>
          <p class="rating-linea">%s %s de 5 &middot; %d rese&ntilde;as</p>
        </div>
      </div>
      <ul class="resena-lista">%s</ul>
    </section>""" % (
                p['id'], foto(p['fotos'][0], 480, prof), e(p['nombre']), p['id'], e(p['nombre']),
                estrellas(p['rating']), p['rating'], p['n_resenas'],
                ''.join('<li class="resena">%s<span class="resena-autora">%s</span>'
                        '<p class="resena-texto">%s</p></li>'
                        % (estrellas(r['estrellas']), e(r['autora']), e(r['texto'] or ''))
                        for r in p['resenas']))
            for p in sorted(con, key=lambda x: -x['n_resenas']))
    else:
        cabecera = ''
        cuerpo_res = """    <section class="marco">
      <div class="caja caja--ojo leer">
        <h2>Todav&iacute;a no hay ninguna, y no las vamos a inventar</h2>
        <p>Podr&iacute;amos escribir diez rese&ntilde;as lindas ahorita mismo. No lo vamos a hacer,
        por dos razones. La primera es que ser&iacute;a mentirte. La segunda es que Google castiga
        las rese&ntilde;as fabricadas m&aacute;s duro que la ausencia de rese&ntilde;as.</p>
        <p>Lo que s&iacute; estamos haciendo: le escribimos a las clientas que ya compraron y les
        preguntamos c&oacute;mo les qued&oacute;. Lo que ellas contesten &mdash;y solo si nos dan
        permiso de publicarlo&mdash; va a aparecer ac&aacute;, con su nombre y la prenda que compraron.</p>
        <p><strong>Si vos ya compraste en BOLEM</strong>, tu rese&ntilde;a es de las primeras.</p>
        <a class="btn btn--wa" style="max-width:22rem" href="%s" target="_blank" rel="noopener">%s Contar mi experiencia</a>
      </div>
    </section>""" % (e(wa('Hola, compre en BOLEM y quiero contarles como me fue')), SVG_WA)

    titulo = 'Lo que dicen las clientas — BOLEM'
    desc = ('Reseñas reales de clientas de BOLEM sobre las prendas, las tallas y el servicio. '
            'Solo publicamos lo que las clientas escriben y autorizan.')
    ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': titulo,
          'description': desc, 'url': url}

    enc = """    <section class="marco bloque-ancho">
      <div class="caja caja--acento leer">
        <p class="etiqueta">C&oacute;mo se arma esta p&aacute;gina</p>
        <p>Cada rese&ntilde;a viene de una clienta que compr&oacute; de verdad. La marcamos como
        <strong>compra verificada</strong> cuando la prenda aparece en su historial. No editamos
        el texto y no borramos las que no nos gustan: una p&aacute;gina donde todas las
        rese&ntilde;as son de cinco estrellas no le sirve a nadie para decidir.</p>
      </div>
    </section>"""

    cuerpo = """  <main id="principal">
    <header class="col-cabeza marco">
      <p class="etiqueta">Rese&ntilde;as</p>
      <h1>Lo que dicen las clientas</h1>
      %s
    </header>
%s
%s
  </main>
""" % (cabecera, cuerpo_res, enc)
    return cabeza(prof, titulo, desc, url, None, [ld]) + nav(prof, 'resenas') + cuerpo + pie(prof)


def pagina_tallas(prods):
    prof = 1
    url = SITIO + '/tallas'
    n = len(prods)
    cuenta = {t: sum(1 for p in prods if t in p['tallas']) for t in ORDEN_TALLAS}
    cruzan = [p for p in prods if 'XL' in p['tallas'] and '1XL' in p['tallas']]
    rangos = len({tuple(p['tallas']) for p in prods})
    con_medidas = [p for p in prods if p['medidas']]

    filas_cuenta = ''.join(
        '<tr><td class="talla">%s</td><td class="n">%d</td>'
        '<td><span class="barra" style="--p:%d%%"></span></td></tr>'
        % (t, cuenta[t], round(100 * cuenta[t] / n)) for t in ORDEN_TALLAS if cuenta[t])

    if con_medidas:
        lista_med = ''.join(
            '<li><a href="../prendas/%s/">%s</a></li>' % (p['id'], e(p['nombre']))
            for p in con_medidas[:20])
        bloque_med = ('<p>Ya medimos <strong>%d de %d</strong> prendas. Estas ya tienen su tabla '
                      'publicada:</p><ul class="lista-2col">%s</ul>'
                      % (len(con_medidas), n, lista_med))
    else:
        bloque_med = falta(
            'Todav&iacute;a no publicamos medidas en plano de ninguna prenda. Las estamos midiendo '
            'una por una y cada una aparece en su p&aacute;gina apenas est&aacute; medida. '
            'Mientras tanto te la damos por chat, prenda por prenda.',
            'Hola, quiero las medidas exactas de una prenda')

    FAQ = [
        ('¿XL y 1XL son la misma talla?',
         'No. XL es la talla más grande de la escala recta (S, M, L, XL) y 1XL es la más chica de '
         'la escala plus (1XL a 4XL). Se tocan en el ancho pero están cortadas con proporciones '
         'distintas: la plus lleva más espacio en busto, cadera y sisa. En nuestro catálogo hay '
         '%d prendas que ofrecen XL y 1XL como dos opciones distintas de la misma pieza; si '
         'fueran lo mismo, no tendría sentido ofrecer las dos.' % len(cruzan)),
        ('¿Qué significa 16W, 18W o 20W?',
         'La W viene de women’s, la escala numérica plus de Estados Unidos. Es la misma '
         'familia que 1XL a 4XL pero contada con números: 14W-16W suele corresponder a 1XL, '
         '18W-20W a 2XL, 22W-24W a 3XL y 26W-28W a 4XL. Aparece sobre todo en jeans y pantalones.'),
        ('¿Por qué una misma talla me queda distinta en cada marca?',
         'Porque no existe una norma obligatoria de tallas. Cada marca corta sobre su propio molde '
         'base y decide cuánto crece de una talla a la siguiente. Por eso la única medida '
         'confiable es la de la prenda, no la de la etiqueta.'),
        ('Si estoy entre dos tallas, ¿cuál pido?',
         'Depende de la prenda, no de vos. En algo estructurado —un blazer, un pantalón formal— '
         'la talla mayor. En algo con elástico, smocked o de caída suelta, la menor suele quedar '
         'mejor porque la prenda ya tiene el espacio incorporado.'),
        ('¿Por qué no publican una tabla de medidas general?',
         'Porque nos equivocaríamos en la mitad de los casos. Compramos a varios mayoristas de '
         'Estados Unidos y cada uno corta distinto: una tabla única sería un promedio que no '
         'describe a ninguna prenda. Publicamos la medida de cada prenda, una por una.'),
    ]
    faq_ld = {'@context': 'https://schema.org', '@type': 'FAQPage',
              'mainEntity': [{'@type': 'Question', 'name': q,
                              'acceptedAnswer': {'@type': 'Answer', 'text': a}}
                             for q, a in FAQ]}
    faq_html = ''.join('<details class="faq"><summary>%s</summary><p>%s</p></details>'
                       % (e(q), e(a)) for q, a in FAQ)

    titulo = 'XL, 1XL o 2XL: cómo elegir tu talla | BOLEM'
    desc = ('XL y 1XL no son la misma talla. Te explicamos las tres escalas que conviven en la '
            'ropa plus size, qué significa 16W, y cómo medir una prenda para no equivocarte.')
    art_ld = {'@context': 'https://schema.org', '@type': 'Article',
              'headline': 'XL, 1XL o 2XL: cómo elegir tu talla',
              'description': desc, 'url': url, 'inLanguage': 'es-SV',
              'author': {'@type': 'Organization', 'name': 'BOLEM'},
              'publisher': {'@type': 'Organization', 'name': 'BOLEM'},
              'datePublished': '2026-08-17', 'dateModified': '2026-08-17'}

    cuerpo = """  <main id="principal">
    <header class="col-cabeza marco">
      <p class="etiqueta">Tu talla</p>
      <h1>XL, 1XL o 2XL:<br><span class="subrayado">no son lo mismo</span></h1>
      <p class="col-bajada leer">Si alguna vez compraste una XL que te qued&oacute; y otra XL que
      no te entr&oacute;, no fue tu cuerpo. Fueron dos escalas distintas usando la misma letra.</p>
    </header>

    <section class="marco bloque-ancho leer">
      <h2>Son dos escalas, no una fila que crece</h2>
      <p>La confusi&oacute;n nace de creer que las tallas van en una sola fila: S, M, L, XL, y
      despu&eacute;s 2XL, 3XL, 4XL. No es as&iacute;. En la ropa que se fabrica en Estados Unidos
      &mdash;de donde viene casi todo lo que se vende ac&aacute;&mdash; hay <strong>dos escalas
      separadas, cada una con su propio molde</strong>.</p>
    </section>

    <section class="marco bloque-ancho">
      <div class="escalas">
        <div class="escala">
          <p class="etiqueta">Escala recta</p>
          <div class="escala-fila"><b>S</b><b>M</b><b>L</b><b class="borde">XL</b></div>
          <p>Termina en XL. Cortada sobre un molde que asume ciertas proporciones y las agranda parejo.</p>
        </div>
        <div class="escala">
          <p class="etiqueta">Escala plus</p>
          <div class="escala-fila"><b class="borde">1XL</b><b>2XL</b><b>3XL</b><b>4XL</b></div>
          <p>Empieza en 1XL. Otro molde de arranque: m&aacute;s espacio en busto y cadera, sisa
          m&aacute;s ancha. No es la escala recta estirada.</p>
        </div>
      </div>
      <p class="leer" style="margin-top:1.5rem"><strong>XL es la m&aacute;s grande de una escala;
      1XL es la m&aacute;s chica de otra.</strong> Son vecinas, no gemelas.</p>
    </section>

    <section class="marco bloque-ancho">
      <div class="dato-duro">
        <p class="dato-n">%(cruzan)d de %(n)d</p>
        <p class="dato-txt">prendas nuestras ofrecen <strong>XL y 1XL como dos opciones
        distintas</strong> de la misma pieza. Si fueran la misma talla, ninguna marca
        ofrecer&iacute;a las dos.</p>
      </div>
      <p class="leer">Y no es la &uacute;nica se&ntilde;al de que ac&aacute; conviven varias formas
      de contar: entre las %(n)d prendas hay <strong>%(rangos)d rangos de talla diferentes</strong>.
      Pasa porque BOLEM no le compra a una sola f&aacute;brica, y cada mayorista etiqueta con la
      escala de su molde. No lo unificamos a la fuerza: cambiarle la etiqueta a una prenda no le
      cambia el corte, solo esconde el problema.</p>
    </section>

    <section class="marco bloque-ancho">
      <h2>Qu&eacute; tenemos en cada talla</h2>
      <div class="tabla-marco"><table class="datos">
        <thead><tr><th class="talla">Talla</th><th>Piezas</th><th>Del cat&aacute;logo</th></tr></thead>
        <tbody>%(filas)s</tbody>
      </table></div>
      <p class="leer" style="margin-top:1rem"><a href="../coleccion">Ver la colecci&oacute;n
      completa</a> o entrar directo a tu talla desde el inicio.</p>
    </section>

    <section class="marco bloque-ancho leer">
      <h2>La tercera escala: la W</h2>
      <p>En jeans y pantalones vas a toparte con <strong>16W</strong>, <strong>18W</strong> o
      <strong>20W</strong>. La W viene de <em>women&rsquo;s</em>: la escala num&eacute;rica plus
      de Estados Unidos, la misma familia que 1XL&ndash;4XL contada con n&uacute;meros.</p>
      <div class="tabla-marco"><table class="datos">
        <thead><tr><th>Si la etiqueta dice</th><th>Suele corresponder a</th></tr></thead>
        <tbody>
          <tr><td class="talla">14W &ndash; 16W</td><td class="talla">1XL</td></tr>
          <tr><td class="talla">18W &ndash; 20W</td><td class="talla">2XL</td></tr>
          <tr><td class="talla">22W &ndash; 24W</td><td class="talla">3XL</td></tr>
          <tr><td class="talla">26W &ndash; 28W</td><td class="talla">4XL</td></tr>
        </tbody>
      </table></div>
      <p>Decimos &laquo;suele&raquo; a prop&oacute;sito: es una equivalencia de referencia, no una ley.</p>
    </section>

    <section class="marco bloque-ancho leer">
      <h2>C&oacute;mo elegir sin equivocarte</h2>
      <p><strong>Dej&aacute; de mirar la letra y mir&aacute; la prenda.</strong> La etiqueta es una
      decisi&oacute;n que tom&oacute; alguien en una f&aacute;brica; la medida de la prenda es un hecho.</p>
      <ol class="pasos">
        <li><strong>Busc&aacute; algo tuyo que te quede como te gusta.</strong> Una blusa, un vestido, lo que sea.</li>
        <li><strong>Acostalo sobre la cama</strong> y estiralo sin forzarlo.</li>
        <li><strong>Med&iacute; el ancho del busto de costura a costura</strong> y multiplic&aacute; por dos.</li>
        <li><strong>Compar&aacute; ese n&uacute;mero</strong> con el que publicamos en cada prenda.</li>
      </ol>
      <p>Y despu&eacute;s, el corte manda sobre el n&uacute;mero:</p>
      <ul>
        <li><strong>Estructurada</strong> (blazer, chaleco sastre, pantal&oacute;n formal): si
        est&aacute;s entre dos, la mayor. Ah&iacute; no hay de d&oacute;nde ceder.</li>
        <li><strong>Con el&aacute;stico o smocked</strong>: la menor suele quedar mejor. El espacio
        ya viene puesto en la prenda.</li>
        <li><strong>De ca&iacute;da suelta</strong> (camisas oversize, blusas globo): la talla
        importa menos. Ah&iacute; mandan el largo y el hombro.</li>
      </ul>
    </section>

    <section class="marco bloque-ancho">
      <h2>Las medidas que ya publicamos</h2>
      %(medidas)s
    </section>

    <section class="marco bloque-ancho">
      <h2>Preguntas</h2>
      <div class="faq-lista leer">%(faq)s</div>
    </section>

    <section class="cierre">
      <div class="marco">
        <h2>&iquest;Te gust&oacute; una prenda y no sab&eacute;s qu&eacute; talla pedir?</h2>
        <p class="leer">Mandanos el nombre. Te damos la medida exacta de <em>esa</em> pieza,
        no de una tabla general.</p>
        <a class="btn btn--wa cierre-btn" href="%(wa)s" target="_blank" rel="noopener">%(svg)s Preguntar por una prenda</a>
      </div>
    </section>
  </main>
""" % dict(cruzan=len(cruzan), n=n, rangos=rangos, filas=filas_cuenta,
           medidas=bloque_med, faq=faq_html,
           wa=e(wa('Hola, quiero saber las medidas de: ')), svg=SVG_WA)

    return cabeza(prof, titulo, desc, url, None, [art_ld, faq_ld]) + nav(prof, 'tallas') + cuerpo + pie(prof)


def pagina_nosotras(prods):
    prof = 1
    url = SITIO + '/nosotras'
    titulo = 'Quién elige la ropa de BOLEM — Mónica'
    desc = ('BOLEM nació del amor de Mónica por su mamá y su hermana, que siempre salían de las '
            'tiendas con las manos vacías. Quién elige cada pieza y con qué criterio.')
    ld = {'@context': 'https://schema.org', '@type': 'AboutPage', 'name': titulo,
          'description': desc, 'url': url,
          'mainEntity': {'@type': 'Organization', 'name': 'BOLEM',
                         'founder': {'@type': 'Person', 'name': 'Mónica Claros'}}}

    cuerpo = """  <main id="principal">
    <header class="col-cabeza marco">
      <p class="etiqueta">Nosotras</p>
      <h1>BOLEM empez&oacute; mirando a dos personas<br>
      <span class="subrayado">salir con las manos vac&iacute;as</span></h1>
    </header>

    <section class="marco bloque-ancho leer">
      <p>La mam&aacute; y la hermana de M&oacute;nica siempre sufrieron para encontrar ropa. Iban a
      la tienda, se probaban, y sal&iacute;an sin nada &mdash;o con lo &uacute;nico que hab&iacute;a
      en su talla, que casi nunca era lo que les gustaba.</p>
      <p>M&oacute;nica encontraba lo que quer&iacute;a. Ellas no. Y ver eso una y otra vez es lo
      que termin&oacute; en BOLEM.</p>
      <p><strong>Por eso ac&aacute; no hay una secci&oacute;n &laquo;tallas grandes&raquo;.</strong>
      Todo el cat&aacute;logo lo es. Tu talla no es la excepci&oacute;n: es la regla.</p>

      <h2>Qu&eacute; hace BOLEM exactamente</h2>
      <p>BOLEM <strong>no fabrica ropa</strong>, y es importante decirlo claro. Lo que hace
      M&oacute;nica es buscar entre marcas de Estados Unidos que s&iacute; cortan para cuerpos
      curvy &mdash;con moldes propios, no con una talla recta estirada&mdash; y traer solo lo que
      se pondr&iacute;a ella.</p>
      <p>Eso significa que cada pieza pas&oacute; por el criterio de una persona, no por un
      algoritmo de compras. Y significa tambi&eacute;n que el cat&aacute;logo es chico a
      prop&oacute;sito: %(n)d piezas, no mil.</p>

      <h2>C&oacute;mo se compra</h2>
      <p>Hablando. No hay carrito, y no es porque nos falte tecnolog&iacute;a: es porque la
      pregunta que importa &mdash;&laquo;&iquest;me va a quedar?&raquo;&mdash; no la contesta un
      bot&oacute;n de &laquo;agregar al carrito&raquo;. La contesta M&oacute;nica, mirando la
      prenda y preguntando tu talla.</p>
      <p>Apart&aacute;s por WhatsApp, te llega en uno a tres d&iacute;as, la ves,
      y <strong>reci&eacute;n ah&iacute; pag&aacute;s</strong>.</p>

      <h2>Lo que estamos construyendo</h2>
      <p>Estamos midiendo cada prenda, acostada, talla por talla, para publicar el n&uacute;mero
      real en vez de una tabla promedio que no describe a ninguna. Y le estamos preguntando a las
      clientas que ya compraron c&oacute;mo les qued&oacute;, para que lo que leas ac&aacute; sea
      de ellas y no nuestro.</p>
      <p>Va lento porque se hace bien. Lo que todav&iacute;a no sabemos, el sitio lo dice.</p>
    </section>

    <section class="cierre">
      <div class="marco">
        <h2>&iquest;Empezamos?</h2>
        <p class="leer">Contale a M&oacute;nica qu&eacute; and&aacute;s buscando y cu&aacute;l es tu talla.</p>
        <a class="btn btn--wa cierre-btn" href="%(wa)s" target="_blank" rel="noopener">%(svg)s Escribir por WhatsApp</a>
      </div>
    </section>
  </main>
""" % dict(n=len(prods), wa=e(wa('Hola Monica, ando buscando: ')), svg=SVG_WA)

    return cabeza(prof, titulo, desc, url, None, [ld]) + nav(prof, 'nosotras') + cuerpo + pie(prof)


# ==================================================================== salida
def escribir(rel, contenido, revisar, estado):
    destino = os.path.join(V2, rel)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    viejo = open(destino, encoding='utf-8').read() if os.path.exists(destino) else None
    if viejo == contenido:
        estado['igual'] += 1
        return
    estado['nueva' if viejo is None else 'cambia'] += 1
    if not revisar:
        open(destino, 'w', encoding='utf-8').write(contenido)


def sitemap(prods):
    urls = [(SITIO + '/', '1.0', 'weekly'),
            (SITIO + '/coleccion', '0.9', 'weekly'),
            (SITIO + '/tallas', '0.9', 'monthly'),
            (SITIO + '/resenas', '0.7', 'weekly'),
            (SITIO + '/nosotras', '0.5', 'monthly')]
    for t in ORDEN_TALLAS:
        if any(t in p['tallas'] for p in prods):
            urls.append(('%s/talla/%s' % (SITIO, t.lower()), '0.8', 'weekly'))
    for p in prods:
        urls.append(('%s/prendas/%s' % (SITIO, p['id']), '0.8', 'weekly'))
    filas = ''.join('  <url><loc>%s</loc><lastmod>2026-08-17</lastmod>'
                    '<changefreq>%s</changefreq><priority>%s</priority></url>\n'
                    % (u, f, pr) for u, pr, f in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % filas)


JS = """// BOLEM v2 — lo minimo. El sitio funciona entero sin este archivo.
(function () {
  var nav = document.getElementById('nav'), btn = document.getElementById('navBtn');
  if (nav && btn) btn.addEventListener('click', function () {
    var abierto = nav.classList.toggle('abierto');
    btn.setAttribute('aria-expanded', abierto ? 'true' : 'false');
  });
  // Galeria: sin JS se ven todas las fotos igual; esto solo sube la que se toca.
  var grande = document.getElementById('galPrincipal');
  var tira = document.querySelector('.gal-tira');
  if (grande && tira) tira.addEventListener('click', function (ev) {
    var b = ev.target.closest('button[data-src]');
    if (!b) return;
    grande.src = b.dataset.src; grande.srcset = b.dataset.set;
    tira.querySelectorAll('button').forEach(function (o) {
      o.setAttribute('aria-current', o === b ? 'true' : 'false');
    });
  });
})();
"""


def main(revisar):
    if not os.path.exists(DATOS):
        print('falta %s — corre antes: python _tools/sincronizar_hoja.py' % DATOS)
        return 1
    d = json.load(open(DATOS, encoding='utf-8'))
    prods, resumen = d['productos'], d['resumen']
    estado = {'nueva': 0, 'cambia': 0, 'igual': 0}

    escribir('index.html', pagina_home(prods, resumen), revisar, estado)
    escribir('coleccion/index.html', pagina_coleccion(prods), revisar, estado)
    escribir('tallas/index.html', pagina_tallas(prods), revisar, estado)
    escribir('resenas/index.html', pagina_resenas(prods), revisar, estado)
    escribir('nosotras/index.html', pagina_nosotras(prods), revisar, estado)
    for t in ORDEN_TALLAS:
        if any(t in p['tallas'] for p in prods):
            escribir('talla/%s/index.html' % t.lower(), pagina_talla(t, prods), revisar, estado)
    for p in prods:
        escribir('prendas/%s/index.html' % p['id'], pagina_prenda(p, prods), revisar, estado)
    escribir('sitemap.xml', sitemap(prods), revisar, estado)
    escribir('bolem.js', JS, revisar, estado)

    fav = os.path.join(ROOT, 'favicon.svg')
    if os.path.exists(fav) and not revisar:
        shutil.copy2(fav, os.path.join(V2, 'favicon.svg'))

    n_tallas = sum(1 for t in ORDEN_TALLAS if any(t in p['tallas'] for p in prods))
    print('BOLEM v2 construido desde la Hoja Madre')
    print('  %d prendas · %d paginas de talla · 5 paginas fijas' % (len(prods), n_tallas))
    print('  archivos: %d nuevos · %d actualizados · %d sin cambio'
          % (estado['nueva'], estado['cambia'], estado['igual']))
    print('\n  datos que Monica todavia no dio (el sitio lo dice, no lo inventa):')
    for etq, k in (('medidas en plano', 'n_con_medidas'), ('tela', 'n_con_tela'),
                   ('veredicto de calce', 'n_con_calce'),
                   ('altura/talla de modelo', 'n_con_modelo'),
                   ('resenas', 'n_resenas')):
        print('    %-24s %d' % (etq, resumen[k]))
    if revisar:
        print('\n(--revisar: no se escribio nada)')
    return 0


if __name__ == '__main__':
    sys.exit(main('--revisar' in sys.argv))
