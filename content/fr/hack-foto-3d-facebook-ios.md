---
title: "Hack photo 3D pour Facebook sans iPhone"
created: 2018-11-10
updated: 2026-09-29
origin_link: "https://www.facebook.com/hangingpixels/posts/pfbid0jdGR2MTLDEpbpKuupembkTngoJANph8XcyCZaSfo5PSAvkCxSEtp42VgbPBcZKsEl"
description: "Oat Vaiyaboon de Hangingpixels a créé un depth map manuel dans Photoshop pour mettre en ligne des photos de DSLR et de drone comme 3D Photo sur Facebook. 12 tentatives pour y arriver."
slug: hack-foto-3d-facebook-ios
tags:
  - facebook-import
  - photographie
  - photo 3d
  - photoshop
lang: fr
lang_group: hack-foto-3d-facebook-ios
---

À cette époque, j'étais plutôt dans le thème des caméras et de la photographie. **Cette photo de [Hangingpixels Photo Art](https://www.facebook.com/hangingpixels) était trop stylée.** L'auteur est [Oat Vaiyaboon](https://lumecube.com/blogs/ambassador/oat-vaiyaboon), un photographe australien.

![Josh de Drake & Josh disant "J'aimerais essayer"](/static/posts/drake-josh-quiero-intentarlo.gif)

<iframe src="https://www.facebook.com/plugins/post.php?href=https%3A%2F%2Fwww.facebook.com%2Fhangingpixels%2Fposts%2Fpfbid0jdGR2MTLDEpbpKuupembkTngoJANph8XcyCZaSfo5PSAvkCxSEtp42VgbPBcZKsEl&width=500" title="Publication originale de Hangingpixels Photo Art sur Facebook" style="width:100%; max-width:500px; height:1000px; border:0;" frameborder="0"></iframe>

Facebook a lancé la fonction 3D Photos en 2018, conçue pour les photos en mode portrait des iPhones à double caméra. Le problème : ça ne marchait qu'avec les photos qui avaient déjà un depth map généré par le matériel du téléphone.

**Vaiyaboon a hacké le système.** Il a créé son propre depth map manuellement dans Photoshop : chaque calque de la photo converti en niveaux de gris avec des opacités différentes. Puis il a combiné la photo originale et le depth map avec l'app iOS [DepthCam](https://apps.apple.com/us/app/depth-cam-depth-editor/id1261191886) pour générer un fichier JPEG avec les métadonnées de profondeur que Facebook interprète comme photo en mode portrait.

La logique du depth map est simple : **plus c'est sombre, plus c'est proche de la caméra ; plus c'est clair, plus c'est loin.**

<div style="display:flex; border-radius:4px; overflow:hidden; margin:12px 0;">
  <div style="flex:1; background-color:#000; color:#fff; text-align:center; padding:8px 4px; font-size:0.75rem;">100%<br>noir</div>
  <div style="flex:1; background-color:#333; color:#fff; text-align:center; padding:8px 4px; font-size:0.75rem;">80%</div>
  <div style="flex:1; background-color:#666; color:#fff; text-align:center; padding:8px 4px; font-size:0.75rem;">60%</div>
  <div style="flex:1; background-color:#999; color:#fff; text-align:center; padding:8px 4px; font-size:0.75rem;">40%</div>
  <div style="flex:1; background-color:#fff; color:#000; text-align:center; padding:8px 4px; font-size:0.75rem;">0%<br>blanc</div>
</div>
<p style="font-size:0.85rem; color:var(--text-faint); text-align:center;">Gros plan → Arrière-plan. Chaque calque de la photo est converti en un gris différent dans le depth map.</p>

Le résultat : des photos de DSLR et de drone qui fonctionnent comme 3D Photo sur Facebook. **Il lui a fallu 12 tentatives pour réussir le depth map.**

**Équipe :** Canon 5D III, Canon 16-35mm f/2.8, filtres Kase GND 0.9, CPL, ND64

**Ressources :**

- [Tutoriel par Marc Keegan](https://marckeegan.com/facebook-3d-photos/)
- [Couverture sur Fstoppers](https://fstoppers.com/originals/hacking-portrait-mode-create-3d-parallax-photo-facebook-189359)
- [Couverture sur PetaPixel](https://petapixel.com/2018/10/23/photographer-turns-drone-shot-into-a-facebook-3d-photo/)

Moi, je n'ai jamais essayé ça directement. Je crois que je l'ai essayé après, mais avec des trucs After Effects ou un truc comme ça. Je n'ai jamais réussi en publiant une photo sur Facebook.
