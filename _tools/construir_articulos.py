# -*- coding: utf-8 -*-
"""Arma articulos del blog reusando el esqueleto de uno que ya existe.

Por que no se escriben a mano: el nav y el pie del sitio estan unificados por
`unificar_nav.py` / `unificar_footer.py`, y un articulo tecleado se sale de esa
unificacion en cuanto alguien toca el menu. Aca el nav y el pie se COPIAN tal
cual del articulo modelo, asi que no pueden divergir.

Las cifras del catalogo (cuantas prendas llegan a 4XL, etc.) se DERIVAN de
`_data/catalogo.json` en cada corrida. Si no, serian numeros escritos a mano
mas — el problema que ya nos costo un H1 diciendo "33 Estilos" con 49 prendas.

Los dos articulos nacen con `noindex`: son borradores para que Monica opine.
Se quitan las dos lineas marcadas BOLEM:NOINDEX cuando ella apruebe.

Uso:  python _tools/construir_articulos.py [--revisar]
"""
import io, os, re, sys, json, datetime, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELO = os.path.join(ROOT, 'blog', 'tallas-xl-1xl-plus-size.html')
BLOG = os.path.join(ROOT, 'blog')
SITIO = 'https://bolemsv.com'
FECHA = '2026-08-18'


# ───────────────────────── datos derivados ─────────────────────────

def catalogo():
    d = json.load(open(os.path.join(ROOT, '_data', 'catalogo.json'), encoding='utf-8'))
    p = d['productos']
    cuatro = [x for x in p if '4XL' in str(x.get('tallas'))]
    por_cat, cuatro_cat = {}, {}
    for x in p:
        por_cat[x['categoria']] = por_cat.get(x['categoria'], 0) + 1
    for x in cuatro:
        cuatro_cat[x['categoria']] = cuatro_cat.get(x['categoria'], 0) + 1
    return {'n': len(p), 'n4': len(cuatro), 'por_cat': por_cat, 'cuatro_cat': cuatro_cat}


# ───────────────────────── esqueleto ─────────────────────────

def piezas_del_modelo():
    """Devuelve (nav, pie) del articulo modelo, verbatim."""
    L = open(MODELO, encoding='utf-8').read().split('\n')
    i_body = next(i for i, l in enumerate(L) if l.strip() == '<body>')
    i_head = next(i for i, l in enumerate(L) if 'class="page-header"' in l)
    i_pie = next(i for i, l in enumerate(L) if '<footer' in l)
    return '\n'.join(L[i_body:i_head]), '\n'.join(L[i_pie:])


def faq_schema(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in faqs]}


def faq_visible(faqs):
    """La MISMA lista alimenta el schema y la pagina, para que no puedan
    divergir. Una FAQ que Google ve y el lector no es media respuesta."""
    fuera = []
    for q, a in faqs:
        fuera.append('      <h3>%s</h3>' % q)
        fuera.append('      <p>%s</p>' % a)
        fuera.append('')
    return chr(10).join(fuera)


def migas(titulo, slug):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Inicio", "item": SITIO + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITIO + "/blog"},
                {"@type": "ListItem", "position": 3, "name": titulo,
                 "item": '%s/blog/%s' % (SITIO, slug)}]}


