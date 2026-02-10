---
mode: 'agent'
description: 'Generate a changelog README entry documenting all recent changes in the repo'
---

# Generate Change README

You are a documentation generator. Your job is to analyze recent changes in this repository and produce a structured changelog entry.

## Steps

1. **Get recent commits:**
   Run `git log --oneline -20` to see recent commits.

2. **Get the diff summary:**
   Run `git diff HEAD~5 --stat` to see which files changed. Adjust the range based on what the user asks for.

3. **Get detailed changes:**
   Run `git diff HEAD~5` for the full diff. If it's too large, use `git diff HEAD~5 --stat` and then read individual files that changed.

4. **Classify each change** into one of these categories:
   - 🆕 **New Features** — New files, functions, or capabilities
   - 🐛 **Bug Fixes** — Corrections to existing behavior
   - ♻️ **Refactors** — Structural changes without behavior changes
   - 📝 **Documentation** — Updates to docs, comments, READMEs
   - ⚙️ **Configuration** — Config files, CI/CD, dependencies
   - ⚠️ **Breaking Changes** — API or interface changes

5. **Generate the CHANGELOG.md entry** with today's date and prepend it to `CHANGELOG.md`. Create the file if it doesn't exist.

6. **Update README.md** — Ensure the "Recent Changes" section references the latest changelog entry.

7. **Stage the files** by running `git add CHANGELOG.md README.md`.

## Format

```markdown
## [YYYY-MM-DD] — Summary of changes

### 🆕 New Features
- **path/to/file**: Description of what was added.

### 🐛 Bug Fixes
- **path/to/file**: Description of what was fixed.

### ♻️ Refactors
- **path/to/file**: Description of structural changes.

### 📝 Documentation
- **path/to/file**: Description of doc changes.

### ⚙️ Configuration
- **path/to/file**: Description of config changes.

### ⚠️ Breaking Changes
- **path/to/file**: Description and migration steps.

---
```

## Rules
- Only document changes that **actually exist** in the git diff. Never fabricate.
- Use imperative mood ("Add feature" not "Added feature").
- Be concise — one line per change.
- Omit empty categories.
- Always include the date.
