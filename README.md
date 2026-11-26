# The Greatest Dynasty Ever

A static weekly newsletter for the Sleeper dynasty league **The Greatest Dynasty Ever**. This is a local copy of the original site, with the same look, type, layout, and writing, ready to host free on GitHub Pages.

The site asks search engines not to index it (`robots.txt` and a `noindex, nofollow` meta tag). Pages use team names and Sleeper handles only — no real legal names.

## What’s here

The page is the original design: gilt Cinzel masthead, the knight crest, Barlow body type, stone panels, hatched art slots, and the Week 10 cover and matchup paintings. Every headline, blurb, recap, profile, and rivalry line from the original is included verbatim.

Each issue also has a new section, **The Story**, styled like the existing story slots (pilcrow and a dashed rule when empty). That is where the longer weekly chronicle will go. It is empty for now.

Manager portraits use the official full-size character art.

## Weeks 1–10 archive

Matchup art, covers (Weeks 6–9; Week 10 keeps the original cover), and **The Story** for Weeks 1–10 were loaded from a ChatGPT handoff. Every Story chronicle is an *archival reconstruction*, not a verbatim recovery of the originally posted recap. In `content/story.json` each is flagged with `"wN/story/reconstructed": true`. Character descriptions are in `docs/character-guide.md`; the official art in `art/managers/` wins over any description.

## Local preview

From this folder:

```bash
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080). Opening `index.html` as a file will not load the scripts.

## Weekly update flow (typically Tuesday)

1. **Pull scores**

   ```bash
   python3 scripts/pull_sleeper.py
   ```

   This regenerates `js/data-league.js` from the Sleeper public API (current season, plus the 2025 trophy record stored in `data/seasons-2025.json`). It does **not** overwrite story text or art.

2. **Add the week’s writing** in `content/story.json`. Keys follow the original scheme:

   - `w11/headline`, `w11/intro`, `w11/story` (the long chronicle)
   - `w11/m1/title`, `w11/m1/recap` through `w11/m5/...`

   Then compile it into the page:

   ```bash
   python3 scripts/build_content.py
   ```

3. **Add art (optional)** in `art/w11/` — `cover.jpg`, `m1.jpg`–`m5.jpg`, and optionally `film.mp4`. Register the paths in `content/art.json` (for example `"w11/cover": "art/w11/cover.jpg"`) and run `build_content.py` again. Missing keys still render as hatched slots that name the expected file.

4. **Preview** locally, then publish only after you say it looks good.

## Deploying to GitHub Pages (when you’re ready)

There is no compile step beyond the two scripts above. The site is plain HTML, CSS, and JavaScript.

1. Create a GitHub repository (for example `greatest-dynasty-ever`).
2. Push this folder to the `main` branch.
3. In the repo: **Settings → Pages**. Deploy from branch `main`, folder `/ (root)`.
4. The public URL will be `https://<account>.github.io/greatest-dynasty-ever/` for a project site.

A `.nojekyll` file is already included. Paths are relative, so a project site works. No paid hosting is required.

## League

- Sleeper league id: `1312073772823490560`
- 2025 season: `previous_league_id` `1179572164415840256`
- 10 teams, half-PPR, 1QB, 3 FLEX, 3 taxi, 3 IR, 3-round rookie draft
- Playoffs: top 6, starting Week 15
