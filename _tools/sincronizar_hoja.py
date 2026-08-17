# -*- coding: utf-8 -*-
"""Baja la Hoja Madre de BOLEM y la deja como JSON para construir el sitio v2.

LA HOJA MANDA. El JSON es una copia de trabajo, no una fuente: se sobrescribe
entero en cada corrida. Nadie edita el JSON a mano.

Reglas de lectura aplicadas (rules/excel-writes.md), no por gusto:
  - get_all_values(), NUNCA get_all_records(): con locale es, un precio vuelve
    como "$1.100,00" y un parser ingenuo lo infla x100.
  - normalizacion europea de numeros: si termina en ,dd -> quitar puntos de
    miles y cambiar la coma por punto.
  - fechas con parser tolerante a tres formatos (ISO, d-mmm, DD/MM), nunca
    filtrando por substring.
  - campo vacio se queda VACIO. No se rellena con un valor por defecto: el
    sitio decide no mostrar la seccion, que es distinto de mostrarla mal.

Uso:
    python _tools/sincronizar_hoja.py            (baja y escribe)
    python _tools/sincronizar_hoja.py --revisar  (baja y solo reporta)
"""
import io, os, sys, json, re, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(ROOT, 'v2', '_data', 'bolem.json')
HOJA_ID = '1-fow67oGgzEw4OM2Pq_gu2sus-gl_kTHCfuZYobwWgQ'

PESTANAS = ('PRODUCTOS', 'MEDIDAS', 'CLIENTAS', 'COMPRAS', 'RESENAS', 'ENCUESTA')


# ------------------------------------------------------------------ numeros
def num(v):
    """'$1.100,50' -> 1100.5   ·  '25.5' -> 25.5  ·  '' -> None"""
    if v is None:
        return None
    s = str(v).strip().replace('$', '').replace(' ', '').replace('\xa0', '')
    if not s:
        return None
    if re.search(r',\d{2}$', s):          # formato europeo: 1.100,50
        s = s.replace('.', '').replace(',', '.')
    else:
        s = s.replace(',', '')            # 1,100.50 -> 1100.50
    try:
        return float(s)
    except ValueError:
        return None


def entero(v, defecto=None):
    n = num(v)
    return int(n) if n is not None else defecto


# ------------------------------------------------------------------ fechas
MESES = {'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6, 'jul': 7,
         'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12,
         'jan': 1, 'apr': 4, 'aug': 8, 'dec': 12}


def fecha(v):
    """Devuelve ISO o None. Tolera ISO, 12-jun-2026 y DD/MM/AAAA."""
    if not v:
        return None
    s = str(v).strip()
    m = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})', s)
    if m:
        try:
            return datetime.date(*map(int, m.groups())).isoformat()
        except ValueError:
            return None
    m = re.match(r'^(\d{1,2})-([a-zA-Zá]{3})\.?-(\d{4})$', s)
    if m and m.group(2)[:3].lower() in MESES:
        try:
            return datetime.date(int(m.group(3)), MESES[m.group(2)[:3].lower()],
                                 int(m.group(1))).isoformat()
        except ValueError:
            return None
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', s)
    if m:
        d_, mo, y = map(int, m.groups())
        try:
            return datetime.date(y, mo, d_).isoformat()
        except ValueError:
            return None
    return None


def si(v):
    return str(v).strip().upper() in ('SI', 'SÍ', 'S', 'YES', 'TRUE', 'X', '1')


def lista(v):
    return [x.strip() for x in str(v or '').split(',') if x.strip()]


def txt(v):
    s = str(v or '').strip()
    return s or None


# ------------------------------------------------------------------ bajada
def bajar():
    import gspread
    gc = gspread.oauth()
    sh = gc.open_by_key(HOJA_ID)
    crudo = {}
    for nombre in PESTANAS:
        try:
            ws = sh.worksheet(nombre)
        except Exception:
            print('  aviso: falta la pestana %s' % nombre)
            crudo[nombre] = []
            continue
        vals = ws.get_all_values()          # NUNCA get_all_records
        if not vals:
            crudo[nombre] = []
            continue
        cab = [c.strip() for c in vals[0]]
        filas = []
        for fila in vals[1:]:
            fila = fila + [''] * (len(cab) - len(fila))
            d = dict(zip(cab, fila))
            if any(str(x).strip() for x in fila):
                filas.append(d)
        crudo[nombre] = filas
        print('  %-9s %3d filas' % (nombre, len(filas)))
    return crudo


