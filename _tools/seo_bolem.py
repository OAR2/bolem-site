"""Source-grounded search metadata and useful editorial content for BOLEM."""
import html
import re

CATEGORIES = {
 'vestido': ('vestidos-plus-size', 'Vestidos plus size en El Salvador', 'Vestidos largos, midi y para eventos. Compará fotos, precios y tallas de cada pieza; te ayudamos por WhatsApp a elegir antes de apartar.', 'Antes de elegir un vestido', 'Revisá las tallas de la ficha y contanos cómo preferís que te quede en busto y cintura. Si te interesa el largo o la tela, pedinos las medidas y composición de esa pieza: no todos los vestidos tienen el mismo ajuste.'),
 'blusa': ('blusas-plus-size', 'Blusas plus size en El Salvador', 'Blusas, camisas, tops y chalecos para combinar a tu manera. Encontrá el precio y las tallas de cada prenda y consultá disponibilidad por WhatsApp.', 'Elegí pensando en tu combinación', 'Usá el escote, las mangas y el largo que ves en las fotos como punto de partida. Para comparar el ajuste, medí una blusa similar que ya te quede bien y preguntanos por la prenda que te gustó.'),
 'pantalon': ('jeans-y-pantalones-plus-size', 'Jeans y pantalones plus size en El Salvador', 'Jeans flare y pantalones de distintos cortes. Consultá las tallas, el precio y las fotos de cada pieza, con asesoría y envíos a todo El Salvador.', 'Qué revisar en un pantalón', 'Compará cintura, cadera y largo con un pantalón que uses. Decinos si la medida es el ancho de la prenda extendida o el contorno completo. No asumás que dos pantalones con la misma etiqueta tienen las mismas medidas.'),
 'conjunto': ('conjuntos-plus-size', 'Conjuntos plus size en El Salvador', 'Conjuntos para llevar juntos o combinar por separado. Mirá fotos, precios y tallas de cada opción; coordiná tu pedido y envío por WhatsApp.', 'Un conjunto, dos ajustes', 'Revisá cómo querés que te quede cada pieza del conjunto. Si normalmente usás tallas distintas arriba y abajo, consultanos antes de apartar para revisar las medidas y las opciones de esa referencia.'),
}

