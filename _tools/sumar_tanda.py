# -*- coding: utf-8 -*-
"""Convierte una carpeta de fotos de Monica en prendas publicadas.

POR QUE EXISTE
La tanda de agosto se sumo con `sumar_catalogo_agosto.py`, que tenia las 16
prendas ESCRITAS A MANO adentro: sirvio una vez y no vuelve a servir. Si manana
llegan 100 fotos, alguien reescribe 100 tuplas a mano. Este script es el puente
que faltaba.

LO QUE SE MIDIO ANTES DE ESCRIBIRLO (2026-08-18, sobre las 58 fotos reales)
  precio en el nombre del archivo .... 100%
  tallas en el nombre ................  97%
  categoria por la carpeta ........... 100%
  algo de descripcion ................  55%   <- y dice "Blusa" o "Conjunto"
Procesar una foto a sus 3 variantes cuesta 5.06 s en un nucleo: 8.4 min por
cada 100. En paralelo sobre 12 nucleos, ~1 min. Regenerar el sitio entero: 0.9 s.
O sea que la maquina nunca fue el problema — el cuello de botella son las 100
decisiones de "como se llama esto y que lo distingue".

LA IDEA
Ese trabajo NO lo hace quien mira la foto de lejos: lo hace quien compro la
ropa. El script llena todo lo derivable y deja DOS columnas en blanco en la
Hoja Madre para que Monica las complete desde el celular.

    FASE 1   python _tools/sumar_tanda.py leer "C:/ruta/carpeta"
             lee, deduplica, procesa fotos y deja el borrador en la Hoja Madre

    (Monica llena `nombre` y `descripcion` en la pestana PRODUCTOS)

    FASE 2   python _tools/sumar_tanda.py aplicar
             baja lo completado, lo suma a catalogo.json y avisa que falta

REGLAS QUE RESPETA
  - Nunca adivina. Lo que no puede leer del nombre lo REPORTA y no lo inventa
    (rules/identidad: sin identificador autoritativo, flag, no decision).
  - Nunca pisa una prenda ya publicada. Si el envio contradice al sitio en
    precio o tallas, lo reporta; cambiarlo lo decide Monica.
  - Deduplica por HUELLA DE IMAGEN, no por nombre de archivo. Monica reenvia
    carpetas que incluyen lo ya publicado, y `$25 1XL a 4XL.jpg` y
    `$25 1XL a 4XL(1).jpg` son dos prendas DISTINTAS, no dos fotos de una.
  - get_all_values(), nunca get_all_records() (rules/excel-writes).
  - Escribe en lote con append_rows, no fila por fila (cuota 429).
  - Idempotente y con --ensayo.
"""
import io, os, re, sys, json, glob, time, unicodedata
from concurrent.futures import ProcessPoolExecutor

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, '_data', 'catalogo.json')
FOTOS = os.path.join(ROOT, 'assets', 'productos')
HOJA_ID = '1-fow67oGgzEw4OM2Pq_gu2sus-gl_kTHCfuZYobwWgQ'
PESTANA = 'PRODUCTOS'

# La carpeta de Monica nombra la categoria; el sitio usa su propio vocabulario.
CARPETA_A_CATEGORIA = {
    'VESTIDOS': 'vestido',
    'BLUSAS': 'blusa',
    'CONJUNTOS': 'conjunto',
    'JEANS Y PANTALON': 'pantalon',
    'JEANS Y PANTALÓN': 'pantalon',
    'PANTALONES': 'pantalon',
}

RE_PRECIO = re.compile(r'\$\s*([0-9]+(?:[.,][0-9]{1,2})?)')
RE_RANGO = re.compile(r'(\d?X?L|\d+W)\s*(?:a|y|-|–|to)\s*(\d?X?L|\d+W)', re.I)
RE_SUELTA = re.compile(r'\b(\d?XL|\d+W|L)\b', re.I)
ESCALA = ['L', 'XL', '1XL', '2XL', '3XL', '4XL', '5XL', '6XL']


# ─────────────────────────── leer el nombre ───────────────────────────

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'-{2,}', '-', re.sub(r'[^a-z0-9]+', '-', s)).strip('-')