def armar(spec, nav, pie):
    url = '%s/blog/%s' % (SITIO, spec['slug'])
    post = {"@context": "https://schema.org", "@type": "BlogPosting",
            "headline": spec['titulo'], "description": spec['desc'],
            "author": {"@type": "Organization", "name": "BOLEM", "url": SITIO},
            "publisher": {"@type": "Organization", "name": "BOLEM"},
            "datePublished": FECHA, "dateModified": FECHA,
            "mainEntityOfPage": url, "inLanguage": "es-SV",
            "about": [{"@type": "Thing", "name": t} for t in spec['temas']]}
    j = lambda o: json.dumps(o, ensure_ascii=False, indent=2)
    return '''<!DOCTYPE html>
<html lang="es-SV">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>%(titulo)s | BOLEM</title>
  <meta name="description" content="%(desc)s">
  <!-- BOLEM:NOINDEX borrador para revision de Monica - quitar al aprobar -->
  <meta name="robots" content="noindex, nofollow">
  <link rel="canonical" href="%(url)s">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inconsolata:wght@300;400;500;600&family=Outfit:wght@300;400;500;600&family=Playfair+Display:wght@400;500;600&display=swap">
  <link rel="stylesheet" href="../styles.css">

  <meta property="og:title" content="%(titulo)s">
  <meta property="og:description" content="%(desc)s">
  <meta property="og:type" content="article">
  <meta property="og:url" content="%(url)s">
  <meta property="og:site_name" content="BOLEM">
  <meta property="og:locale" content="es_SV">

  <script type="application/ld+json">
%(post)s
  </script>
  <script type="application/ld+json">
%(faq)s
  </script>
  <script type="application/ld+json">
%(migas)s
  </script>

  <style>
    .dato-fuerte {
      background: var(--color-ink); color: var(--color-white);
      padding: 1.6rem 1.5rem; margin: var(--space-element) 0; text-align: center;
    }
    .dato-fuerte b {
      display: block; font-family: var(--font-display);
      font-size: clamp(2rem, 6vw, 2.8rem); line-height: 1; margin-bottom: 0.6rem;
    }
    .dato-fuerte span { font-size: 0.95rem; line-height: 1.6; opacity: 0.92; }
    .dato-fuerte strong { color: var(--color-white); }

    .rechazos {
      border: var(--border-thin); background: var(--color-white);
      padding: 1.3rem 1.5rem; margin: var(--space-element) 0;
    }
    .rechazos h3 {
      font-family: var(--font-accent); font-size: var(--text-micro);
      letter-spacing: 0.14em; text-transform: uppercase;
      color: var(--color-ink-muted); margin: 0 0 0.9rem;
    }
    .rechazos ul { margin: 0; padding-left: 1.1rem; }
    .rechazos li { margin-bottom: 0.45rem; line-height: 1.55; }

    .cuadro-curva {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 0.8rem; margin: var(--space-element) 0;
    }
    .curva-caja {
      border: var(--border-thin); background: var(--color-white);
      padding: 1.1rem 1.2rem; text-align: center;
    }
    .curva-caja b {
      display: block; font-family: var(--font-display); font-size: 1.9rem;
      line-height: 1; margin-bottom: 0.35rem;
    }
    .curva-caja span {
      font-size: 0.86rem; color: var(--color-ink-muted); line-height: 1.5;
    }
    .borrador-aviso {
      border: 2px dashed var(--color-ink-muted); padding: 1rem 1.2rem;
      margin: 0 0 var(--space-element); font-size: 0.9rem;
      color: var(--color-ink-muted); line-height: 1.6;
    }
  </style>
</head>
%(nav)s
    <header class="page-header">
      <p class="page-header-eyebrow">Blog &bull; borrador</p>
      <h1 class="page-header-title">%(titulo)s</h1>
      <p class="page-header-subtitle">%(bajada)s</p>
    </header>

    <div class="page-content">

      <div class="borrador-aviso">
        <strong>Borrador para revisi&oacute;n.</strong> Todav&iacute;a no est&aacute; publicado ni lo ve Google.
        Si algo no suena a BOLEM o hay un dato que no es as&iacute;, decilo y se cambia.
      </div>

%(cuerpo)s

      <h2>Preguntas frecuentes</h2>
%(faq_visible)s
      <div class="cta-final" style="background: var(--color-white); border: var(--border-thin); padding: var(--space-element); margin-top: var(--space-block); text-align: center;">
        <h2 style="font-family: var(--font-display); font-size: 1.2rem; margin: 0 0 0.6rem;">%(cta_titulo)s</h2>
        <p style="margin-bottom: var(--space-element); font-size: 0.97rem;">%(cta_texto)s</p>
        <a href="https://wa.me/50368590899?text=%(cta_wa)s" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:0.5rem;background:#25D366;color:var(--color-ink);padding:0.8rem 1.6rem;font-weight:600;text-decoration:none;border:none;">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M12 0C5.373 0 0 5.373 0 12c0 2.625.846 5.059 2.284 7.034L.789 23.492a.5.5 0 00.611.611l4.458-1.495A11.943 11.943 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-2.347 0-4.518-.801-6.24-2.144l-.436-.348-3.17 1.063 1.063-3.17-.348-.436A9.956 9.956 0 012 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/></svg>
          %(cta_boton)s
        </a>
      </div>

      <div style="margin-top: var(--space-block); padding-top: var(--space-element); border-top: var(--border-thin);">
        <h3 style="font-family: var(--font-display); font-size: 1.15rem; margin: 0 0 0.8rem; color: var(--color-ink);">Segu&iacute; leyendo</h3>
        <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.55rem;">
%(relacionados)s
        </ul>
      </div>

    </div>
  </div>
%(pie)s''' % {'titulo': spec['titulo'], 'desc': spec['desc'], 'url': url,
       'post': j(post), 'faq': j(faq_schema(spec['faqs'])),
       'migas': j(migas(spec['titulo'], spec['slug'])),
       'nav': nav, 'pie': pie, 'bajada': spec['bajada'], 'cuerpo': spec['cuerpo'],
       'faq_visible': faq_visible(spec['faqs']),
       'cta_titulo': spec['cta'][0], 'cta_texto': spec['cta'][1],
       'cta_boton': spec['cta'][2], 'cta_wa': urllib.parse.quote(spec['cta'][3]),
       'relacionados': chr(10).join('          <li><a href="%s">%s</a></li>' % (u, x)
                                 for u, x in spec['relacionados'])}