PAGES = {
 '': ('Ropa plus size en El Salvador | BOLEM', 'Descubrí ropa plus size en El Salvador: vestidos, blusas, jeans y conjuntos. Tallas XL a 4XL según la prenda. Asesoría y pedidos por WhatsApp.'),
 'coleccion/': ('Colección de ropa plus size en El Salvador | BOLEM', 'Explorá vestidos, blusas, pantalones y conjuntos BOLEM. Filtrá por talla y precio, mirá cada prenda y consultá disponibilidad por WhatsApp.'),
 'tallas': ('Guía de tallas plus size: XL, 1XL a 4XL | BOLEM', 'XL y 1XL no siempre son equivalentes. Aprendé a comparar medidas de una prenda y pedí asesoría de talla antes de comprar en BOLEM.'),
 'nosotras': ('BOLEM: moda plus size elegida por Mónica en El Salvador', 'Conocé la historia de BOLEM, nacida de la experiencia de la mamá y la hermana de Mónica. Ropa importada y atención cercana en El Salvador.'),
 'cambios': ('Envíos y cambios de talla en El Salvador | BOLEM', 'Consultá las tarifas de envío, tiempos de entrega y condiciones para solicitar un cambio de talla en tus pedidos de ropa BOLEM.'),
 'privacidad': ('Política de privacidad y datos personales | BOLEM', 'Conocé cómo BOLEM trata tus datos de contacto y pedidos, para qué los utiliza y cómo consultar sobre tu privacidad.'),
 'terminos': ('Términos de compra, pagos y pedidos | BOLEM', 'Revisá las condiciones de compra de BOLEM: pedidos por WhatsApp, confirmación de disponibilidad, precios, pagos y entregas en El Salvador.'),
 'blog/': ('Guías de tallas y moda plus size en El Salvador | BOLEM', 'Resolvé dudas sobre XL y 1XL, cómo comparar medidas y cómo encontrar opciones en 4XL. Consejos prácticos e historias de BOLEM.'),
 'blog/tallas-xl-1xl-plus-size': ('¿XL y 1XL son lo mismo? Cómo elegir tu talla | BOLEM', 'En BOLEM algunas prendas tienen XL y 1XL por separado. Mirá ejemplos del catálogo y qué medidas consultar antes de elegir tu talla.'),
 'blog/guia-tallas-plus-size': ('Cómo medir una prenda para elegir tu talla plus size | BOLEM', 'Compará busto, cintura, cadera y largo con una prenda que ya usás. Prepará tus medidas y consultá el ajuste de tu próxima prenda BOLEM.'),
 'blog/por-que-casi-no-existe-la-4xl': ('Ropa en talla 4XL en El Salvador: cómo encontrarla | BOLEM', 'Encontrá las prendas que incluyen 4XL en el catálogo BOLEM. Aprendé a usar el filtro y qué confirmar sobre medidas y disponibilidad.'),
 'blog/looks-plus-size-clima-calido': ('Ideas de looks plus size para clima cálido | BOLEM', 'Explorá vestidos, blusas y conjuntos para combinar a tu manera. Qué consultar sobre tela, forro y ajuste antes de elegir ropa para el calor.'),
 'blog/como-elegimos-la-ropa': ('Cómo elige Mónica la ropa plus size de BOLEM', 'BOLEM selecciona e importa ropa terminada para mujeres plus size en El Salvador. Conocé qué podés consultar sobre cada pieza antes de pedirla.'),
 'blog/historia-bolem-moda-plus-size-el-salvador': ('La historia de BOLEM: moda plus size en El Salvador', 'La experiencia de la mamá y la hermana de Mónica dio origen a BOLEM. Conocé la historia y nuestra forma de acompañarte al elegir ropa.'),
}

