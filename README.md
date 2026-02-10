# 🐠 All the Vibes Agent Swarm 🐠

```
                                        ,.
                                      ,o'
                                     :o'
                 _....._            ``::o
               .'       ``-.         `':oo
              /   __       `.        ::oo'
             |   /  \        |      ::ooo
             |   `._;        |     ::ooo'
             \     ;  ,.     /    ::ooo;
              `.   ``'  `. .'   ,::ooo;
         _      ``--.....::'   ::ooooo;
       .` `.             `.  ,::ooooo;
      /     `.             `::ooooooo;
     :        `.            `::oooooo;
     ;     `:  `._     _..-- ::ooooo;
     :      `. `-.`_.-'   /  ::ooo;'
      `.     :`..__  _.-'   ,::o;``
        `.  ;    ``-'      ,::;``
          `-.             ,:;``
             `-.        .:'
                `-.   .-'
        _._      ) .-'
      .'   ``--.'  /
     /             /
    ;  JUST KEEP  ;
    |  PUSHING!   |
    ;             ;
     `.         .'
       `-.__.-'

        🐠  "Just keep pushing, just keep pushing..."  🐠
             — Nemo (probably), Agent Swarm Edition
```

> An automated documentation engine + chaotic agent swarm toolkit — powered by GitHub Copilot skills, prompts, and GitHub Actions.

---

## What is the All the Vibes Agent Swarm?

This is a **collaborative, rapid-fire AI hackathon repo** where everyone contributes agents, skills, utilities, and experiments to a shared "agent swarm." There are no rules — just vibes.

The repo includes:
- **An automated documentation engine** that keeps README and CHANGELOG in sync on every push
- **A Copilot skill** that teaches Copilot how to analyze diffs and write changelogs
- **Fun swarm tools** like the Vibe Oracle and ASCII Swarm Mascot
- Whatever else the swarm decides to build

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/shyamsridhar123/AlltheVibes-WildHackathon.git
cd AlltheVibes-WildHackathon

# See the swarm mascot
python swarm_mascot.py

# Consult the Vibe Oracle
python vibe_oracle.py "what should I build?"

# Make changes, push, repeat every 5 minutes 🐠
```

---

## 🔮 What's in the Swarm

| Contribution | Author | Description | Run it |
|---|---|---|---|
| 📝 Auto-Changelog Engine | dc995 | Copilot skill + GitHub Action that auto-generates CHANGELOG.md on every push | Automatic on push to `main` |
| � Knock Knock Agent | — | AI agent that responds to everything with knock-knock jokes (OpenAI-powered) | `cd KnockKnock && python knock_knock_agent.py` |
| �🔮 Vibe Oracle | ZacharyLuz | Chaotic vibe generator — ask it anything, receive cosmic wisdom | `python vibe_oracle.py "your question"` |
| 🐝 Swarm Mascot | ZacharyLuz | ASCII art mascot + banner for the swarm | `python swarm_mascot.py` |
| 🐠 Nemo README | ZacharyLuz | This README with Nemo ASCII art and contribution guide | You're reading it |

---

## How the Auto-Documentation Works

### Copilot Skill
The skill in `.vscode/skills/readme-changelog-generator/SKILL.md` teaches Copilot how to:
- Analyze git diffs and commit messages
- Classify changes into categories (Features, Fixes, Refactors, etc.)
- Generate structured changelog entries
- Update the README

### Prompts
| Prompt | What It Does |
|--------|-------------|
| `generate-change-readme` | Analyzes recent commits and generates a changelog entry |
| `summarize-changes` | Finds all changes since the last changelog entry |
| `generate-full-readme` | Creates a complete README from the current repo state |

### GitHub Action
On every push to `main`, the workflow:
1. Reads the commit messages and diff
2. Categorizes changes using conventional commit prefixes
3. Generates a changelog entry with date and commit range
4. Prepends it to `CHANGELOG.md`
5. Commits and pushes the update

---

## Project Structure

```
AlltheVibes-WildHackathon/
├── .github/
│   ├── copilot-instructions.md              # Global Copilot behavior rules
│   ├── instructions/                        # Copilot instruction files
│   ├── prompts/                             # Copilot prompt files
│   └── workflows/
│       └── auto-readme.yml                  # GitHub Action for auto-changelog
├── .vscode/
│   └── skills/
│       └── readme-changelog-generator/      # Copilot skill definition
├── KnockKnock/                              # 🚪 Knock Knock Joke Agent
│   ├── knock_knock_agent.py                 # The agent itself
│   ├── requirements.txt                     # Python deps
│   └── README.md                            # Setup instructions
├── CHANGELOG.md                             # Auto-generated changelog
├── README.md                                # This file (you are here 🐠)
├── swarm_mascot.py                          # 🐝 ASCII swarm mascot
└── vibe_oracle.py                           # 🔮 Chaotic vibe generator
```

---

## How to Contribute

### 1. Get the repo
```bash
git clone https://github.com/shyamsridhar123/AlltheVibes-WildHackathon.git
```
Or fork it: `gh repo fork shyamsridhar123/AlltheVibes-WildHackathon --clone`

### 2. Build anything
- ✅ Agents, skills, utilities, experiments, partial ideas, vibes
- ❌ Nothing is off limits. No required tech stack or language.

### 3. Push fast
> **Push something every ~5 minutes.** Speed over polish.

### 4. Push or PR
- **Direct push** to `main` if you have access (no branch protection)
- **Fork + PR** if you don't — Copilot auto-approves

### 5. Don't overthink it
No coding standards. No linting rules. No cleanup expectations. Just vibes.

---

## Recent Changes

See [CHANGELOG.md](CHANGELOG.md) for a full history of changes.

## License

MIT

---

```
   🐠 Just keep pushing. Just keep pushing. 🐠
```
