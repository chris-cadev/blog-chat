---
title: 'Moving Out Windows: Bitácora de mudanza a Omarchy'
slug: moving-out-windows
tags:
  - linux
  - omarchy
  - windows
  - mudanza
  - productividad
created: '2026-09-22'
updated: '2026-09-22'
description: Bitácora del proceso de migrar de Windows a Omarchy, una distribución de Arch Linux creada por DHH. Inventario, herramientas y lecciones del camino.
lang: es
lang_group: moving-out-windows
---

Llevo usando Windows desde los seis años, prácticamente toda mi vida. Linux apareció después, de forma esporádica, cuando empecé la universidad (2015). Los cuatro años de carrera fueron los que más lo toqué, pero siempre como segundo sistema. Ya había intentado mudarme en mayo de 2026, pero no se dio. Esta vez armé el inventario completo antes de mover nada. Ahora decidí dar el salto completo a [Omarchy](https://omarchy.org/), una distribución de Arch Linux creada por [DHH](https://world.hey.com/dhh). Esta bitácora documenta el proceso: desde el inventario de lo que tengo hasta la instalación y configuración final.

<!-- PLACEHOLDER: imagen de bienvenida o captura de Omarchy -->

## Por qué me voy de Windows

La razón principal es la velocidad. PowerShell tarda un segundo en cargar, suena a nada, pero esas microfricciones se acumulan cuando hacés trabajo creativo digital. Lo mismo pasa con [Open Code](https://opencode.ai): en Windows va lento, y cuando lo cierro con Ctrl+C me sale un "unknown hard error" y se cierra la terminal. No sé si es algo de Bun, de Node, o de mi setup de PowerShell, pero es otra fricción que me como.

VS Code a veces carga lento, quizás por las 181 extensiones que tengo instaladas. Habrá que correr un análisis para ver cuáles uso de verdad y cuáles puedo quitar. Las integraciones con Docker podrían ser más sencillas. Y hay algo más profundo: siento que mi sistema operativo determina cómo me trackean los servicios digitales. Google, Instagram, Facebook, YouTube, Reddit, todos reciben datos que terminan sesgando lo que me muestran, empujándome hacia productos físicos que no necesito. Con Linux hay menos de eso. Me agrada la idea de ser menos consumidor y más creador.

![](os-privacy-meme.jpg)

Omarchy me llamó la atención porque es Arch sin el dolor de configuración inicial. DHH lo pensó para que funcione desde el primer arranque, pero sin esconder lo que hay debajo.

También está el tema de los videojuegos. Ya casi no juego, y los que juego suelen ser cooperativos sin anti-cheat agresivo. No necesito Windows para eso, con los juegos que me agarran con linux y mi Nintendo Switch con Smash me alcanza. Quiero hacer más tiempo para leer, y parte de esa reorganización pasa por simplificar mi setup.

<!-- PLACEHOLDER: captura del escritorio actual en Windows o comparativa -->

## El inventario: qué tengo antes de mudarme

El primer paso es saber qué llevo en las cajas. Usé `winget list` (~170 entradas), el registro de Windows, `Get-AppxPackage`, `wsl --list`, `code --list-extensions` (181), `docker ps/images` y `mise ls` para armar un mapa completo.

### Sistema y base

Windows 10 Pro (build 26100) con AtlasOS. WSL2 corriendo Debian + docker-desktop. NVIDIA driver 581.57. Shell: PowerShell 7.6, Windows Terminal, Alacritty. El tiling actual es komorebi + whkd + YASB, un setup personalizado que voy a mapear a Hyprland + waybar en Omarchy.

### Discos

5 discos físicos: NVMe Samsung 970 EVO 1TB (sistema, 258 GB libres), Kingston 120GB (backup), WD Blue 1TB (DaVinci Projects, SteamLibrary), WD Black 2TB (lab, anime, un mp4 de 58 GB), WD Blue 2TB (PARA, Downloads, Videos, notas de voz). En Arch hay que montar los NTFS vía ntfs-3g y confirmar UUIDs con `blkid`.

### Herramientas de desarrollo

- **mise**: gestor de versiones: bun 1.3.14, deno 2.8.0, go 1.26.5, java 26.0.1, maven 3.9.16, node 26.9.0, python 3.14.5, rust 1.95, neovim 0.12.2. El config ya está en `mise-config.toml`
- **Docker**: 22 contenedores, 8 stacks: job-seeking, crowsystems (app + api), crowsys (api + nginx + copyparty + db), cook-2026, pricehooks, pallet-flow, pc/syncthing, autonomous-opencode. 38 volúmenes (1.96 GB, 87% reclamable), imágenes 15 GB + build cache 13 GB
- **VS Code**: 181 extensiones categorizadas: 88 lenguajes (Python+data, JS/TS/web, sistemas/JVM/móvil, DB), 20 plataforma (Docker, remote, git), 7 docs, 21 estética, 25 productividad, 14 config, 3 IA. La poda sugerida: 9 temas a 1 (Catppuccin), quitar remote-wsl (inútil en Arch), powershellprotools y tfswitcher (Windows-only), duplicados de sqlite y mysql
- **SSH**: conexiones personales que voy a migrar tal cual

### Proyectos

32 en Windows (`C:\Users\chris\projects`), 26 repos en WSL (`/home/chris/projects`). Clasificados en tres tier: **corriendo** (job-ops, cv-tailoring, blog-chat, opencode-go, crowsystems), **standby** (auto-editor, obsidian-clipper, cook-2026, pricehooks, autonomous-opencode) y **hold** (fleetops, micoach, palets, net.chrislabs/contenedor). Los de hold no migran por ahora.

### Scripts

Hay scripts sueltos en `~/projects/` sin versionar, el más útil es `merge-media.sh` para unir archivos por fecha. Dentro de repos, `tech-workspace/apps/` tiene ~30 scripts bash que sí migran. Los `.ps1` de Windows (komorebi, run, obsidian-wsl) se quedan.

### Atajos y tiling

komorebi maneja ventanas con padding 4, 7 workspaces BSP, borde Catppuccin Mocha. YASB es la barra superior: workspaces, reloj, media, systray, volumen, CPU, memoria. whkd tiene ~30 atajos para apps, ventanas y sistema. PowerToys contribuye Alt+Espacio (PowerToys Run) y FancyZones. Todo eso se mapea a Hyprland/waybar en Omarchy.

### Juegos

30 juegos en Steam. 11 son nativos Linux (Terraria, Hades, Undertale, SpeedRunners). 7 funcionan platinum con Proton. 8 son gold (hay que probar). Fall Guys y THE FINALS usan EAC, el matchmaking puede fallar en Linux. Para acceso remoto uso Parsec, pero el hosting en Linux es limitado, la alternativa es Sunshine + Moonlight.

### Shell y perfiles

PowerShell 7 tiene oh-my-posh, posh-fzf (Ctrl+T archivos, Alt+C dirs, Ctrl+R historial), zoxide, Terminal-Icons. ZSH en WSL es más básico, sin fuzzy ni autosuggestions, y tiene JAVA_HOME y ANDROID_HOME rotos. En Arch voy a necesitar zsh + fzf + zoxide + oh-my-posh + autosuggestions + syntax-highlighting, todo ya tiene script de instalación.

### Media y modelos locales

DaVinci Resolve 21 con licencia Studio, necesaria para H.264/H.265 en Linux. 121 LUTs. Modelos locales ~10 GB (gemma-4 E2B/E4B). OBS portable. Calibre con 34 autores. Affinity 3.2.3 (Photo+Designer+Publisher, gratis). Pake empaqueta 5 webs como apps: WhatsApp, ChatGPT, ExcaliDraw, Netflix, PairDrop. Pake soporta Linux, se pueden reconstruir con pake-cli.

### Licencias y red

Windows 11 Pro Retail, Office 365 Home Premium (suscripción, en Arch se usa web). Solo impresoras virtuales. Red doméstica con Syncthing sincronizando carpetas entre dispositivos. 2 vaults de Obsidian.

### Uso real (historiales)

Lo que más corro: `git` (182 en PowerShell, 1345 en WSL), `docker` (130/294), `opencode` (122/525), `python` (84), `nvim` (39/50), `mise` (29/443). El patrón claro es que WSL ya es mi entorno de trabajo real, Windows es solo el host.

### Configuraciones y dotfiles

Todo está documentado en el repo `move-out-windows`: komorebi.json, YASB config + styles, whkdrc, mise config, opencode.jsonc. El mapeo a Hyprland/waybar ya está en `docs/migracion/omarchy-mapping.md`.

## Lo que quiero preservar

La checklist ya está armada en el repo `move-out-windows`:

- **Toolchain**: MISE con todas las versiones (bun, deno, go, java, maven, node, python, rust, neovim)
- **SSH**: configuración y llaves personales
- **opencode**: jsonc + plugins + AGENTS.md global
- **Docker**: 8 stacks con sus compose y `.env` via EnvSitter (excepto cloudflared sin token nuevo)
- **Repos**: los que están en "corriendo" y "standby". Los de "hold" se quedan.
- **Dotfiles**: mapeo komorebi/whkd/YASB → Hyprland/waybar, configs de Alacritty + Catppuccin Mocha
- **Scripts**: `tech-workspace/apps/` completo, `merge-media.sh`, scripts de blog-chat y pricehooks
- **Entretenimiento**: saves de N64 respaldados, Steam cloud cubierto, Ares para emulación, Parsec para acceso remoto (hosting en Linux es limitado, evaluar Sunshine/Moonlight como alternativa)
- **Bootstrap**: 10 scripts de instalación en el repo (mise, opencode, opendesign, ares, nvidia, coop, fonts, davinci-studio, obs-portable, shell) y prompts para que opencode decida cada migración

Lo que necesito reemplazar (no descarto la idea, solo la implementación Windows-only): komorebi (tiling de ventanas → Hyprland), whkd (atajos de teclado → Hyprland binds), YASB (barra de estado → waybar), PowerToys Run (launcher → rofi/wofi), Flow Launcher (otro launcher). Me gustan esas herramientas, pero son nativas de Windows. El mapeo a Hyprland/waybar ya cubre komorebi/whkd/YASB; falta ver PowerToys Run y Flow Launcher.

## Archivando antes de mudarme: comandos para el disco D

Antes de borrar Windows, quiero comprimir y mover lo importante al disco D (WD Blue 2TB). Todo se hace desde WSL — ahí tengo acceso a ambos discos: `/home/chris/projects` y `/mnt/c/Users/chris/projects`.

**Regla general:** no respaldar lo que se puede regenerar. Si está en `.gitignore`, no va al disco D. `npm install` reconstruye `node_modules`, `bun run build` reconstruye `dist/`.

### Empacar un repo: código + `.git` en un solo archivo

La idea es que al descomprimir en Omarchy quede el repo listo con remotes, branches e historial. Un solo `.tar.gz` por repo.

```bash
# Desde WSL, un repo en cualquiera de los dos discos
cd /home/chris/projects/blog-chat
tar -czf /mnt/d/backups/blog-chat.tar.gz --exclude-vcs-ignores .

# Si el repo está en el disco C de Windows
cd /mnt/c/Users/chris/projects/otro-repo
tar -czf /mnt/d/backups/otro-repo.tar.gz --exclude-vcs-ignores .

# En Omarchy, descomprimir y listo
tar -xzf blog-chat.tar.gz -C ~/projects/
# Resultado: ~/projects/blog-chat/ con .git, remotes, todo
```

`--exclude-vcs-ignores` lee los `.gitignore` de cada carpeta y excluye lo que ahí se liste (node_modules, dist, build, .venv, etc.). No hay que hardcodear nada.

### Empacar todos los repos de un golpe

```bash
# Repos en WSL (/home/chris/projects/)
WSL_REPOS="job-ops cv-tailoring blog-chat opencode-go crowsystems"

# Repos en Windows (/mnt/c/Users/chris/projects/)
WIN_REPOS="auto-editor cook-2026 pricehooks"

for repo in $WSL_REPOS; do
  cd /home/chris/projects/$repo
  tar -czf /mnt/d/backups/$repo.tar.gz --exclude-vcs-ignores .
  echo "✓ $repo archivado"
done

for repo in $WIN_REPOS; do
  cd /mnt/c/Users/chris/projects/$repo
  tar -czf /mnt/d/backups/$repo.tar.gz --exclude-vcs-ignores .
  echo "✓ $repo archivado"
done
```

Al descomprimir en Omarchy:

```bash
mkdir -p ~/projects && cd ~/projects
for f in /mnt/d/backups/*.tar.gz; do tar -xzf "$f"; done
```

### Verificar qué se archivó

```bash
# Ver contenido de un archive (sin extraer)
tar -tzf /mnt/d/backups/blog-chat.tar.gz | head -20

# Contar archivos
tar -tzf /mnt/d/backups/blog-chat.tar.gz | wc -l

# Verificar que .git está incluido
tar -tzf /mnt/d/backups/blog-chat.tar.gz | grep '\.git/' | head -5
```

### Espejo vivo (sin comprimir, actualizable)

Si en vez de un snapshot quiero un espejo que se actualiza:

```bash
rsync -avz --delete --exclude-from=.gitignore /home/chris/projects/blog-chat/ /mnt/d/backups/blog-chat/
```

### Toolchain (MISE)

Mise guarda la config global en `~/.config/mise/config.toml`. Cada repo puede tener su propio `mise.toml`, pero el global define las versiones base.

```bash
# Backup: copiar config global
cp ~/.config/mise/config.toml /mnt/d/backups/mise-global.toml

# Backup: copiar configs de cada repo que tenga mise.toml
for repo in /home/chris/projects/*/; do
  [ -f "$repo/mise.toml" ] && cp "$repo/mise.toml" /mnt/d/backups/mise-$(basename $repo).toml
  [ -f "$repo/.mise.toml" ] && cp "$repo/.mise.toml" /mnt/d/backups/mise-$(basename $repo).toml
done

# Restore en Omarchy:
# 1. Instalar mise
curl https://mise.run | sh
# 2. Copiar config global
cp mise-global.toml ~/.config/mise/config.toml
# 3. Instalar todas las versiones
mise install
```

### SSH

Una sola llave ED25519, diferente en WSL y Windows. El `known_hosts` se regenera al conectar, no vale la pena respaldarlo.

```bash
# Backup (desde WSL, la llave que voy a usar en Omarchy)
mkdir -p /mnt/d/backups/ssh
cp ~/.ssh/id_ed25519 /mnt/d/backups/ssh/
cp ~/.ssh/id_ed25519.pub /mnt/d/backups/ssh/
cp ~/.ssh/config /mnt/d/backups/ssh/

# Restore en Omarchy
mkdir -p ~/.ssh
cp ~/backups/ssh/id_ed25519 ~/.ssh/
cp ~/backups/ssh/id_ed25519.pub ~/.ssh/
cp ~/backups/ssh/config ~/.ssh/
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub ~/.ssh/config
```

### opencode

La config completa vive en `~/.config/opencode/`. Hay plugins locales, AGENTS.md global, comandos personalizados y skills.

```bash
# Backup: todo el directorio de opencode, menos node_modules
rsync -av --exclude='node_modules' ~/.config/opencode/ /mnt/d/backups/opencode-config/

# Restore en Omarchy
rsync -av ~/backups/opencode-config/ ~/.config/opencode/
cd ~/.config/opencode && npm install
```

### Docker (stacks)

No respaldar imágenes ni volúmenes — se re-buildean con `docker compose up -d`. Solo necesito los compose files y los `.env`. De los 15 stacks encontrados, 4 usan EnvSitter (`.envsitter/pepper`).

```bash
# Backup de todos los stacks con compose
#!/bin/bash
STACKS=(
  "/home/chris/projects/net.chrislabs/blog-chat"
  "/home/chris/projects/phone-2026/pricehooks"
  "/home/chris/projects/com.latitudm2m/fleet-operations"
  "/home/chris/projects/mx.com.crowsystems/crm"
  "/home/chris/projects/mx.com.crowsystems/web"
  "/home/chris/projects/mx.com.crowsystems/api"
  "/home/chris/projects/pallets-product-retail/infra"
  "/home/chris/projects/net.chrislabs/cook-tournament-2026"
  "/home/chris/projects/net.chrislabs/autonomous-opencode/web"
  "/home/chris/projects/net.chrislabs/CV_Host"
)

for stack in "${STACKS[@]}"; do
  name=$(echo $stack | sed 's|.*/||')
  mkdir -p /mnt/d/backups/docker/$name
  cp $stack/docker-compose*.yml /mnt/d/backups/docker/$name/
  cp $stack/.env* /mnt/d/backups/docker/$name/ 2>/dev/null
  # EnvSitter: copiar pepper files
  [ -d "$stack/.envsitter" ] && cp -r $stack/.envsitter /mnt/d/backups/docker/$name/
done
```

> **Nota:** cloudflared necesita un token nuevo en Omarchy. Los `.env` de cloudflare no van a funcionar tal cual. El script de restore ([gist](https://gist.github.com/chris-cadev/de9317386e6f756a8287523bd5c87da0)) levanta los stacks automáticamente.

### Dotfiles

Los configs de komorebi, whkd y YASB ya no sirven en Linux, pero los guardo como referencia por si necesito recordar cómo funcionaban. Lo que sí migro es Alacritty y Catppuccin.

```bash
# Backup: Alacritty + Catppuccin (migran a Omarchy)
mkdir -p /mnt/d/backups/dotfiles
cp -r ~/.config/alacritty/ /mnt/d/backups/dotfiles/alacritty/
cp -r ~/.config/catppuccin/ /mnt/d/backups/dotfiles/catppuccin/ 2>/dev/null

# Backup: referencias Windows (komorebi, whkd, YASB)
cp -r /mnt/c/Users/chris/.config/komorebi/ /mnt/d/backups/dotfiles/komorebi/
cp ~/.config/whkd/ /mnt/d/backups/dotfiles/whkd/ 2>/dev/null
cp -r /mnt/c/Users/chris/.config/yasb/ /mnt/d/backups/dotfiles/yasb/ 2>/dev/null

# El mapeo a Hyprland ya está en omarchy-mapping.md (en el repo move-out-windows)
```

### Entretenimiento

Steam cloud se encarga de los saves. Los de N64 están en Ares. Parsec funciona pero el hosting en Linux es limitado — evaluar Sunshine + Moonlight como alternativa.

```bash
# Backup: saves de N64 (Ares)
mkdir -p /mnt/d/backups/gaming
cp -r ~/.ares/ /mnt/d/backups/gaming/ares-saves/

# Steam: no necesita backup, pero por si acaso
cp -r ~/.steam/steam/userdata/ /mnt/d/backups/gaming/steam-userdata/ 2>/dev/null
```

### Scripts

`tech-workspace/apps/` tiene ~30 scripts bash que sí migran. Los `.ps1` de Windows (komorebi, run, obsidian-wsl) se quedan. Ya están cubiertos por el loop de repos si `tech-workspace` está en la lista.

```bash
# Si tech-workspace no está en el loop de repos, copiar solo la carpeta de scripts
rsync -av /home/chris/projects/tech-workspace/apps/ /mnt/d/backups/scripts/tech-workspace-apps/
cp /home/chris/projects/merge-media.sh /mnt/d/backups/scripts/
```

### Bootstrap: scripts de instalación para Omarchy

Estos scripts se ejecutan después de instalar Omarchy para preparar el entorno. Cada uno es independiente, pero `bootstrap-all.sh` orquesta todos en orden.

**Orquestador** ([gist](https://gist.github.com/chris-cadev/221a40407be24082b9275bb30e48418a)): ejecuta todos los scripts en secuencia.

| Script | Gist | Qué hace |
|--------|------|----------|
| `mise.sh` | [gist](https://gist.github.com/chris-cadev/9acea44e34f7bcebeb5d1d7e2c2e73c4) | Instala mise, copia config global, ejecuta `mise install` |
| `opencode.sh` | [gist](https://gist.github.com/chris-cadev/214ef0a8b3cae4e790db6c45f4f260ac) | Instala opencode, copia config, AGENTS.md, plugins |
| `shell.sh` | [gist](https://gist.github.com/chris-cadev/fe16289e4de9719e53d5e47c0490db71) | ZSH + fzf + zoxide + oh-my-posh + autosuggestions + syntax-highlighting |
| `ssh.sh` | [gist](https://gist.github.com/chris-cadev/1ab8c2fb9d90c8a0632ffac476f633e2) | Restaura llaves ED25519, config SSH, permisos correctos |
| `docker-restore.sh` | [gist](https://gist.github.com/chris-cadev/de9317386e6f756a8287523bd5c87da0) | Restaura compose + .env de cada stack, levanta containers |

Los que faltan crear (por ahora documentados como comandos inline): `fonts.sh`, `nvidia.sh`, `davinci-studio.sh`, `ares.sh`, `obs-portable.sh`, `coop.sh`, `opendesign.sh`.

```bash
# Uso rápido: descargar y ejecutar el orquestador
curl -sL https://gist.githubusercontent.com/chris-cadev/221a40407be24082b9275bb30e48418a/raw/bootstrap-all.sh | bash -s ~/backups
```

## Primeros pasos en Omarchy

[PLACEHOLDER: documentar la instalación inicial de Omarchy]

[PLACEHOLDER: captura de pantalla del primer arranque]

[PLACEHOLDER: configuración inicial y primeras impresiones]

## Lecciones del camino

[PLACEHOLDER: qué funcionó, qué fue más difícil de lo esperado, qué haría diferente]

---

*Esta bitácora se actualiza conforme avance en el proceso. Si estás pensando en hacer una mudanza similar, estos posts te pueden servir como referencia.*
