---
title: 'FirstCommit: Micro Tool'
slug: firstcommit
tags:
  - project
  - tool
  - git
  - github
  - python
created: '2025-10-17'
updated: '2025-10-17'
description: A micro Python tool to discover the first commit of any GitHub repository. Developed
  by Christian Camacho and deployed on Vercel.
lang: en
lang_group: firstcommit
---

I wanted to know when I had started an old project. I looked for a tool that shows the first commit of any GitHub repo and only found personal-history tools. I got annoyed and built one.

Paste any public URL below. You'll get date, author and original message without cloning.

<iframe loading="lazy" src="https://firstcommit.debugchris.com" title="FirstCommit - first commit of a GitHub repo" style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>

I was about to finish my Friday shift at the plant when that project came to mind. I wanted the exact start date, not a guess.

I searched for a while. Everything I found asked for your username or analyzed your profile, nothing for a repo that isn't yours. After a bit I thought *I'll do it myself*.

Building something like this is cheap today. A few prompts and you have a working site on Vercel your colleagues can open. A few more prompts and a couple of bugs later, I had something simple I could actually publish. No login, no cloning. Just paste the URL.

It's made with Python. Code is at the [first-commit repository on GitHub](https://github.com/chris-cadev/first-commit/).
