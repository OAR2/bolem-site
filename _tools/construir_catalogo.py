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
SITIO = "https://bolemsv.com"

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
# Las dos bandas del home. El criterio es editorial y no cambia: arriba lo que
# se lleva puesto completo (vestidos, conjuntos, pantalones), abajo lo que se
# combina (blusas). Eso las mantiene parejas solo, porque el catalogo crece
# parejo por los dos lados.
#
# Antes esto era una lista de ids escrita a mano, y se pudria cada vez que
# entraba un producto: al pasar de 33 a 49 prendas quedo en 17 contra 33, o sea
# las dos bandas girando a distinta velocidad. Ahora es una REGLA; la lista de
# abajo solo dice que va PRIMERO dentro de la banda 1, no quien pertenece.
BANDA_1_CATEGORIAS = ("vestido", "conjunto", "pantalon")
BANDA_1_PRIMERO = ["vestido-mangas-globo", "vestido-maxi-smocked", "vestido-cobalto",
                   "jeans-flare", "conjunto-blanco-palazzo", "vestido-batik",
                   "conjunto-negro-satinado", "vestido-eventos-sage",
                   "conjunto-burdeos", "vestido-midi-algodon", "pantalon-lino",
                   "conjunto-chaleco-short", "vestido-broderie-rojo"]


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


def wa_apartar(nombre, agotada=False):
    if agotada:
        return "https://wa.me/%s?text=%s" % (
            WA, quote("Hola, vi que el %s aparece agotado. Me avisan cuando vuelva?" % nombre))
    return "https://wa.me/%s?text=%s" % (
        WA, quote("Hola, quiero apartar el %s. Mi talla es: ____ y lo quiero en color: " % nombre))


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
        hay = disponible(p)
        agot_clase = '' if hay else ' product-card--agotada'
        agot_cinta = '' if hay else (
            '          <span class="product-agotada">Agotada</span>\n')
        agot_cta = 'Apartar' if hay else 'Avisame cuando vuelva'
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
            '      <div class="product-card%s%s" data-category="%s" data-id="%s" data-images="%s" '
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
            '%s'
            '        </div>\n'
            '        <div class="product-info">\n'
            '          <h3 class="product-name"><a href="../prendas/%s" class="product-link">%s</a></h3>\n'
            '          <div class="product-meta">\n'
            '            <span class="product-sizes">%s</span>\n'
            '            <span class="product-price">%s</span>\n'
            '          </div>\n'
            '          <a href="%s" class="product-cta" target="_blank" rel="noopener">%s</a>\n'
            '        </div>\n'
            '      </div>\n'
            % (grande, agot_clase, p["categoria"], p["id"], imgs, p["nombre"],
               precio_txt(p["precio"]),
               b0, b0, b0, b0, tam, p["alt"], onerr, alt2, agot_cinta,
               p["id"], p["nombre"], tallas_txt(p, escala), precio_txt(p["precio"]),
               wa_apartar(p["nombre"], not disponible(p)), agot_cta))
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
    # Banda 1 = lo que se lleva puesto completo. Banda 2 = lo que se combina.
    # BANDA_1_PRIMERO solo fija el orden de arranque; la pertenencia sale de la
    # categoria, asi que las bandas se mantienen parejas solas al crecer.
    de_banda1 = [p["id"] for p in prods if p["categoria"] in BANDA_1_CATEGORIAS]
    orden1 = ([i for i in BANDA_1_PRIMERO if i in porid and i in de_banda1] +
              [i for i in de_banda1 if i not in BANDA_1_PRIMERO])
    orden2 = [p["id"] for p in prods if p["id"] not in orden1]

    # Las dos filas comparten la duracion de animacion del CSS. Si miden
    # distinto, se mueven a distinta velocidad y se nota. La fila de arriba
    # lleva ademas la tarjeta que va a la coleccion, asi que cuenta una mas.
    largo1, largo2 = len(orden1) + 1, len(orden2)
    if abs(largo1 - largo2) > 2:
        print("  AVISO: las bandas del home quedaron desparejas (%d vs %d tarjetas)."
              % (largo1, largo2))
        print("         Van a girar a distinta velocidad. Se empareja moviendo una")
        print("         categoria entre BANDA_1_CATEGORIAS y el resto.")
    elif largo1 != largo2:
        print("  bandas del home: %d vs %d tarjetas (diferencia tolerable)"
              % (largo1, largo2))

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


