---
mode: 'agent'
description: 'Generate a full project README based on current repo state'
---

# Generate Full README

You are a README generator. Analyze the entire repository and produce a comprehensive README.md.

## Steps

1. **Scan the repository structure:**
   List all directories and key files to understand the project layout.

2. **Read key files** like `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or any config files to understand:
   - Project name and description
   - Language/framework
   - Dependencies
   - Scripts/commands

3. **Read source files** to understand what the project does.

4. **Generate README.md** with these sections:
   - **Title & Badges** — Project name and relevant status badges
   - **Description** — What the project does in 2-3 sentences
   - **Quick Start** — Setup and run instructions
   - **Project Structure** — Directory tree with descriptions
   - **Usage** — Key commands and examples
   - **Recent Changes** — Link to CHANGELOG.md
   - **Contributing** — Contribution guidelines
   - **License** — License info if found

5. **Write the README.md** file.

## Rules
- Base everything on actual files in the repo — never fabricate.
- Keep it concise and scannable.
- Use proper Markdown formatting.
- Include a "Recent Changes" section that links to CHANGELOG.md.
