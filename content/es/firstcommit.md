---
title: 'FirstCommit: Micro herramienta'
slug: firstcommit
tags:
  - proyecto
  - herramienta
  - git
  - github
  - python
  - software
created: '2025-10-17'
updated: '2025-10-17'
description: Una micro herramienta en Python para descubrir el primer commit de cualquier repositorio
  en GitHub. Desarrollada por Christian Camacho y desplegada en Vercel.
lang: es
lang_group: firstcommit
---

Quería saber cuándo había empezado un proyecto viejo. Busqué una herramienta que me diera el primer commit de cualquier repo en GitHub y solo encontré cosas para historial personal. Me enojé un poco y la hice yo.

Pega cualquier URL pública abajo y ves fecha, autor y mensaje original sin clonar nada.

<iframe loading="lazy" src="https://firstcommit.debugchris.com" title="FirstCommit - primer commit de un repo en GitHub" style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>

Estaba por terminar la guardia del viernes en planta cuando me quedé pensando en ese proyecto. Quería la fecha exacta de inicio, no un aproximado.

Busqué un rato. Todo lo que encontraba pedía tu usuario o analizaba tu perfil, nada pensado para un repositorio ajeno. Después de un rato me dije *lo hago yo*.

Hoy montar algo así cuesta poco. Unos prompts y tenés un sitio funcional en Vercel que tus colegas pueden abrir. Unos prompts más y un par de bugs después, ya tenía algo sencillo que podía publicar con confianza. Sin login, sin clonar, solo pegar la URL.

Está hecho con Python, podés ver el código en el [repositorio first-commit en GitHub](https://github.com/chris-cadev/first-commit/).
