---
title: "L'enfer des helpers"
slug: helpers-hell
created: '2025-01-10'
updated: '2026-09-29'
description: 'Les discussions inutiles sur les "helpers" et le nommage détournent l''attention de l''essentiel : la logique métier et la simplicité.'
lang: fr
lang_group: helpers-hell
tags:
  - logiciel
  - code
  - développement
---

![Représentation de l'enfer des helpers : chaos de noms et de discussions](../assets/helpers-hell-representation.webp)

Il y a quelques jours, en travaillant sur quelque chose avec React, j'ai réalisé qu'il y avait déjà deux projets où les _helpers_ sont partout, et parfois ils arrivent même à l'étape de _code review_, avec des discussions sur la question de savoir si une méthode, une classe ou un fichier devrait être appelé _helper_ ou non. C'est généralement fastidieux.

En cherchant sur Internet pour voir si c'était quelque chose qui m'avait seulement touché, j'ai trouvé que c'est plus un moyen d'éviter de tomber dans l'autre _rabbit hole_ : ne pas savoir comment nommer les choses quand il s'agit de programmer.

Dans les vingt minutes que j'ai passées à chercher, j'ai trouvé un [post sur Reddit](https://www.reddit.com/r/AskProgramming/comments/d4o6i2/best_practices_for_implementation_of_helper/) qui mentionne que le problème potentiel est que nous exprimons directement nos propres modèles de pensée dans les noms que nous donnons aux fonctions. Il n'y a rien de mal en ça, mais cela peut nous limiter.

Je suis d'accord avec cet argument. Il y a des moments où les discussions tournent uniquement autour de la façon de nommer quelque chose. Ce qui nous limite, c'est que ces petits blocs nous éloignent de ce qui compte vraiment dans le code que nous programmons :

> la _logique métier_

La logique métier est ce qui nous permet de distinguer si les exigences sont bien exprimées dans des lignes de code, pas les noms que nous donnons aux variables. **Les bons noms, la claire expressivité et l'expérience sont les éléments qui apportent vraiment de la valeur.** Et cette expérience ne vient pas seulement du travail : aussi d'une sortie au parc avec la famille, avec des amis, lors d'une fête bien organisée.

Ce qui rend le travail monotone aujourd'hui, ce n'est pas le travail lui-même : il y a des problèmes amusants et divers, pas de jour comme le précédent. Ce qui génère des obstacles mentaux, ce sont ces limitations subtiles.

Donc, voici une idée : **arrêter d'appeler _"helpers"_ quelque chose qui, en réalité, sont des fonctions.**

Des gens avant nous, à travers des livres comme _Clean Code_, _Clean Architecture_ et bien d'autres, l'ont déjà exprimé : il faut faire les choses simples. Je me souviens d'une règle qu'une maîtresse de bases de données à UTT nous a enseignée : **KISS – Keep It Simple, Stu\*\*\***. C'était amusant à l'époque, mais cela reflète comment les gens avaient tendance à compliquer les choses.

Jusqu'à quand allons-nous rester passifs dans notre travail ? Combien de temps devons-nous attendre pour mûrir et prendre les rênes ?

Je vous invite à vous demander : ce qui est discuté dans cette _code review_ ou ce _meeting_ est-il une vraie limitation, ou sommes-nous simplement en train de tomber dans la **loi de la trivialité de Parkinson** ?
