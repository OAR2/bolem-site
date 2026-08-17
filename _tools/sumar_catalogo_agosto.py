# -*- coding: utf-8 -*-
"""Suma al catalogo las prendas nuevas del envio de Monica del 17-ago-2026.

Que hace y que NO hace, a proposito:

  SUMA  16 prendas que no estaban, con foto ya procesada.
  SUMA  una segunda foto a dos prendas que ya existian.
  SUMA  la talla "L" a la escala, porque Monica la usa en 3 prendas.

  NO TOCA precios ni tallas de nada ya publicado. Donde el envio de Monica
  contradice al sitio, lo REPORTA y sigue de largo: cambiar una talla o un
  precio publicado por una lectura nuestra es exactamente el error que manda
  la prenda equivocada. Eso lo decide Monica, no este script.
  (regla: rules/identidad.md — sin identificador autoritativo, flag, no decision)

Es idempotente: correrlo dos veces deja el archivo igual.

Uso:
    python _tools/sumar_catalogo_agosto.py --ensayo    (no escribe, solo reporta)
    python _tools/sumar_catalogo_agosto.py
"""
import io, os, sys, json, shutil, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, '_data', 'catalogo.json')
FOTOS = os.path.join(ROOT, 'assets', 'productos')

WA_BASE = 'https://wa.me/50368590899?text='


def wa(nombre, multicolor=False):
    t = 'Hola, quiero apartar el %s. Mi talla es: ' % nombre
    if multicolor:
        t += ' y lo quiero en color: '
    return WA_BASE + urllib.parse.quote(t, safe='')


def alt(nombre, desc, texto_tallas):
    return '%s %s plus size, tallas %s — BOLEM El Salvador' % (nombre, desc, texto_tallas)


# id, nombre, categoria, precio, tallas, texto, descripcion-para-alt, fotos
NUEVAS = [
    ('camiseta-rayas-fucsia', 'Camiseta de Rayas', 'blusa', 23.0,
     ['2XL', '3XL'], '2XL–3XL', 'en rayas rosa y fucsia',
     ['camiseta-rayas-fucsia.webp']),
    ('blusa-encaje-negro', 'Blusa con Encaje', 'blusa', 23.0,
     ['XL', '1XL', '2XL'], 'XL–2XL', 'negra con ruedo de encaje floral',
     ['blusa-encaje-negro.webp']),
    ('halter-argolla-vino', 'Halter de Argolla', 'blusa', 24.0,
     ['L', 'XL', '1XL'], 'L–1XL', 'en vino con argolla dorada al cuello',
     ['halter-argolla-vino.webp']),
    ('halter-satin-encaje', 'Halter Satín con Encaje', 'blusa', 25.0,
     ['1XL', '2XL', '3XL', '4XL'], '1XL–4XL', 'negro con ruedo asimétrico de encaje',
     ['halter-satin-encaje.webp']),
    ('top-drapeado-marfil', 'Top Drapeado', 'blusa', 25.0,
     ['1XL', '2XL'], '1XL–2XL', 'en marfil con escote drapeado asimétrico',
     ['top-drapeado-marfil.webp']),
    ('blusa-vichy-lazos', 'Blusa Vichy con Lazos', 'blusa', 25.0,
     ['XL', '1XL', '2XL'], 'XL–2XL', 'en cuadro vichy blanco y negro con lazos de terciopelo',
     ['blusa-vichy-lazos.webp']),
    ('blusa-peplum-broches', 'Blusa Peplum con Broches', 'blusa', 25.0,
     ['XL', '1XL', '2XL', '3XL'], 'XL–3XL', 'en marfil sin mangas con broches plateados',
     ['blusa-peplum-broches.webp']),
    ('blusa-chambray', 'Blusa Chambray', 'blusa', 29.0,
     ['2XL', '3XL', '4XL'], '2XL–4XL', 'en mezclilla suave con mangas globo y cintura ajustable',
     ['blusa-chambray.webp']),
    ('chaleco-denim', 'Chaleco Denim', 'blusa', 29.0,
     ['L', 'XL', '1XL', '2XL'], 'L–2XL', 'en mezclilla con botones dorados',
     ['chaleco-denim.webp']),
    ('camisa-mantequilla', 'Camisa Mantequilla', 'blusa', 32.5,
     ['2XL'], '2XL', 'amarillo mantequilla, corte oversize',
     ['camisa-mantequilla.webp']),

    ('pantalon-formal-negro', 'Pantalón Formal Negro', 'pantalon', 37.5,
     ['XL', '1XL', '2XL'], 'XL–2XL', 'de pierna ancha con cinturón',
     ['pantalon-formal-negro.webp']),
    ('pantalon-lunares', 'Pantalón de Lunares', 'pantalon', 45.0,
     ['4XL'], '4XL', 'crema con lunares negros, pierna ancha',
     ['pantalon-lunares.webp']),

    ('vestido-largo-volantes', 'Vestido Largo de Volantes', 'vestido', 28.0,
     ['3XL'], '3XL', 'negro con cinturón de lazo y volante en cascada',
     ['vestido-largo-volantes.webp']),
    ('vestido-negro-corte-a', 'Vestido Corte A', 'vestido', 35.0,
     ['2XL', '3XL'], '2XL–3XL', 'negro midi de manga corta',
     ['vestido-negro-corte-a.webp']),
    ('vestido-capas-gasa', 'Vestido de Capas', 'vestido', 45.0,
     ['2XL', '3XL'], '2XL–3XL', 'negro en gasa con falda de capas',
     ['vestido-capas-gasa.webp']),
    ('vestido-camisero-denim', 'Vestido Camisero Denim', 'vestido', 55.0,
     ['1XL', '2XL', '3XL'], '1XL–3XL', 'en mezclilla con cinturón de lazo',
     ['vestido-camisero-denim.webp']),
]

