# BOLEM — Briefing para revisión externa de diseño

> Documento de entrada para una **segunda opinión** sobre el sitio BOLEM.
> Escrito 2026-09-06. Todo lo de acá está verificado contra el disco y el sitio vivo, no recordado.
> Si algo en este archivo contradice al README del repo, **gana este archivo**: el README quedó
> congelado el 16-abr y describe rutas que ya no existen (`assets/catalog/`) y un workflow
> (`start index.html`) que el propio `_tools/LEEME.md` prohíbe.

---

## 1. La pregunta que se te pide contestar

OAR quiere saber **si el sitio merece publicarse ya**. Pero cuidado con la forma de la pregunta,
porque el sitio **ya está publicado**: sirve en `https://oar2.github.io/bolem-site/` y responde 200.

Lo que en realidad está trabado son tres decisiones:

1. **¿La v1 que está viva aguanta que se le cuelgue el dominio real (`bolemsv.com`)?**
   Publicar de verdad = conectar el dominio. Eso es lo irreversible: hoy la ve quien recibe el link
   de Instagram; con el dominio la ve Google, y lo que esté flojo queda indexado.
2. **¿O primero hay que reemplazarla con la v2**, que vive en `/v2/` como 64 páginas `noindex`?
3. **Si es la v2, ¿cuál de las tres direcciones de diseño** (`/v2/disenos/{a,b,c}`)?

Un veredicto de "sí/no" sin decir **cuál de los dos sitios** no le sirve a OAR.

---

## 2. Los dos sitios (esto es lo que más confunde al entrar al repo)

El repo tiene **dos sitios completos que comparten las mismas fotos y los mismos 49 productos**.
No es duplicación accidental — fue decisión explícita del 17-ago: corren en paralelo hasta que
Mónica (la dueña de BOLEM) elija.

| | **v1 — el sitio vivo** | **v2 — el borrador** |
|---|---|---|
| Dónde | raíz del repo | `v2/` |
| Páginas | 7 raíz + 49 prendas + 5 colección + 7 blog | 64 HTML |
| Datos | `_data/catalogo.json` (49 productos) | `v2/_data/bolem.json` (49 productos) |
| CSS | `styles.css`, `home.css`, `prenda.css`, `quickview.css` | `v2/bolem.css` |
| Indexable | sí, en el sitemap | **no** — `noindex` en las 64 |
| Último toque | 18-ago | 17-ago |
| Tesis | catálogo plus-size con SEO fuerte | resolver la **confusión de escalas de talla** (ver §5) |

**Cómo verlos.** No abras los `.html` desde el disco: el sitio enlaza rutas **sin `.html`**
(`/nosotros`, `/coleccion/`), que es como las sirven GitHub Pages y Cloudflare. Abierto como archivo
parece roto sin estarlo. Levantá un servidor:

```bash
cd C:/Users/othma/dev/projects/bolem-site
python -m http.server 8000
# v1 → http://localhost:8000/
# v2 → http://localhost:8000/v2/
# las tres direcciones → http://localhost:8000/v2/disenos/a/  (y /b/, /c/)
```

---

## 3. El contrato de diseño — contra esto se juzga

No inventes criterio estético propio. **Mónica ya rechazó dos direcciones** y dejó dicho lo que
quiere. Una propuesta que ignore esto no sirve aunque sea bonita.

- **Referencias que ella dio:** `colettecurve.com` y `thedress.me` (esta última es salvadoreña y
  competencia directa con e-commerce propio).
- **La regla:** fondo blanco, tipografía tinta fina, **el color lo ponen las fotos**, acentos mínimos.
  *Todo diseño BOLEM parte de ahí.*
- **Rechazado v1 "Acento cálido":** mucho rojo, ilegible.
- **Rechazado v2 "Blanco galería":** mucho negro y rojo, sin conexión con la marca.

### Paleta oficial (de la tarjeta de marca de Mónica, 15-ago) y sus límites de contraste

