# -*- coding: utf-8 -*-
"""Tres direcciones de diseño para el inicio de BOLEM, con los datos reales.

POR QUE EXISTE
    Al construir v2 me fui directo al generador. Un generador necesita una
    plantilla repetible, asi que congele el diseño en la primera media hora y
    nunca explore: v2 termino pareciendose a v1. Ademas herede un resumen de
    tres palabras del gusto de Monica ("blanco y limpio") en vez de ir a sus
    referencias — que son sans-serif, densas y product-first, o sea casi lo
    contrario de lo que hice.

    Esto lo corrige: se diseña UNA pagina tres veces antes de generar sesenta.

LAS TRES
    A · Catalogo denso     la ruta de sus referencias: sans, denso, producto
    B · Editorial de talla el cuerpo como eje: la talla es el heroe
    C · Vitrina de Monica  bloques alternados, una prenda con su historia

Las tres respetan lo unico que Monica dejo claro: fondo blanco, el color lo
ponen las fotos. Lo demas esta a discusion, que es justamente el punto.

Uso:  python _tools/construir_disenos.py
"""
import io, os, sys, json, html
from urllib.parse import quote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(ROOT, 'v2', '_data', 'bolem.json')
SALIDA = os.path.join(ROOT, 'v2', 'disenos')
WA = '50368590899'
ORDEN_TALLAS = ['L', 'XL', '1XL', '2XL', '3XL', '4XL']
CATS = {'vestido': 'Vestidos', 'blusa': 'Blusas y chalecos',
        'pantalon': 'Jeans y pantalones', 'conjunto': 'Conjuntos'}
SUBT = {
    'vestido': 'Midi, maxi y de evento. De la XL a la 4XL.',
    'blusa': 'Peplum, halter, chalecos y camisas oversize.',
    'pantalon': 'Palazzo, lino, jeans flare y de lunares.',
    'conjunto': 'Dos piezas que ya combinan entre si.',
}
FUENTES = ('https://fonts.googleapis.com/css2?family=Inconsolata:wght@400;600'
           '&family=Outfit:wght@200;300;400;500;600;700'
           '&family=Playfair+Display:ital,wght@0,400;0,500;1,400&display=swap')


def e(s):
    return html.escape(str(s), quote=True) if s is not None else ''


def wa(t):
    return 'https://wa.me/%s?text=%s' % (WA, quote(t, safe=''))


def pr(v):
    return '%.2f' % float(v)


# las paginas viven en v2/disenos/<x>/index.html -> la raiz esta 3 arriba
def img(nombre, ancho=None):
    b = nombre[:-5] if nombre.endswith('.webp') else nombre
    s = '-%d' % ancho if ancho else ''
    return '../../../assets/productos/%s%s.webp' % (b, s)


def sset(nombre):
    return '%s 480w, %s 800w, %s 1200w' % (img(nombre, 480), img(nombre, 800), img(nombre))


def cabeza(titulo, css):
    return """<!DOCTYPE html>
<html lang="es-SV">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="%s">
<style>
%s
</style>
</head>
<body>
<div class="aviso">Dirección <b>%s</b> · maqueta con datos reales · <a href="../">comparar las tres</a></div>
""" % (e(titulo), FUENTES, css, titulo.split('·')[0].strip()[-1])


