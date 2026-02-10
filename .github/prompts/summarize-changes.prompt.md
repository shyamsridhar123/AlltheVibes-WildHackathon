---
mode: 'agent'
description: 'Summarize all changes since the last changelog entry and update the README'
---

# Summarize Changes Since Last Entry

You are a changelog summarizer. Find what changed since the last CHANGELOG.md entry and document it.

## Steps

1. **Read CHANGELOG.md** to find the date or commit of the last entry.

2. **Get commits since then:**
   Run `git log --oneline --since="<last-entry-date>"` or use the commit SHA range.

3. **Get the diff** for those commits.

4. **Generate a new CHANGELOG entry** following the standard format and prepend it.

5. **Update README.md** with a brief summary of what's new.

6. **Stage and suggest a commit message:**
   ```
   docs: update changelog for changes since <last-date>
   ```

## Rules
- Only document real changes from the diff.
- If no changes are found, report that and do nothing.
- Preserve all existing CHANGELOG.md content.