# ───────────────────────── los articulos ─────────────────────────

def specs(c):
    n, n4 = c['n'], c['n4']
    cc, pc = c['cuatro_cat'], c['por_cat']
    pct = round(n4 * 100.0 / n)

    a1_cuerpo = '''
      <p>Cuando ves una blusa en esta p&aacute;gina, ya pas&oacute; por una decisi&oacute;n. Alguien la tuvo en la mano, mir&oacute; la etiqueta, calcul&oacute; si a vos te iba a servir, y dijo que s&iacute;. Y antes de esa, dijo que no un mont&oacute;n de veces.</p>

      <p>Queremos contarte c&oacute;mo es esa parte, porque casi nunca se cuenta y explica bastante de lo que ves ac&aacute; &mdash; incluida alguna cosa que quiz&aacute; te ha frustrado.</p>

      <h2>Primero: BOLEM elige, no fabrica</h2>

      <p>No tenemos taller. Lo que hacemos es <strong>escoger</strong>, y esa es toda la diferencia entre una tienda que revende lo que le mandan y una que va a buscar.</p>

      <p>M&oacute;nica viaja a la feria de moda mayorista m&aacute;s grande de Estados Unidos. No es un cat&aacute;logo por internet: son pasillos, perchas y muestras que se tocan. Se prueba la tela con la mano, se mira el cierre, se levanta la prenda a contraluz para ver si transparenta.</p>

      <p>Eso importa por una raz&oacute;n concreta: <strong>una foto no te dice si una tela se marca</strong>, y vos esa diferencia la vas a sentir el d&iacute;a que te la pongas.</p>

      <h2>Lo que NO compramos dice m&aacute;s que lo que compramos</h2>

      <p>Hay una secci&oacute;n entera de la feria dedicada a talla grande. M&oacute;nica la recorri&oacute; completa y sali&oacute; sin comprar <strong>una sola prenda</strong>. Once marcas revisadas, once descartadas.</p>

      <p>Las razones, en sus palabras:</p>

      <div class="rechazos">
        <h3>Por qu&eacute; se descartaron</h3>
        <ul>
          <li><strong>&laquo;Ropa de se&ntilde;ora.&raquo;</strong> Cortes que suman a&ntilde;os. Talla grande no quiere decir vestir mayor.</li>
          <li><strong>&laquo;No est&aacute; en tendencia.&raquo;</strong> Piezas correctas, pero de hace tres temporadas.</li>
          <li><strong>&laquo;Muy brillante.&raquo;</strong> Lentejuela y sat&iacute;n para eventos de gala, no para un martes.</li>
        </ul>
      </div>

      <p>Es el patr&oacute;n que m&aacute;s se repite en la industria: <strong>a la talla grande se le ofrece formalidad o se le ofrece disfraz, y casi nunca se le ofrece ropa normal y linda</strong>. Por eso esa secci&oacute;n, que en teor&iacute;a era &laquo;la nuestra&raquo;, se fue entera al descarte.</p>

      <h2>La regla de los 30 grados</h2>

      <p>La feria es en agosto y se compra pensando en el oto&ntilde;o del norte. Medio piso son su&eacute;teres, abrigos y tejidos gruesos.</p>

      <p>Ac&aacute; eso no se usa <em>nunca</em>. Una prenda as&iacute; no es una mala compra: es una compra <strong>muerta</strong>, plata parada en una bodega. Descartar categor&iacute;as enteras por clima es de las primeras cosas que hay que hacer, y explica buena parte de lo que qued&oacute; fuera.</p>

      <p>Cuando ves que ac&aacute; hay lino, algod&oacute;n y gasa y casi nada de tejido pesado, no es casualidad ni falta de variedad. Es el pa&iacute;s en el que vivimos.</p>

      <h2>Un dato que nos molest&oacute; encontrar</h2>

      <p>Ac&aacute; est&aacute; la parte inc&oacute;moda. Comparando la misma prenda en talla recta y en talla plus, con el mismo proveedor:</p>

      <div class="dato-fuerte">
        <b>$1</b>
        <span>es la diferencia real de costo entre una prenda en talla regular y la misma en plus. <strong>Un d&oacute;lar.</strong></span>
      </div>

      <p>O sea que <strong>la talla grande no cuesta el doble de producir</strong>. Cuando la ves mucho m&aacute;s cara en una tienda, casi nunca es la tela ni el molde: es margen, o es una marca cara.</p>

      <p>Sabiendo eso, cobrarte un recargo por tu talla ser&iacute;a dif&iacute;cil de defender. No lo hacemos.</p>

      <h2>Y cuando llega la caja, se mide</h2>

      <p>Ac&aacute; hay algo que aprendimos a los golpes. <strong>No todas las marcas cuentan las tallas igual.</strong> Una escribe <em>XL &middot; 2XL &middot; 3XL</em> y otra escribe <em>XL &middot; 1XL &middot; 2XL</em> para prendas que ocupan m&aacute;s o menos el mismo lugar en el cuerpo. La segunda est&aacute; un escal&oacute;n abajo de la primera.</p>

      <p>Si uno se conf&iacute;a de la etiqueta y la pone en la p&aacute;gina tal cual, te vende una talla que no es la que cre&iacute;as pedir. As&iacute; que <strong>medimos antes de etiquetar</strong>, y cuando una marca cuenta distinto, lo decimos en la ficha de esa prenda.</p>

      <p>Si te interesa el tema a fondo, lo desarmamos en <a href="tallas-xl-1xl-plus-size">XL o 1XL: por qu&eacute; no son la misma talla</a>.</p>

      <h2>Por qu&eacute; te contamos todo esto</h2>

      <p>Porque cuando comprar es por WhatsApp y sin probador, lo &uacute;nico que sostiene la compra es <strong>confiar en quien eligi&oacute;</strong>.</p>

      <p>No podemos ofrecerte un probador. S&iacute; podemos contarte qu&eacute; se mir&oacute;, qu&eacute; se descart&oacute; y por qu&eacute;. Y podemos decirte con la misma franqueza lo que <em>no</em> tenemos &mdash; que es justo de lo que habla <a href="por-que-casi-no-existe-la-4xl">el otro art&iacute;culo</a>.</p>

      <p>Si ten&eacute;s una duda sobre una prenda en particular, escribinos. La respuesta va a salir de alguien que la tuvo en la mano.</p>
'''

    a2_cuerpo = '''
      <p>Nos llega seguido, y casi siempre con la misma resignaci&oacute;n adelante: <em>&laquo;&iquest;tendr&aacute;n algo en 4XL? seguro que no&raquo;</em>.</p>

      <p>La respuesta honesta es: <strong>tenemos poco, y no es por falta de ganas</strong>. Es porque la industria se detiene antes. Te explicamos d&oacute;nde se detiene y qu&eacute; estamos haciendo.</p>

      <h2>La curva plus americana termina antes de lo que cre&eacute;s</h2>

      <p>Casi toda la ropa plus que se vende en El Salvador viene de Estados Unidos. Y all&aacute; la escala plus est&aacute;ndar corre as&iacute;:</p>

      <div class="cuadro-curva">
        <div class="curva-caja"><b>1X</b><span>equivale a 14W&ndash;16W</span></div>
        <div class="curva-caja"><b>2X</b><span>equivale a 18W&ndash;20W</span></div>
        <div class="curva-caja"><b>3X</b><span>equivale a 22W&ndash;24W<br><strong>ac&aacute; se acaba</strong></span></div>
      </div>

      <p><strong>La mayor&iacute;a de las marcas para en 3X.</strong> No es una decisi&oacute;n de una tienda: es d&oacute;nde deciden cortar los moldes las f&aacute;bricas. Del 3X para arriba hay que hacer patrones nuevos, y muchas marcas simplemente no los hacen.</p>

      <p>Por eso cuando busc&aacute;s 4XL sent&iacute;s que el mundo se cierra. No es tu impresi&oacute;n.</p>

      <h2>Lo que vimos en la feria m&aacute;s grande del rubro</h2>

      <p>En la feria mayorista de moda m&aacute;s grande de Estados Unidos &mdash;pasillos y pasillos de marcas, secci&oacute;n plus incluida&mdash; buscamos expresamente quien llegara m&aacute;s arriba del 3X.</p>

      <div class="dato-fuerte">
        <b>1</b>
        <span>fue la cantidad de marcas que encontramos anunciando hasta <strong>4XL</strong> en toda la feria.</span>
      </div>

      <p>Una. Y su estilo no era el de BOLEM, as&iacute; que esa vez no compramos ah&iacute;. Pero el n&uacute;mero dice todo lo que hay que saber: <strong>el 4XL no es dif&iacute;cil de conseguir en El Salvador porque nadie lo traiga. Es dif&iacute;cil porque casi nadie lo fabrica.</strong></p>

      <h2>Qu&eacute; tenemos hoy, sin maquillar</h2>

      <p>Ac&aacute; van los n&uacute;meros de nuestro propio cat&aacute;logo, tal cual:</p>

      <div class="dato-fuerte">
        <b>%(n4)d de %(n)d</b>
        <span>prendas de BOLEM llegan hasta 4XL. Es el <strong>%(pct)d%%</strong> del cat&aacute;logo.</span>
      </div>

      <p>Y desglosado por tipo, porque el promedio esconde lo importante:</p>

      <div class="cuadro-curva">
        <div class="curva-caja"><b>%(b4)d/%(bt)d</b><span>blusas</span></div>
        <div class="curva-caja"><b>%(c4)d/%(ct)d</b><span>conjuntos</span></div>
        <div class="curva-caja"><b>%(v4)d/%(vt)d</b><span>vestidos</span></div>
        <div class="curva-caja"><b>%(p4)d/%(pt)d</b><span>pantalones</span></div>
      </div>

      <p>Ah&iacute; est&aacute; lo que m&aacute;s nos incomoda: <strong>en vestidos tenemos uno solo</strong>. Si sos 4XL y entraste buscando un vestido para una boda, encontraste una opci&oacute;n. Eso no alcanza y lo sabemos.</p>

      <h2>Qu&eacute; estamos haciendo</h2>

      <p><strong>Buscar arriba a prop&oacute;sito.</strong> En la pr&oacute;xima compra, llegar al 4XL deja de ser algo que pasa si se da y pasa a ser un requisito, sobre todo en vestidos. Ya identificamos marcas que s&iacute; suben hasta ah&iacute;.</p>

      <p><strong>Decirte la verdad en cada ficha.</strong> Cada prenda de esta p&aacute;gina lista sus tallas reales. Ninguna dice 4XL si no la tiene. Preferimos que veas menos opciones a que pidas una que no existe.</p>

      <p><strong>Preguntarte a vos.</strong> Si sos 4XL y hay un tipo de prenda que nunca encontr&aacute;s, escribinos y decinos cu&aacute;l. Esa lista es lo que se lleva M&oacute;nica al pr&oacute;ximo viaje &mdash; literalmente.</p>

      <h2>Mientras tanto</h2>

      <p>Dos cosas que s&iacute; te sirven hoy:</p>

      <p><strong>Fijate en las prendas que arrancan en 1XL.</strong> Una que corre de 1XL a 3XL suele dar m&aacute;s cuerpo que una que va de XL a 3XL, porque arranca de otro molde. Lo explicamos en <a href="tallas-xl-1xl-plus-size">XL o 1XL: por qu&eacute; no son la misma talla</a>.</p>

      <p><strong>Preguntanos por la prenda concreta antes de pedirla.</strong> Podemos decirte c&oacute;mo le qued&oacute; a alguien de tu talla y si esa marca corta grande o chico. Es lo m&aacute;s parecido a un probador que podemos darte por ahora.</p>

      <p>Preferimos que sepas d&oacute;nde estamos parados a venderte una promesa. Si el 4XL es tu talla, esta p&aacute;gina todav&iacute;a te queda corta &mdash; y estamos trabajando en eso.</p>
''' % {'n': n, 'n4': n4, 'pct': pct,
       'b4': cc.get('blusa', 0), 'bt': pc.get('blusa', 0),
       'c4': cc.get('conjunto', 0), 'ct': pc.get('conjunto', 0),
       'v4': cc.get('vestido', 0), 'vt': pc.get('vestido', 0),
       'p4': cc.get('pantalon', 0), 'pt': pc.get('pantalon', 0)}

    return [
        {'slug': 'como-elegimos-la-ropa',
         'titulo': 'C&oacute;mo elegimos la ropa que te vendemos',
         'bajada': 'Alguien viaja, la toca y dice que no muchas m&aacute;s veces de las que dice que s&iacute;. As&iacute; se arma lo que ves ac&aacute;.',
         'desc': 'C&oacute;mo elige BOLEM la ropa plus size que vende: qu&eacute; se descarta y por qu&eacute;, la regla del clima, y por qu&eacute; no cobramos recargo por talla grande.',
         'temas': ['Moda plus size', 'Compra mayorista de ropa', 'Curadur&iacute;a de moda'],
         'cuerpo': a1_cuerpo,
         'cta': ('¿Querés saber cómo se siente una tela antes de pedirla?',
                 'Preguntanos por la prenda que te gustó. Te decimos cómo es al tacto, si transparenta y cómo cae — porque alguien la tuvo en la mano.',
                 'Preguntar por una prenda',
                 'Hola, leí cómo eligen la ropa y quiero preguntar por: '),
         'relacionados': [
             ('por-que-casi-no-existe-la-4xl', 'Por qué casi no existe la 4XL'),
             ('tallas-xl-1xl-plus-size', 'XL o 1XL: por qué no son la misma talla'),
             ('historia-bolem-moda-plus-size-el-salvador', 'Por qué existe BOLEM'),
             ('../coleccion/', 'Ver las %d prendas de la colección' % n),
         ],
         'faqs': [
             ('¿BOLEM fabrica su propia ropa?',
              'No. BOLEM elige y trae ropa plus size de marcas de Estados Unidos. No tenemos taller propio: nuestro trabajo es seleccionar, revisando las prendas en persona antes de comprarlas.'),
             ('¿Por qué la ropa plus size suele ser más cara?',
              'Por costo de producción casi no lo es: la diferencia entre una prenda en talla regular y la misma en plus puede ser de alrededor de un dólar. Cuando ves precios mucho más altos, normalmente es margen o marca, no el molde ni la tela.'),
             ('¿Por qué BOLEM casi no vende suéteres o ropa de abrigo?',
              'Porque en El Salvador no se usan. Las ferias mayoristas de agosto se compran pensando en el otoño de Estados Unidos, así que buena parte de la oferta es tejido grueso. Para nuestro clima eso es inventario que no rota.'),
             ('¿Las tallas de la página son las que dice la etiqueta?',
              'Medimos las prendas al recibirlas, porque no todas las marcas cuentan las tallas igual: algunas escriben XL·2XL·3XL y otras XL·1XL·2XL para rangos parecidos. Cuando una marca cuenta distinto, lo decimos en la ficha de esa prenda.'),
         ]},
        {'slug': 'por-que-casi-no-existe-la-4xl',
         'titulo': 'Por qu&eacute; casi no existe la 4XL',
         'bajada': 'No es que no la busquemos. Es que la industria se detiene antes &mdash; y ac&aacute; te decimos exactamente cu&aacute;nto tenemos.',
         'desc': 'Por qu&eacute; es tan dif&iacute;cil encontrar ropa 4XL en El Salvador: d&oacute;nde termina la curva plus americana, qu&eacute; encontramos en la feria mayorista m&aacute;s grande, y cu&aacute;ntas prendas 4XL tiene BOLEM hoy.',
         'temas': ['Ropa 4XL', 'Tallas plus size', 'Moda plus size El Salvador'],
         'cuerpo': a2_cuerpo,
         'cta': ('¿Sos 4XL y nunca encontrás cierto tipo de prenda?',
                 'Decinos cuál. Esa lista es literalmente lo que Mónica se lleva al próximo viaje de compra.',
                 'Decirnos qué buscar',
                 'Hola, soy talla 4XL y lo que nunca encuentro es: '),
         'relacionados': [
             ('tallas-xl-1xl-plus-size', 'XL o 1XL: por qué no son la misma talla'),
             ('como-elegimos-la-ropa', 'Cómo elegimos la ropa que te vendemos'),
             ('guia-tallas-plus-size', 'Cómo medirte paso a paso'),
             ('../coleccion/', 'Ver las %d prendas de la colección' % n),
         ],
         'faqs': [
             ('¿Por qué es tan difícil encontrar ropa 4XL en El Salvador?',
              'Porque casi no se fabrica. La escala plus estándar de Estados Unidos —de donde viene la mayor parte de la ropa plus que se vende acá— suele terminar en 3X, que equivale a 22W–24W. Del 3X para arriba hacen falta moldes nuevos y muchas marcas no los hacen.'),
             ('¿Cuántas prendas 4XL tiene BOLEM?',
              '%d de %d prendas del catálogo llegan hasta 4XL, alrededor del %d%%. Están repartidas sobre todo en blusas y conjuntos; en vestidos hay una sola opción.' % (n4, n, pct)),
             ('¿4XL es lo mismo que 24W?',
              'No exactamente. 3X equivale más o menos a 22W–24W, así que una 4XL queda por encima de eso. Como cada marca corta distinto, lo mejor es preguntar por la prenda concreta antes de pedirla.'),
             ('¿Van a traer más 4XL?',
              'Sí. En la próxima compra el 4XL pasa de ser algo deseable a ser un requisito, con prioridad en vestidos, que es donde hoy tenemos menos. Si sos 4XL y hay un tipo de prenda que nunca encontrás, podés escribirnos para que entre en la lista de búsqueda.'),
         ]},
    ]


def main(revisar):
    c = catalogo()
    nav, pie = piezas_del_modelo()
    print('catalogo: %d prendas, %d llegan a 4XL' % (c['n'], c['n4']))
    for spec in specs(c):
        html = armar(spec, nav, pie)
        destino = os.path.join(BLOG, spec['slug'] + '.html')
        viejo = open(destino, encoding='utf-8').read() if os.path.exists(destino) else ''
        estado = 'sin cambio' if viejo == html else ('nuevo' if not viejo else 'actualizado')
        palabras = len(re.sub(r'<[^>]+>', ' ', spec['cuerpo']).split())
        if not revisar and viejo != html:
            open(destino, 'w', encoding='utf-8').write(html)
        print('  %-34s %-11s ~%d palabras  %d KB'
              % (spec['slug'], estado, palabras, len(html) / 1024))
    if revisar:
        print('\n(--revisar: no se escribio nada)')
    else:
        print('\nlos dos llevan noindex: son borradores. Al aprobarse, quitar las')
        print('lineas marcadas BOLEM:NOINDEX y volver a correr construir_sitemap.py')
    return 0


if __name__ == '__main__':
    sys.exit(main('--revisar' in sys.argv))