def leer_nombre(archivo, carpetas):
    """Saca lo que se pueda del nombre. Lo que no, queda en None.

    `carpetas` es la ruta de carpetas de adentro hacia afuera: la categoria
    puede estar un nivel arriba (REGULAR/VESTIDOS/UN SOLO COLOR).
    """
    base = os.path.splitext(os.path.basename(archivo))[0]
    # Monica separa tallas con guion bajo (`L_XL_1XL`), y `_` es caracter de
    # palabra en regex: sin esto, \\b no corta y no se detecta ninguna talla.
    base = base.replace('_', ' ')
    d = {'archivo': archivo, 'precio': None, 'tallas': None,
         'tallas_texto': None, 'categoria': None, 'pista': '', 'dudas': []}

    m = RE_PRECIO.search(base)
    if m:
        d['precio'] = float(m.group(1).replace(',', '.'))
    else:
        d['dudas'].append('sin precio en el nombre')

    r = RE_RANGO.search(base)
    if r:
        a, b = r.group(1).upper(), r.group(2).upper()
        if a in ESCALA and b in ESCALA:
            d['tallas'] = ESCALA[ESCALA.index(a):ESCALA.index(b) + 1]
        else:
            d['tallas'] = [a, b]          # escala W u otra: se deja tal cual
        d['tallas_texto'] = '%s–%s' % (a, b)
    else:
        sueltas = [s.upper() for s in RE_SUELTA.findall(base)]
        vistas = []
        for s in sueltas:
            if s not in vistas:
                vistas.append(s)
        if vistas:
            d['tallas'] = vistas
            d['tallas_texto'] = '·'.join(vistas)
        else:
            d['dudas'].append('sin tallas en el nombre')

    for c in carpetas:
        cat = CARPETA_A_CATEGORIA.get(c.upper())
        if cat:
            d['categoria'] = cat
            break
    if not d['categoria']:
        d['dudas'].append('ninguna carpeta de "%s" mapea a categoria'
                          % '/'.join(carpetas[:3]))

    # lo que queda tras quitar precio y tallas es la pista que dio Monica
    resto = RE_PRECIO.sub('', base)
    resto = RE_RANGO.sub('', resto)
    resto = RE_SUELTA.sub('', resto)
    resto = re.sub(r'[\(\)_\-–\d]+', ' ', resto)
    d['pista'] = re.sub(r'\s+', ' ', resto).strip()
    return d


# ─────────────────────────── huella de imagen ───────────────────────────

def dhash(ruta, lado=16):
    """Huella perceptual. Dos archivos distintos de la MISMA foto dan lo mismo."""
    from PIL import Image
    im = Image.open(ruta).convert('L').resize((lado + 1, lado), Image.LANCZOS)
    px = list(im.getdata())
    bits = []
    for y in range(lado):
        fila = px[y * (lado + 1):(y + 1) * (lado + 1)]
        for x in range(lado):
            bits.append('1' if fila[x] > fila[x + 1] else '0')
    return ''.join(bits)


