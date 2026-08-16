# -*- coding: utf-8 -*-
"""Reconstruye TODO lo que se deriva del catalogo, desde _data/catalogo.json

Antes, los datos de cada prenda vivian repetidos en unos diez lugares: las
tarjetas de la coleccion, su JSON-LD, los conteos de los botones de filtro, los
azulejos de categoria de las dos paginas, las dos bandas del home y el llms.txt.
Agregar un producto obligaba a tocarlos todos, y el que se olvidara quedaba
mintiendo. Peor: al aplicar el redisenio el home se quedo con SUS PROPIAS copias
de las listas de fotos, asi que ya no se enteraba si cambiaba la coleccion.

Ahora se edita el JSON y se corre esto.

Cada region generada va entre marcas HTML (<!-- BOLEM:X --> ... <!-- /BOLEM:X -->).
Solo se reemplaza lo que hay entre marcas: todo lo escrito a mano alrededor
queda intacto. La primera corrida coloca las marcas sola.

Uso:
    python _tools/construir_catalogo.py            (reconstruye)
    python _tools/construir_catalogo.py --revisar  (solo dice que cambiaria)
"""
import io, sys, os, json, re, difflib
from urllib.parse import quote

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(ROOT, "_data", "catalogo.json")
WA = "50368590899"

ETIQUETA_CAT = {
    "vestido": "Vestidos",
    "blusa": "Blusas",
    "pantalon": "Jeans y Pantalones",
    "conjunto": "Conjuntos",
}
# foto de portada de cada azulejo de categoria (decision editorial, no derivable)
PORTADA_CAT = {
    "vestido": "vestido-verano-rojo.webp",
    "blusa": "chaleco-elegante-marfil.webp",
    "pantalon": "pantalon-lino.webp",
    "conjunto": "conjunto-burdeos.webp",
}
# orden de las dos bandas del home (editorial: arriba lo que se lleva puesto
# completo, abajo lo que se combina). Los que no esten listados van al final.
BANDA_1 = ["vestido-mangas-globo", "vestido-maxi-smocked", "vestido-cobalto", "jeans-flare",
           "conjunto-blanco-palazzo", "vestido-batik", "conjunto-negro-satinado",
           "vestido-eventos-sage", "conjunto-burdeos", "vestido-midi-algodon",
           "pantalon-lino", "conjunto-chaleco-short", "vestido-broderie-rojo",
           "blusa-denim-peplum", "blusa-peplum-gingham", "blusa-off-shoulder"]


def cargar():
    d = json.load(open(DATOS, encoding="utf-8"))
    prods = d["productos"]
    porid = {p["id"]: p for p in prods}
    assert len(porid) == len(prods), "hay ids repetidos en catalogo.json"
    for p in prods:
        assert p["fotos"], "%s no tiene fotos" % p["id"]
        assert p["precio"] is not None, "%s no tiene precio" % p["id"]
        assert p["tallas"], "%s no tiene tallas" % p["id"]
        assert p["categoria"] in ETIQUETA_CAT, "%s: categoria desconocida '%s'" % (p["id"], p["categoria"])
    return d, prods, porid


def precio_txt(v):
    """74.5 -> '$74.50' ; 65.0 -> '$65'  (asi los muestra el sitio hoy)"""
    return "$%d" % v if float(v) == int(v) else "$%.2f" % v


def rango_txt(tallas, escala):
    if len(tallas) == 1:
        return tallas[0]
    return "%s–%s" % (tallas[0], tallas[-1])


def tallas_txt(p, escala):
    base = rango_txt(p["tallas"], escala)
    if p.get("colores", 1) and p["colores"] > 1:
        return "%s · %d colores" % (base, p["colores"])
    return base


def wa_apartar(nombre):
    return "https://wa.me/%s?text=%s" % (
        WA, quote("Hola, quiero apartar el %s. Mi talla es: ____ y lo quiero en color: " % nombre))


def base(foto):
    return re.sub(r'\.webp$', '', foto)


# ── generadores de cada region ───────────────────────────────────────────────

def tarjetas_coleccion(prods, escala, cats):
    """Emite, por categoria: separador -> tarjetas -> linea editorial.

    Los separadores y las lineas editoriales son texto escrito a mano (viven en
    catalogo.json, no se derivan). La primera version de este script los
    borraba: se rescataron del respaldo antes de que se perdieran."""
    fuera = []
    orden_cat = ["vestido", "blusa", "pantalon", "conjunto"]
    por_cat = {}
    for p in prods:
        por_cat.setdefault(p["categoria"], []).append(p)

    for k in orden_cat:
        grupo = por_cat.get(k, [])
        if not grupo:
            continue
        c = cats.get(k, {})
        fuera.append(
            '      <!-- %s (%d) -->\n'
            '      <div class="category-divider" data-category="%s">\n'
            '        <span class="category-divider-line"></span>\n'
            '        <span class="category-divider-label">%s</span>\n'
            '        <span class="category-divider-line"></span>\n'
            '      </div>\n' % (c.get("etiqueta_larga", k).upper(), len(grupo), k,
                                c.get("etiqueta", k)))
        fuera.append(tarjetas_de(grupo, escala))
        if c.get("editorial"):
            fuera.append(
                '      <div class="catalog-editorial" data-category="%s">\n'
                '        <span class="gold-line" aria-hidden="true"></span>\n'
                '        <p class="catalog-editorial-text">%s</p>\n'
                '      </div>\n' % (k, c["editorial"]))
    return "".join(fuera)


