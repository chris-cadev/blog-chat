---
title: Actualicé el diseño del blog
created: '2026-09-19'
updated: '2026-09-19'
description: Cómo pasé de DaisyUI y Stitch a luego usar Open Design, por qué elegí el
  verde como acento y qué cambió en tags, navegación, tipografía y traducciones.
tags:
- blog
- diseño
- update
slug: actualice-mi-blog-nuevo-diseno-colores-y-detalles
lang: es
lang_group: actualice-mi-blog-nuevo-diseno-colores-y-detalles
---

Actualicé mi blog. Antes usaba [DaisyUI](https://daisyui.com/), lo había elegido porque fue lo que usé en un proyecto de mi empresa anterior, y está bien, es bueno.

Escogí esos azules apagados pensando en accesibilidad: quería que fuera amable para quienes no perciben los colores como la mayoría. Busqué información sobre daltonismo y por eso opté por tonos tenues, cuidando contrastes y formas. Al final, el diseño no me terminaba de convencer y quise probar otra cosa, pero lo dejé de iterar en su momento.

Para rediseñar probé con IA. Primero [Stitch](https://stitch.withgoogle.com), pero al hacer clic en un proyecto que había estado trabajando se congelaba (sep 2026) y luego marcaba error con una carita como la que sale cuando se muere YouTube, no parecía error de sobrecarga del navegador. Parecía roto por dentro. Lo tomé como síntoma de que Google quizá termine matando Stitch.

Busqué alternativas y terminé en [Open Design](https://open-design.ai/), y la verdad estoy muy entusiasmado: a diferencia de Stitch, puedo tocar el código directamente, ya sea en [VS Code](https://code.visualstudio.com/) o en su editor integrado. No solo sirve para páginas o apps móviles, también genera design systems, slides y varias cosas más. Siento que me deja salir de la caja de los estándares sin quedarme encerrado, y por ahora me quedaré con él.

Aproveché para cambiar varias cosas. El verde es uno de mis colores favoritos, un verde tipo Rolex, así que los acentos ahora son verdes y el blog ya tiene más de mi esencia. Aún no verifiqué si pasa [contraste AA](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), lo ajustaré más adelante.

Los tags son más coloridos y lo único nuevo en navegación es que ahora puedes navegar a `/tags` después de hacer clic en un tag. El chat off-topic sigue igual, con nombre libre. También ajusté el layout: el ancho del contenido y el chat intenta respetar el [Golden Ratio](https://es.wikipedia.org/wiki/N%C3%BAmero_%C3%A1ureo) (~1.618) para que la lectura sea más agradable al ojo y, sí, se ve bastante mejor.

Otro detalle es el selector de idioma. Antes no mostraba el botón del idioma activo; ahora muestra las tres banderitas y deja claro cuál está seleccionado. Queda más limpio poder elegir entre Español 🇲🇽, Inglés 🇬🇧 y Francés 🇫🇷.

Las versiones clara y oscura siguen ahí, por si quieres prender o apagar las luces. En francés solo aparecen los posts ya traducidos; los pendientes aún no se muestran. Ahora uso traductores convencionales y de IA, pero quiero aprender francés.

En conjunto, a la vista está mucho mejor. Me recuerda a un «default», supongo que la IA promedia lo que más se comenta en internet sobre cómo hacer un blog de este tipo, y ahí está mi autocrítica: está un poco pegado al estilo corporativo, le falta un toque más geek, algún sticker por ahí. Aun así me agrada, estoy contento con el resultado.

Al final, este blog será el escaparate de mis mantras y de mis formas de pensar; aunque no siempre sea tan ordenado, este diseño es el ideal al que me gustaría aspirar.

### Antes y después

En vez de alojar las imágenes yo mismo, las dejo en Internet Archive para que quede testimonio aunque pase el tiempo, que se sienta vivo o muerto según lo que quede. Aquí el antes y después:

<div id="compare-images" style="display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; margin: 16px 0;">
  <figure style="flex: 1 1 300px; margin: 0; border: 1px solid var(--border-strong); border-radius: 6px; overflow: hidden; background-color: var(--bg-surface);">
    <a href="https://web.archive.org/web/20260920011434/http://web.archive.org/screenshot/https://blog.chrislabs.net/en/" target="_blank" rel="noopener">
      <img src="https://web.archive.org/web/20260920011434/http://web.archive.org/screenshot/https://blog.chrislabs.net/en/" alt="Captura del blog antes del rediseño" loading="lazy" style="width: 100%; height: auto; display: block;">
    </a>
    <figcaption style="padding: 8px 12px; font-size: 0.85em; color: var(--text-muted); text-align: center;">Antes,  captura del 19 sep 2026 vía Internet Archive. <a href="https://web.archive.org/web/20260920011434/http://web.archive.org/screenshot/https://blog.chrislabs.net/en/" target="_blank" rel="noopener">Ver original</a></figcaption>
  </figure>
  <figure style="flex: 1 1 300px; margin: 0; border: 1px solid var(--border-strong); border-radius: 6px; overflow: hidden; background-color: var(--bg-surface);">
    <a href="https://web.archive.org/web/20260921092939/http://web.archive.org/screenshot/https://blog.chrislabs.net/es/" target="_blank" rel="noopener">
      <img src="https://web.archive.org/web/20260921092939/http://web.archive.org/screenshot/https://blog.chrislabs.net/es/" alt="Captura del blog despues del rediseño" loading="lazy" style="width: 100%; height: auto; display: block;">
    </a>
    <figcaption style="padding: 8px 12px; font-size: 0.85em; color: var(--text-muted); text-align: center;">Después,  nuevo diseño (verde Rolex, Golden Ratio en layout, tags coloridos)</figcaption>
  </figure>
</div>

<details style="border: 1px solid var(--border-strong); border-radius: 6px; padding: 12px 16px; background-color: var(--bg-surface); margin: 16px 0;">
<summary style="cursor: pointer; font-weight: 600;">🎧 Notas de voz — Cómo actualicé mi blog (de DaisyUI a Open Design)</summary>
<p style="color: var(--text-muted); font-size: 0.9em; margin: 8px 0 12px;">Las grabé mientras hacía el análisis — 10 min hablando de DaisyUI y accesibilidad, el fallo de Stitch, por qué elegí Open Design y el verde Rolex.</p>
<audio controls preload="none" style="width: 100%;">
  <source src="/drafts/handy-1789869763.opus" type="audio/opus" />
  <source src="/drafts/handy-1789869763.mp3" type="audio/mpeg" />
  <source src="/drafts/handy-1789869763.wav" type="audio/wav" />
  Tu navegador no soporta audio. <a href="/drafts/handy-1789869763.opus">Descargar OPUS (907KB)</a> / <a href="/drafts/handy-1789869763.mp3">MP3 (2.4MB)</a> / <a href="/drafts/handy-1789869763.wav">WAV (19MB)</a>
</audio>
</details>
