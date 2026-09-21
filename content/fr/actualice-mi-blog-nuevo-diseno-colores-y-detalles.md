---
title: J'ai mis à jour le design du blog
slug: actualice-mi-blog-nuevo-diseno-colores-y-detalles
created: '2026-09-19'
updated: '2026-09-19'
description: Comment je suis passé de DaisyUI et Stitch à utiliser Open Design, pourquoi
  j'ai choisi le vert comme accent et ce qui a changé dans les tags, la navigation,
  la typographie et les traductions.
tags:
  - blog
  - design
  - update
lang: fr
lang_group: actualice-mi-blog-nuevo-diseno-colores-y-detalles
---

J'ai mis à jour mon blog. Avant, j'utilisais [DaisyUI](https://daisyui.com/), je l'avais choisi parce que c'était ce que j'avais utilisé dans un projet de mon ancienne entreprise, et c'est bien, c'est bon.

J'ai choisi ces bleus ternes en pensant à l'accessibilité : je voulais que ce soit agréable pour les personnes qui ne perçoivent pas les couleurs comme la majorité. J'ai cherché des informations sur le daltonisme, c'est pourquoi j'ai opté pour des tons doux, en veillant aux contrastes et aux formes. Au final, le design ne me convenait pas tout à fait et j'ai voulu essayer autre chose, mais j'ai arrêté d'y iterer à l'époque.

Pour refaire le design, j'ai essayé des outils IA. D'abord [Stitch](https://stitch.withgoogle.com), mais quand j'ai cliqué sur un projet sur lequel je travaillais, il se gelait (sep 2026) puis affichait une erreur avec un visage comme celui quand YouTube meurt, ça ne ressemblait pas à une erreur de surcharge du navigateur. Ça semblait cassé de l'intérieur. Je l'ai pris comme un signe que Google finirait peut-être par tuer Stitch.

J'ai cherché des alternatives et j'ai fini sur [Open Design](https://open-design.ai/), et honnêtement je suis très enthousiaste : contrairement à Stitch, je peux toucher le code directement, que ce soit dans [VS Code](https://code.visualstudio.com/) ou dans son éditeur intégré. Ça ne sert pas seulement pour les sites web ou les apps mobiles, ça génère aussi des design systems, des slides et plusieurs autres choses. J'ai l'impression que ça me permet de sortir du cadre des standards sans m'y enfermer, et pour l'instant je vais rester avec.

J'en ai profité pour changer plusieurs choses. Le vert est l'une de mes couleurs préférées, un vert Rolex, donc les accents sont maintenant verts et le blog a déjà plus de mon essence. Je n'ai pas encore vérifié si ça passe le [contraste AA](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), j'ajusterai plus tard.

Les tags sont plus colorés et la seule nouveauté dans la navigation, c'est que maintenant on peut naviguer vers `/tags` après avoir cliqué sur un tag. Le chat off-topic reste identique, avec un nom libre. J'ai aussi ajusté la mise en page : la largeur du contenu et du chat essaie de respecter le [nombre d'or](https://es.wikipedia.org/wiki/N%C3%BAmero_%C3%A1ureo) (~1.618) pour que la lecture soit plus agréable à l'œil et oui, c'est beaucoup mieux.

Un autre détail, c'est le sélecteur de langue. Avant, il n'affichait pas le bouton de la langue active ; maintenant il montre les trois drapeaux et indique clairement lequel est sélectionné. C'est plus propre de pouvoir choisir entre Espagnol 🇲🇽, Anglais 🇬🇧 et Français 🇫🇷.

Les versions claire et sombre sont toujours là, si on veut allumer ou éteindre les lumières. En français, seuls les posts déjà traduits apparaissent ; les en cours ne sont pas encore affichés. Maintenant j'utilise des traducteurs classiques et de l'IA, mais je veux apprendre le français.

Dans l'ensemble, c'est beaucoup mieux à l'œil. Ça me rappelle un « default », je suppose que l'IA fait la moyenne de ce qui se discute le plus sur internet pour faire ce type de blog, et voilà mon autocritique : c'est un peu collé au style corporatif, il manque une touche plus geek, un sticker par ici ou par là. Malgré tout, ça me plaît, je suis content du résultat.

Au final, ce blog sera la vitrine de mes mantras et de mes façons de penser ; même si ce n'est pas toujours aussi ordonné, ce design est l'idéal auquel j'aimerais aspirer.

### Avant et après

Au lieu d'héberger les images moi-même, je les laisse sur Internet Archive pour que ça reste un témoignage même avec le temps, que ça se sente vivant ou mort selon ce qui reste. Voici l'avant et l'après :

<div id="compare-images" style="display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; margin: 16px 0;">
  <figure style="flex: 1 1 300px; margin: 0; border: 1px solid var(--border-strong); border-radius: 6px; overflow: hidden; background-color: var(--bg-surface);">
    <a href="https://web.archive.org/web/20260920011434/http://web.archive.org/screenshot/https://blog.chrislabs.net/en/" target="_blank" rel="noopener">
      <img src="https://web.archive.org/web/20260920011434/http://web.archive.org/screenshot/https://blog.chrislabs.net/en/" alt="Capture d'écran du blog avant le redesign" loading="lazy" style="width: 100%; height: auto; display: block;">
    </a>
    <figcaption style="padding: 8px 12px; font-size: 0.85em; color: var(--text-muted); text-align: center;">Avant, capture du 19 sep 2026 via Internet Archive. <a href="https://web.archive.org/web/20260920011434/http://web.archive.org/screenshot/https://blog.chrislabs.net/en/" target="_blank" rel="noopener">Voir l'original</a></figcaption>
  </figure>
  <figure style="flex: 1 1 300px; margin: 0; border: 1px solid var(--border-strong); border-radius: 6px; overflow: hidden; background-color: var(--bg-surface);">
    <a href="https://web.archive.org/web/20260921092939/http://web.archive.org/screenshot/https://blog.chrislabs.net/es/" target="_blank" rel="noopener">
      <img src="https://web.archive.org/web/20260921092939/http://web.archive.org/screenshot/https://blog.chrislabs.net/es/" alt="Capture d'écran du blog après le redesign" loading="lazy" style="width: 100%; height: auto; display: block;">
    </a>
    <figcaption style="padding: 8px 12px; font-size: 0.85em; color: var(--text-muted); text-align: center;">Après, nouveau design (vert Rolex, mise en page au nombre d'or, tags colorés)</figcaption>
  </figure>
</div>

<details style="border: 1px solid var(--border-strong); border-radius: 6px; padding: 12px 16px; background-color: var(--bg-surface); margin: 16px 0;">
<summary style="cursor: pointer; font-weight: 600;">Notes vocales — Comment j'ai mis à jour mon blog (de DaisyUI à Open Design)</summary>
<p style="color: var(--text-muted); font-size: 0.9em; margin: 8px 0 12px;">Je les ai enregistrées pendant l'analyse — 10 min à parler de DaisyUI et d'accessibilité, de la panne de Stitch, pourquoi j'ai choisi Open Design et le vert Rolex.</p>
<audio controls preload="none" style="width: 100%;">
  <source src="/drafts/handy-1789869763.opus" type="audio/opus" />
  <source src="/drafts/handy-1789869763.mp3" type="audio/mpeg" />
  <source src="/drafts/handy-1789869763.wav" type="audio/wav" />
  Votre navigateur ne supporte pas l'audio. <a href="/drafts/handy-1789869763.opus">Télécharger OPUS (907KB)</a> / <a href="/drafts/handy-1789869763.mp3">MP3 (2.4MB)</a> / <a href="/drafts/handy-1789869763.wav">WAV (19MB)</a>
</audio>
</details>
