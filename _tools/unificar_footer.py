# -*- coding: utf-8 -*-
"""Un solo pie de pagina para las 12 paginas del sitio.

Hermano de `unificar_nav.py`, misma enfermedad un piso mas abajo: al 16-ago
habia CUATRO footers distintos. El home listaba ocho enlaces (incluidos
"Envios" y "Pagos", que en realidad iban los dos al mismo bloque de FAQ);
coleccion listaba tres; nosotras y el blog, cuatro; las legales, cinco. Otra
vez "Tallas" y "Guia de Tallas" conviviendo como si fueran paginas distintas.

Criterio de que va en cada sitio, que es lo que evita que esto vuelva:

    el NAV responde DONDE COMPRAR       -> Coleccion, Guia de tallas, Nosotras, Blog
    el FOOTER responde COMO COMPRAR     -> Preguntas frecuentes, Guia de tallas,
       TRANQUILA, y lo legal                Cambios, Privacidad, Terminos

Por eso Nosotras y Blog salen del footer: ya estan en el nav de todas las
paginas y repetirlos no agrega un camino, agrega ruido.

Y "Preguntas frecuentes" entra en las 12: el FAQ del home contesta envios,
pagos, tallas, cambios y si es seguro comprar por WhatsApp — o sea justo las
dudas que frenan a alguien que no conoce la marca. Hasta hoy solo se llegaba
desde el home, y disfrazado de "Envios" y "Pagos".

De paso se corrigen tres cosas que arrastraban las copias:
  · el logo del home era un <span> muerto; ahora es enlace al inicio, como en
    las demas
  · los iconos de Instagram y WhatsApp iban sin `aria-label` en 5 paginas: un
    lector de pantalla no leia nada
  · `rel="noopener"` faltaba en varias

Regla de la casa: TODO o NADA. Si una pagina no calza, aborta sin escribir.

Uso:  python _tools/unificar_footer.py          (aplica)
      python _tools/unificar_footer.py --dry    (solo reporta)
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WA = ('https://wa.me/50368590899?text=Hola%2C%20vi%20la%20p%C3%A1gina%20de%20'
      'BOLEM%20y%20quiero%20saber%20m%C3%A1s')
IG = 'https://instagram.com/bolem_sv'

SVG_IG = ('<svg fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.163c3.204 0 '
          '3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205'
          '-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0'
          '-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204'
          '.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 '
          '8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 '
          '4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782'
          '-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78'
          '-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 '
          '16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>')

SVG_WA = ('<svg fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M17.472 14.382c-.297-.149'
          '-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075'
          '-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133'
          '.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207'
          '-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 '
          '2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 '
          '1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57'
          '-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 '
          '01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 '
          '6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 '
          '11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 '
          '11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>')

# pagina -> prefijo de rutas
PAGINAS = {
    'index.html':                                          '',
    'nosotros.html':                                        '',
    'guia-de-tallas.html':                                  '',
    'cambios.html':                                         '',
    'terminos.html':                                        '',
    'privacidad.html':                                      '',
    '404.html':                                             '',
    'coleccion/index.html':                                 '../',
    'blog/index.html':                                      '../',
    'blog/guia-tallas-plus-size.html':                      '../',
    'blog/historia-bolem-moda-plus-size-el-salvador.html':  '../',
    'blog/looks-plus-size-clima-calido.html':               '../',
}

ENLACES = [
    # `#faq` vive en el home. Desde la raiz es `./#faq`; desde blog/ y
    # coleccion/ es `../#faq`. Se marca con None y se resuelve al construir,
    # porque pegarle el prefijo a secas daria el horrendo `.././#faq`.
    (None,              'Preguntas frecuentes'),
    ('guia-de-tallas',  'Guía de tallas'),
    ('cambios',         'Cambios'),
    ('privacidad',      'Privacidad'),
    ('terminos',        'Términos'),
]

# El home lleva el footer oscuro por diseno (cae bajo una seccion oscura). Es
# una decision de piel, no deriva: se conserva.
MODIFICADORES = {'index.html': ' site-footer--dark'}

RE_FOOTER = re.compile(r'<footer\b[^>]*>.*?</footer>', re.S)


def construir_footer(prefijo, modificador):
    nav = []
    for i, (ruta, etiqueta) in enumerate(ENLACES):
        if i:
            nav.append('        <span>&bull;</span>')
        href = (prefijo or './') + '#faq' if ruta is None else prefijo + ruta
        nav.append('        <a href="%s">%s</a>' % (href, etiqueta))
    return '\n'.join([
        '<footer class="site-footer%s">' % modificador,
        '    <a href="%s" class="footer-logo" aria-label="BOLEM — inicio">BOL<span class="accent">E</span>M</a>' % (prefijo or './'),
        '    <div class="footer-links">',
        '      <p class="footer-copy">&copy; 2026 BOLEM &mdash; Moda Plus Size &bull; El Salvador</p>',
        '      <div class="footer-nav">',
        '\n'.join(nav),
        '      </div>',
        '    </div>',
        '    <div class="footer-social">',
        '      <a href="%s" target="_blank" rel="noopener" aria-label="BOLEM en Instagram">%s</a>' % (IG, SVG_IG),
        '      <a href="%s" target="_blank" rel="noopener" aria-label="Escribile a BOLEM por WhatsApp">%s</a>' % (WA, SVG_WA),
        '    </div>',
        '  </footer>',
    ])


def main():
    seco = '--dry' in sys.argv
    resultados = []
    fallas = []

    for ruta, prefijo in PAGINAS.items():
        completa = os.path.join(RAIZ, ruta)
        if not os.path.exists(completa):
            fallas.append('%s — no existe' % ruta)
            continue
        original = open(completa, encoding='utf-8').read()
        encontrados = RE_FOOTER.findall(original)
        if len(encontrados) != 1:
            fallas.append('%s — esperaba 1 <footer>, encontre %d' % (ruta, len(encontrados)))
            continue
        nuevo = RE_FOOTER.sub(
            lambda m: construir_footer(prefijo, MODIFICADORES.get(ruta, '')),
            original, count=1)
        resultados.append((completa, ruta, nuevo, nuevo != original))

    if fallas:
        print('ABORTADO — no se escribio ningun archivo:')
        for f in fallas:
            print('   x ' + f)
        return 1

    for completa, ruta, nuevo, cambio in resultados:
        if cambio and not seco:
            open(completa, 'w', encoding='utf-8', newline='').write(nuevo)
        print('   %s %s' % ('*' if cambio else '=', ruta))

    print('\n%d paginas, %d modificadas%s'
          % (len(resultados), sum(1 for r in resultados if r[3]), ' (simulacro)' if seco else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