# ============================================================ DIRECCION A ===
CSS_A = """
:root{--tinta:#141414;--tinta2:#5C5C5C;--tinta3:#8C8C8C;--linea:#E6E6E6;
      --acento:#A5427E;--verde:#25D366;--papel:#FFF;--papel2:#F7F6F5;}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--papel);color:var(--tinta);
     font-family:'Outfit',system-ui,sans-serif;font-size:15px;line-height:1.5;-webkit-text-size-adjust:100%}
img{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
.aviso{background:#141414;color:#fff;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
       padding:.5rem 1rem;text-align:center;font-family:'Inconsolata',monospace}
.aviso a{color:#FFD9A0;text-decoration:underline}
.marco{max-width:1500px;margin-inline:auto;padding-inline:clamp(.75rem,2vw,1.5rem)}

/* barra */
.barra{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.97);border-bottom:1px solid var(--linea)}
.barra-in{display:flex;align-items:center;gap:1.5rem;height:56px;max-width:1500px;margin-inline:auto;
          padding-inline:clamp(.75rem,2vw,1.5rem)}
.logo{font-weight:200;font-size:1.25rem;letter-spacing:.4em;margin-right:auto}
.logo b{font-weight:700}
.barra nav{display:flex;gap:1.2rem;font-size:.82rem;font-weight:500;text-transform:uppercase;letter-spacing:.06em}
.barra nav a:hover{color:var(--acento)}
.wa{background:var(--verde);color:#111;font-weight:700;font-size:.78rem;text-transform:uppercase;
    letter-spacing:.06em;padding:.5rem .9rem}
@media(max-width:820px){.barra nav{display:none}}

/* franja de campaña */
.campana{position:relative;background:#EFEBE7}
.campana img{width:100%;height:clamp(320px,52vh,520px);object-fit:cover;object-position:50% 22%}
.campana-txt{position:absolute;left:0;right:0;bottom:0;padding:clamp(1rem,3vw,2rem);
             background:linear-gradient(transparent,rgba(0,0,0,.55));color:#fff}
.campana-txt p{margin:0 0 .3rem;font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;opacity:.9}
.campana-txt h1{margin:0;font-size:clamp(1.35rem,3.4vw,2.1rem);font-weight:600;letter-spacing:-.01em;line-height:1.15}

/* tallas: tira horizontal pegada bajo la campaña */
.tallas{display:flex;gap:0;border-bottom:1px solid var(--linea);overflow-x:auto}
.tallas a{flex:1 0 auto;min-width:88px;text-align:center;padding:.85rem .4rem;
          border-right:1px solid var(--linea);white-space:nowrap}
.tallas a:last-child{border-right:none}
.tallas b{display:block;font-size:1.05rem;font-weight:700;letter-spacing:.02em}
.tallas span{display:block;font-size:.68rem;color:var(--tinta3);font-family:'Inconsolata',monospace}
.tallas a:hover{background:var(--papel2);color:var(--acento)}

/* rejilla densa */
.tit{display:flex;align-items:baseline;gap:.8rem;flex-wrap:wrap;margin:2.2rem 0 .3rem}
.tit h2{margin:0;font-size:1.05rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.tit p{margin:0;font-size:.82rem;color:var(--tinta2)}
.tit a{margin-left:auto;font-size:.75rem;font-weight:600;text-transform:uppercase;
       letter-spacing:.08em;color:var(--acento)}
.rej{display:grid;grid-template-columns:repeat(auto-fill,minmax(148px,1fr));
     gap:.55rem;margin:.9rem 0 0}
@media(min-width:900px){.rej{grid-template-columns:repeat(6,1fr)}}
.p{display:block}
.p-img{position:relative;background:var(--papel2);aspect-ratio:2/3;overflow:hidden}
.p-img img{width:100%;height:100%;object-fit:cover}
.p-img .alt{position:absolute;inset:0;opacity:0;transition:opacity .25s}
.p:hover .alt{opacity:1}
.p-n{font-size:.79rem;font-weight:500;margin:.4rem 0 .05rem;line-height:1.25}
.p-d{display:flex;gap:.45rem;align-items:baseline;font-family:'Inconsolata',monospace;font-size:.78rem;color:var(--tinta3)}
.p-d b{color:var(--tinta);font-weight:600}
.p:hover .p-n{color:var(--acento)}

.franja{background:var(--papel2);margin-top:2.5rem;padding:1.1rem 0;border-block:1px solid var(--linea)}
.franja-in{display:flex;gap:2rem;flex-wrap:wrap;justify-content:center;font-size:.8rem;color:var(--tinta2)}
.franja-in b{color:var(--tinta)}
.pie{padding:2rem 0 3rem;font-size:.78rem;color:var(--tinta3);text-align:center}
"""