# ------------------------------------------------------------------ armado
def armar(crudo):
    avisos = []

    # --- medidas indexadas por producto ---
    medidas = {}
    for m in crudo['MEDIDAS']:
        pid = txt(m.get('id_producto'))
        talla = txt(m.get('talla'))
        if not pid or not talla:
            continue
        fila = {k: num(m.get(k)) for k in ('busto_cm', 'cintura_cm', 'cadera_cm', 'largo_cm')}
        if any(v is not None for v in fila.values()):
            fila['talla'] = talla
            medidas.setdefault(pid, []).append(fila)

    # --- resenas publicables ---
    resenas = {}
    for r in crudo['RESENAS']:
        pid = txt(r.get('id_producto'))
        if not pid:
            continue
        # SIN un SI explicito NO se publica, aunque la resena sea buena.
        if not si(r.get('permiso_publicar')) or not si(r.get('publicada')):
            continue
        est = num(r.get('estrellas'))
        if est is None or not (1 <= est <= 5):
            avisos.append('resena de %s sin estrellas validas: se ignora' % pid)
            continue
        resenas.setdefault(pid, []).append({
            'fecha': fecha(r.get('fecha')),
            'estrellas': int(est),
            'titulo': txt(r.get('titulo')),
            'texto': txt(r.get('texto')),
            'calce_real': txt(r.get('calce_real')),
            'talla_pedida': txt(r.get('talla_pedida')),
            'autora': txt(r.get('nombre_a_mostrar')) or 'Clienta BOLEM',
            'verificada': si(r.get('verificada')),
        })

    # --- productos ---
    productos = []
    for p in crudo['PRODUCTOS']:
        pid = txt(p.get('id'))
        if not pid:
            continue
        if not si(p.get('activo')):
            continue
        precio = num(p.get('precio'))
        if precio is None:
            avisos.append('%s sin precio: NO se publica' % pid)
            continue
        fotos = lista(p.get('fotos'))
        if not fotos:
            avisos.append('%s sin fotos: NO se publica' % pid)
            continue
        tallas = lista(p.get('tallas'))
        rs = resenas.get(pid, [])
        prod = {
            'id': pid,
            'nombre': txt(p.get('nombre')) or pid,
            'categoria': txt(p.get('categoria')) or 'otro',
            'precio': precio,
            'tallas': tallas,
            'colores': entero(p.get('colores'), 1),
            'fotos': fotos,
            'destacada': si(p.get('destacada')),
            # --- lo que solo Monica sabe. None = el sitio NO muestra nada ---
            'tela': txt(p.get('tela')),
            'cuidado': txt(p.get('cuidado')),
            'calce': txt(p.get('calce')),
            'modelo_altura': txt(p.get('modelo_altura')),
            'modelo_talla': txt(p.get('modelo_talla')),
            'descripcion': txt(p.get('descripcion')),
            'por_que_la_elegi': txt(p.get('por_que_la_elegi')),
            'medidas': sorted(medidas.get(pid, []),
                              key=lambda m: tallas.index(m['talla'])
                              if m['talla'] in tallas else 99),
            'resenas': sorted(rs, key=lambda r: r['fecha'] or '', reverse=True),
        }
        if rs:
            prod['rating'] = round(sum(r['estrellas'] for r in rs) / len(rs), 2)
            prod['n_resenas'] = len(rs)
        productos.append(prod)

    # --- clientas y compras: solo agregados, nunca datos personales al sitio ---
    compras = []
    for c in crudo['COMPRAS']:
        f = fecha(c.get('fecha'))
        pr = num(c.get('precio'))
        if f and pr is not None:
            compras.append({'fecha': f, 'id_clienta': txt(c.get('id_clienta')),
                            'id_producto': txt(c.get('id_producto')),
                            'talla': txt(c.get('talla')), 'precio': pr})

    total_r = sum(len(p.get('resenas', [])) for p in productos)
    datos = {
        '_nota': ('Copia de trabajo de la Hoja Madre. NO editar a mano: se '
                  'sobrescribe entera cada vez que corre sincronizar_hoja.py. '
                  'La fuente es la hoja.'),
        '_hoja': HOJA_ID,
        'productos': productos,
        'resumen': {
            'n_productos': len(productos),
            'n_resenas': total_r,
            'n_con_medidas': sum(1 for p in productos if p['medidas']),
            'n_con_tela': sum(1 for p in productos if p['tela']),
            'n_con_calce': sum(1 for p in productos if p['calce']),
            'n_con_modelo': sum(1 for p in productos if p['modelo_altura']),
            'n_clientas': len(crudo['CLIENTAS']),
            'n_compras': len(compras),
            'precio_min': min((p['precio'] for p in productos), default=None),
            'precio_max': max((p['precio'] for p in productos), default=None),
        },
    }
    return datos, avisos


def main(revisar):
    print('bajando la Hoja Madre...')
    crudo = bajar()
    datos, avisos = armar(crudo)
    r = datos['resumen']

    print('\n--- LO QUE SE PUBLICA ---')
    print('  productos activos      %d' % r['n_productos'])
    print('  precios                $%s a $%s' % (r['precio_min'], r['precio_max']))
    print('  resenas publicables    %d' % r['n_resenas'])

    print('\n--- LO QUE FALTA DE MONICA (el sitio deja el hueco, no lo inventa) ---')
    n = r['n_productos'] or 1
    for etiqueta, k in (('medidas en plano', 'n_con_medidas'), ('tela', 'n_con_tela'),
                        ('veredicto de calce', 'n_con_calce'),
                        ('altura/talla de la modelo', 'n_con_modelo')):
        print('  %-26s %2d de %d  (%d%%)' % (etiqueta, r[k], r['n_productos'],
                                             100 * r[k] // n))

    if avisos:
        print('\n--- AVISOS ---')
        for a in avisos[:20]:
            print('  ! ' + a)

    if revisar:
        print('\n(--revisar: no se escribio nada)')
        return 0
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    json.dump(datos, open(DESTINO, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\nescrito: %s' % os.path.relpath(DESTINO, ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main('--revisar' in sys.argv))
