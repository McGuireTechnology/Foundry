# Docs Information Architecture

This page defines where documentation should live as Vortex grows.

## Top-Level Areas

- `users/`: user-facing product guidance.
- `admins/`: administrative and operational guidance.
- `developers/`: engineering and implementation guidance.
- `community/`: community resources and participation links.
- `changelog/`: shared release history across audiences.

## Shared and Audience Structure

- `developers/repository-management/`: branching, commits, PR strategy, release strategy, ownership, and hygiene.
- `/admins/backlog`: prioritized planning and maintenance rules.
- `changelog/`: release history and unreleased deltas shared across audiences.
- audience pages: focused policies and templates (for example, testing, security, incidents, release operations).

## Placement Rules

- Put user workflows in `users/`.
- Put engineering standards and implementation guidance in `developers/`.
- Put operational/project administration guidance in `admins/`.
- Put future/planned work in `/admins/backlog`.
- Put shipped work in `/changelog/`.

## Naming Rules

- Use kebab-case file names.
- Keep page titles explicit and stable.
- Prefer directory indexes (`index.md`) for sections with multiple child pages.