def dir_a(prods, cuenta):
    hero = next((p for p in prods if p['id'] == 'vestido-cobalto'), prods[0])
    tallas = ''.join(
        '<a href="#"><b>%s</b><span>%d piezas</span></a>' % (t, cuenta[t])
        for t in ORDEN_TALLAS if cuenta[t])

    def tarjeta(p):
        alt = ''
        if len(p['fotos']) > 1:
            alt = ('<img class="alt" src="%s" srcset="%s" sizes="16vw" alt="" loading="lazy">'
                   % (img(p['fotos'][1], 480), sset(p['fotos'][1])))
        return ("""<a class="p" href="#">
  <div class="p-img"><img src="%s" srcset="%s" sizes="(max-width:900px) 45vw, 16vw" alt="%s" loading="lazy">%s</div>
  <p class="p-n">%s</p>
  <p class="p-d"><b>$%s</b><span>%s</span></p>
</a>""" % (img(p['fotos'][0], 480), sset(p['fotos'][0]), e(p['nombre']), alt,
           e(p['nombre']), pr(p['precio']), e(' '.join(p['tallas']))))

    bloques = []
    for k, etq in CATS.items():
        g = sorted([p for p in prods if p['categoria'] == k], key=lambda x: x['precio'])
        if not g:
            continue
        bloques.append("""<section class="marco">
  <div class="tit"><h2>%s</h2><p>%s</p><a href="#">Ver las %d &rarr;</a></div>
  <div class="rej">%s</div>
</section>""" % (e(etq), e(SUBT.get(k, '')), len(g), ''.join(tarjeta(p) for p in g)))

    return cabeza('A · Catálogo denso', CSS_A) + """
<header class="barra"><div class="barra-in">
  <a class="logo" href="#">BOL<b>E</b>M</a>
  <nav><a href="#">Vestidos</a><a href="#">Blusas</a><a href="#">Jeans</a><a href="#">Conjuntos</a><a href="#">Tu talla</a></nav>
  <a class="wa" href="%s">WhatsApp</a>
</div></header>

<div class="campana">
  <img src="%s" srcset="%s" sizes="100vw" alt="%s" fetchpriority="high">
  <div class="campana-txt">
    <p>Colección 2026 · El Salvador</p>
    <h1>%d piezas de la XL a la 4XL</h1>
  </div>
</div>

<nav class="tallas" aria-label="Comprar por talla">%s</nav>

%s

<div class="franja"><div class="franja-in">
  <span><b>Pagás al recibir</b> — no adelantás nada</span>
  <span><b>Envío $5</b> a todo el país</span>
  <span><b>Cambios</b> en 2 días</span>
  <span><b>Medidas reales</b> de cada prenda</span>
</div></div>
<p class="pie">Dirección A · densa, sans-serif, el producto manda. La ruta de colettecurve y thedress.</p>
</body></html>
""" % (wa('Hola, vi la pagina de BOLEM'), img(hero['fotos'][0], 800), sset(hero['fotos'][0]),
       e(hero['nombre']), len(prods), tallas, ''.join(bloques))


