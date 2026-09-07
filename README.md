# BOLEM — Landing Site

Sitio de **BOLEM**, moda plus-size salvadoreña de [Mónica Claros](https://instagram.com/bolem_sv).
Desplegado vía GitHub Pages: **https://bolemsv.com** · **https://oar2.github.io/bolem-site/**

Repo: [`OAR2/bolem-site`](https://github.com/OAR2/bolem-site)

---

## Mapa del ecosistema BOLEM

BOLEM vive en **tres ubicaciones** según el componente. Este repo es solo la landing.

| Componente | Ruta | Repo | Qué hace |
|---|---|---|---|
| **Landing (este repo)** | `C:/Users/othma/dev/projects/bolem-site/` | `OAR2/bolem-site` (public) | Sitio público: catálogo, blog, SEO, AI visibility |
| **WhatsApp SaaS** | `C:/Users/othma/dev/projects/whatsapp-saas/` | `OAR2/whatsapp-saas` (private) | Automatización WhatsApp Business multi-tenant (BOLEM + UNCSA). Node + TS + Prisma + Postgres |
| **Content Engine** | `G:/My Drive/00 - TOOLS/content/bolem/` | *no-git* (volumen de imágenes) | Gemini Imagen 4.0: genera fotos de producto/lifestyle. `brand.json`, `templates/`, `approved/`, `drafts/` |

> **¿Por qué en 3 lugares?**
> - Landing: público, SEO-visible, `/projects/` como el resto del dev local
> - WhatsApp SaaS: privado, multi-tenant (no solo BOLEM — también UNCSA)
> - Content Engine: Drive por volumen de imágenes y necesidad de sync entre dispositivos

---

## Estructura del repo

**El repo tiene TRES sitios que comparten las mismas fotos y el mismo catálogo de 49 prendas.**
No es duplicación accidental: corren en paralelo hasta que Mónica elija. Solo el de la raíz es público.

| | Ruta | Páginas | Indexable |
|---|---|---|---|
| **v1** — el sitio vivo | raíz | 7 raíz + 49 prendas + 5 colección + 7 blog | **sí** |
| **v2** — borrador (17-ago) | `v2/` | 64 · tesis: escalas de talla | no (`noindex`) |
| **v3** — propuesta (06-sep) | `v3/` | 63 · generada, minificada | no (`noindex`) |

```
bolem-site/
├── index.html · coleccion/ · nosotros.html · guia-de-tallas.html   # v1
├── prendas/                    # 49 fichas, una por prenda
├── blog/                       # 7 artículos
├── privacidad.html · terminos.html · cambios.html · 404.html
├── styles.css · home.css · prenda.css · quickview.css
├── _data/catalogo.json         # FUENTE ÚNICA de productos
├── _tools/                     # generadores + verificar.py  → ver _tools/LEEME.md
├── assets/productos/           # fotos, 3 tamaños c/u (1200 / 800 / 480)
├── v2/ · v3/                   # borradores, noindex, reusan assets/productos/
├── _headers · _redirects       # sintaxis Cloudflare Pages (ver nota de deploy)
└── robots.txt · sitemap.xml · llms.txt
```

⚠️ **`assets/catalog/` no existe** — la ruta real es `assets/productos/`. Este README decía lo
contrario hasta el 06-sep.

## Skill relacionada

- **`/bolem`** (en `.claude/commands/bolem.md`) — router del proyecto
- **`/content bolem`** — generación de fotos con Gemini Imagen 4.0
- Memoria: [`memory/proyectos/bolem.md`](../../memory/proyectos/bolem.md)

## Estado actual (2026-09-06)

- **v1 sirve en `oar2.github.io/bolem-site/`.** Rediseño v3.8 aplicado el 16-ago (crítica: 7.5/10).
- 🔴 **`bolemsv.com` NO resuelve.** Nameservers en Cloudflare pero **cero registros A/CNAME**, y el
  repo **no tiene archivo `CNAME`**. Falta la conexión de los dos lados. Consecuencia: hay **1,952
  referencias a `bolemsv.com`** en 131 archivos (canonicals, sitemap, OG, `llms.txt`), así que Google
  ve un canonical que apunta a un dominio muerto y trata la URL viva como duplicado.
- 🔴 **Sin decidir: GitHub Pages o Cloudflare Pages.** El repo está a medio camino — se despliega por
  GitHub Pages, pero `_headers` y `_redirects` son sintaxis de **Cloudflare** Pages y allí no hacen
  nada. La decisión define si hace falta un `CNAME` (GitHub) o un proyecto Pages (Cloudflare).
- ⚠️ **OAR reporta que la navegación se traba** en v1. Se corrigieron 3 costos reales en agosto, pero
  no se midió ni antes ni después. Ver `docs/` o el workbench para el diagnóstico estructural.
- SEO Sprint 1-2 completados. Sprint 3 pendiente (Search Console, GA4, Business Profile — es gestión
  humana, y además depende del dominio).
- Content Engine: prompts v2 validados. Carousel Folk Art pausado esperando que Mónica elija favoritos.
- WhatsApp SaaS: código completo (6 intents, 41 tests, multi-tenant). Pausado por credenciales Meta.

## Workflow local

**Nunca abras los `.html` desde el disco.** El sitio enlaza rutas **sin `.html`** (`/nosotros`,
`/coleccion/`), que es como las sirven GitHub Pages y Cloudflare. Abierto como archivo, el navegador
muestra el índice de la carpeta y el sitio *parece* roto sin estarlo.

```bash
cd C:/Users/othma/dev/projects/bolem-site
python _tools/servidor_preview.py     # resuelve las rutas sin extensión
#   v1 → http://localhost:8777/        v2 → .../v2/        v3 → .../v3/

# Productos: NUNCA se edita el HTML a mano
#   1. fotos    → python _tools/procesar_fotos.py "<carpeta>"
#   2. producto → editar _data/catalogo.json
#   3. build    → python _tools/construir_catalogo.py    (idempotente)
#   4. v3       → python v3/_source/build.py
python _tools/verificar.py            # obligatorio antes de commitear
```

```bash
# Deploy (auto via GitHub Pages on push to master)
git add <archivos específicos>        # nunca -A
git commit -m "tipo: descripción"
git push
```
