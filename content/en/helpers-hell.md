---
title: "Helpers Hell"
slug: helpers-hell
created: '2025-01-10'
updated: '2026-09-29'
description: 'Unnecessary discussions about "helpers" and naming conventions distract from what matters: business logic and simplicity.'
tags:
  - software
  - coding
  - naming
lang: en
lang_group: helpers-hell
---

![Helpers hell representation: chaos of names and discussions](../assets/helpers-hell-representation.webp)

A few days ago, working on something in React, I realized there are already two projects where _helpers_ are everywhere, and sometimes they even reach the _code review_ stage, with discussions about whether a method, class or file should be called _helper_ or not. It's usually annoying.

Looking on the Internet to see if this was something that only happened to me, I found that it's more of a convenience to avoid falling into the other _rabbit hole_: not knowing how to name things when programming.

Of the twenty minutes I spent searching, I found a [post on Reddit](https://www.reddit.com/r/AskProgramming/comments/d4o6i2/best_practices_for_implementation_of_helper/) that mentions the possible problem is that we directly express our own thought patterns in the names we give to functions. There's nothing wrong with that, but it can limit us.

I agree with that argument. There are times when discussions revolve solely around how to name something. What limits us is that these little blocks take us away from what really matters in the code we program:

> _business logic_

Business logic is what allows us to differentiate whether the requirements are well expressed in lines of code, not the names we give to variables. **Good names, clear expressiveness, and experience are the elements that really bring value.** And that experience doesn't just come from work: also from a trip to the park with family, with friends, at a well-organized party.

What makes work monotonous today isn't the work itself: there are entertaining, diverse problems, no day like the last one. What does create mental obstacles are these subtle limitations.

So here's an idea: **stop calling something _"helpers"_ when they're actually functions.**

People before us, through books like _Clean Code_, _Clean Architecture_ and others, already expressed it: keep things simple. I remember a rule a database teacher taught us at UTT: **KISS – Keep It Simple, Stu\*\*\***. It was fun at the time, but it reflects how people tended to complicate things.

How long are we going to be passive about our work? How long do we have to wait to mature and take the reins?

I invite you to ask yourself: is what's being discussed in this _code review_ or _meeting_ a real limitation, or are we just falling into the **Parkinson's Law of Triviality**?