ARTICLES = {
 'tallas-xl-1xl-plus-size': '''<h2>Un ejemplo del catálogo BOLEM</h2><p>El <a href="../prendas/vestido-maxi-smocked">Vestido Maxi Smocked</a> muestra XL, 1XL y 2XL como opciones distintas. La <a href="../prendas/camisa-fucsia">Camisa Oversize</a> también incluye XL y 1XL. Por eso no reemplazamos una etiqueta por otra al preparar tu consulta.</p><h2>Qué conviene preguntar</h2><ul><li>Las medidas de la talla que te interesa, especialmente busto, cintura o cadera según la prenda.</li><li>Si la tela estira y si la pieza tiene forro o un ajuste particular.</li><li>Qué talla y color están disponibles en ese momento.</li></ul><p>Podés escribir: «Me interesa esta prenda. Uso XL en otra marca; ¿me ayudás a comparar las medidas con la XL y la 1XL de esta pieza?».</p><h2>La talla es una referencia, no una equivalencia universal</h2><p>El catálogo te permite filtrar por la etiqueta; la conversación sobre medidas ayuda a decidir. No publicamos una conversión universal entre XL y 1XL porque el ajuste cambia entre marcas y prendas.</p>''',
 'guia-tallas-plus-size': '''<h2>Prepará una referencia que ya conozcás</h2><p>Elegí una prenda similar a la que querés comprar y que te quede como te gusta. Extendela sobre una superficie plana, sin estirar la tela, y usá una cinta métrica.</p><h2>Qué medidas compartir</h2><ul><li><strong>Blusas y vestidos:</strong> ancho a la altura del busto, cintura si está marcada y largo.</li><li><strong>Pantalones:</strong> cintura, cadera y largo; contanos también si el ajuste que buscás es suelto o cercano al cuerpo.</li><li><strong>Conjuntos:</strong> compará por separado la pieza superior y la inferior.</li></ul><p>Indicá las unidades y si mediste la prenda de lado a lado en plano o el contorno completo. Son medidas diferentes y no conviene mezclarlas.</p><h2>Mandanos la referencia de la pieza</h2><p>En cada ficha BOLEM podés elegir talla y foto antes de abrir WhatsApp. El mensaje incluye la referencia para que podamos hablar de la misma prenda. Agregá tus medidas y las dudas que tengás.</p><p>No tenemos una tabla de medidas publicada para todas las piezas. <a href="../tallas">Consultá nuestra guía de tallas</a> y confirmá las medidas antes de apartar.</p>''',
 'por-que-casi-no-existe-la-4xl': '''<h2>Cómo ver únicamente las opciones en 4XL</h2><ol><li>Abrí la <a href="../coleccion/?talla=4XL">colección filtrada en 4XL</a>.</li><li>Si querés, elegí una categoría: blusas, vestidos, pantalones o conjuntos.</li><li>Abrí la ficha de la prenda para ver sus fotos y precio.</li><li>Consultá por WhatsApp si esa talla y el color que elegiste siguen disponibles.</li></ol><h2>Opciones que incluyen 4XL en el catálogo</h2><p>Podés empezar por la <a href="../prendas/blusa-negra-botones">Blusa Manga Larga</a>, el <a href="../prendas/vestido-broderie-rojo">Vestido Broderie Rojo</a> o la <a href="../prendas/falda-maxi-blanca">Falda Maxi Blanca</a>. La presencia de la talla en la ficha no sustituye la confirmación de existencias.</p><h2>Si un filtro no muestra resultados</h2><p>Probá quitar la categoría para ver todas las piezas con esa etiqueta. También podés contarnos qué tipo de prenda buscás. No todas las referencias llegan a 4XL y no prometemos reposiciones sin confirmarlas.</p>''',
 'looks-plus-size-clima-calido': '''<h2>Tres formas de empezar un look</h2><ul><li><strong>Un vestido:</strong> explorá los <a href="../coleccion/vestidos-plus-size">vestidos de BOLEM</a> y compará largos, mangas y escotes en las fotos.</li><li><strong>Una blusa con tus pantalones favoritos:</strong> elegí entre <a href="../coleccion/blusas-plus-size">blusas, tops y camisas</a> pensando en las piezas que ya usás.</li><li><strong>Un conjunto:</strong> mirá los <a href="../coleccion/conjuntos-plus-size">conjuntos</a> como un look completo y también como dos piezas para combinar.</li></ul><h2>Qué no se puede saber solo por una foto</h2><p>La apariencia no confirma la composición, el grosor ni si la prenda lleva forro. Si la frescura de la tela es decisiva para vos, preguntanos por esa referencia antes de pedirla. No todas las piezas del catálogo tienen la composición publicada.</p><h2>Elegí el ajuste que te gusta</h2><p>Contanos si preferís una silueta suelta o más cercana al cuerpo y compará las medidas con una prenda similar. La mejor combinación empieza por cómo te gusta vestirte.</p>''',
 'como-elegimos-la-ropa': '''<h2>Qué hace BOLEM</h2><p>Mónica elige e importa ropa terminada. BOLEM no presenta estas piezas como diseños propios ni como prendas fabricadas en El Salvador: el trabajo de la marca es ampliar las opciones y acompañarte al elegir.</p><h2>Qué información tenés antes de consultar</h2><p>En cada ficha encontrás fotografías, precio en dólares, tallas del catálogo y una referencia. Algunas prendas tienen varias fotografías o colores; podés seleccionar una foto para incluirla en el mensaje de WhatsApp.</p><h2>Qué confirmamos en la conversación</h2><p>Consultá existencias, color, medidas, composición y ajuste de la prenda concreta. Coordinamos el pago y el envío después de confirmar tu pedido. <a href="../cambios">Las tarifas y condiciones de cambios</a> están disponibles para revisarlas antes de comprar.</p>''',
 'historia-bolem-moda-plus-size-el-salvador': '''<h2>La experiencia que dio origen a la marca</h2><p>Mónica encontraba ropa que le gustaba, mientras su mamá y su hermana se enfrentaban a opciones limitadas en su talla. BOLEM nace de esa experiencia familiar y de la intención de ofrecer más alternativas para mujeres plus size en El Salvador.</p><h2>Cómo se refleja hoy</h2><p>El catálogo reúne vestidos, blusas, pantalones y conjuntos. El rango habitual es XL a 4XL según la prenda; algunas referencias también incluyen L. Cada ficha muestra sus opciones para que puedas empezar por la pieza que te gusta.</p><h2>Atención cercana, desde la elección hasta el pedido</h2><p>Podés conversar por WhatsApp sobre talla, estilo y entrega. La consulta no confirma una compra: primero revisamos disponibilidad y coordinamos los detalles. <a href="../nosotras">Conocé más de BOLEM</a> o <a href="../coleccion/">explorá la colección</a>.</p>''',
}