def itemlist_jsonld(prods, cats):
    """El ItemList de la coleccion: lo que lee Google Shopping.

    Estaba escrito a mano y fuera del constructor, asi que se quedo en 33
    productos mientras la pagina ya mostraba 49 — justo el bloque que no puede
    mentir. Ahora se deriva igual que todo lo demas.

    Cambio de fondo: `offers.url` apuntaba a wa.me para los 33. Un Offer tiene
    que apuntar a la pagina donde se ve ESE producto; wa.me es un chat, no una
    ficha. Por eso Merchant Center era inviable. Ahora apunta a /prendas/<id>.
    """
    items = []
    for i, p in enumerate(prods, 1):
        cat = cats.get(p["categoria"], {}).get("etiqueta_larga", p["categoria"])
        url = "%s/prendas/%s" % (SITIO, p["id"])
        color = " en %d colores." % p["colores"] if p.get("colores", 1) > 1 else ""
        items.append({
            "@type": "Product",
            "position": i,
            "name": p["nombre"],
            "url": url,
            "image": "%s/assets/productos/%s" % (SITIO, p["fotos"][0]),
            "description": "%s plus size, tallas %s.%s" % (
                p["nombre"], p["tallas_texto_original"], color),
            "sku": p["id"],
            "category": cat,
            "brand": {"@type": "Brand", "@id": SITIO + "/#marca-bolem", "name": "BOLEM"},
            "size": p["tallas"],
            "offers": {
                "@type": "Offer",
                "url": url,
                "price": "%.2f" % float(p["precio"]),
                "priceCurrency": "USD",
                "availability": ("https://schema.org/InStock" if disponible(p)
                                 else "https://schema.org/OutOfStock"),
                "itemCondition": "https://schema.org/NewCondition",
                "seller": {"@type": "ClothingStore", "@id": SITIO + "/#bolem", "name": "BOLEM"},
                "shippingDetails": {
                    "@type": "OfferShippingDetails",
                    "shippingRate": {"@type": "MonetaryAmount", "value": "5.00", "currency": "USD"},
                    "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "SV"},
                    "deliveryTime": {"@type": "ShippingDeliveryTime",
                                     "transitTime": {"@type": "QuantitativeValue", "minValue": 1,
                                                     "maxValue": 3, "unitCode": "DAY"}},
                },
                "hasMerchantReturnPolicy": {
                    "@type": "MerchantReturnPolicy",
                    "applicableCountry": "SV",
                    "returnPolicyCategory":
                        "https://schema.org/MerchantReturnFiniteReturnWindow",
                    "merchantReturnDays": 2,
                    "returnMethod": "https://schema.org/ReturnByMail",
                    "returnFees": "https://schema.org/FreeReturn",
                },
            },
        })
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Colección BOLEM 2026",
        "numberOfItems": len(prods),
        "itemListElement": items,
    }, ensure_ascii=False, indent=2)


