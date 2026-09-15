# Prose linting

House style for `src/writings/` is enforced automatically by three linters,
wired into the pre-commit hook via `lint-staged`. None of it touches the
Eleventy build.

## Stack

| Tool | Covers | Why it's in the stack |
| ---- | ------ | --------------------- |
| [Vale](https://vale.sh) | Prose style: house rules + Google/write-good packages | The only linter with a real style-rule engine (existence, substitution, metric, occurrence). Custom rules live in `styles/House/`. |
| [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) | Markdown structure: heading levels, spacing | Vale checks prose, not document structure. Heading increment, single H1, trailing punctuation, and blank lines around lists/fences are markdownlint's job. |
| [cspell](https://cspell.org) | Spelling | Fast, dictionary-driven, CI-friendly. Project dictionary at `cspell/project-terms.txt` is seeded from terms already used in the posts. |

Deliberately not used: textlint, proselint, alex, Joblint, LanguageTool, and
readability-grade gates. Enabling several style packages at once produces
thousands of false positives; E-Prime-style rules flag every form of "to be";
readability grade scores are vanity metrics.

## Setup

`markdownlint-cli2`, `cspell`, `husky`, and `lint-staged` are devDependencies —
`npm install` covers them.

Vale is a Go binary, not an npm package, so it is a prerequisite install:

```sh
# Linux/macOS — pick one:
brew install vale
# or download a release tarball and drop it on PATH:
#   https://github.com/errata-ai/vale/releases  (this repo was set up with v3.21.0)
#   e.g. tar -xzf vale_3.21.0_Linux_64-bit.tar.gz && mv vale ~/.local/bin/
```

Then fetch the configured style packages once per clone:

```sh
npm run vale:sync   # runs `vale sync`; pulls Google + write-good into styles/
```

`styles/Google/` and `styles/write-good/` are gitignored (downloaded
artifacts). `styles/House/` is the local rule set and is committed.

## Commands

```sh
npm run lint         # all three; exits non-zero if any fail
npm run lint:prose   # vale src/writings
npm run lint:md      # markdownlint-cli2 src/writings/**/*.md
npm run lint:spell   # cspell src/writings/**/*.md
```

Vale exits non-zero only on **error**-level alerts; warnings are reported but
don't fail. So `lint:prose` blocks on banned vocabulary, filler phrases, and
first person — everything else is advisory.

## Pre-commit

`.husky/pre-commit` runs `npx lint-staged` whenever `src/writings/*.md` files
are staged (before the existing build+verify step). The lint-staged entry in
`package.json` runs, in order:

1. `node scripts/lint-frontmatter.mjs` (pre-existing)
2. `markdownlint-cli2`
3. `cspell lint --no-progress --no-summary`
4. `vale`

All four receive only the staged file list. A Vale error level fails the
commit; warnings do not.

## Vale configuration (`.vale.ini`)

- `MinAlertLevel = warning`
- `Packages = Google, write-good` (fetched by `vale sync`)
- `BasedOnStyles = Google, write-good, House` for `*.md`
- `IgnoredScopes = code, tt, kbd, frontmatter` — inline code and YAML front
  matter fields are not linted.
- `BlockIgnores` drops pipe-table rows: a cell like `| 2021 | … |` would
  misfire the sentence-initial-numeral rule. (Side effect: prose inside table
  cells is not linted at all.)
- Vale's built-in Markdown handling already skips fenced code, indented code,
  `$$…$$`/`$…$` math, and URLs; link text is a separate `link` scope that
  text-scoped rules never touch.

Disabled stock rules (duplicates or noise):

| Rule | Reason |
| ---- | ------ |
| `write-good.Passive` | duplicate of `House.PassiveVoice` |
| `write-good.E-Prime` | flags every form of "to be" — noise |
| `Google.Passive` | duplicate of `House.PassiveVoice` |
| `Google.We` | `House.FirstPerson` covers all pronouns at error level |
| `Google.FirstPerson` | same |
| `Google.EmDash` | presumes dashes are legal and polices their spacing; `House.EmDash` bans them |
| `write-good.TooWordy` | flags precise technical nouns (`maximum`, `minimum`, `requirement`, `utilization`, `equivalent`) as wordiness — 361 hits sitewide, mostly false. `House.Wordy` keeps only phrases with a strictly shorter equivalent |

## House rules (`styles/House/`)

Errors fail `lint:prose` and the pre-commit hook; warnings only report.

| Rule | Level | Extension | Catches |
| ---- | ----- | --------- | ------- |
| `House.FirstPerson` | error in the Evals series, warning elsewhere | existence | `I, me, my, mine, we, our, us, ours` + contractions (`I'm`, `we're`, …), `let's`/`let us`, `myself`, `ourselves`. Roman-numeral and cloud-region exceptions built in. |
| `House.BannedVocab` | error | substitution | The banned word list (delve, leverage, utilize, facilitate, foster, empower, streamline, robust, cutting-edge, paradigm shift, game changer, tapestry, realm, beacon, multifaceted, meticulous, intricate, paramount, transformative, elevate, embark, supercharge, harnessed/harnessing, ever-evolving) incl. inflections, with suggested replacements. `beacon chain/block/node/…` excepted — it's an Ethereum protocol term. |
| `House.FillerPhrases` | error | existence | it is worth noting, it's worth noting, it is important to note, it should be noted, at the end of the day, when it comes to, at its core, in today's world, in the age of, the reality is, the truth is, going forward, in this article, let's dive in. |
| `House.EmDash` | warning | existence | `—`, `―`, and `--` used as dashes. `--flag`-style CLI options are not matched; `---` rules/front matter never reach it. |
| `House.Semicolon` | warning | existence | Every `;` in prose — Vale can't parse clauses, so it flags all of them and asks you to check. HTML entities excepted. |
| `House.SentenceNumeral` | warning | existence | A sentence (not a heading) opening with a numeral — `^\s*["'“”‘’]?\d`. |
| `House.LongSentence` | warning | metric | Any non-heading sentence over 40 words. |
| `House.AvgSentenceLength` | warning | metric | Whole-document average over 25 words/sentence. |
| `House.ParagraphSentences` | warning | metric | Body paragraphs over 6 sentences (lists, blockquotes, table cells aren't paragraphs). |
| `House.ParagraphWords` | warning | metric | Body paragraphs over 160 words. |
| `House.Wordy` | warning | substitution | Filler phrases with a strictly shorter equivalent (`due to the fact that`, `in order to`, `prior to`, `has the ability to`, `the majority of`, …). Replaces `write-good.TooWordy`. |
| `House.PassiveVoice` | warning | existence | BE-verb + past participle heuristic (`was stored`, `has been taken`, …). Warning, never an error. |

### Scoped rules

`House.FirstPerson` is an error only for the Evals series and a warning
everywhere else. The series is technical writing for an outside reader, where
the house style bans first person outright. The earlier posts are personal
essays whose voice is first person by design, so an error there would block
every commit that touches them without improving the writing. The scope is a
path section at the bottom of `.vale.ini`; add new series files to that glob.

`House.BannedVocab` bans only the verb inflections of "harness". The noun
"agent harness" is the term of art for the scaffolding that runs a model, and
it appears throughout the Evals series.

Headings: sentence case is enforced by `Google.Headings`; no trailing
punctuation is double-covered by `Google.HeadingPunctuation` and MD026.

## Suppressing a rule

Vale, per line or region — inline HTML comments:

```md
<!-- vale House.FirstPerson = NO -->   …quoted first person…   <!-- vale House.FirstPerson = YES -->
<!-- vale off -->                     …nothing linted…          <!-- vale on -->
<!-- vale House.BannedVocab["delve"] = NO -->  …specific match only…  <!-- vale House.BannedVocab["delve"] = YES -->
```

Whole file: put `<!-- vale off -->` at the top. Permanent config changes go in
`.vale.ini` (`House.Semicolon = NO` under `[*.md]`).

markdownlint:

```md
<!-- markdownlint-disable MD025 -->  …rest of file…
<!-- markdownlint-disable-next-line MD026 -->
```

cspell:

```md
<!-- cspell:disable -->  …rest of file…   <!-- cspell:enable -->
Local file directive: # cspell: wordone wordtwo
```

Add genuinely reusable vocabulary to `cspell/project-terms.txt` rather than
suppressing — that's what the project dictionary is for.

## Baseline counts across the 43 posts (2026-09-14)

`npm run lint` is currently red on the existing corpus — that is the backlog
this setup was built to surface. Old posts were not mass-edited to pass.

### Vale — House rules

| Rule | Hits | Genuine? |
| ---- | ---- | -------- |
| `House.PassiveVoice` | 409 | Mostly genuine — the corpus is passive-heavy. Regex heuristic also flags adjectival `-ed` ("is connected"), which is expected noise for a warning. |
| `House.FirstPerson` | 196 | Genuine — posts use I/we/our throughout. |
| `House.BannedVocab` | 65 | Genuine — `utilize/utilization` (15), `robust` (9), `leverage` (9), `beacon` now excepted for Beacon Chain usage, `harness` (4), `foster*` (4), `facilitate*` (4), plus singletons. |
| `House.EmDash` | 62 | Genuine — `—` throughout. |
| `House.LongSentence` | 43 | Genuine — >40-word sentences. |
| `House.Semicolon` | 33 | Genuine hits, but the rule flags *all* semicolons — a few may be serial/list uses, not clause joins. By design; warning only. |
| `House.SentenceNumeral` | 21 | Genuine, with two borderline classes: bullets that open with a numeral (`- 4 always-on …`) and identifier-led sentences (`0xknxwledge/…`). Both are rewordable; kept as warnings. |
| `House.ParagraphSentences` | 10 | Genuine. |
| `House.ParagraphWords` | 4 | Genuine. |
| `House.FillerPhrases` | 2 | Genuine ("In this article", "going forward"). |
| `House.AvgSentenceLength` | 0 | No post exceeds the 25-word average. |

Vale totals: **333 errors, 1470 warnings** (the warnings include stock
Google/write-good noise: `write-good.TooWordy` 361, `Google.Headings` 200 —
sentence-case heading violations, real but a large backlog — `Google.Colons`
78, `Google.Will` 76, `write-good.Weasel` 75, `Google.WordListCase` 55, and a
long tail under 25 each).

### markdownlint — 96 violations

| Rule | Hits | Genuine? |
| ---- | ---- | -------- |
| MD025 single H1 | 54 | Genuine — many posts use `#` for every section instead of one H1 + `##` sections. |
| MD001 heading increment | 19 | Genuine — `h2 → h4` jumps etc. |
| MD026 no trailing punctuation | 14 | Genuine — headings ending in `. : ?` |
| MD012 no multiple blanks | 8 | Genuine |
| MD047 single trailing newline | 1 | Genuine |

### cspell — 0 issues

Seeded `cspell/project-terms.txt` (238 entries) covers the corpus's real
vocabulary: protocol/product names, author names, ticker symbols, and
LaTeX-source artifacts (`mathbb`, `pbot`, …). The first run found 9 genuine
typos, all fixed in place: `Aribtrageurs→Arbitrageurs`, `faliure→failure`,
`embarassingly→embarrassingly`, `Intepretation→Interpretation` (×2),
`Porftolio→Portfolio` (×2), `Goldksy→Goldsky`, `Crytpohouse→Cryptohouse`,
`facilitiates→facilitates`, `ergonomical→ergonomic`.

## Known limitations

- `House.Semicolon` cannot tell a clause join from other uses — warning only.
- `House.PassiveVoice` is a regex heuristic; adjectives ending in `-ed`
  occasionally trip it.
- `House.SentenceNumeral` intentionally still fires on numeral-led list items
  and identifier-led sentences; reword so a word leads.
- Vale does not run at all on machines without the binary; the pre-commit hook
  fails closed with `vale: command not found`. Install per Setup above.