def escape(value):
    return html.escape(str(value), quote=True)

def metadata_for(route, products):
    if route.startswith('prendas/'):
        p = products[route.split('/')[-1]]
        sizes = ', '.join(p['tallas'])
        price = f"{p['precio']:.2f}".removesuffix('.00')
        if p.get('descripcion'):
            return (f"{p['nombre']} plus size en El Salvador | BOLEM",
                    f"{p['descripcion'].split('. ')[0].rstrip('.')}. ${price} USD. Tallas {sizes}. Consultá disponibilidad en BOLEM; envíos en El Salvador.")
        return (f"{p['nombre']} plus size en El Salvador | BOLEM",
                f"{p['nombre']} por ${price}. Tallas {sizes}. Mirá las fotos y consultá medidas, color y disponibilidad por WhatsApp. Envíos en El Salvador.")
    for cat in CATEGORIES.values():
        if route=='coleccion/'+cat[0]: return cat[1]+' | BOLEM',cat[2]
    return PAGES[route]

def enrich(text, route):
    if route.startswith('prendas/vestido-'):
        guides='<nav class="dress-guides" aria-label="Ayuda para elegir un vestido"><p>Antes de elegir tu vestido</p><a href="../blog/guia-tallas-plus-size">Cómo comparar las medidas</a><a href="../blog/tallas-xl-1xl-plus-size">Diferencias entre XL y 1XL</a><a href="../coleccion/vestidos-plus-size">Comparar todos los vestidos</a></nav>'
        text=text.replace('<p class="sku">',guides+'<p class="sku">',1)
    if route=='tallas' or route in ['blog/guia-tallas-plus-size','blog/tallas-xl-1xl-plus-size','blog/por-que-casi-no-existe-la-4xl','blog/looks-plus-size-clima-calido']:
        base='' if route=='tallas' else '../'
        text=text.replace('</main>',f'<nav class="wrap dress-guide-category" aria-label="Explorar vestidos"><a class="text-link" href="{base}coleccion/vestidos-plus-size">Ver vestidos plus size: fotos, tallas y precios</a></nav></main>')
    if route.startswith('blog/') and route!='blog/':
        extra=ARTICLES[route.split('/')[-1]]
        byline='<p class="article-byline">Por el equipo de BOLEM · Actualizado el <time datetime="2026-09-15">15 de septiembre de 2026</time></p>'
        text=text.replace('<div class="prose wrap">','<div class="prose wrap">'+byline)
        text=text.replace('<a class="text-link" href="../tallas">',extra+'<a class="text-link" href="../tallas">',1)
    return text