# ============================================================ DIRECCION B ===
CSS_B = """
:root{--tinta:#0F0D10;--tinta2:#565059;--tinta3:#8D858F;--linea:#E9E4EA;
      --acento:#A5427E;--verde:#25D366;--papel:#FFF;--papel2:#F8F5F7;--crema:#FFE4B3}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--papel);color:var(--tinta);
     font-family:'Outfit',system-ui,sans-serif;font-size:16px;line-height:1.55;-webkit-text-size-adjust:100%}
img{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
.aviso{background:#0F0D10;color:#fff;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
       padding:.5rem 1rem;text-align:center;font-family:'Inconsolata',monospace}
.aviso a{color:var(--crema);text-decoration:underline}
.marco{max-width:1240px;margin-inline:auto;padding-inline:clamp(1rem,4vw,2.5rem)}
.barra{display:flex;align-items:center;gap:1.5rem;height:68px;max-width:1240px;margin-inline:auto;
       padding-inline:clamp(1rem,4vw,2.5rem)}
.logo{font-weight:200;font-size:1.3rem;letter-spacing:.4em;margin-right:auto}
.logo b{font-weight:600}
.barra nav{display:flex;gap:1.3rem;font-size:.85rem;color:var(--tinta2)}
@media(max-width:760px){.barra nav{display:none}}

/* la pregunta */
.preg{padding:clamp(2rem,6vh,4rem) 0 0}
.preg h1{margin:0 0 .4rem;font-family:'Playfair Display',Georgia,serif;font-weight:400;
         font-size:clamp(1.9rem,5.5vw,3.4rem);line-height:1.05;letter-spacing:-.02em}
.preg p{margin:0 0 clamp(1.3rem,3vh,2rem);color:var(--tinta2);max-width:34rem;font-size:1.05rem}
.tallas-b{display:grid;grid-template-columns:repeat(auto-fit,minmax(96px,1fr));gap:.6rem}
.tb{position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;
    aspect-ratio:1;border:1.5px solid var(--tinta);overflow:hidden;background:var(--papel)}
.tb em{font-family:'Playfair Display',Georgia,serif;font-style:normal;font-size:clamp(1.6rem,4.5vw,2.6rem);
       line-height:1;letter-spacing:-.02em}
.tb span{font-family:'Inconsolata',monospace;font-size:.72rem;color:var(--tinta3);margin-top:.3rem}
.tb:hover{background:var(--tinta);color:var(--papel)}
.tb:hover span{color:rgba(255,255,255,.7)}

/* mosaico asimetrico */
.mos{display:grid;grid-template-columns:repeat(4,1fr);gap:.7rem;margin-top:clamp(2.5rem,6vh,4.5rem)}
@media(max-width:860px){.mos{grid-template-columns:repeat(2,1fr)}}
.mp{position:relative;display:block;background:var(--papel2);overflow:hidden}
.mp img{width:100%;height:100%;object-fit:cover;object-position:50% 18%;aspect-ratio:2/3}
.mp.g{grid-column:span 2;grid-row:span 2}
.mp.g img{aspect-ratio:1/1.28;object-position:50% 12%}
.mp-info{position:absolute;left:0;right:0;bottom:0;padding:.7rem .8rem;color:#fff;
         background:linear-gradient(transparent,rgba(0,0,0,.62))}
.mp-info b{display:block;font-size:.92rem;font-weight:500;line-height:1.25}
.mp-info span{font-family:'Inconsolata',monospace;font-size:.8rem;opacity:.85}
.calce{position:absolute;top:.6rem;left:.6rem;background:var(--crema);color:#0F0D10;
       font-family:'Inconsolata',monospace;font-size:.66rem;font-weight:600;letter-spacing:.06em;
       text-transform:uppercase;padding:.2rem .45rem}
.med{position:absolute;top:.6rem;right:.6rem;background:rgba(255,255,255,.94);
     font-family:'Inconsolata',monospace;font-size:.66rem;padding:.2rem .45rem}
.sec-t{font-family:'Playfair Display',Georgia,serif;font-size:clamp(1.4rem,3vw,2rem);
       margin:clamp(2.5rem,6vh,4rem) 0 .3rem;font-weight:400}
.sec-p{color:var(--tinta2);margin:0 0 1.2rem;max-width:36rem}
.pie{padding:3rem 0;font-size:.82rem;color:var(--tinta3)}
"""


