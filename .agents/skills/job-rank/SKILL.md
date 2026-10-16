---
name: job-rank
description: >
  Use for /rank, rank new jobs, score scraped jobs, or show a ranked
  shortlist.
enabled: false  # /scrape scans .agents/skills for portal CLIs
---

This is the Codex entry point for ranking jobs; follow the [canonical /rank specification](../../../.claude/commands/rank.md).

Pass the user's supplied text and options as `$ARGUMENTS` in that specification.
