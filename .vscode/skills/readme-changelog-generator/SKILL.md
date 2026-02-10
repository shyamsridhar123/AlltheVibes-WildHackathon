# Skill: README Changelog Generator

## Purpose
Automatically generates and updates a README that documents every meaningful change in the repository. This skill analyzes git history, diffs, and commit messages to produce clear, structured documentation of what changed, why, and how it impacts the project.

## When to Use
Use this skill when the user asks to:
- Generate a README from recent changes
- Document what changed in the repo
- Create a changelog or change summary
- Update the README with latest commits
- Summarize a PR or set of commits

## Workflow

### Step 1: Gather Change Context
1. Run `git log --oneline -20` to get recent commits.
2. Run `git diff HEAD~N --stat` to get a file-level summary of changes (where N = number of commits to cover).
3. Run `git diff HEAD~N` to get the full diff for detailed analysis.
4. If a specific commit range or PR is specified, scope the diff accordingly.

### Step 2: Classify Changes
Categorize each change into one of:
- **New Features** — New files, functions, endpoints, or capabilities added.
- **Bug Fixes** — Corrections to existing behavior.
- **Refactors** — Structural changes without behavior changes.
- **Documentation** — Updates to docs, comments, or READMEs.
- **Configuration** — Changes to config files, CI/CD, dependencies.
- **Breaking Changes** — Changes that alter existing APIs or interfaces.

### Step 3: Generate README Content
Produce a structured README section or standalone file with:

```markdown
## 📋 What Changed

### 🆕 New Features
- **[filename]**: Description of what was added and why.

### 🐛 Bug Fixes
- **[filename]**: Description of what was fixed.

### ♻️ Refactors
- **[filename]**: Description of structural changes.

### ⚙️ Configuration
- **[filename]**: Description of config changes.

### ⚠️ Breaking Changes
- **[filename]**: Description of breaking changes and migration steps.
```

### Step 4: Update or Create Files
- If `CHANGELOG.md` exists, prepend the new entry with a date header.
- If `CHANGELOG.md` does not exist, create it.
- If the user requests updating `README.md`, update the "Recent Changes" section.
- Always include the date and commit range in the header.

### Step 5: Stage and Prepare for Commit
- Stage the updated files with `git add`.
- Suggest a commit message: `docs: update changelog for [commit range]`.

## Output Format

### CHANGELOG.md Entry Format
```markdown
## [YYYY-MM-DD] — Changes from `<start-sha>` to `<end-sha>`

### 🆕 New Features
- **path/to/file.ext**: Brief description of the feature.

### 🐛 Bug Fixes
- **path/to/file.ext**: Brief description of the fix.

### ♻️ Refactors
- **path/to/file.ext**: Brief description of the refactor.

### ⚙️ Configuration
- **path/to/file.ext**: Brief description of the config change.

### ⚠️ Breaking Changes
- **path/to/file.ext**: Description and migration guidance.

---
```

## Rules
1. **Never fabricate changes** — only document what the git diff actually shows.
2. **Be concise** — one line per change, with the filename bolded.
3. **Group logically** — related changes across files should be described together.
4. **Include context** — mention the "why" when commit messages provide it.
5. **Date every entry** — use ISO 8601 format (YYYY-MM-DD).
6. **Preserve existing content** — when updating CHANGELOG.md, prepend; never overwrite.
7. **Use conventional commit style** for suggested commit messages.

## Dependencies
- Git CLI available in the terminal
- Repository has at least one commit
