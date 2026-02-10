---
applyTo: '**'
---

# AlltheVibes-WildHackathon — Copilot Instructions

## Repository Purpose
This repository uses an automated README/Changelog generation skill to document every change made to the codebase.

## Core Principles
1. **Every change gets documented** — No commit should go undocumented in the CHANGELOG.
2. **READMEs stay current** — The root README reflects the current state of the project.
3. **Changes are categorized** — Use conventional categories: Features, Fixes, Refactors, Config, Breaking Changes.
4. **Git history is the source of truth** — All documentation is derived from actual diffs and commit messages.

## When Working in This Repo
- After making code changes, run the `generate-change-readme` prompt to update documentation.
- Use clear, descriptive commit messages — they feed directly into the changelog.
- Follow [Conventional Commits](https://www.conventionalcommits.org/) format when possible:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `refactor:` for refactors
  - `docs:` for documentation changes
  - `chore:` for maintenance tasks
  - `ci:` for CI/CD changes

## File Conventions
| File | Purpose |
|------|---------|
| `README.md` | Project overview and current state |
| `CHANGELOG.md` | Chronological record of all changes |
| `.github/workflows/auto-readme.yml` | GitHub Action for automated README updates |
| `.vscode/skills/readme-changelog-generator/SKILL.md` | Copilot skill definition |

## Change Documentation Standards
- Each changelog entry must include the **date**, **commit range**, and **categorized list of changes**.
- File paths must be relative to the repo root.
- Descriptions should be one line, written in imperative mood ("Add feature" not "Added feature").
- Breaking changes must include migration guidance.