def dir_b(prods, cuenta):
    tallas = ''.join(
        '<a class="tb" href="#"><em>%s</em><span>%d piezas</span></a>' % (t, cuenta[t])
        for t in ORDEN_TALLAS if cuenta[t])
    g = [p for p in prods if p['destacada']] + [p for p in prods if not p['destacada']]
    piezas = []
    for i, p in enumerate(g[:10]):
        grande = ' g' if i in (0, 5) else ''
        calce = ('<span class="calce">%s</span>' % e(p['calce'].split('(')[0].strip())) if p.get('calce') else ''
        med = ('<span class="med">%s</span>' % e(p['modelo_talla'])) if p.get('modelo_talla') else ''
        piezas.append("""<a class="mp%s" href="#">
  <img src="%s" srcset="%s" sizes="(max-width:860px) 50vw, 25vw" alt="%s" loading="lazy">
  %s%s
  <span class="mp-info"><b>%s</b><span>$%s · %s</span></span>
</a>""" % (grande, img(p['fotos'][0], 800), sset(p['fotos'][0]), e(p['nombre']),
           calce, med, e(p['nombre']), pr(p['precio']), e(' · '.join(p['tallas']))))

    return cabeza('B · Editorial de talla', CSS_B) + """
<header class="barra">
  <a class="logo" href="#">BOL<b>E</b>M</a>
  <nav><a href="#">La colección</a><a href="#">Tu talla</a><a href="#">Lo que dicen</a><a href="#">Nosotras</a></nav>
</header>

<section class="marco preg">
  <h1>¿Cuál es tu talla?</h1>
  <p>Empezá por ahí y la tienda entera se reordena para vos. Nada de buscar entre
  cosas que no te van a quedar.</p>
  <div class="tallas-b">%s</div>
</section>

<section class="marco">
  <h2 class="sec-t">Lo que hay ahorita</h2>
  <p class="sec-p">Cada foto dice cuánto mide la modelo y qué talla lleva puesta. Cuando ese dato
  todavía no lo tenemos, la prenda lo dice en su ficha en vez de callarlo.</p>
  <div class="mos">%s</div>
</section>

<p class="marco pie">Dirección B · el cuerpo como eje. Menos piezas a la vista, cada una diciendo cómo queda.</p>
</body></html>
""" % (tallas, ''.join(piezas))


