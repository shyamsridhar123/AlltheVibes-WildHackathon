# Changelog


## [2026-02-10] — Changes `a94886b` to `ae34b8a`

### 📦 Other
- 🦈 Agent Sharkbait — ocean-themed code review agent (Shark bait, ooh ha ha!)

<details><summary>Files changed</summary>

```
 sharkbait/README.md          |  64 +++++++
 sharkbait/agent_sharkbait.py | 387 +++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 451 insertions(+)
```
</details>

---




## [2026-02-10] — Changes `eb78981` to `67d7276`

### 📦 Other
- Add best practices for React and Next.js performance optimization

<details><summary>Files changed</summary>

```
 .beads/.gitignore                                  |   46 +
 .beads/README.md                                   |   81 +
 .beads/config.yaml                                 |    4 +
 .beads/interactions.jsonl                          |    0
 .beads/issues.jsonl                                |    0
 .beads/metadata.json                               |    4 +
 .gitattributes                                     |    3 +
 .github/agents/beth.agent.md                       |  329 +++
 .github/agents/developer.agent.md                  |  572 +++++
 .github/agents/product-manager.agent.md            |  272 +++
 .github/agents/researcher.agent.md                 |  338 +++
 .github/agents/security-reviewer.agent.md          |  465 ++++
 .github/agents/tester.agent.md                     |  496 ++++
 .github/agents/ux-designer.agent.md                |  393 +++
 .github/skills/framer-components/SKILL.md          |  564 +++++
 .github/skills/prd/SKILL.md                        |  244 ++
 .github/skills/security-analysis/SKILL.md          |  799 +++++++
 .github/skills/shadcn-ui/SKILL.md                  |  562 +++++
 .../skills/vercel-react-best-practices/AGENTS.md   | 2516 ++++++++++++++++++++
 .../skills/vercel-react-best-practices/SKILL.md    |  125 +
 .../rules/advanced-event-handler-refs.md           |   55 +
 .../rules/advanced-use-latest.md                   |   49 +
 .../rules/async-api-routes.md                      |   38 +
 .../rules/async-defer-await.md                     |   80 +
 .../rules/async-dependencies.md                    |   36 +
 .../rules/async-parallel.md                        |   28 +
 .../rules/async-suspense-boundaries.md             |   99 +
 .../rules/bundle-barrel-imports.md                 |   59 +
 .../rules/bundle-conditional.md                    |   31 +
 .../rules/bundle-defer-third-party.md              |   49 +
 .../rules/bundle-dynamic-imports.md                |   35 +
 .../rules/bundle-preload.md                        |   50 +
 .../rules/client-event-listeners.md                |   74 +
 .../rules/client-localstorage-schema.md            |   71 +
 .../rules/client-passive-event-listeners.md        |   48 +
 .../rules/client-swr-dedup.md                      |   56 +
 .../rules/js-batch-dom-css.md                      |   57 +
 .../rules/js-cache-function-results.md             |   80 +
 .../rules/js-cache-property-access.md              |   28 +
 .../rules/js-cache-storage.md                      |   70 +
 .../rules/js-combine-iterations.md                 |   32 +
 .../rules/js-early-exit.md                         |   50 +
 .../rules/js-hoist-regexp.md                       |   45 +
 .../rules/js-index-maps.md                         |   37 +
 .../rules/js-length-check-first.md                 |   49 +
 .../rules/js-min-max-loop.md                       |   82 +
 .../rules/js-set-map-lookups.md                    |   24 +
 .../rules/js-tosorted-immutable.md                 |   57 +
 .../rules/rendering-activity.md                    |   26 +
 .../rules/rendering-animate-svg-wrapper.md         |   47 +
 .../rules/rendering-conditional-render.md          |   40 +
 .../rules/rendering-content-visibility.md          |   38 +
 .../rules/rendering-hoist-jsx.md                   |   46 +
 .../rules/rendering-hydration-no-flicker.md        |   82 +
 .../rules/rendering-svg-precision.md               |   28 +
 .../rules/rerender-defer-reads.md                  |   39 +
 .../rules/rerender-dependencies.md                 |   45 +
 .../rules/rerender-derived-state.md                |   29 +
 .../rules/rerender-functional-setstate.md          |   74 +
 .../rules/rerender-lazy-state-init.md              |   58 +
 .../rules/rerender-memo.md                         |   44 +
 .../rules/rerender-simple-expression-in-memo.md    |   35 +
 .../rules/rerender-transitions.md                  |   40 +
 .../rules/server-after-nonblocking.md              |   73 +
 .../rules/server-auth-actions.md                   |   96 +
 .../rules/server-cache-lru.md                      |   41 +
 .../rules/server-cache-react.md                    |   76 +
 .../rules/server-dedup-props.md                    |   65 +
 .../rules/server-parallel-fetching.md              |   83 +
 .../rules/server-serialization.md                  |   38 +
 .github/skills/web-design-guidelines/SKILL.md      |   39 +
 .vscode/settings.json                              |   16 +
 AGENTS.md                                          |   95 +
 Backlog.md                                         |   80 +
 README.md                                          |  102 +-
 agent.py                                           |  240 ++
 mcp.json.example                                   |    9 +
 tools.py                                           |  273 +++
 78 files changed, 11244 insertions(+), 35 deletions(-)
```
</details>