def category_page(collection, key, products):
    slug,title,intro,subtitle,advice=CATEGORIES[key]
    subset=[p for p in products.values() if p['categoria']==key]
    text=re.sub(r'<form class="catalog-controls.*?</form>','',collection,flags=re.S)
    text=re.sub(r'<noscript>.*?</noscript>','',text,flags=re.S)
    text=re.sub(r'<div class="empty-state".*?</div>','',text,flags=re.S)
    text=re.sub(r'<article class="product-card".*?</article>',lambda m:m.group() if f'data-category="{key}"' in m.group() else '',text,flags=re.S)
    text=re.sub(r'<header class="catalog-heading wrap">.*?</header>',f'<header class="catalog-heading wrap"><p class="eyebrow">LA COLECCIÓN BOLEM</p><h1>{title}</h1><p class="category-intro">{intro}</p></header>',text,flags=re.S)
    text=re.sub(r'<p id="result-count".*?</p>',f'<p id="result-count">{len(subset)} prendas en esta categoría</p>',text,flags=re.S)
    advice_html=f'<div class="category-advice"><h2>{subtitle}</h2><p>{advice}</p><p><a class="text-link" href="../tallas">Guía de tallas</a> · <a class="text-link" href="../coleccion/">Ver toda la colección y filtrar por talla</a></p></div>'
    if key=='vestido':
        money=lambda value: ('$'+f'{value:.2f}').removesuffix('.00')
        active=[p for p in subset if not p.get('agotada')]
        prices=([p['precio'] for p in active])
        price_answer=(f"Los vestidos no marcados como agotados van de {money(min(prices))} a {money(max(prices))} USD, sin incluir envío. Cada ficha muestra el precio de esa referencia. Confirmamos disponibilidad antes de apartar." if prices else 'Consultanos por reposiciones y precios antes de apartar.')
        sizes=[s for s in ['L','XL','1XL','2XL','3XL','4XL'] if any(s in p['tallas'] for p in subset)]
        size_links=''.join(f'<a href="../coleccion/?talla={s}&amp;categoria=vestido">{s}</a>' for s in sizes)
        quick=f'<nav class="dress-size-links" aria-label="Buscar vestidos por talla"><span>Explorá por talla</span>{size_links}</nav><p class="dress-size-note">Las tallas corresponden al catálogo. Confirmá existencias por WhatsApp.</p>'
        text=text.replace('<div class="catalog-count">',quick+'<div class="catalog-count">',1)
        faqs=[
          ('¿Qué tallas tienen los vestidos?',f'En esta categoría encontrás {", ".join(sizes)} según el modelo. Cada vestido tiene sus propias opciones; XL y 1XL no son equivalentes automáticas. <a href="../blog/tallas-xl-1xl-plus-size">Mirá cómo comparar XL y 1XL</a>.'),
          ('¿Cuánto cuestan?',price_answer),
          ('¿Cómo pido un vestido?', 'Abrí su ficha, elegí una talla y, si hay varias fotos, seleccioná la del color que te interesa. Tocá «Consultar por WhatsApp». El mensaje incluye la referencia; confirmamos talla, color, disponibilidad, pago y entrega antes de apartar.'),
          ('¿Hacen envíos en El Salvador?', 'Sí. El envío cuesta $3.50 en el área metropolitana y $5 en el resto del país, con entrega de 1 a 3 días hábiles. Podés pagar en efectivo contra entrega o por transferencia. <a href="../cambios">Consultá las condiciones de envío y cambios</a>.'),
          ('¿Cómo elijo la talla si no puedo probarme el vestido?', 'Compará con un vestido que ya te quede bien y compartinos sus medidas de busto, cintura y largo, indicando si mediste ancho plano o contorno. Consultá las medidas de la pieza que te gusta. <a href="../blog/guia-tallas-plus-size">Seguí esta guía para medir una prenda</a>.'),
          ('¿Puedo solicitar un cambio de talla?', 'Podés solicitarlo dentro de los 2 días de recibir la prenda, sin uso y con etiquetas, sujeto a disponibilidad. <a href="../cambios">Revisá la política completa antes de comprar</a>.')]
        advice_html += '<section class="dress-faq" aria-labelledby="dress-faq-title"><h2 id="dress-faq-title">Antes de pedir tu vestido</h2>'+''.join(f'<details><summary>{question}</summary><p>{answer}</p></details>' for question,answer in faqs)+'</section>'
    text=text.replace('<div class="catalog-help">',advice_html+'<div class="catalog-help">')
    return text,subset