# prendas ya publicadas que ganan una segunda foto
FOTO_EXTRA = {
    'blusa-blazer-negro': 'blusa-blazer-negro-2.webp',
    'jeans-flare': 'jeans-flare-2.webp',
}

# La foto vino de un catalogo de proveedor (otra modelo, fondo de estudio ajeno).
# Precedente: las 3 fotos de jeans "Most Wanted" quedaron fuera en jul-2026
# hasta aclarar derechos.
DERECHOS_POR_CONFIRMAR = {'vestido-camisero-denim'}

# Lo que el envio de Monica contradice del sitio. NO se aplica: se reporta.
DISCREPANCIAS = [
    ('pantalon-formal-crema', 'precio',
     'el sitio publica $45.00; el archivo de Mónica dice $37.50'),
    ('pantalon-formal-crema', 'tallas',
     'el sitio publica XL–3XL; el archivo de Mónica dice XL a 2XL'),
    ('jeans-flare', 'tallas',
     'el sitio publica 1XL–3XL; el archivo de Mónica dice 16W a 20W '
     '(escala numérica gringa — es otra forma de medir, no otra prenda)'),
    ('blusa-blazer-negro', 'tallas',
     'el sitio publica 1XL–3XL; el archivo de Mónica dice XL a 2XL'),
]

# Publicadas hoy que NO aparecen en el envio nuevo, en ningun color. Puede ser
# que se agotaron o que solo no se volvieron a fotografiar. No se quitan: eso
# lo decide Monica.
SIN_FOTO_NUEVA = ['blusa-off-shoulder', 'blusa-peplum-rayas', 'vestido-verano-rojo']

# Prendas que SI vienen en el envio, pero a las que les falta un color.
COLOR_SIN_FOTO_NUEVA = [
    ('vestido-shirtdress', 'el color camel no viene en el envio; el crema sí'),
]


