# -*- coding: utf-8 -*-
"""BOLEM elige e importa producto terminado; no diseña ni fabrica.
Reescribe los claims duros de autoría a lenguaje de curaduría y repara
el canon de marca que el commit 54ac3ad dejó a medias (Mónica no es plus size;
BOLEM nace del amor por su mamá y su hermana).
Confirmado por OAR 2026-08-16."""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r"C:\Users\othma\dev\projects\bolem-site"

CANON = (
    "Cada pieza de BOLEM se elige pensando en cuerpos de talla XL a 4XL%s. "
    "No traemos tallas peque\u00f1as estiradas con cent\u00edmetros extra: buscamos marcas "
    "que cortan para cuerpos curvy de verdad. Empezamos por los cuerpos que nos "
    "ense\u00f1aron el problema \u2014 la mam\u00e1 y la hermana de M\u00f3nica, que sal\u00edan de las "
    "tiendas con las manos vac\u00edas."
)

EDICIONES = {
    "index.html": [
        # pilar de Nuestra Esencia
        ("Cada pieza se dise\u00f1a pensando en cuerpos reales",
         "Cada pieza se elige pensando en cuerpos reales"),
        # franja de datos: BOLEM no fabrica en El Salvador, importa
        ("Hecho en El Salvador", "Marca salvadore\u00f1a"),
        # FAQ \u2014 JSON-LD (lo que Google y los motores de IA citan como hecho)
        ("S\u00ed. Nuestras tallas est\u00e1n dise\u00f1adas para cuerpos reales de mujeres curvy, "
         "no son adaptaciones de tallas peque\u00f1as con cent\u00edmetros extra.",
         "S\u00ed. Elegimos marcas que cortan para cuerpos curvy, no que estiran una talla "
         "peque\u00f1a con cent\u00edmetros extra."),
        ("Todos nuestros dise\u00f1os est\u00e1n pensados para el clima c\u00e1lido de El Salvador: "
         "telas frescas como lino, algod\u00f3n y viscosa, en cortes que celebran las curvas.",
         "Todo lo que tra\u00e9mos est\u00e1 elegido para el clima c\u00e1lido de El Salvador: "
         "telas frescas como lino, algod\u00f3n y viscosa, en cortes que celebran las curvas."),
        # FAQ \u2014 versi\u00f3n visible
        ("S\u00ed. Nuestras tallas est\u00e1n dise\u00f1adas para cuerpos reales de mujeres curvy, "
         "no son adaptaciones de tallas peque\u00f1as.",
         "S\u00ed. Elegimos marcas que cortan para cuerpos curvy, no que estiran una talla "
         "peque\u00f1a."),
        ("Todos nuestros dise\u00f1os est\u00e1n pensados para el clima c\u00e1lido de El Salvador: "
         "telas frescas como lino, algod\u00f3n y viscosa.",
         "Todo lo que tra\u00e9mos est\u00e1 elegido para el clima c\u00e1lido de El Salvador: "
         "telas frescas como lino, algod\u00f3n y viscosa."),
    ],
    "nosotros.html": [
        ("La marca salvadore\u00f1a de ropa plus size en El Salvador. Dise\u00f1ada desde "
         "cuerpos reales, para mujeres reales.",
         "La marca salvadore\u00f1a de ropa plus size en El Salvador. Elegida desde "
         "cuerpos reales, para mujeres reales."),
        ("<strong>Dise\u00f1o que celebra curvas:</strong> Cortes pensados para resaltar, "
         "no para esconder.",
         "<strong>Selecci\u00f3n que celebra curvas:</strong> Cortes que resaltan, "
         "no que esconden."),
        ("Cada pieza de BOLEM est\u00e1 dise\u00f1ada desde cero pensando en cuerpos de talla "
         "XL a 4XL. No adaptamos patrones de tallas peque\u00f1as y les agregamos "
         "cent\u00edmetros. No. <strong>Empezamos desde nuestros cuerpos.</strong> Desde "
         "c\u00f3mo nos movemos, c\u00f3mo vivimos, c\u00f3mo nos queremos sentir.",
         CANON % ""),
        ("Tallaje honesto: si nuestra <a href=\"guia-de-tallas\">gu\u00eda de tallas</a> "
         "dice 1XL, es 1XL de verdad. Modelos reales. Sin filtros. Sin Photoshop. "
         "Cada dise\u00f1o se prueba en cuerpos reales y se ajusta hasta que el calce sea "
         "perfecto. No publicamos nada que no nos pondr\u00edamos nosotras mismas.",
         "Tallaje honesto: si nuestra <a href=\"guia-de-tallas\">gu\u00eda de tallas</a> "
         "dice 1XL, es 1XL de verdad. Modelos reales, fotos de producto sin retoque de "
         "cuerpo. Y no tra\u00e9mos nada que no nos pondr\u00edamos nosotras mismas."),
    ],
    "guia-de-tallas.html": [
        ("Nuestra ropa plus size en El Salvador est\u00e1 dise\u00f1ada para abrazar tu cuerpo, "
         "no para esconderlo.",
         "Nuestra ropa plus size en El Salvador est\u00e1 elegida para abrazar tu cuerpo, "
         "no para esconderlo."),
    ],
    os.path.join("coleccion", "index.html"): [
        ("No dise\u00f1amos ropa para que te quede. Dise\u00f1amos ropa para que te sientas "
         "imparable.",
         "No eleg\u00edmos ropa para que te quede. Eleg\u00edmos ropa para que te sientas "
         "imparable."),
    ],
    os.path.join("blog", "historia-bolem-moda-plus-size-el-salvador.html"): [
        ("Cada pieza de BOLEM est\u00e1 dise\u00f1ada desde cero pensando en cuerpos de talla "
         "XL a 4XL seg\u00fan la prenda. No adaptamos patrones de tallas peque\u00f1as y les "
         "agregamos cent\u00edmetros. No. Empezamos desde nuestros cuerpos. Desde c\u00f3mo nos "
         "movemos, c\u00f3mo vivimos, c\u00f3mo nos queremos sentir.",
         CANON % " seg\u00fan la prenda"),
    ],
    os.path.join("blog", "guia-tallas-plus-size.html"): [
        # JSON-LD de la FAQ del art\u00edculo
        ("En BOLEM dise\u00f1amos nuestras prendas espec\u00edficamente para cuerpos curvy, en "
         "tallas XL a 4XL seg\u00fan la prenda, con cortes que favorecen la silueta.",
         "En BOLEM eleg\u00edmos marcas que cortan espec\u00edficamente para cuerpos curvy, en "
         "tallas XL a 4XL seg\u00fan la prenda, con cortes que favorecen la silueta."),
        ("En BOLEM dise\u00f1amos cada pieza pensando en cuerpos reales de mujeres curvy. "
         "No adaptamos moldes de tallas peque\u00f1as ni agregamos cent\u00edmetros a lo loco. "
         "Nuestros cortes nacen desde el cuerpo plus size, con proporciones que "
         "favorecen la silueta, dan movimiento y te hacen sentir <strong>poderosa</strong>.",
         "En BOLEM eleg\u00edmos cada pieza pensando en cuerpos reales de mujeres curvy. "
         "No tra\u00e9mos moldes de tallas peque\u00f1as con cent\u00edmetros agregados a lo loco. "
         "Buscamos cortes que nacen desde el cuerpo plus size, con proporciones que "
         "favorecen la silueta, dan movimiento y te hacen sentir <strong>poderosa</strong>."),
        ("En BOLEM dise\u00f1amos desde cero para tallas XL a 4XL seg\u00fan la prenda, con "
         "proporciones reales.",
         "En BOLEM eleg\u00edmos marcas que cortan desde el cuerpo plus size para tallas "
         "XL a 4XL seg\u00fan la prenda, con proporciones reales."),
    ],
    "llms.txt": [
        ("BOLEM disena y vende ropa plus size para mujeres en El Salvador.",
         "BOLEM elige, importa y vende ropa plus size para mujeres en El Salvador."),
        ("con disenos modernos pensados para el clima calido tropical",
         "con prendas modernas elegidas para el clima calido tropical"),
    ],
}

total = 0
for rel, pares in EDICIONES.items():
    p = os.path.join(ROOT, rel)
    t = open(p, encoding='utf-8').read()
    for viejo, nuevo in pares:
        assert viejo in t, "NO ENCONTRADO en %s:\n  %s" % (rel, viejo[:90])
        n = t.count(viejo)
        t = t.replace(viejo, nuevo)
        total += n
        print("  %-52s x%d" % (rel, n), viejo[:52].replace("\n", " "))
    open(p, 'w', encoding='utf-8').write(t)

print("\nreemplazos aplicados:", total)