def tarjetas_de(prods, escala):
    fuera = []
    for p in prods:
        pre = "../assets/productos/"
        imgs = ",".join(pre + f for f in p["fotos"])
        grande = ' product-card--large' if p["destacada"] else ''
        tam = '(max-width: 1024px) 100vw, 66vw' if p["destacada"] else '(max-width: 1024px) 50vw, 33vw'
        b0 = pre + base(p["fotos"][0])
        onerr = ('onerror="var w=this.closest(&quot;.product-image-wrap&quot;); '
                 'if(w){w.classList.add(&quot;img-error&quot;);} this.style.display=&quot;none&quot;;"')
        alt2 = ""
        if len(p["fotos"]) > 1:
            b1 = pre + base(p["fotos"][1])
            alt2 = ('          <img src="%s.webp" srcset="%s-480.webp 480w, %s-800.webp 800w, %s.webp 1200w" '
                    'sizes="%s" alt="" aria-hidden="true" class="product-img product-img--alt" '
                    'width="600" height="900" loading="lazy">\n' % (b1, b1, b1, b1, tam))
        fuera.append(
            '      <div class="product-card%s" data-category="%s" data-id="%s" data-images="%s" '
            'tabindex="0" role="button" aria-label="Ver detalles de %s, ropa plus size — %s">\n'
            '        <div class="product-image-wrap">\n'
            '          <div class="product-placeholder">\n'
            '            <svg class="product-placeholder-icon" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1"><rect x="3" y="3" width="18" height="18" rx="2"/>'
            '<circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>\n'
            '            <span class="product-placeholder-text">Foto próximamente</span>\n'
            '          </div>\n'
            '          <img src="%s.webp" srcset="%s-480.webp 480w, %s-800.webp 800w, %s.webp 1200w" '
            'sizes="%s" alt="%s" class="product-img" width="600" height="900" loading="lazy" %s>\n'
            '%s'
            '        </div>\n'
            '        <div class="product-info">\n'
            '          <h3 class="product-name">%s</h3>\n'
            '          <div class="product-meta">\n'
            '            <span class="product-sizes">%s</span>\n'
            '            <span class="product-price">%s</span>\n'
            '          </div>\n'
            '          <a href="%s" class="product-cta" target="_blank" rel="noopener">Apartar</a>\n'
            '        </div>\n'
            '      </div>\n'
            % (grande, p["categoria"], p["id"], imgs, p["nombre"], precio_txt(p["precio"]),
               b0, b0, b0, b0, tam, p["alt"], onerr, alt2,
               p["nombre"], tallas_txt(p, escala), precio_txt(p["precio"]), wa_apartar(p["nombre"])))
    return "".join(fuera)


def botones_filtro(prods):
    c = {}
    for p in prods:
        c[p["categoria"]] = c.get(p["categoria"], 0) + 1
    s = ['      <button class="filter-btn active" data-filter="all">Todas (%d)</button>\n' % len(prods)]
    for k in ("vestido", "blusa", "pantalon", "conjunto"):
        s.append('      <button class="filter-btn" data-filter="%s">%s (%d)</button>\n'
                 % (k, ETIQUETA_CAT[k], c.get(k, 0)))
    return "".join(s)