def main(ensayo):
    d = json.load(open(CAT, encoding='utf-8'))
    ids = {p['id'] for p in d['productos']}
    antes = len(d['productos'])

    problemas = []

    # --- escala de tallas: Monica usa L en 3 prendas ---
    if 'L' not in d['escala_tallas']:
        d['escala_tallas'] = ['L'] + d['escala_tallas']
        print('escala de tallas: se agrega "L" -> %s' % d['escala_tallas'])

    # --- prendas nuevas ---
    agregadas = 0
    for (pid, nombre, cat, precio, tallas, texto, desc, fotos) in NUEVAS:
        for f in fotos:
            if not os.path.exists(os.path.join(FOTOS, f)):
                problemas.append('%s: falta la foto %s' % (pid, f))
        if pid in ids:
            continue
        d['productos'].append({
            'id': pid,
            'nombre': nombre,
            'categoria': cat,
            'precio': precio,
            'tallas': tallas,
            'tallas_texto_original': texto,
            'colores': 1,
            'fotos': fotos,
            'destacada': False,
            'alt': alt(nombre, desc, texto),
            'wa': wa(nombre),
        })
        agregadas += 1
        marca = '  [DERECHOS POR CONFIRMAR]' if pid in DERECHOS_POR_CONFIRMAR else ''
        print('  + %-26s $%-7s %-10s %s%s' % (pid, precio, texto, nombre, marca))

    # --- segunda foto a prendas existentes ---
    extras = 0
    for pid, foto in FOTO_EXTRA.items():
        if not os.path.exists(os.path.join(FOTOS, foto)):
            problemas.append('%s: falta la foto extra %s' % (pid, foto))
            continue
        for p in d['productos']:
            if p['id'] == pid and foto not in p['fotos']:
                p['fotos'].append(foto)
                extras += 1
                print('  ~ %-26s segunda foto: %s' % (pid, foto))

    # --- orden: por categoria y precio, como estaba ---
    orden_cat = list(d['categorias'].keys())
    d['productos'].sort(key=lambda p: (orden_cat.index(p['categoria']), p['precio'], p['id']))

    print('\nproductos: %d -> %d   (nuevas %d, segundas fotos %d)'
          % (antes, len(d['productos']), agregadas, extras))

    if problemas:
        print('\n--- NO SE ESCRIBE: faltan fotos ---')
        for x in problemas:
            print('  ' + x)
        return 1

    if not ensayo:
        shutil.copy2(CAT, CAT + '.bak')
        json.dump(d, open(CAT, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('\nescrito: %s   (respaldo en catalogo.json.bak)' % CAT)
    else:
        print('\nENSAYO: no se escribio nada')

    # ---------- lo que queda para Monica ----------
    print('\n' + '=' * 72)
    print('PARA MONICA — esto NO se toco, hay que preguntarle')
    print('=' * 72)
    print('\n1) El envio contradice lo publicado en %d puntos:' % len(DISCREPANCIAS))
    for pid, campo, texto in DISCREPANCIAS:
        print('   - %-24s %-7s %s' % (pid, campo, texto))
    print('\n2) %d prendas publicadas hoy NO vienen en el envio nuevo.' % len(SIN_FOTO_NUEVA))
    print('   Se quedan en el sitio. ¿Se agotaron o solo no se volvieron a fotografiar?')
    for pid in SIN_FOTO_NUEVA:
        p = next((x for x in d['productos'] if x['id'] == pid), None)
        if p:
            print('   - %-24s $%-7s %s' % (pid, p['precio'], p['nombre']))
    print('\n   OJO: las dos primeras son las UNICAS de $22 del catalogo, y el sitio')
    print('   anuncia el rango "$22–$85" en el schema, en llms.txt y en el copy.')
    print('   Si se agotaron, ese rango hay que corregirlo.')
    print('\n   Ademas, %d prenda(s) vienen incompletas de color:' % len(COLOR_SIN_FOTO_NUEVA))
    for pid, nota in COLOR_SIN_FOTO_NUEVA:
        print('   - %-24s %s' % (pid, nota))
    print('\n3) 1 prenda con foto de catalogo ajeno (otra modelo, fondo de proveedor):')
    for pid in sorted(DERECHOS_POR_CONFIRMAR):
        print('   - %s' % pid)
    print('   Queda cargada pero hay que confirmar derechos antes de publicar.')
    print('\n4) Los nombres de las %d prendas nuevas los puse yo.' % len(NUEVAS))
    print('   Monica corrige el que quiera: se edita _data/catalogo.json y se')
    print('   reconstruye con _tools/construir_catalogo.py.')
    return 0


if __name__ == '__main__':
    sys.exit(main('--ensayo' in sys.argv))
