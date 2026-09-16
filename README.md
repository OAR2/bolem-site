# BOLEM — sitio público

Diseño editorial de septiembre de 2026, publicado con GitHub Pages desde `master`.
URL principal: https://bolemsv.com/
GitHub Pages redirige https://oar2.github.io/bolem-site/ al dominio principal.

## Mantener el sitio

Fuente única de prendas: `_data/catalogo.json`. Confirmar inventario antes de cambiar disponibilidad.

```powershell
python _tools/publicar_v3.py --origin https://bolemsv.com
python _tools/verificar.py
python v3/_source/verify.py
python _tools/verificar_publicacion.py
```

El generador reconstruye la propuesta en `v3/` y publica el HTML en la raíz. La fuente visual está en `v3/_source/build.py` y `v3/ui/`; los textos legales preservados están en `v3/_source/legal/`. No editar manualmente los HTML generados ni usar los generadores antiguos de v1 para reconstruir producción.

Las rutas de las 49 prendas se mantienen. `nosotros` y `guia-de-tallas`, y las antiguas páginas de categorías, redirigen a sus destinos nuevos. La colección acepta enlaces antiguos con `#vestido`, etc. Las carpetas v2/v3 conservan `noindex`.

Paleta: naranja #FE470A, coral #FA5857, acento interactivo #A5427E. Los neutros de pantalla son #FFFDF9 y #F4EEE3. Tipografía Playfair Display + DM Sans, con fuentes locales. No hay selector público de variantes de marca.

## Publicar

Revisar el diff y las comprobaciones; commit de archivos específicos y push a master. GitHub Pages publica automáticamente. Verificar el resultado remoto después.

El dominio está asociado a GitHub Pages mediante CNAME y cuatro registros A en Cloudflare. www apunta a oar2.github.io. La generación usa automáticamente CNAME como origen; --origin permite una previsualización explícita. Mantener HTTPS habilitado cuando el certificado esté emitido.

## Ecosistema

- Landing: este repositorio, OAR2/bolem-site.
- WhatsApp SaaS: C:/Users/othma/dev/projects/whatsapp-saas/, independiente del sitio.
- Content Engine: G:/My Drive/00 - TOOLS/content/bolem/.

La compra se coordina por WhatsApp; elegir talla/foto prepara un mensaje, no confirma un pedido. No se inventan existencias ni se envían mensajes en las pruebas.