| Color | Hex | Uso permitido |
|---|---|---|
| Naranja BOLEM | `#FE470A` | **solo CTA grande** (3.43:1 con blanco) · y el logotipo |
| Naranja profundo | `#C93400` | texto (5.28:1) — pero *seguía leyéndose rojo*, se jubiló como acento |
| Fucsia profundo | `#A5427E` | **acento interactivo actual** (5.71:1 sobre blanco) |
| Mango | `#FFB61F` | nunca texto sobre claro; con tinta encima (9.9:1) o sobre oscuro (11.3:1) |
| Crema durazno | `#FFE4B3` | el "subrayador" de las cursivas = la firma visual · acento sobre oscuro |
| Rosa `#FF789F` / Fucsia `#FF66C3` | | **solo decorativo** (2.5:1) |
| Verde WhatsApp | `#25D366` | botón final, **con tinta encima** (blanco encima da 1.98:1) |

Tipografía del design system: **Caveat + Quicksand**.
⚠️ El workbench apunta a `bolem/design-system/bolem/MASTER.md` para los tokens —
**ese archivo no existe** (verificado 06-sep). El `brand.json` vivo sí:
`C:/Users/othma/dev/projects/agencia-ai/clients/bolem/brand.json`.

### La última crítica de diseño dio **7.5/10**

Fue sobre la v3.8 (16-ago), que es lo que está vivo hoy. Cambios que salieron de ahí y ya están
aplicados: hero de dos pantallas de tipografía → texto a la izquierda + vestido a sangre en el 44%
derecho; el slab de color se mudó del formulario VIP al Vestidor; el formulario de un campo murió y
quedó un botón de WhatsApp. **Un 7.5 es el piso desde el que arrancás, no un punto de partida en cero.**

---

## 4. Restricciones de contenido que NO son opinables

Estas se rompieron ya una vez y costaron trabajo de reparación. Si una propuesta de diseño las
vuelve a romper, es un rojo, no un detalle.

1. **BOLEM no diseña ni fabrica: elige, importa y vende producto terminado.**
   El 16-ago el sitio decía lo contrario en **19 lugares de 9 archivos** — y cuatro de esos vivían
   dentro del JSON-LD de las FAQ y de `llms.txt`, o sea lo que Google y los motores de IA citan
   *como hecho*. Lenguaje válido: *elige*, *cura*. Prohibido: *diseña*, *adapta patrones*, *fabrica*.
2. **Mónica no es ni ha sido plus size.** El canon es que la historia empieza por los cuerpos de su
   mamá y su hermana. Cualquier copy tipo "empezamos desde nuestros cuerpos" es falso.
3. **El retrato de la fundadora salió de un pipeline generativo.** La página `nosotros.html` decía
   "Modelos reales. Sin filtros. Sin Photoshop." en esa misma página. Se acotó a "fotos de producto
   sin retoque de cuerpo" (eso sí es cierto: las fotos de producto son reales).
   🟡 **Sigue abierto y es decisión de OAR/Mónica:** si el retrato generativo debe declararse.

---

## 5. La tesis de la v2, por si te toca juzgarla

El hallazgo que la justifica: en el mercado salvadoreño **conviven cuatro escalas de talla**
(XL–4XL · 2X–6X · 20W–28W · 13/15/17/19) y **nadie resuelve esa confusión**. Es el diferenciador más
defendible que apareció en el análisis de competencia. Pero depende de que Mónica **tome medidas
reales de las prendas**, no de comprar mejor — o sea que la v2 tiene una dependencia humana que la
v1 no tiene. Pesalo en la recomendación.

---

## 6. Estado técnico — el sitio pasa sus propias pruebas

`python _tools/verificar.py` → **PASA** (corrido 06-sep):

```
250 bloques JSON-LD, 0 rotos · 184 fotos, 0 faltantes, 0 variantes faltantes
3,679 enlaces internos, 0 rotos · 0 páginas con encabezados fuera de norma
catálogo 49 · tarjetas 49 · Product en JSON-LD 49 · 0 números desactualizados
rango $22–$85, 0 reclamos que no cuadran
```

Git limpio, `master == origin/master`, último commit `b7671a4`.

**Corré ese verificador antes y después de cualquier propuesta.** No es decorativo: caza números
escritos a mano que se desincronizan del catálogo, que es el error que más ha vuelto en este repo.

### El pipeline (importante si vas a proponer cambios)

