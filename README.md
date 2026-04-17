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

```
bolem-site/
├── index.html                  # Homepage
├── coleccion/index.html        # Colección SS26
├── nosotros.html               # Página "Nosotras" (historia de Mónica)
├── guia-de-tallas.html         # Guía tallas 1XL-3XL
├── blog/
│   ├── index.html
│   ├── historia-bolem-moda-plus-size-el-salvador.html
│   ├── guia-tallas-plus-size.html
│   └── looks-plus-size-clima-calido.html
├── privacidad.html · terminos.html · cambios.html
├── 404.html · _headers · _redirects
├── styles.css
├── assets/                     # Imágenes (webp + png)
│   └── catalog/                # Fotos de producto
├── favicon.svg
└── robots.txt · sitemap.xml · llms.txt
```

## Skill relacionada

- **`/bolem`** (en `.claude/commands/bolem.md`) — router del proyecto
- **`/content bolem`** — generación de fotos con Gemini Imagen 4.0
- Memoria: [`memory/proyectos/bolem.md`](../../memory/proyectos/bolem.md)

## Estado actual (2026-04-16)

- Landing **en producción**. Hero redesign reciente (full-bleed dark con animación slide-in).
- SEO Sprint 1-2 completados. Sprint 3 pendiente (Search Console, GA4, Business Profile — gestión humana).
- Dominio `bolemsv.com` pendiente de activar (actualmente sirve en `oar2.github.io/bolem-site/`).
- Content Engine: prompts v2 validados. Carousel Folk Art pausado esperando que Mónica elija favoritos.
- WhatsApp SaaS: código completo (6 intents, 41 tests, multi-tenant). Pausado por credenciales Meta.

## Workflow local

```bash
# Editar y previsualizar
cd C:/Users/othma/dev/projects/bolem-site
start index.html                # abre en browser default

# Deploy (auto via GitHub Pages on push to master)
git add <archivos>
git commit -m "tipo: descripción"
git push
```
