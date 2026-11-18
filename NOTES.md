# news-image-20261118 — notes

Entry: a pure-stdlib Python program (`main.py`) that draws a 1024x1024
front-page image summing up Wednesday 18 November 2026 world news.
Layout differs from the 17 November entry: a full-width lead story, a
2x2 grid, and a bottom strip.

## The six stories (researched 2026-11-18 ~08:00 WIB, from that day's reporting)

1. GULF - CONFLICT (lead): US and Iran exchange fire. Iran drones
   target a US radar at the Sheikh Isa air base in Bahrain (intercepted,
   no damage); US jets hit an IRGC missile launch site on Qeshm Island.
   Third Iranian attack on Bahrain in five days.
2. MIDDLE EAST - ENERGY: Three tankers strike mines in the Strait of
   Hormuz; the LPG tanker Tara Gas is hit twice off Oman and catches
   fire; Kuwait reports drone attacks.
3. EUROPE - CONFLICT: Ukraine strikes the Crimean bridge for a second
   consecutive day; Russia pounds bridges in Kyiv.
4. ASIA - DIPLOMACY: Trump lands in Manila for Quad talks ahead of his
   China visit; Xi, Trump and Putin are set to meet Thursday in Shenzhen.
5. TRADE - APEC: Canada and China extend trade deals as Xi meets Carney
   ahead of the APEC summit.
6. SPORT - CRICKET: MS Dhoni announces his retirement from the IPL and
   becomes the Chennai Super Kings mentor.

## Verification (local, 2026-11-18 ~08:05 WIB)

- `python3 -m py_compile main.py`: OK.
- Two runs with different output dirs: byte-identical entry.png,
  sha256 391fcf8e7af6bb37dc1bf884b0c401dd0eaa6c926293378e782b00b42ee977d1.
- PNG valid (signature + IHDR 1024x1024), 37,842 bytes (cap 1,048,576).
- Rendered image inspected visually: masthead date legible, all six
  headlines + subheads legible, scenes read (radar + drones, tanker
  with flames and mine, bridge gap, four Quad flags, trade arrows,
  stumps + bat + ball + 7).
- Fixes applied after first render: tanker scene redrawn for the
  48px band (containers were clipped at the top); the cricket "7"
  moved clear of the bat's swing.

## Repo

- jekglory/news-image-20261118, PUBLIC, MIT (SPDX line), created
  after the 2026-11-18T00:00:00Z opening.
- Files: main.py, LICENSE, README.md, NOTES.md, .makefun/owner.json.