# ============================================================ DIRECCION C ===
CSS_C = """
:root{--tinta:#17141A;--tinta2:#57505A;--tinta3:#8B838E;--linea:#EAE5EC;
      --acento:#A5427E;--verde:#25D366;--papel:#FFF;--papel2:#FAF7F9;--crema:#FFE4B3}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--papel);color:var(--tinta);
     font-family:'Outfit',system-ui,sans-serif;font-size:16px;line-height:1.7;-webkit-text-size-adjust:100%}
img{display:block;max-width:100%}
a{color:inherit;text-decoration:none}
.aviso{background:#17141A;color:#fff;font-size:11px;letter-spacing:.1em;text-transform:uppercase;
       padding:.5rem 1rem;text-align:center;font-family:'Inconsolata',monospace}
.aviso a{color:var(--crema);text-decoration:underline}
.marco{max-width:1160px;margin-inline:auto;padding-inline:clamp(1.15rem,5vw,3rem)}
.barra{display:flex;align-items:center;gap:1.5rem;height:76px;max-width:1160px;margin-inline:auto;
       padding-inline:clamp(1.15rem,5vw,3rem)}
.logo{font-weight:200;font-size:1.3rem;letter-spacing:.42em;margin-right:auto}
.logo b{font-weight:600}
.barra nav{display:flex;gap:1.4rem;font-size:.85rem;color:var(--tinta2)}
@media(max-width:760px){.barra nav{display:none}}

.intro{padding:clamp(2rem,6vh,4.5rem) 0 clamp(1.5rem,4vh,3rem);max-width:40rem}
.rot{font-family:'Inconsolata',monospace;font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;
     color:var(--tinta3);margin:0 0 .8rem}
.intro h1{margin:0 0 1rem;font-family:'Playfair Display',Georgia,serif;font-weight:400;font-style:italic;
          font-size:clamp(1.7rem,4vw,2.7rem);line-height:1.25;letter-spacing:-.01em}
.intro p{margin:0;color:var(--tinta2);font-size:1.08rem}

/* bloques alternados */
.b{display:grid;grid-template-columns:1fr 1fr;gap:clamp(1.5rem,4vw,3.5rem);align-items:center;
   padding:clamp(2rem,5vh,3.5rem) 0;border-top:1px solid var(--linea)}
.b:nth-child(even) .b-foto{order:2}
@media(max-width:820px){.b{grid-template-columns:1fr}.b:nth-child(even) .b-foto{order:0}}
.b-foto{background:var(--papel2)}
.b-foto img{width:100%;aspect-ratio:2/3;object-fit:cover}
.b-txt h2{margin:0 0 .5rem;font-family:'Playfair Display',Georgia,serif;font-weight:400;
          font-size:clamp(1.4rem,3vw,2rem);line-height:1.15}
.b-precio{font-family:'Inconsolata',monospace;font-size:1.15rem;font-weight:600;margin:0 0 1rem}
.b-cita{margin:0 0 1.2rem;color:var(--tinta2);font-size:1.02rem}
.b-cita em{font-family:'Playfair Display',Georgia,serif;font-style:italic}
.b-datos{list-style:none;margin:0 0 1.4rem;padding:0;display:flex;flex-direction:column;gap:.4rem;
         font-size:.9rem;color:var(--tinta2);border-top:1px solid var(--linea);padding-top:1rem}
.b-datos b{color:var(--tinta);font-family:'Inconsolata',monospace;font-size:.82rem;
           letter-spacing:.08em;text-transform:uppercase;margin-right:.5rem}
.b-falta{border:1px dashed var(--linea);padding:.6rem .8rem;font-size:.86rem;color:var(--tinta3)}
.bt{display:inline-flex;align-items:center;gap:.5rem;background:var(--verde);color:#111;
    font-weight:600;padding:.75rem 1.4rem;font-size:.95rem}
.tallas-c{display:flex;flex-wrap:wrap;gap:.4rem;margin:0 0 1.2rem}
.tallas-c span{font-family:'Inconsolata',monospace;font-size:.82rem;font-weight:600;
               border:1px solid var(--tinta);padding:.25rem .6rem}
.cierre{background:var(--papel2);margin-top:3rem;padding:clamp(2rem,5vh,3.5rem) 0;text-align:center}
.pie{padding:2.5rem 0;font-size:.82rem;color:var(--tinta3)}
"""


