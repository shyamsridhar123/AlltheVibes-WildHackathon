---
applyTo: '**/CHANGELOG.md'
---

# Changelog Generation Instructions

## Format Rules
- Each entry starts with a level-2 heading: `## [YYYY-MM-DD] — description`
- Changes are grouped under level-3 headings by category
- Each change is a bullet point with the file path bolded
- Entries are ordered newest-first (prepend, don't append)
- Separate entries with a horizontal rule (`---`)

## Categories (in order)
1. 🆕 New Features
2. 🐛 Bug Fixes
3. ♻️ Refactors
4. 📝 Documentation
5. ⚙️ Configuration
6. ⚠️ Breaking Changes

## Content Rules
- Only document changes that actually appear in the git diff
- Use imperative mood: "Add X" not "Added X"
- Keep descriptions to one sentence
- Bold file paths: `**path/to/file.ext**`
- Include commit SHA references when available
