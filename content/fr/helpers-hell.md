---
title: L'enfer des "helpers"
slug: helpers-hell
created: '2025-01-10'
updated: '2025-01-10'
description: 'Ce blog explore comment les discussions inutiles sur les « fonctions d''assistance
  » et les conventions de nommage du code peuvent détourner l''attention de l''essentiel
  : la logique métier et la simplicité dans le développement logiciel.'
lang: fr
lang_group: helpers-hell
---

Il y a quelques jours, en travaillant sur quelque chose à React, j'ai réalisé qu'il y avait déjà deux projets dans lesquels je vois des "helpers" partout, et parfois ils arrivent même à l'étape de "code review", avec des discussions sur la question de savoir si une méthode, une classe ou un fichier devrait être appelé "helper" ou non.

En cherchant un peu sur Internet pour voir si c'était quelque chose qui m'avait seulement touché, j'ai trouvé que, apparemment, c'est plus un avantage pour éviter de tomber dans l'autre "rabbit hole": ne pas savoir comment nommer les choses quand il s'agit de programmer.

Dans les 20 minutes que j'ai passées à chercher un peu, j'ai trouvé un [post sur Reddit](https://www.reddit.com/r/AskProgramming/comments/d4o6i2/best_practices_for_implementation_of_helper/) qui mentionne que le problème potentiel est que nous exprimons directement nos propres modèles de pensée dans les noms que nous donnons aux fonctions.

Je suis d'accord avec cet argument. Il y a des moments où les discussions tournent uniquement autour de la façon de nommer quelque chose. Je ne dis pas que nommer des choses est une mauvaise chose; ce qui nous limite, c'est que ces petits blocs nous éloignent de ce qui compte vraiment dans le code que nous programmons:

> la logique des affaires

La _logique des affaires_ est ce qui nous permet de distinguer si les exigences sont bien exprimées dans des lignes de code, pas les noms que nous donnons aux variables. Les bons noms, la claire expressivité dans le code, l'application de modèles de conception et, en général, l'expérience que nous avons déjà soit au travail ou même lors d'une sortie au parc avec la famille, avec des amis, lors d'une fête bien organisée, etc. sont les éléments qui apportent vraiment de la valeur.

Ce qui nous rend monotone du travail aujourd'hui, ce n'est pas le travail lui-même: il y a des problèmes amusants et divers, il n'y a pas de jour comme le précédent. Ce qui génère des obstacles mentaux, tant dans les équipes de travail que dans nous-mêmes, ce sont ces limites subtiles.

C'est pourquoi je vous laisse ici une liste de bonnes pratiques que nous pouvons appliquer, en commençant par arrêter d'appeler _"helpers"_ à quelque chose qui, en réalité, sont des fonctions.

Des gens avant nous, à travers des livres comme _Clean Code_, _Clean Architecture_ et bien d'autres, l'ont déjà exprimé: il faut faire les choses simples. Je me souviens d'une règle qu'une maîtresse de base de données à UTT nous a enseignée: **KISS Keep It Simple, Stu\*\*\*\***. C'était amusant à l'époque, mais cela reflète comment, même après des années de travail ou d'expérimentation avec des bases de données, les gens avaient tendance à compliquer les choses, probablement à cause d'autres limitations.

Jusqu'à quand serons-nous passifs dans notre travail? Combien de temps devons-nous attendre pour mûrir et prendre le contrôle de notre capacité à gérer notre temps et nos ressources?

Je vous invite aujourd'hui à laisser de côté ces différences et à commencer à vous demander: est-ce que ce qui est discuté dans cette revue de code ou cette réunion est quelque chose qui, à la base, est limitant, ou sommes-nous simplement tombés dans la loi de la trivialité de Parkinson ?