---




## [2026-02-10] — Changes `697d4b0` to `520f59f`

### 🆕 New Features
- feat: add Dad Joke Agent - pun-powered AI comedy companion

### 📦 Other
- Merge pull request #11 from lshade/feature/knock-knock

<details><summary>Files changed</summary>

```
 DadJokes/.env.example      |  2 ++
 DadJokes/README.md         | 65 ++++++++++++++++++++++++++++++++++
 DadJokes/dad_joke_agent.py | 88 ++++++++++++++++++++++++++++++++++++++++++++++
 DadJokes/requirements.txt  |  2 ++
 4 files changed, 157 insertions(+)
```
</details>

---




## [2026-02-10] — Changes `89af5f0` to `e1a3f6c`

### 🆕 New Features
- feat: add AI Chaos Agent Toolkit - 6 agents + prompt playground

### 📦 Other
- Merge pull request #8 from MarziZadeh/feature/marzi

<details><summary>Files changed</summary>

```
 .env.example               |   4 ++
 .gitignore                 |   3 ++
 agents/__init__.py         |   1 +
 agents/chaos_visualizer.py | 126 +++++++++++++++++++++++++++++++++++++++++++++
 agents/code_reviewer.py    |  97 ++++++++++++++++++++++++++++++++++
 agents/commit_whisperer.py |  84 ++++++++++++++++++++++++++++++
 agents/repo_copilot.py     | 121 +++++++++++++++++++++++++++++++++++++++++++
 agents/router.py           | 114 ++++++++++++++++++++++++++++++++++++++++
 agents/sql_generator.py    |  83 +++++++++++++++++++++++++++++
 config.py                  |  34 ++++++++++++
 main.py                    |  92 +++++++++++++++++++++++++++++++++
 prompts/chaos.md           |  24 +++++++++
 prompts/code_review.md     |  20 +++++++
 prompts/sql_generator.md   |  23 +++++++++
 prompts/summarizer.md      |  20 +++++++
 requirements.txt           |   3 ++
 16 files changed, 849 insertions(+)
```
</details>

---




## [2026-02-10] — Changes `9ec00ba` to `978201f`

### 📦 Other
- Merge pull request #5 from lshade/feature/knock-knock
- Knock Knock Who's There

<details><summary>Files changed</summary>

```
 KnockKnock/.env.example         |  2 +
 KnockKnock/.gitignore           |  5 +++
 KnockKnock/README.md            | 58 +++++++++++++++++++++++++++
 KnockKnock/knock_knock_agent.py | 88 +++++++++++++++++++++++++++++++++++++++++
 KnockKnock/requirements.txt     |  2 +
 5 files changed, 155 insertions(+)
```
</details>

---




## [2026-02-10] — Changes `65b66d8` to `b3855fc`

### 🆕 New Features
- feat: add README changelog generator skill with prompts, instructions, and CI workflow

### 📦 Other
- Merge pull request #2 from dc995/feat/readme-changelog-generator

<details><summary>Files changed</summary>

```
 .github/copilot-instructions.md                    |  39 +++++++
 .../instructions/changelog-format.instructions.md  |  27 +++++
 .github/instructions/readme-update.instructions.md |  24 +++++
 .github/prompts/generate-change-readme.prompt.md   |  66 ++++++++++++
 .github/prompts/generate-full-readme.prompt.md     |  39 +++++++
 .github/prompts/summarize-changes.prompt.md        |  31 ++++++
 .github/workflows/auto-readme.yml                  | 112 +++++++++++++++++++++
 .vscode/skills/readme-changelog-generator/SKILL.md |  98 ++++++++++++++++++
 CHANGELOG.md                                       |  18 ++++
 README.md                                          |  86 ++++++++++++++++
 10 files changed, 540 insertions(+)
```
</details>

---



## [2026-02-10] — Initial setup

### 🆕 New Features
- **README.md**: Add project README with structure, usage, and contributing guide.
- **.vscode/skills/readme-changelog-generator/SKILL.md**: Add Copilot skill for automated changelog generation.
- **.github/prompts/generate-change-readme.prompt.md**: Add prompt to generate changelog from recent changes.
- **.github/prompts/summarize-changes.prompt.md**: Add prompt to summarize changes since last entry.
- **.github/prompts/generate-full-readme.prompt.md**: Add prompt to generate a full README.

### ⚙️ Configuration
- **.github/copilot-instructions.md**: Add global Copilot instructions for the repo.
- **.github/instructions/changelog-format.instructions.md**: Add changelog formatting rules.
- **.github/instructions/readme-update.instructions.md**: Add README update rules.
- **.github/workflows/auto-readme.yml**: Add GitHub Action for automatic changelog generation on push.

---