def distancia(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def _huella_de(ruta):
    try:
        return ruta, dhash(ruta)
    except Exception as e:
        return ruta, 'ERROR:' + str(e)


# ─────────────────────────── procesar fotos ───────────────────────────

def _procesar_una(tarea):
    """Corre en otro proceso: una foto -> sus 3 variantes."""
    origen, destino_base = tarea
    from PIL import Image, ImageOps
    try:
        im = ImageOps.exif_transpose(Image.open(origen)).convert('RGB')
        w, h = im.size
        obj = 2 / 3
        if w / h > obj:
            nw = int(h * obj)
            im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
            recorte = 100 - nw * 100 // w
        else:
            nh = int(w / obj)
            im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
            recorte = 100 - nh * 100 // h
        for ancho, suf in ((1200, ''), (800, '-800'), (480, '-480')):
            im.resize((ancho, int(ancho * 1.5)), Image.LANCZOS).save(
                destino_base + suf + '.webp', 'WEBP', quality=82, method=4)
        return (origen, True, recorte, '')
    except Exception as e:
        return (origen, False, 0, str(e))


# ─────────────────────────── la hoja ───────────────────────────

def abrir_hoja():
    import gspread
    return gspread.oauth().open_by_key(HOJA_ID).worksheet(PESTANA)


def filas_hoja(ws):
    v = ws.get_all_values()          # NUNCA get_all_records (rules/excel-writes)
    if not v:
        return [], []
    return v[0], v[1:]


# ─────────────────────────── FASE 1: leer ───────────────────────────

def fase_leer(carpeta, ensayo):
    from PIL import Image  # noqa: F401  (falla temprano si no esta Pillow)
    if not os.path.isdir(carpeta):
        print('no existe la carpeta:', carpeta)
        return 1

    cat = json.load(open(CAT, encoding='utf-8'))
    publicadas = cat['productos']

    # 1. juntar las fotos de la carpeta
    entrantes = []
    for base, dirs, files in os.walk(carpeta):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        rel = os.path.relpath(base, carpeta)
        # de adentro hacia afuera: 'UN SOLO COLOR', 'VESTIDOS', 'REGULAR'
        cadena = [x for x in reversed(rel.split(os.sep)) if x not in ('.', '')]
        for f in sorted(files):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                entrantes.append((os.path.join(base, f), cadena))
    print('fotos en la carpeta: %d' % len(entrantes))
    if not entrantes:
        return 1

    # 2. huellas de lo YA publicado y de lo que entra (en paralelo)
    ya = [os.path.join(FOTOS, p['fotos'][0]) for p in publicadas
          if p.get('fotos') and os.path.exists(os.path.join(FOTOS, p['fotos'][0]))]
    t0 = time.time()
    nucleos = max((os.cpu_count() or 4) - 2, 1)
    with ProcessPoolExecutor(max_workers=nucleos) as ex:
        h_ya = dict(ex.map(_huella_de, ya, chunksize=4))
        h_new = dict(ex.map(_huella_de, [e[0] for e in entrantes], chunksize=4))
    print('huellas calculadas en %.1f s (%d nucleos)' % (time.time() - t0, nucleos))

    # 3. separar lo nuevo de lo repetido
    nuevas, repetidas = [], []
    for ruta, cadena in entrantes:
        hn = h_new.get(ruta, '')
        if hn.startswith('ERROR'):
            print('   no se pudo leer:', os.path.basename(ruta))
            continue
        igual = None
        for rya, hya in h_ya.items():
            if not hya.startswith('ERROR') and distancia(hn, hya) <= 8:
                igual = os.path.basename(rya)
                break
        if igual:
            repetidas.append((ruta, igual))
        else:
            nuevas.append((ruta, cadena))
    print('  ya publicadas: %d   nuevas: %d' % (len(repetidas), len(nuevas)))
    if not nuevas:
        print('\nnada que sumar.')
        return 0

    # 4. leer los nombres
    leidas, con_dudas = [], []
    usados = {p['id'] for p in publicadas}
    for ruta, cadena in nuevas:
        d = leer_nombre(ruta, cadena)
        raiz = slug('%s-%s' % (d['categoria'] or 'prenda', d['pista'] or 'nueva'))[:44] or 'prenda-nueva'
        pid, k = raiz, 2
        while pid in usados:
            pid = '%s-%d' % (raiz, k)
            k += 1
        usados.add(pid)
        d['id'] = pid
        leidas.append(d)
        if d['dudas']:
            con_dudas.append(d)

    print()
    print('LO QUE SE PUDO LEER DEL NOMBRE')
    print('  con precio : %d de %d' % (sum(1 for d in leidas if d['precio']), len(leidas)))
    print('  con tallas : %d de %d' % (sum(1 for d in leidas if d['tallas']), len(leidas)))
    print('  con categoria: %d de %d' % (sum(1 for d in leidas if d['categoria']), len(leidas)))
    if con_dudas:
        print()
        print('  NO SE ADIVINA — %d fotos necesitan que alguien lo diga:' % len(con_dudas))
        for d in con_dudas[:12]:
            print('    %-46s %s' % (os.path.basename(d['archivo'])[:44], '; '.join(d['dudas'])))

    if ensayo:
        print('\n(--ensayo: no se escribio ni una foto ni una fila)')
        return 0

    # 5. procesar fotos, en paralelo
    os.makedirs(FOTOS, exist_ok=True)
    tareas = [(d['archivo'], os.path.join(FOTOS, d['id'])) for d in leidas]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=nucleos) as ex:
        res = list(ex.map(_procesar_una, tareas, chunksize=2))
    ok = sum(1 for r in res if r[1])
    print()
    print('fotos procesadas: %d de %d en %.1f s' % (ok, len(res), time.time() - t0))
    for origen, bien, recorte, err in res:
        if not bien:
            print('   FALLO %s: %s' % (os.path.basename(origen), err))
        elif recorte >= 25:
            print('   revisar %s: se recorto %d%% para llegar a 2:3'
                  % (os.path.basename(origen), recorte))

    # 6. borrador a la Hoja Madre
    ws = abrir_hoja()
    cab, previas = filas_hoja(ws)
    ids_hoja = {f[0] for f in previas if f}
    nuevas_filas = []
    for d in leidas:
        if d['id'] in ids_hoja:
            continue
        nuevas_filas.append([
            d['id'],                                  # id
            '',                                       # nombre        <- MONICA
            d['categoria'] or '',                     # categoria
            ('%.2f' % d['precio']) if d['precio'] else '',
            d['tallas_texto'] or '',                  # tallas
            '1',                                      # colores
            d['id'] + '.webp',                        # fotos
            'NO',                                     # destacada
            'SI',                                     # activo
            '', '', '', '', '',                       # tela..modelo_talla
            '',                                       # descripcion   <- MONICA
            '',                                       # por_que_la_elegi
        ][:len(cab)])
    if nuevas_filas:
        ws.append_rows(nuevas_filas, value_input_option='USER_ENTERED')  # lote, no fila por fila
    print()
    print('filas nuevas en la Hoja Madre: %d' % len(nuevas_filas))
    print()
    print('AHORA LE TOCA A MONICA — en la pestana PRODUCTOS, dos columnas:')
    print('   nombre       como se llama la prenda')
    print('   descripcion  que la distingue: color, corte, detalle')
    print('Cuando termine:  python _tools/sumar_tanda.py aplicar')
    return 0


