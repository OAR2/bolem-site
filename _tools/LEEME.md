# Herramientas del sitio BOLEM

## Ver el sitio en la computadora

**Doble clic en `ver-preview.cmd`.**

No abrás los `.html` directo desde el disco. El sitio enlaza rutas **sin `.html`**
(`nosotros`, `guia-de-tallas`, `coleccion/`), que es como las sirven Cloudflare
Pages y GitHub Pages y de donde cuelgan los canonicals del SEO. Abierto como
archivo, nadie resuelve esas rutas: el navegador muestra el índice de la carpeta
y el sitio *parece* roto sin estarlo.

---

## Agregar o cambiar productos

El catálogo tiene **una sola fuente**: `_data/catalogo.json`. De ahí salen las
tarjetas de la colección, su JSON-LD, los conteos de los botones de filtro, los
azulejos de categoría de las dos páginas, las dos bandas del home y el
`llms.txt`. Antes eso estaba escrito a mano en unos diez lugares y el que se
olvidara quedaba mintiendo.

**Nunca se edita el HTML de productos a mano. Se edita el JSON y se reconstruye.**

### 1. Las fotos

```
python _tools/procesar_fotos.py "C:/ruta/carpeta-de-Monica"
```

Deja en `assets/productos/` las **tres versiones** que necesita cada foto:
`nombre.webp` (1200 de ancho), `nombre-800.webp` y `nombre-480.webp`. El
navegador elige sola cuál bajar; sin las tres, una banda de 300px terminaría
descargando la de 1200.

- Recorta todo a **2:3** al centro, que es la proporción del catálogo.
- **Avisa si descartó más del 12%** — puede estar cortando cabezas o pies.
- Respeta la rotación del teléfono y limpia los nombres
  (`Vestido Ámbar Nuevo.jpg` → `vestido-ambar-nuevo`).
- No pisa nada sin `--sobrescribir`. Con `--ensayo` no escribe.

### 2. El producto

En `_data/catalogo.json`, agregá al arreglo `productos`:

```json
{
  "id": "vestido-ambar",
  "nombre": "Vestido Ámbar",
  "categoria": "vestido",              // vestido | blusa | pantalon | conjunto
  "precio": 49.9,
  "tallas": ["1XL", "2XL", "3XL"],
  "colores": 2,
  "fotos": ["vestido-ambar.webp", "vestido-ambar-verde.webp"],
  "destacada": false,
  "alt": "Vestido midi ámbar plus size, tallas 1XL–3XL — BOLEM El Salvador"
}
```

La primera foto es la portada. Las demás alimentan la galería del Quick View
(flechas, puntitos y deslizar con el dedo).

### 3. Reconstruir

```
python _tools/construir_catalogo.py --revisar   # dice qué cambiaría
python _tools/construir_catalogo.py             # lo hace
```

Es **idempotente**: correrlo dos veces seguidas no cambia nada. Solo toca lo que
está entre marcas `<!-- BOLEM:X --> ... <!-- /BOLEM:X -->`; todo lo escrito a
mano alrededor queda intacto.

Si avisa que **las bandas del home quedaron desparejas**, hacele caso: las dos
filas comparten la duración de la animación, así que con distinta cantidad de
tarjetas giran a distinta velocidad. Se emparejan moviendo ids entre `BANDA_1` y
el resto, dentro del mismo script.

---

## Qué vive en el JSON y qué no

| En `catalogo.json` | En el código |
|---|---|
| Productos: nombre, precio, categoría, tallas, colores, fotos, texto alternativo | El diseño de la tarjeta |
| Líneas editoriales de cada categoría | El orden de las bandas (`BANDA_1`) |
| Foto de portada de cada azulejo | Las etiquetas de categoría |

Las líneas editoriales (*"El vestido no te tiene que quedar. Te tiene que
celebrar."*) son texto escrito a mano. La primera versión del constructor las
borraba; se rescataron del respaldo antes de que se perdieran, y por eso ahora
viven en el JSON.

---

## Scripts de una sola vez

`aplicar_rediseno.py`, `extraer_quickview.py`, `extraer_catalogo.py`,
`fix_claims_fabricacion.py`, `fix_scroll_lenis.py`, `hero_y_color.py`,
`perf_y_estructura.py`, `v39_precio_logo_categorias.py`.

Ya se corrieron. **No son idempotentes**: sus verificaciones fallan al segundo
intento porque los cambios ya están aplicados. Quedan como registro de qué se
hizo y por qué, no como herramientas a repetir.
