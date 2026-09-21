---
title: I updated the blog design
slug: actualice-mi-blog-nuevo-diseno-colores-y-detalles
created: '2026-09-19'
updated: '2026-09-19'
description: How I went from DaisyUI and Stitch to then using Open Design, why I chose
  green as an accent and what changed in tags, navigation, typography and translations.
tags:
  - blog
  - design
  - update
lang: en
lang_group: actualice-mi-blog-nuevo-diseno-colores-y-detalles
---

I updated my blog. I was using [DaisyUI](https://daisyui.com/) before, I had chosen it because it was what I used in a project at my previous company, and it's fine, it's good.

I chose those muted blues thinking about accessibility: I wanted it to be friendly for people who don't perceive colors like the majority. I looked up information about color blindness, which is why I went for soft tones, watching out for contrast and shapes. In the end, the design didn't quite convince me and I wanted to try something else, but I stopped iterating on it at the time.

To redesign I tried AI tools. First [Stitch](https://stitch.withgoogle.com), but when I clicked on a project I had been working on it would freeze (Sep 2026) and then show an error with a face like the one when YouTube dies, it didn't seem like a browser overload error. It seemed broken inside. I took it as a sign that Google might end up killing Stitch.

I looked for alternatives and ended up on [Open Design](https://open-design.ai/), and honestly I'm very excited: unlike Stitch, I can touch the code directly, whether in [VS Code](https://code.visualstudio.com/) or in its built-in editor. It's not just for websites or mobile apps, it also generates design systems, slides and several other things. I feel like it lets me step outside the box of standards without locking me in, and for now I'll stick with it.

I took the opportunity to change several things. Green is one of my favorite colors, a Rolex green, so the accents are now green and the blog already has more of my essence. I haven't checked if it passes [AA contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) yet, I'll adjust it later.

The tags are more colorful and the only new thing in navigation is that you can now navigate to `/tags` after clicking on a tag. The off-topic chat is still the same, with a free name. I also adjusted the layout: the content and chat width tries to respect the [Golden Ratio](https://es.wikipedia.org/wiki/N%C3%BAmero_%C3%A1ureo) (~1.618) so reading is more pleasant to the eye and yes, it looks much better.

Another detail is the language selector. Before it didn't show the active language button; now it shows all three flags and makes it clear which one is selected. It's cleaner to choose between Spanish 🇲🇽, English 🇬🇧 and French 🇫🇷.

The light and dark versions are still there, in case you want to turn the lights on or off. In French, only translated posts appear; pending ones are not shown yet. Now I use conventional and AI translators, but I want to learn French.

Overall, it looks much better. It reminds me of a "default", I suppose AI averages what's most discussed on the internet about how to make this kind of blog, and there's my self-criticism: it's a bit stuck to the corporate style, it needs a more geek touch, a sticker here and there. Still, I like it, I'm happy with the result.

In the end, this blog will be the showcase of my mantras and my ways of thinking; even if it's not always that organized, this design is the ideal I'd like to aspire to.

### Before and after

Instead of hosting the images myself, I leave them on Internet Archive so they stand as a record as time passes, whether it feels alive or dead depending on what remains. Here's the before and after:

<div id="compare-images" style="display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; margin: 16px 0;">
  <figure style="flex: 1 1 300px; margin: 0; border: 1px solid var(--border-strong); border-radius: 6px; overflow: hidden; background-color: var(--bg-surface);">
    <a href="https://web.archive.org/web/20260920011434/http://web.archive.org/screenshot/https://blog.chrislabs.net/en/" target="_blank" rel="noopener">
      <img src="https://web.archive.org/web/20260920011434/http://web.archive.org/screenshot/https://blog.chrislabs.net/en/" alt="Screenshot of the blog before the redesign" loading="lazy" style="width: 100%; height: auto; display: block;">
    </a>
    <figcaption style="padding: 8px 12px; font-size: 0.85em; color: var(--text-muted); text-align: center;">Before, screenshot from Sep 19, 2026 via Internet Archive. <a href="https://web.archive.org/web/20260920011434/http://web.archive.org/screenshot/https://blog.chrislabs.net/en/" target="_blank" rel="noopener">View original</a></figcaption>
  </figure>
  <figure style="flex: 1 1 300px; margin: 0; border: 1px solid var(--border-strong); border-radius: 6px; overflow: hidden; background-color: var(--bg-surface);">
    <a href="https://web.archive.org/web/20260921092939/http://web.archive.org/screenshot/https://blog.chrislabs.net/es/" target="_blank" rel="noopener">
      <img src="https://web.archive.org/web/20260921092939/http://web.archive.org/screenshot/https://blog.chrislabs.net/es/" alt="Screenshot of the blog after the redesign" loading="lazy" style="width: 100%; height: auto; display: block;">
    </a>
    <figcaption style="padding: 8px 12px; font-size: 0.85em; color: var(--text-muted); text-align: center;">After, new design (Rolex green, Golden Ratio layout, colorful tags)</figcaption>
  </figure>
</div>

<details style="border: 1px solid var(--border-strong); border-radius: 6px; padding: 12px 16px; background-color: var(--bg-surface); margin: 16px 0;">
<summary style="cursor: pointer; font-weight: 600;">Notas de voz — Cómo actualicé mi blog (de DaisyUI a Open Design)</summary>
<p style="color: var(--text-muted); font-size: 0.9em; margin: 8px 0 12px;">Las grabé mientras hacía el análisis — 10 min hablando de DaisyUI y accesibilidad, el fallo de Stitch, por qué elegí Open Design y el verde Rolex.</p>
<audio controls preload="none" style="width: 100%;">
  <source src="/drafts/handy-1789869763.opus" type="audio/opus" />
  <source src="/drafts/handy-1789869763.mp3" type="audio/mpeg" />
  <source src="/drafts/handy-1789869763.wav" type="audio/wav" />
  Your browser doesn't support audio. <a href="/drafts/handy-1789869763.opus">Download OPUS (907KB)</a> / <a href="/drafts/handy-1789869763.mp3">MP3 (2.4MB)</a> / <a href="/drafts/handy-1789869763.wav">WAV (19MB)</a>
</audio>
</details>
