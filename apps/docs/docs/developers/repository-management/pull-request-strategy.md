# Pull Request Strategy

- Open PRs early as draft when work is in progress.
- Keep PR scope narrow.
- Include a short change summary and test notes.
- Link related issue(s).
- Apply [Definition of Done](/developers/definition-of-done) before merge.

## PR Checklist

- Behavior verified locally
- Docs updated when behavior/config changed
- Feature updates include documentation updates in:
  - backlog (`admins/backlog.md`)
  - changelog (`changelog/index.md`)
  - relevant feature-specific docs (for example, `users/authentication.md`)
- New config keys added to `.env*.example`
- No secrets committed
- AI review run (prompt example: `Please review my PR`) using Codex and Codex Security when applicable
- AI recommendations triaged:
  - in-scope recommendations implemented in this PR
  - out-of-scope recommendations captured in backlog
- Verifiable evidence added to PR description:
  - test commands run and pass/fail status
  - links to AI review comments/threads
  - links to backlog items created for out-of-scope recommendations



