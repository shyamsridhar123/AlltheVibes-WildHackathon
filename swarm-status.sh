#!/usr/bin/env bash
# 🧰 swarm-status.sh — Quick overview of the All the Vibes Agent Swarm
# MacGyver says: "Give me a find command and a git log. That's all I need."

set -euo pipefail
cd "$(dirname "$0")"

echo ""
echo "🐠 ═══════════════════════════════════════════════════"
echo "   ALL THE VIBES AGENT SWARM — STATUS REPORT"
echo "═══════════════════════════════════════════════════════"
echo ""

# Agents
echo "🤖 AGENTS:"
agents=$(find . -name "*.agent.md" -o -name "*_agent.py" -o -name "*agent*.py" 2>/dev/null | grep -v __pycache__ | grep -v .git | sort)
if [ -n "$agents" ]; then
    echo "$agents" | while read -r f; do echo "   • $f"; done
else
    echo "   (none found)"
fi
echo ""

# Skills
echo "🧠 SKILLS:"
skills=$(find . -name "SKILL.md" 2>/dev/null | sort)
if [ -n "$skills" ]; then
    echo "$skills" | while read -r f; do echo "   • $f"; done
else
    echo "   (none found)"
fi
echo ""

# Prompts
echo "💬 PROMPTS:"
prompts=$(find . -name "*.prompt.md" 2>/dev/null | sort)
if [ -n "$prompts" ]; then
    echo "$prompts" | while read -r f; do echo "   • $f"; done
else
    echo "   (none found)"
fi
echo ""

# Recent activity
echo "📊 LAST 10 COMMITS:"
git log --oneline -10 --format="   %C(yellow)%h%C(reset) %C(blue)%an%C(reset) — %s" 2>/dev/null || echo "   (not a git repo)"
echo ""

# Contributors
echo "👥 CONTRIBUTORS:"
git shortlog -sn --no-merges 2>/dev/null | while read -r line; do echo "   $line"; done || echo "   (unknown)"
echo ""

echo "═══════════════════════════════════════════════════════"
echo "   🧰 \"Give me a find command and a git log."
echo "      That's all I need.\" — MacGyver"
echo "═══════════════════════════════════════════════════════"
echo ""