def dir_c(prods, cuenta):
    HISTORIAS = {
        'vestido-maxi-smocked': 'La espalda es toda elástica. Por eso le queda a cuerpos muy distintos '
                                'y por eso lo traje en cuatro colores en vez de uno.',
        'chaleco-elegante-marfil': 'Lo vi y pensé en mi hermana yendo a una boda sin querer usar vestido. '
                                   'Se lleva con jeans o con pantalón de vestir.',
        'conjunto-burdeos': 'Dos piezas que ya combinan es media hora menos frente al clóset. '
                            'El vino no es fácil de encontrar en talla grande.',
        'pantalon-formal-crema': 'Encontrar un palazzo que caiga bien y no se transparente me costó '
                                 'tres proveedores. Éste es el que pasó.',
    }
    elegidas = [p for p in prods if p['id'] in HISTORIAS]
    elegidas.sort(key=lambda p: list(HISTORIAS).index(p['id']))

    bloques = []
    for p in elegidas:
        datos = []
        if p.get('calce'):
            datos.append('<li><b>Calce</b>%s</li>' % e(p['calce']))
        if p.get('tela'):
            datos.append('<li><b>Tela</b>%s</li>' % e(p['tela']))
        if p.get('modelo_altura'):
            datos.append('<li><b>La modelo</b>mide %s y lleva %s</li>'
                         % (e(p['modelo_altura']), e(p.get('modelo_talla') or '—')))
        cuerpo = ('<ul class="b-datos">%s</ul>' % ''.join(datos)) if datos else (
            '<p class="b-falta">Todavía no publicamos la tela ni cómo queda esta prenda. '
            'Estamos midiéndolas una por una.</p>')
        bloques.append("""<article class="b">
  <div class="b-foto"><img src="%s" srcset="%s" sizes="(max-width:820px) 100vw, 50vw" alt="%s" loading="lazy"></div>
  <div class="b-txt">
    <h2>%s</h2>
    <p class="b-precio">$%s</p>
    <p class="b-cita"><em>&laquo;%s&raquo;</em></p>
    <div class="tallas-c">%s</div>
    %s
    <a class="bt" href="%s">Apartar por WhatsApp</a>
  </div>
</article>""" % (img(p['fotos'][0], 800), sset(p['fotos'][0]), e(p['nombre']), e(p['nombre']),
                 pr(p['precio']), e(HISTORIAS[p['id']]),
                 ''.join('<span>%s</span>' % e(t) for t in p['tallas']), cuerpo,
                 e(wa('Hola, quiero apartar el %s' % p['nombre']))))

    return cabeza('C · Vitrina de Mónica', CSS_C) + """
<header class="barra">
  <a class="logo" href="#">BOL<b>E</b>M</a>
  <nav><a href="#">La colección</a><a href="#">Tu talla</a><a href="#">Lo que dicen</a><a href="#">Nosotras</a></nav>
</header>

<section class="marco intro">
  <p class="rot">%d piezas · elegidas una por una</p>
  <h1>No fabrico ropa. Busco la que sí está cortada para nosotras — y traigo solo la que me pondría yo.</h1>
  <p>Mónica, fundadora de BOLEM</p>
</section>

<div class="marco">
%s
</div>

<div class="cierre"><div class="marco">
  <p class="rot">Y hay %d más</p>
  <a class="bt" href="#">Ver toda la colección</a>
</div></div>
<p class="marco pie">Dirección C · la vitrina. Pocas prendas, cada una con por qué está acá.</p>
</body></html>
""" % (len(prods), ''.join(bloques), len(prods) - len(elegidas))


# =================================================================== indice ==
CSS_IX = """
:root{--tinta:#16131A;--tinta2:#5A525E;--tinta3:#8D848F;--linea:#E8E2EA;--acento:#A5427E;--papel2:#FAF7F9}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:#fff;color:var(--tinta);font-family:'Outfit',system-ui,sans-serif;
     font-size:16px;line-height:1.65;padding:0 1.15rem 4rem}
.marco{max-width:56rem;margin-inline:auto}
h1{font-family:'Playfair Display',Georgia,serif;font-weight:400;font-size:clamp(1.8rem,5vw,2.6rem);
   margin:2.5rem 0 .5rem;line-height:1.15}
.sub{color:var(--tinta2);margin:0 0 2rem;max-width:38rem}
.rot{font-family:'Inconsolata',monospace;font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;
     color:var(--tinta3);margin:0 0 .5rem}
.ops{display:grid;gap:1rem}
.op{border:1px solid var(--linea);padding:1.2rem 1.3rem;display:block;text-decoration:none;color:inherit}
.op:hover{border-color:var(--acento)}
.op h2{margin:0 0 .3rem;font-family:'Playfair Display',Georgia,serif;font-weight:400;font-size:1.4rem}
.op p{margin:0 0 .7rem;color:var(--tinta2);font-size:.95rem}
.op ul{margin:0;padding-left:1.1rem;font-size:.88rem;color:var(--tinta3)}
.op .ver{display:inline-block;margin-top:.8rem;font-family:'Inconsolata',monospace;font-size:.8rem;
         font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--acento)}
.caja{background:var(--papel2);border-left:3px solid var(--acento);padding:1rem 1.2rem;margin:2rem 0}
.caja p{margin:0;font-size:.95rem;color:var(--tinta2)}
"""