**Nunca se edita a mano el HTML de productos.** Hay una sola fuente, `_data/catalogo.json`, y de ahí
se reconstruye todo lo derivado. `_tools/construir_catalogo.py` toca **solo lo que está entre marcas
`<!-- BOLEM:X -->`** y es idempotente; lo escrito a mano queda intacto. Un producto agregado al JSON
aparece solo en 9 lugares. Herramientas en `_tools/` (documentadas en `_tools/LEEME.md`).

---

## 7. Problemas abiertos conocidos — no los reportes como hallazgos nuevos

| # | Qué | Estado |
|---|---|---|
| 1 | 🔴 **`bolemsv.com` no resuelve.** NS en Cloudflare, **cero registros A/CNAME**; el repo tampoco tiene archivo `CNAME`. Falta la conexión de los dos lados | abierto, es el nudo |
| 2 | 🔴 **1,952 referencias a `bolemsv.com` en 131 archivos** — canonicals, sitemap, OG, `llms.txt`. Google trata la URL viva como duplicado de un dominio muerto | consecuencia de #1 |
| 3 | ⚠️ **OAR reporta que la navegación se traba.** Se corrigieron 3 costos reales (backdrop-filter ×3, ruido SVG rasterizado a pantalla completa, `offsetHeight` leído en cada scroll) pero **no se midió ni antes ni después** — el intento vía Chrome MCP era inválido (Chrome no corre rAF en pestañas ocultas) | **sin confirmar si mejoró** |
| 4 | `home-comunidad` (`index.html:2051`) renderiza con altura 0 | **no es bug** — lleva `hidden` a propósito desde el 10-jul, por 6 cajas de UGC vacías |
| 5 | SEO Sprint 3 sin arrancar: Search Console, GA4, Google Business Profile, micro-influencers | todo requiere gestión humana |
| 6 | Rama `v2-correcciones`: 0 commits adelante, 15 atrás de master | se puede borrar |

**El #3 es el que más te conviene atacar con instrumentación seria**, porque es el único síntoma
reportado por un humano usando el sitio y nadie lo ha medido todavía.

---

## 8. Dónde vive el resto de BOLEM (por si necesitás ir más lejos)

| Casa | Ruta | Es fuente de verdad de |
|---|---|---|
| **El sitio** (este repo) | `C:/Users/othma/dev/projects/bolem-site/` | lo publicado |
| Fotos originales, modelos IA, prompts | `C:/Users/othma/dev/projects/agencia-ai/clients/bolem/` | los originales (274 MB) |
| Historia y decisiones | `G:/My Drive/00 - TOOLS/CLAUDE/memory/proyectos/bolem.md` | **572 líneas — el porqué de todo** |
| Documentos, marca, financiero | Drive `01 - OAR/BOLEM/` | facturas y documentos |
| Catálogo de Mónica | Drive compartido «Catálogo» | qué vende ella hoy (solo lectura) |
| GSheet «BOLEM — Hoja Madre» | 8 pestañas | datos de prenda de la v2 (🔴 no compartida) |

Relación fotos: `assets/productos/` (15 MB, 183 web-optimizadas) es **derivado** de
`agencia-ai/.../product-photos` (221 MB originales). Es un pipeline, no duplicación. No tocar.

---

## 9. Qué se espera de vos como entregable

Un veredicto que OAR pueda ejecutar el mismo día:

1. **v1, v2, o v2/diseños {a,b,c}** — cuál, y por qué contra el contrato de §3.
2. **¿Se le cuelga el dominio ya, o hay algo que arreglar antes?** Si hay bloqueantes, listalos
   separando **"esto sale indexado y duele"** de **"esto se arregla después sin costo"**.
3. **Lo que encontraste que no está en §7.** Eso es el valor de una segunda opinión.
4. Diseño juzgado **en celular primero**: la clienta llega del link de Instagram, en teléfono.
   El hover no existe ahí — es una restricción que ya movió decisiones en este proyecto.

Contexto de negocio para calibrar: BOLEM es ropa plus-size en El Salvador, de Mónica Claros
(`@bolem_sv`), 49 prendas, rango $22–$85, venta por WhatsApp. No hay carrito ni checkout: el sitio
es catálogo + captación, y el cierre es humano por WhatsApp. **No propongas e-commerce.**
