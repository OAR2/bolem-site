# -*- coding: utf-8 -*-
"""Arreglos de presentacion en buscadores. Paso 5 del plan del 16-ago.

Nada de esto cambia lo que dice la marca: corrige COMO se presenta cada pagina
ante Google. Tres cosas, todas medidas antes de tocarlas:

1. EL H1 DE COLECCION. Decia "NUEVA COLECCION" — decorativo — mientras el
   encabezado con la frase que la gente busca ("33 Estilos de Ropa Plus Size —
   Tallas XL a 4XL") estaba de H2. El H1 es el titular del periodico y lo
   ocupaba algo que no dice de que trata la pagina. Se intercambian las
   etiquetas; el diseno no se mueve **porque ningun selector CSS del sitio
   depende del tag h1/h2** (verificado: todos son por clase).

2. DOS TITULOS QUE GOOGLE CORTA. Pasaban de 60 caracteres, asi que en los
   resultados salian con "...". Se acortan sin perder la palabra clave.

3. SEIS DESCRIPCIONES FUERA DE RANGO. Cuatro cortas (desperdician espacio que
   Google si muestra) y dos largas (se cortan). Se llevan a 120-160.
   Si `og:description` traia el MISMO texto que la descripcion, se actualiza
   tambien para que no se separen.

Regla de la casa: TODO o NADA. Si un texto esperado no aparece tal cual,
aborta sin escribir un solo archivo.

Uso:  python _tools/arreglos_seo.py          (aplica)
      python _tools/arreglos_seo.py --dry    (solo reporta)
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 1. jerarquia de encabezados ────────────────────────────────────────────
ENCABEZADOS = [
    ('coleccion/index.html',
     '<h1 class="hero-headline">',
     '<p class="hero-headline">'),
    ('coleccion/index.html',
     '</h1>\n      <p class="hero-subtitle"',
     '</p>\n      <p class="hero-subtitle"'),
    ('coleccion/index.html',
     '<h2 class="catalog-title">33 Estilos de Ropa Plus Size — Tallas XL a 4XL</h2>',
     '<h1 class="catalog-title">33 Estilos de Ropa Plus Size — Tallas XL a 4XL</h1>'),
    # "Guia de Tallas" a secas no dice para quien es. Un renglon, dato real.
    ('guia-de-tallas.html',
     '>Guía de Tallas</h1>',
     '>Guía de Tallas Plus Size</h1>'),
]

# ── 2. titulos que Google corta (>60) ──────────────────────────────────────
TITULOS = {
    'blog/guia-tallas-plus-size.html': (
        'Guía de Tallas Plus Size: Cómo Encontrar Tu Talla Perfecta | BOLEM',
        'Guía de Tallas Plus Size — Cómo Elegir la Tuya | BOLEM'),
    'blog/historia-bolem-moda-plus-size-el-salvador.html': (
        'Por Qué Creamos BOLEM: Moda Plus Size Hecha para la Mujer Salvadoreña',
        'Por Qué Creamos BOLEM — Moda Plus Size Salvadoreña'),
}

# ── 3. descripciones fuera de 120-160 ──────────────────────────────────────
DESCRIPCIONES = {
    'guia-de-tallas.html': (
        'Encontrá tu talla perfecta: guía de medidas para ropa plus size en El Salvador, tallas XL a 4XL según la prenda.',
        'Encontrá tu talla perfecta: cómo medirte paso a paso y tabla de medidas para ropa plus size en El Salvador, tallas XL a 4XL según la prenda.'),
    'terminos.html': (
        'Términos y condiciones de compra en BOLEM. Precios, envíos, cambios y jurisdicción. Moda plus size en El Salvador.',
        'Términos y condiciones de compra en BOLEM: precios, formas de pago, envíos a todo el país, cambios de talla y jurisdicción. Moda plus size en El Salvador.'),
    'privacidad.html': (
        'Política de privacidad de BOLEM. Cómo recopilamos, usamos y protegemos tu información personal.',
        'Política de privacidad de BOLEM: qué datos recopilamos cuando nos escribís por WhatsApp, cómo los usamos y cómo los protegemos. Moda plus size en El Salvador.'),
    'blog/index.html': (
        'Consejos de moda plus size en El Salvador, guías de tallas y tendencias. El blog de BOLEM — moda que abraza tu cuerpo.',
        'Consejos de moda plus size en El Salvador: guías de tallas, looks para clima cálido y tendencias curvy. El blog de BOLEM, tallas XL a 4XL.'),
    'blog/guia-tallas-plus-size.html': (
        'Guía tallas plus size con tabla de medidas BOLEM (XL a 4XL según la prenda). Aprendé a medirte correctamente y elegí tu talla perfecta. Asesoría personalizada por WhatsApp.',
        'Guía de tallas plus size con la tabla de medidas de BOLEM (XL a 4XL según la prenda). Aprendé a medirte bien y elegí tu talla con confianza.'),
    'blog/looks-plus-size-clima-calido.html': (
        'Outfits curvy para clima cálido: 5 looks plus size pensados para el calor salvadoreño. Piezas reales de BOLEM en tallas XL a 4XL según la prenda que combinan frescura y estilo.',
        'Outfits curvy para clima cálido: 5 looks plus size pensados para el calor salvadoreño, con piezas reales de BOLEM en tallas XL a 4XL.'),
}


def main():
    seco = '--dry' in sys.argv
    archivos = {}
    fallas = []
    cambios = []

    def cargar(rel):
        if rel not in archivos:
            ruta = os.path.join(RAIZ, rel)
            if not os.path.exists(ruta):
                return None
            archivos[rel] = open(ruta, encoding='utf-8').read()
        return archivos[rel]

    def sustituir(rel, viejo, nuevo, etiqueta):
        c = cargar(rel)
        if c is None:
            fallas.append('%s — no existe' % rel)
            return
        n = c.count(viejo)
        if n != 1:
            fallas.append('%s — %s: esperaba 1 coincidencia, encontre %d' % (rel, etiqueta, n))
            return
        archivos[rel] = c.replace(viejo, nuevo, 1)
        cambios.append('%s · %s' % (rel, etiqueta))

    for rel, viejo, nuevo in ENCABEZADOS:
        sustituir(rel, viejo, nuevo, 'encabezado')

    for rel, (viejo, nuevo) in TITULOS.items():
        sustituir(rel, '<title>%s</title>' % viejo, '<title>%s</title>' % nuevo,
                  'title %d->%d' % (len(viejo), len(nuevo)))

    for rel, (viejo, nuevo) in DESCRIPCIONES.items():
        sustituir(rel, 'name="description" content="%s"' % viejo,
                  'name="description" content="%s"' % nuevo,
                  'description %d->%d' % (len(viejo), len(nuevo)))
        # og:description solo si traia EXACTAMENTE el mismo texto: si alguien
        # lo escribio distinto a proposito, no es nuestro para cambiarlo.
        c = cargar(rel)
        if c and 'property="og:description" content="%s"' % viejo in c:
            archivos[rel] = c.replace('property="og:description" content="%s"' % viejo,
                                      'property="og:description" content="%s"' % nuevo, 1)
            cambios.append('%s · og:description en sincronia' % rel)

    if fallas:
        print('ABORTADO — no se escribio ningun archivo:')
        for f in fallas:
            print('   x ' + f)
        return 1

    for c in cambios:
        print('   * ' + c)
    if not seco:
        for rel, contenido in archivos.items():
            open(os.path.join(RAIZ, rel), 'w', encoding='utf-8', newline='').write(contenido)

    print('\n%d cambios en %d archivos%s'
          % (len(cambios), len(archivos), ' (simulacro)' if seco else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
