---
title: 'FirstCommit : Micro Outil'
slug: firstcommit
tags:
  - projet
  - outil
  - git
  - github
  - python
created: '2025-10-17'
updated: '2025-10-17'
description: Un micro outil en Python pour découvrir le premier commit de n'importe quel dépôt
  GitHub. Développé par Christian Camacho et déployé sur Vercel.
lang: fr
lang_group: firstcommit
---

Je voulais savoir quand j'avais commencé un vieux projet. J'ai cherché un outil qui donne le premier commit de n'importe quel dépôt GitHub et je n'ai trouvé que des outils pour l'historique personnel. Je me suis énervé et je l'ai fait moi-même.

Collez une URL publique ci-dessous. Vous verrez date, auteur et message d'origine sans cloner.

<iframe loading="lazy" src="https://firstcommit.debugchris.com" title="FirstCommit - premier commit d'un dépôt GitHub" style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>

J'allais terminer ma garde du vendredi à l'usine quand ce projet m'est revenu en tête. Je voulais la date exacte du début, pas une approximation.

J'ai cherché un moment. Tout ce que je trouvais demandait votre nom d'utilisateur ou analysait votre profil, rien pour un dépôt qui n'est pas le vôtre. Au bout d'un moment je me suis dit *je le fais moi-même*.

Aujourd'hui, monter ce genre de chose coûte peu. Quelques prompts et vous avez un site fonctionnel sur Vercel que vos collègues peuvent ouvrir. Quelques prompts de plus et deux ou trois bugs corrigés, j'avais quelque chose de simple que je pouvais publier avec confiance. Sans connexion, sans clonage. Juste coller l'URL.

C'est fait en Python. Le code est sur le [dépôt first-commit sur GitHub](https://github.com/chris-cadev/first-commit/).
