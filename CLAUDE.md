# UNI — all university subjects in one git repo

This folder (`~/Desktop/UNI`) is **one git repository** for every subject:
**https://github.com/areg06/UNI** (branch `main`).
It is published as **one GitHub Pages site: https://areg06.github.io/UNI/**

All user-facing text is in **Armenian**; keep it Armenian.

## Rules for every Claude chat working in any subject folder

- The git root is `~/Desktop/UNI`. **Do not run `git init`** in a subject folder, and do not
  create a separate GitHub repo for a subject. Commit and push from this one repo.
- The old per-subject repos `areg06/Meqenanerimaser` and `areg06/kursayin` are **archived
  (read-only)**. Don't push to them; their content and history now live here.
- Stage only the files of the subject you worked on (`git add "<subject folder>/..."`). Other chats
  may have uncommitted work in other folders, so never `git add -A` or `git add .` at the root.
- `git pull --rebase` before pushing: several chats (and phone/cloud sessions) push to this repo.
- When you add a new page that should be reachable on the site, add a link to it in the root
  `index.html` (and in the subject's own `index.html`, if it has one).
- Folder names contain spaces; on the site they appear URL-encoded (`%20`). Link to them with
  relative links (for example `href="meqenamaseri tesutyun/"`); the browser encodes them.
- Large source files (textbook PDFs, photos) are fine below ~50 MB each. Never commit anything
  over 100 MB (GitHub rejects it).

## Subjects

| Folder | Subject | Site |
|---|---|---|
| `meqenamaseri tesutyun/` | Մեքենամասերի տեսություն: gear reducer calculation and explanation | https://areg06.github.io/UNI/meqenamaseri%20tesutyun/ |
| `kursayin ashxatanq/Variant1/` | Կուրսային աշխատանք (ՄՄՏ), variant 1; has its own `CLAUDE.md` with build steps | https://areg06.github.io/UNI/kursayin%20ashxatanq/Variant1/ |
| `nyutagitutyun/` | Նյութագիտություն: lectures 1–7 and the midterm-1 study platform | https://areg06.github.io/UNI/nyutagitutyun/ |
| `gazodinamika/` | Գազադինամիկա: Armenian translation of the textbook | https://areg06.github.io/UNI/gazodinamika/translation/gazadinamika_hy.html |

## Deliberately not in git

Listed in the root `.gitignore`:
- `kursayin ashxatanq/Variant13/`, `Variant13.zip`, and `kursayin ashxatanq/source/` (the variant 7
  generator): other variants, kept only locally.
- The meqenamaser pages for other students (Yuri, Hovhannes, Aren) were removed from the site
  on purpose. Don't add them back.
