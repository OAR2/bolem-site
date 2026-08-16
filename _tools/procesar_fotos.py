# -*- coding: utf-8 -*-
"""Procesa fotos nuevas al formato que el sitio necesita.

Cada prenda vive en el sitio como TRES archivos:
    nombre.webp       1200 de ancho  (la grande, para el visor de fotos)
    nombre-800.webp    800 de ancho  (pantallas densas)
    nombre-480.webp    480 de ancho  (las bandas y las tarjetas)

El navegador elige sola cual bajar segun el ancho real en pantalla. Sin las
tres, una banda de 300px terminaria descargando la de 1200 — cuatro veces mas
peso del necesario, en celulares con datos.

Todas las fotos del sitio son 2:3 (1200x1800). Lo que no venga en esa
proporcion se recorta AL CENTRO, o las bandas quedan desparejas. Si el recorte
es grande, avisa: puede estar cortando cabezas o pies.

Uso:
    python _tools/procesar_fotos.py "C:/ruta/carpeta-de-monica"
    python _tools/procesar_fotos.py "C:/ruta" --sobrescribir
    python _tools/procesar_fotos.py "C:/ruta" --ensayo      (no escribe nada)
"""
import io, sys, os, re, unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from PIL import Image, ImageOps
except ImportError:
    print("Falta Pillow.  Instalar con:  pip install pillow")
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(ROOT, "assets", "productos")
ANCHOS = [1200, 800, 480]
PROPORCION = 2 / 3          # ancho / alto
CALIDAD = 82
ENTRADAS = ('.jpg', '.jpeg', '.png', '.webp', '.heic', '.tif', '.tiff', '.bmp')


def slug(nombre):
    """'Vestido Maxi Ámbar 01.jpg' -> 'vestido-maxi-ambar-01'"""
    base = os.path.splitext(os.path.basename(nombre))[0]
    base = unicodedata.normalize('NFKD', base).encode('ascii', 'ignore').decode()
    base = base.lower()
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-')
    return re.sub(r'-{2,}', '-', base)


def recortar_2x3(im):
    """Recorta al centro a proporcion 2:3. Devuelve (imagen, % descartado)."""
    a, h = im.size
    objetivo = PROPORCION
    actual = a / h
    if abs(actual - objetivo) < 0.005:
        return im, 0.0
    if actual > objetivo:                 # muy ancha: se recorta a los lados
        nueva_a = int(round(h * objetivo))
        x = (a - nueva_a) // 2
        caja = (x, 0, x + nueva_a, h)
        descartado = 1 - nueva_a / a
    else:                                 # muy alta: se recorta arriba y abajo
        nueva_h = int(round(a / objetivo))
        y = (h - nueva_h) // 2
        caja = (0, y, a, y + nueva_h)
        descartado = 1 - nueva_h / h
    return im.crop(caja), descartado * 100


def procesar(origen, sobrescribir, ensayo):
    if not os.path.isdir(origen):
        print("No existe la carpeta:", origen)
        return 1
    os.makedirs(DESTINO, exist_ok=True)

    archivos = sorted(f for f in os.listdir(origen)
                      if f.lower().endswith(ENTRADAS))
    if not archivos:
        print("No hay imagenes en", origen)
        return 1

    print("origen : %s" % origen)
    print("destino: %s" % DESTINO)
    print("fotos  : %d%s\n" % (len(archivos), "   (ENSAYO: no se escribe nada)" if ensayo else ""))

    hechas = saltadas = 0
    avisos = []
    for f in archivos:
        s = slug(f)
        final = os.path.join(DESTINO, s + ".webp")
        if os.path.exists(final) and not sobrescribir:
            print("  SALTA   %-38s ya existe (usar --sobrescribir)" % (s + ".webp"))
            saltadas += 1
            continue
        try:
            im = Image.open(os.path.join(origen, f))
            im = ImageOps.exif_transpose(im)      # respeta la rotacion del telefono
            im = im.convert("RGB")
        except Exception as e:
            avisos.append("%s: no se pudo abrir (%s)" % (f, e))
            continue

        original = im.size
        im, descartado = recortar_2x3(im)
        if descartado > 12:
            avisos.append("%s: se recorto %.0f%% para llegar a 2:3 — revisar que no corte cabeza o pies"
                          % (f, descartado))
        if im.size[0] < 480:
            avisos.append("%s: solo %dpx de ancho; el sitio necesita 1200 para el visor"
                          % (f, im.size[0]))

        for ancho in ANCHOS:
            alto = int(round(ancho / PROPORCION))
            sufijo = "" if ancho == 1200 else "-%d" % ancho
            ruta = os.path.join(DESTINO, "%s%s.webp" % (s, sufijo))
            if ensayo:
                continue
            im.resize((ancho, alto), Image.LANCZOS).save(
                ruta, "WEBP", quality=CALIDAD, method=6)
        peso = os.path.getsize(final) // 1024 if (not ensayo and os.path.exists(final)) else 0
        print("  OK      %-38s %dx%d -> 1200/800/480%s"
              % (s + ".webp", original[0], original[1],
                 ("  (%d KB la grande)" % peso) if peso else ""))
        hechas += 1

    print("\nprocesadas: %d   saltadas: %d" % (hechas, saltadas))
    if avisos:
        print("\n--- REVISAR ---")
        for a in avisos:
            print("  " + a)
    if hechas and not ensayo:
        print("\nSiguiente paso: sumar las fotos al producto en _data/catalogo.json")
        print("y correr  python _tools/construir_catalogo.py")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    sys.exit(procesar(args[0],
                      "--sobrescribir" in sys.argv,
                      "--ensayo" in sys.argv))