def poner_itemlist(html, prods, cats):
    """Reemplaza el bloque JSON-LD que contiene el ItemList, entero."""
    patron = re.compile(
        r'(<script[^>]*type="application/ld\+json"[^>]*>\s*)(\{.*?"@type"\s*:\s*"ItemList".*?\})(\s*</script>)',
        re.S)
    m = patron.search(html)
    assert m, "coleccion/index.html: no se encontro el bloque ItemList"
    return patron.sub(lambda mm: mm.group(1) + itemlist_jsonld(prods, cats) + mm.group(3),
                      html, count=1)


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
    col = poner_itemlist(col, prods, d.get("categorias", {}))
    col = re.sub(r'"numberOfItems"\s*:\s*\d+', '"numberOfItems": %d' % len(prods), col)
    # La cuenta de prendas y el rango de tallas estaban escritos a mano en SEIS
    # lugares de esta pagina (titulo, descripcion, og:title, og:description,
    # JSON-LD y el H1). Al pasar de 33 a 49 el H1 se quedo mintiendo porque el
    # parche viejo buscaba un <h2> que el arreglo de SEO ya habia vuelto <h1>.
    # Ahora se patchea por frase y sin depender de la etiqueta.
    col = re.sub(r'\b\d+ (estilos|Estilos)\b', lambda m: '%d %s' % (len(prods), m.group(1)), col)
    # El rango que la marca anuncia se declara a mano en catalogo.json, NO se
    # deriva de escala_tallas: la L existe en 2 de 49 prendas que cruzan hacia
    # abajo y no es el rango del catalogo. Derivarlo cambio el reclamo de marca
    # a "L a 4XL" sin que nadie lo decidiera.
    rango_pub = d.get("rango_publicado")
    if rango_pub:
        col = re.sub(r'([Tt]allas )[A-Z0-9]{1,3} a [A-Z0-9]{1,3}( seg)',
                     lambda m: m.group(1) + rango_pub + m.group(2), col)
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
        # Cada linea lleva AHORA la direccion de su propia ficha. Un motor de IA
        # que cite una prenda puede mandar a esa pagina y no al catalogo entero.
        lineas = ["- %s (%s) %s, tallas %s — %s/prendas/%s"
                  % (p["nombre"], ETIQUETA_CAT[p["categoria"]], precio_txt(p["precio"]),
                     rango_txt(p["tallas"], escala), SITIO, p["id"])
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

        # Los conteos escritos a mano en el texto de alrededor. Se quedaban en
        # 33 mientras el bloque de abajo ya decia 49 — el archivo se contradecia
        # a si mismo, y esto es justo lo que un motor de IA cita como hecho.
        precios = sorted(float(p["precio"]) for p in prods)
        rango_precio = "$%s a $%s USD" % (precio_txt(precios[0]).lstrip("$"),
                                          precio_txt(precios[-1]).lstrip("$"))
        llms = re.sub(r'Coleccion 2026: \d+ estilos',
                      'Coleccion 2026: %d estilos' % len(prods), llms)
        llms = re.sub(r'Precios de \$[\d.]+ a \$[\d.]+ USD',
                      'Precios de %s' % rango_precio, llms)
        llms = re.sub(r'## Catalogo \(\d+ piezas\)',
                      '## Catalogo (%d piezas)' % len(prods), llms)
        if d.get("rango_publicado"):
            llms = re.sub(r'Tallas [A-Z0-9]{1,3} a [A-Z0-9]{1,3} segun la prenda',
                          'Tallas %s segun la prenda' % d["rango_publicado"], llms)
        # La lista por categoria que vivia escrita a mano arriba: se deriva.
        por_cat = []
        for k in ("vestido", "blusa", "pantalon", "conjunto"):
            g = [p for p in prods if p["categoria"] == k]
            if not g:
                continue
            piezas = "; ".join(
                "%s %s (tallas %s%s)" % (p["nombre"], precio_txt(p["precio"]),
                                         rango_txt(p["tallas"], escala),
                                         (", %d colores" % p["colores"])
                                         if p.get("colores", 1) > 1 else "")
                for p in g)
            por_cat.append("- %s (%d): %s" % (ETIQUETA_CAT[k], len(g), piezas))
        llms = re.sub(
            r'(## Productos \(catalogo completo, precios reales\)\n\n).*?(\n\n## Diferenciadores)',
            lambda m: m.group(1) + "\n".join(por_cat) + m.group(2),
            llms, flags=re.S)
        # el articulo nuevo entra al indice editorial
        art = "- Diferencia entre talla XL y 1XL: %s/blog/tallas-xl-1xl-plus-size" % SITIO
        if art not in llms:
            llms = llms.replace(
                "- Guia de tallas plus size: %s/blog/guia-tallas-plus-size" % SITIO,
                art + "\n- Guia de tallas plus size: %s/blog/guia-tallas-plus-size" % SITIO)
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
