---
name: bench-init
description: Set up Benchside in Claude Code, choose where research records live, and make all seven scientific roles available. Use when the researcher asks to initialize Benchside in a local project.
---

# Set up Benchside

Read the installed sibling `../benchside/SKILL.md` and follow its onboarding
reference. Ask where the researcher wants records stored: a durable local folder,
private native documents, or a compatible installed cloud connector. Do not choose
local storage merely because this is Claude Code. The agent runs setup commands;
the researcher need not use a terminal or provide a model API key.

The shared Benchside skill contains all seven roles and uses `bench app` for a
source installation. Prefer this route for projects also used from another agent.
List existing projects in the chosen store and reuse the selected project ID.

If the researcher specifically wants the legacy per-project slash commands and
Claude Code lifecycle hooks, explain that `bench init --yes` writes project identity
in `.bench/config.yaml`, role skills in `.claude/skills`, and tagged session hooks in
`.claude/settings.json`. SessionStart restores legacy CLI recall; SessionEnd archives
the transcript locally. Follow their request before enabling these hooks. This is
optional; the shared skill records without hooks and works with native memory too.
Legacy CLI journals and app project IDs are separate; do not imply automatic migration.

Optional reporting always requires separate consent, exact preview and approval.
The shared onboarding flow also offers optional discipline/career-stage categories
and a separate choice to include them in reviewed usage reports.