def azulejos(prods, para_home, cats):
    c = {}
    for p in prods:
        c[p["categoria"]] = c.get(p["categoria"], 0) + 1
    pre = "assets/productos/" if para_home else "../assets/productos/"
    s = []
    for k in ("vestido", "blusa", "pantalon", "conjunto"):
        info = cats.get(k, {})
        b = pre + base(info.get("portada", PORTADA_CAT[k]))
        if para_home:
            s.append(
                '                <a href="coleccion/#%s" class="home-categoria">\n'
                '                    <img src="%s-480.webp"\n'
                '                         srcset="%s-480.webp 480w, %s-800.webp 800w"\n'
                '                         sizes="(min-width: 860px) 25vw, 50vw"\n'
                '                         alt="%s plus size &mdash; BOLEM El Salvador"\n'
                '                         width="600" height="750" loading="lazy" decoding="async">\n'
                '                    <span class="home-categoria__label">%s<small>%d estilos</small></span>\n'
                '                </a>\n' % (k, b, b, b, ETIQUETA_CAT[k], ETIQUETA_CAT[k], c.get(k, 0)))
        else:
            s.append(
                '      <a href="#catalogo" class="category-tile" data-filter-target="%s">\n'
                '        <img src="%s.webp" srcset="%s-480.webp 480w, %s-800.webp 800w, %s.webp 1200w" '
                'sizes="(max-width: 768px) 50vw, 25vw" alt="%s plus size BOLEM" loading="lazy" '
                'width="600" height="800">\n'
                '        <span class="category-tile-overlay"></span>\n'
                '        <span class="category-tile-label">%s<small>%d estilos</small></span>\n'
                '      </a>\n' % (k, b, b, b, b, ETIQUETA_CAT[k], ETIQUETA_CAT[k], c.get(k, 0)))
    return "".join(s)


def bandas_home(prods, porid, escala):
    orden1 = [i for i in BANDA_1 if i in porid]
    orden2 = [p["id"] for p in prods if p["id"] not in orden1]

    # Las dos filas comparten la duracion de animacion del CSS. Si miden
    # distinto, se mueven a distinta velocidad y se nota. La fila de arriba
    # lleva ademas la tarjeta que va a la coleccion, asi que cuenta una mas.
    largo1, largo2 = len(orden1) + 1, len(orden2)
    if largo1 != largo2:
        print("  AVISO: las bandas del home quedaron desparejas (%d vs %d tarjetas)."
              % (largo1, largo2))
        print("         Van a girar a distinta velocidad. Emparejarlas moviendo ids")
        print("         entre BANDA_1 y el resto, en este mismo archivo.")

    def tarjeta(pid, dup, prioritaria):
        p = porid[pid]
        b = "assets/productos/" + base(p["fotos"][0])
        extra = ' aria-hidden="true" tabindex="-1"' if dup else ''
        alt = '' if dup else '%s plus size &mdash; BOLEM El Salvador' % p["nombre"]
        carga = 'loading="eager"' if (prioritaria and not dup) else 'loading="eager" fetchpriority="low"'
        fotos = ",".join("assets/productos/" + f for f in p["fotos"])
        return (
            '                    <a href="coleccion/" class="lookbook-item" data-qv%s\n'
            '                       data-qv-nombre="%s" data-qv-precio="%s" data-qv-tallas="%s"\n'
            '                       data-qv-categoria="%s" data-qv-cta="%s"\n'
            '                       data-images="%s">\n'
            '                        <img src="%s-480.webp"\n'
            '                             srcset="%s-480.webp 480w, %s-800.webp 800w"\n'
            '                             sizes="(min-width: 768px) 300px, 60vw"\n'
            '                             alt="%s" width="600" height="800" decoding="async" %s>\n'
            '                        <div class="overlay">\n'
            '                            <span class="lookbook-item__name">%s</span>\n'
            '                        </div>\n'
            '                    </a>\n'
            % (extra, p["nombre"], precio_txt(p["precio"]), tallas_txt(p, escala),
               p["categoria"], wa_apartar(p["nombre"]), fotos, b, b, b, alt, carga, p["nombre"]))

    def puerta(dup, total):
        extra = ' aria-hidden="true" tabindex="-1"' if dup else ''
        return ('                    <a href="coleccion/" class="lookbook-item--todo"%s>\n'
                '                        <strong>Ver la colecci&oacute;n completa</strong>\n'
                '                        <span>%d piezas, con filtros y tallas</span>\n'
                '                    </a>\n' % (extra, total))

    def vuelta(orden, con_puerta, dup):
        s = "".join(tarjeta(i, dup, k < 6 and con_puerta) for k, i in enumerate(orden))
        return s + (puerta(dup, len(prods)) if con_puerta else "")

    return (
        '                <div class="home-lookbook__grid">\n'
        + vuelta(orden1, True, False) + vuelta(orden1, True, True) +
        '                </div>\n'
        '                <div class="home-lookbook__grid home-lookbook__grid--rev">\n'
        + vuelta(orden2, False, False) + vuelta(orden2, False, True) +
        '                </div>\n')


# ── colocar y reemplazar regiones ────────────────────────────────────────────