def indice():
    return """<!DOCTYPE html>
<html lang="es-SV"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BOLEM — tres direcciones de diseño</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="%s">
<style>%s</style></head><body><div class="marco">
<p class="rot" style="margin-top:2.5rem">BOLEM · elegir cómo se ve</p>
<h1>Tres direcciones para el mismo catálogo</h1>
<p class="sub">Las tres usan las 49 prendas y las fotos reales. Cambia cómo se ven, no qué hay.
Lo único que las tres respetan es lo que Mónica dejó claro: <strong>fondo blanco y el color lo
ponen las fotos</strong>.</p>

<div class="caja"><p>Mirálas en el celular, que es donde va a llegar el 90%% de las clientas.
Y fijate en una sola cosa: <strong>en cuál te dan más ganas de tocar una prenda</strong>.</p></div>

<div class="ops">
  <a class="op" href="a/">
    <h2>A · Catálogo denso</h2>
    <p>La ruta de <em>colettecurve</em> y <em>thedress</em>, que son las referencias que dio Mónica.</p>
    <ul>
      <li>Sans-serif en todo, sin titular grande</li>
      <li>Foto de campaña arriba, tallas pegadas debajo</li>
      <li>Seis prendas por fila — se ve casi todo el catálogo sin bajar mucho</li>
      <li>Casi nada de texto: el producto manda</li>
    </ul>
    <span class="ver">Ver la A &rarr;</span>
  </a>

  <a class="op" href="b/">
    <h2>B · Editorial de talla</h2>
    <p>El cuerpo como eje. Arranca preguntando la talla y la tienda se reordena.</p>
    <ul>
      <li>Empieza con «¿Cuál es tu talla?» y seis cuadros grandes</li>
      <li>Mosaico asimétrico: unas fotos grandes, otras chicas</li>
      <li>El calce y la talla de la modelo van <em>encima</em> de la foto</li>
      <li>Menos piezas a la vista, cada una diciendo más</li>
    </ul>
    <span class="ver">Ver la B &rarr;</span>
  </a>

  <a class="op" href="c/">
    <h2>C · La vitrina de Mónica</h2>
    <p>Pocas prendas, cada una con por qué está acá. Apuesta todo a que una persona las eligió.</p>
    <ul>
      <li>Bloques alternados: foto grande a un lado, la prenda contada al otro</li>
      <li>Arranca con Mónica hablando, no con un eslogan</li>
      <li>Lento y generoso — se lee, no se barre</li>
      <li>Riesgo: se ven pocas prendas por pantalla</li>
    </ul>
    <span class="ver">Ver la C &rarr;</span>
  </a>
</div>

<div class="caja" style="border-color:#8A6212"><p><strong>Ojo con la C:</strong> las historias que
aparecen ahí las escribí yo para que se vea cómo funcionaría. <strong>No son de Mónica.</strong>
Si esta dirección gana, esas cuatro frases las tiene que escribir ella — es justamente lo que la
hace imposible de copiar.</p></div>

</div></body></html>
""" % (FUENTES, CSS_IX)


def main():
    d = json.load(open(DATOS, encoding='utf-8'))
    prods = d['productos']
    cuenta = {t: sum(1 for p in prods if t in p['tallas']) for t in ORDEN_TALLAS}
    paginas = {'a/index.html': dir_a(prods, cuenta),
               'b/index.html': dir_b(prods, cuenta),
               'c/index.html': dir_c(prods, cuenta),
               'index.html': indice()}
    for rel, cont in paginas.items():
        p = os.path.join(SALIDA, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(cont)
        print('  %-16s %6.0f KB' % (rel, len(cont.encode()) / 1024))
    print('\ntres direcciones + indice en v2/disenos/')
    return 0


if __name__ == '__main__':
    sys.exit(main())