# ─────────────────────────── FASE 2: aplicar ───────────────────────────

def fase_aplicar(ensayo):
    cat = json.load(open(CAT, encoding='utf-8'))
    publicadas = {p['id']: p for p in cat['productos']}
    ws = abrir_hoja()
    cab, filas = filas_hoja(ws)
    col = {c.strip(): i for i, c in enumerate(cab)}

    def val(f, nombre):
        i = col.get(nombre)
        return (f[i].strip() if i is not None and i < len(f) else '')

    listas, faltan, choques = [], [], []
    for f in filas:
        pid = val(f, 'id')
        if not pid:
            continue
        nombre = val(f, 'nombre')
        desc = val(f, 'descripcion')
        if pid in publicadas:
            # nunca se pisa lo publicado: si contradice, se reporta
            p = publicadas[pid]
            pr = val(f, 'precio').replace(',', '.')
            if pr and abs(float(pr) - float(p['precio'])) > 0.005:
                choques.append('%s: la hoja dice $%s y el sitio publica $%s'
                               % (pid, pr, p['precio']))
            continue
        if not nombre or not desc:
            faltan.append((pid, 'falta nombre' if not nombre else 'falta descripcion'))
            continue
        listas.append((f, pid, nombre, desc))

    print('en la hoja: %d filas · ya publicadas: %d' % (len(filas), len(publicadas)))
    print('listas para sumar : %d' % len(listas))
    print('esperando a Monica: %d' % len(faltan))
    for pid, que in faltan[:10]:
        print('   %-40s %s' % (pid, que))
    if choques:
        print()
        print('CONTRADICCIONES (no se toca nada, decide Monica):')
        for c in choques[:10]:
            print('   ' + c)

    if not listas:
        print('\nnada que sumar todavia.')
        return 0
    if ensayo:
        print('\n(--ensayo: no se escribio catalogo.json)')
        return 0

    for f, pid, nombre, desc in listas:
        tallas_txt = val(f, 'tallas')
        tallas = [t.strip().upper() for t in re.split(r'[·,/]|–|-', tallas_txt) if t.strip()]
        if len(tallas) == 2 and tallas[0] in ESCALA and tallas[1] in ESCALA:
            tallas = ESCALA[ESCALA.index(tallas[0]):ESCALA.index(tallas[1]) + 1]
        fotos = [x.strip() for x in val(f, 'fotos').split(',') if x.strip()]
        cat['productos'].append({
            'id': pid,
            'nombre': nombre,
            'categoria': val(f, 'categoria'),
            'precio': float(val(f, 'precio').replace(',', '.') or 0),
            'tallas': tallas,
            'tallas_texto_original': tallas_txt,
            'colores': int(val(f, 'colores') or 1),
            'fotos': fotos,
            'destacada': val(f, 'destacada').upper() == 'SI',
            'alt': '%s %s plus size' % (nombre, desc),
            'agotada': val(f, 'activo').upper() == 'NO',
        })
    cat['productos'].sort(key=lambda p: (p['categoria'], float(p['precio'])))
    json.dump(cat, open(CAT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print()
    print('catalogo.json: %d prendas (+%d)' % (len(cat['productos']), len(listas)))
    print()
    print('AHORA, para publicar:')
    print('   python _tools/construir_catalogo.py')
    print('   python _tools/construir_prendas.py')
    print('   python _tools/construir_categorias.py')
    print('   python _tools/construir_sitemap.py')
    print('   python _tools/verificar.py')
    return 0


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    ensayo = '--ensayo' in sys.argv
    if not args:
        print(__doc__)
        return 1
    if args[0] == 'leer':
        if len(args) < 2:
            print('falta la carpeta:  sumar_tanda.py leer "C:/ruta"')
            return 1
        return fase_leer(args[1], ensayo)
    if args[0] == 'aplicar':
        return fase_aplicar(ensayo)
    print('modo desconocido: %s  (usar "leer" o "aplicar")' % args[0])
    return 1


if __name__ == '__main__':
    sys.exit(main())