def region(texto, marca, contenido_nuevo, ancla_ini, ancla_fin, archivo):
    """Reemplaza entre <!-- BOLEM:marca --> y <!-- /BOLEM:marca -->.
    Si las marcas no estan, las coloca usando las anclas."""
    ini = "<!-- BOLEM:%s -->" % marca
    fin = "<!-- /BOLEM:%s -->" % marca
    if ini in texto and fin in texto:
        a = texto.index(ini) + len(ini)
        b = texto.index(fin)
        return texto[:a] + "\n" + contenido_nuevo + texto[b:], False
    # primera vez: colocar marcas
    assert ancla_ini in texto, "%s: no se encontro el ancla de inicio de %s" % (archivo, marca)
    a = texto.index(ancla_ini) + len(ancla_ini)
    resto = texto[a:]
    assert ancla_fin in resto, "%s: no se encontro el ancla de fin de %s" % (archivo, marca)
    b = a + resto.index(ancla_fin)
    return texto[:a] + "\n" + ini + "\n" + contenido_nuevo + fin + "\n" + texto[b:], True


def main():
    revisar = "--revisar" in sys.argv
    d, prods, porid = cargar()
    escala = d["escala_tallas"]
    cambios = []

    # ---------- coleccion ----------
    pc = os.path.join(ROOT, "coleccion", "index.html")
    col = original_col = open(pc, encoding="utf-8").read()
    col, nuevo1 = region(col, "TARJETAS", tarjetas_coleccion(prods, escala, d.get("categorias", {})),
                         '<div class="product-grid" data-reveal-stagger>', '\n    </div>', "coleccion")
    col, nuevo2 = region(col, "FILTROS", botones_filtro(prods),
                         '<div class="catalog-filters" data-reveal>', '\n    </div>', "coleccion")
    col, nuevo3 = region(col, "AZULEJOS", azulejos(prods, False, d.get("categorias", {})),
                         '<div class="category-tiles-inner" data-reveal-stagger>', '\n    </div>', "coleccion")
    col = re.sub(r'"numberOfItems"\s*:\s*\d+', '"numberOfItems": %d' % len(prods), col)
    # el titulo del catalogo tambien lleva el numero escrito
    col = re.sub(r'(<h2 class="catalog-title">)\d+( Estilos)', r'\g<1>%d\g<2>' % len(prods), col)
    if col != original_col:
        cambios.append(("coleccion/index.html", original_col, col))

    # ---------- home ----------
    ph = os.path.join(ROOT, "index.html")
    home = original_home = open(ph, encoding="utf-8").read()
    home, nuevo4 = region(home, "BANDAS", bandas_home(prods, porid, escala),
                          '<div class="home-lookbook__banda" role="group" aria-label="Piezas de la colección">',
                          '\n            </div>', "index")
    home, nuevo5 = region(home, "AZULEJOS", azulejos(prods, True, d.get("categorias", {})),
                          '<div class="home-categorias__grid">', '\n            </div>', "index")
    if home != original_home:
        cambios.append(("index.html", original_home, home))

    # ---------- llms.txt ----------
    pl = os.path.join(ROOT, "llms.txt")
    if os.path.exists(pl):
        llms = original_llms = open(pl, encoding="utf-8").read()
        lineas = ["- %s (%s) %s, tallas %s" % (p["nombre"], ETIQUETA_CAT[p["categoria"]],
                                               precio_txt(p["precio"]), rango_txt(p["tallas"], escala))
                  for p in prods]
        bloque = "\n".join(lineas) + "\n"
        ini, fin = "<!-- BOLEM:PRODUCTOS -->", "<!-- /BOLEM:PRODUCTOS -->"
        if ini in llms and fin in llms:
            a = llms.index(ini) + len(ini)
            b = llms.index(fin)
            llms = llms[:a] + "\n" + bloque + llms[b:]
        else:
            llms = llms.rstrip() + "\n\n## Catalogo (%d piezas)\n%s\n%s%s\n" % (
                len(prods), ini, bloque, fin)
        if llms != original_llms:
            cambios.append(("llms.txt", original_llms, llms))

    # ---------- reporte / escritura ----------
    print("productos en el catalogo: %d" % len(prods))
    c = {}
    for p in prods:
        c[p["categoria"]] = c.get(p["categoria"], 0) + 1
    print("  " + " · ".join("%s %d" % (ETIQUETA_CAT[k], v) for k, v in sorted(c.items())))

    if not cambios:
        print("\nnada que cambiar: el HTML ya coincide con el catalogo")
        return 0

    print("\narchivos que %s:" % ("cambiarian" if revisar else "cambian"))
    for nombre, viejo, nuevo in cambios:
        dif = list(difflib.unified_diff(viejo.split("\n"), nuevo.split("\n"), n=0))
        mas = sum(1 for l in dif if l.startswith("+") and not l.startswith("+++"))
        menos = sum(1 for l in dif if l.startswith("-") and not l.startswith("---"))
        print("  %-24s +%d / -%d lineas" % (nombre, mas, menos))
        if not revisar:
            open(os.path.join(ROOT, nombre.replace("/", os.sep)), "w", encoding="utf-8").write(nuevo)

    if revisar:
        print("\n(--revisar: no se escribio nada)")
    else:
        print("\nlisto. Verificar con: python _tools/servidor_preview.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
