---
title: "Infierno de Helpers"
slug: helpers-hell
tags:
  - software
  - codigo
  - desarrollo
created: '2025-01-10'
updated: '2026-09-29'
description: 'Discusiones innecesarias sobre "helpers" y nomenclatura desvían la atención de lo esencial: la lógica de negocio y la simplicidad.'
lang: es
lang_group: helpers-hell
---

![Representación del infierno de helpers: caos de nombres y discusiones](/static/posts/helpers-hell-representation.webp)

Hace unos días, trabajando en algo de React, me di cuenta de que ya van dos proyectos en los que hay _helpers_ por todas partes, y a veces llegan a la etapa de _code review_, con discusiones sobre si un método, clase o archivo debería llamarse _helper_ o no. Suele ser fastidioso.

Buscando en Internet para ver si esto era algo que solo me había tocado a mí, encontré que es más una conveniencia para evitar caer en el otro _rabbit hole_: no saber cómo nombrar las cosas a la hora de programar.

De los veinte minutos que invertí en buscar, encontré un [post en Reddit](https://www.reddit.com/r/AskProgramming/comments/d4o6i2/best_practices_for_implementation_of_helper/) que menciona que el posible problema es que expresamos directamente nuestros propios modelos de pensamiento en los nombres que damos a las funciones. No hay nada de malo en eso, pero puede llegar a limitarnos.

Estoy de acuerdo con ese argumento. Hay ocasiones en las que las discusiones giran únicamente en torno a cómo nombrar algo. Lo que nos limita es que esos pequeños bloqueos nos apartan de lo que realmente importa en el código que programamos:

> el _business logic_

El _business logic_ es lo que nos permite diferenciar si los requerimientos están bien expresados en líneas de código, no los nombres que les damos a las variables. **Los buenos nombres, la clara expresividad y la experiencia son los elementos que realmente aportan valor.** Y esa experiencia no solo viene del trabajo: también de una ida al parque con la familia, con amigos, en una fiesta bien organizada.

Lo que se nos hace monótono del trabajo hoy en día no es el trabajo en sí: hay problemas entretenidos y diversos, no hay un día igual al anterior. Lo que sí genera obstáculos mentales son estas limitantes sutiles.

Por eso, aquí les dejo una idea: **dejar de llamar _"helpers"_ a algo que, en realidad, son funciones.**

Personas antes que nosotros, a través de libros como _Clean Code_, _Clean Architecture_ y otros más, ya lo han expresado: hay que hacer las cosas simples. Recuerdo una regla que nos enseñó una maestra de bases de datos en UTT: **KISS – Keep It Simple, Stu\*\*\***. Fue divertido en su tiempo, pero refleja cómo la gente tendía a complicar las cosas.

¿Hasta cuándo vamos a ser pasivos con nuestro trabajo? ¿Cuánto tiempo hay que esperar para madurar y tomar las riendas?

Los invito a preguntarse: ¿lo que se está discutiendo en este _code review_ o _meeting_ es una limitante real, o estamos cayendo en la **Ley de Parkinson de la trivialidad**?

