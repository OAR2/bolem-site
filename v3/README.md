# BOLEM v3 — propuesta de septiembre de 2026

La v3 vive separada de v1 y v2. Todas sus páginas llevan `noindex,nofollow`. No se cambió el dominio, sitemap, robots ni despliegue público.

## Dirección visual

Moda editorial cálida: fotografía real de producto, superficies claras, tipografía oscura, curvas y recortes coral/naranja como firma. El catálogo permanece limpio. La mujer protagoniza la fotografía y las tallas aparecen como información útil.

- Naranja digital: `#FE470A`, de la paleta suministrada.
- Coral digital propuesto: `#EF4A43`, tomado del SVG conceptual del pop-up. **No es una especificación oficial ni una tinta aprobada.**
- Papel `#FFFDF9`, crema `#F4EEE3`, tinta `#29251F` y acento textual oscuro `#A42E12`: tokens de esta propuesta web.
- Playfair Display + DM Sans: combinación propuesta para conciliar el lenguaje editorial del pop-up con lectura y controles claros. No se afirma que reemplace el manual de marca.
- El nombre conserva las mayúsculas de BOLEM. Su tratamiento tipográfico se adapta a esta propuesta editorial.

## Construcción y contenido

Una sola fuente de productos: `../_data/catalogo.json`. No se inventan medidas, telas, existencias verificadas, reseñas, descuentos ni testimonios. Las fotos son las existentes en `../assets/productos/`. Se evita el retrato generativo de Mónica. El origen de la marca se atribuye a la experiencia de su mamá y su hermana.

Desde la raíz del repositorio:

```
python v3/_source/build.py
python v3/_source/verify.py
python _tools/verificar.py
python _tools/servidor_preview.py
```

Abrir `http://127.0.0.1:8777/v3/`. El servidor del proyecto resuelve las rutas sin extensión.

El generador crea portada, catálogo, fichas de producto, guía de tallas, historia, diario y páginas de políticas. Las políticas conservan el texto de v1 con nueva presentación. Los artículos del diario son adaptaciones breves basadas en hechos del catálogo y el briefing; no reproducen estadísticas sin fuente.

Los filtros de categoría/talla y orden se guardan en la URL, respetan atrás/adelante y ofrecen estado vacío. Sin JavaScript se mantiene todo el catálogo navegable. Las fichas ofrecen tallas y galería, y preparan un mensaje de WhatsApp con nombre, referencia, talla y número de foto. Ningún clic confirma una compra ni envía el mensaje automáticamente.

## Antes de reemplazar v1

Revisar visualmente con Mónica la paleta digital, el tratamiento del nombre y la tipografía. Verificar inventario y condiciones comerciales. Comprobar el recorrido en un teléfono real desde Instagram y WhatsApp. Decidir la promoción a raíz manteniendo las rutas antiguas o sus redirecciones; entonces ajustar canonicals, sitemap, robots e indexación. Esta carpeta no activa ese cambio.
