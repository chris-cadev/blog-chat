---
title: "Hack de foto 3D para Facebook sin iPhone"
created: 2018-11-10
updated: 2026-09-29
origin_link: "https://www.facebook.com/hangingpixels/posts/pfbid0jdGR2MTLDEpbpKuupembkTngoJANph8XcyCZaSfo5PSAvkCxSEtp42VgbPBcZKsEl"
description: "Oat Vaiyaboon de Hangingpixels creó un depth map manual en Photoshop para subir fotos de DSLR y dron como 3D Photo en Facebook. 12 intentos para acertar."
slug: hack-foto-3d-facebook-ios
tags:
  - facebook-import
  - fotografia
  - 3dphoto
  - photoshop
lang: es
lang_group: hack-foto-3d-facebook-ios
---

En ese tiempo estaba medio metido en el tema de las cámaras y la fotografía. **Esta foto de [Hangingpixels Photo Art](https://www.facebook.com/hangingpixels) se veía bien perro.** El autor es [Oat Vaiyaboon](https://lumecube.com/blogs/ambassador/oat-vaiyaboon), un fotógrafo australiano.

![Josh de Drake & Josh diciendo "Quiero intentarlo"](/static/posts/drake-josh-quiero-intentarlo.gif)

<iframe src="https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2Fhangingpixels%2Fposts%2Fpfbid0jdGR2MTLDEpbpKuupembkTngoJANph8XcyCZaSfo5PSAvkCxSEtp42VgbPBcZKsEl&width=500" title="Publicación original de Hangingpixels Photo Art en Facebook" style="width:100%; max-width:500px; height:1000px; border:0;" frameborder="0"></iframe>

Facebook lanzó la función 3D Photos en 2018, diseñada para fotos de modo retrato de iPhones con doble cámara. El problema: solo funcionaba con fotos que ya tuvieran un depth map generado por el hardware del teléfono.

**Vaiyaboon hackeó el sistema.** Creó su propio depth map manualmente en Photoshop: cada capa de la foto convertida a escala de grises con opacidades distintas. Luego combinó la foto original y el depth map con la app iOS [DepthCam](https://apps.apple.com/us/app/depth-cam-depth-editor/id1261191886) para generar un archivo JPEG con los metadatos de profundidad que Facebook interpreta como foto de modo retrato.

La lógica del depth map es simple: **más oscuro = más cerca de la cámara, más claro = más lejos.**

<div style="display:flex; border-radius:4px; overflow:hidden; margin:12px 0;">
  <div style="flex:1; background-color:#000; color:#fff; text-align:center; padding:8px 4px; font-size:0.75rem;">100%<br>negro</div>
  <div style="flex:1; background-color:#333; color:#fff; text-align:center; padding:8px 4px; font-size:0.75rem;">80%</div>
  <div style="flex:1; background-color:#666; color:#fff; text-align:center; padding:8px 4px; font-size:0.75rem;">60%</div>
  <div style="flex:1; background-color:#999; color:#fff; text-align:center; padding:8px 4px; font-size:0.75rem;">40%</div>
  <div style="flex:1; background-color:#fff; color:#000; text-align:center; padding:8px 4px; font-size:0.75rem;">0%<br>blanco</div>
</div>
<p style="font-size:0.85rem; color:var(--text-faint); text-align:center;">Primer plano → Fondo. Cada capa de la foto se convierte a un gris distinto en el depth map.</p>

El resultado: fotos de DSLR y dron funcionando como 3D Photo en Facebook. **Le tomó 12 intentos conseguir el depth map bien.**

**Equipo:** Canon 5D III, Canon 16-35mm f/2.8, Kase filters GND 0.9, CPL, ND64

**Recursos:**

- [Tutorial por Marc Keegan](https://marckeegan.com/facebook-3d-photos/)
- [Cobertura en Fstoppers](https://fstoppers.com/originals/hacking-portrait-mode-create-3d-parallax-photo-facebook-189359)
- [Cobertura en PetaPixel](https://petapixel.com/2018/10/23/photographer-turns-drone-shot-into-a-facebook-3d-photo/)

Yo nunca intenté esto directamente. Creo que sí lo intenté después, pero con cosas de After Effects o por ahí. Nunca lo logré publicando una foto en Facebook.
