# Changelog

## [Unreleased]

## [0.1.0] - 2026-11-13

- Prepare public OpenCode profiles with external access denied by default and
  conservative generic path denies; local access requires separate review.
- Prepare a public snapshot without asserting that a clean root, tag, or release
  has already been created or published.
- Add a preview-first copy installer for the Claude and OpenCode agent sets,
  with Git provenance checks and optional private backups.
- Add isolated installer behavior tests and usage documentation.
- Add explicit `--components` selection for agents, shared review/retro skills,
  and a runtime-independent personal PR template; the default remains agents.
  Global preflight, clean tracked HEAD provenance, preview and private backup
  safeguards apply to the selection. Custom XDG configuration is rejected only
  when OpenCode agent or skill destinations are selected. Copying skills does
  not guarantee runtime discovery or isolation; the template is for manual use,
  not GitHub project auto-discovery.

Versions are planned to follow SemVer, including pre-1.0 versions, with Git
tags in the form `vX.Y.Z`. This describes a future convention; it does not
assert that a release has been published or a tag created.
