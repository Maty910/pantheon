# Pantheon

Pantheon is a local collection of agent prompts and shared skills for Claude and
OpenCode. By default the installer copies nine named agents per selected runtime;
it can also copy two shared skills and a personal PR template. It does not
install either runtime, call models, or download software. It does not validate
legacy frontmatter, skill discovery, or prompt behavior against
the runtimes. Review the contents and history for your own publication and
privacy requirements; this repository does not guarantee sanitization.

## Public profile and release preparation

Version v0.1.0 is prepared locally. Tag creation and publication are separate,
explicitly approved actions; this document does not establish that either has
occurred. A planned clean-root snapshot must be created and reviewed separately:
the preparatory checkout can still inherit private history. Preserve private
history locally; publish only the specifically reviewed public ref, not all refs
or private tags, and do not merge private branches into future public work.

The nine OpenCode profiles deny external-directory access by default. Their
generic `*Vault*` deny can also block unrelated project paths containing that
text; eight profiles additionally deny `*opencode.json*` reads.
These are conservative static rules in legacy frontmatter, not proof of runtime
enforcement or protection for every possible vault name. External code, runners,
or temporary directories may require a reviewed local permission change.
No vault, AI Inbox, or Daily Notes location is preauthorized. Local access
requires a separate Themis contract and explicit approval of exact paths and
actions; the public profiles do not preauthorize AI Inbox writes.

The collection contains nine agents for each of two runtimes, two shared skills,
one PR template, and 25 evaluation documents (12 request/expected pairs plus
their README). The 12 evaluation cases have not been run as part of this release
preparation; their presence does not prove runtime behavior.

## Requirements and provenance

Use Linux with Bash, Git and standard shell utilities (`cmp`, `cp`, `mkdir`,
`mktemp`, `mv`, `chmod`). Python 3 is only needed for the tests. `--apply`
requires a Git checkout whose root is the script's directory, a valid HEAD,
the script and every selected source tracked and byte-identical to HEAD, and
no staged or unstaged tracked changes anywhere in the repository. Untracked
extras do not block installation and are not copied. A missing Git executable,
missing repository, parent repository, missing HEAD, untracked installer or
source, or dirty tracked tree blocks apply before writes. Preview reports the
full source commit and tracked-tree state when known, otherwise `unknown`.
Any tracked entry marked `assume-unchanged` or `skip-worktree` blocks apply,
even when its bytes are unchanged; preview reports the state as `unknown` when
those flags prevent verification. The installer never clears index flags.
Apply reports the full commit of the sources for that operation. There is no
manifest: this does not establish which commit is installed at a later time.

## Preview and install

From the checkout (the script also works from another current directory):

```bash
./install.sh --runtime claude --dry-run
./install.sh --runtime opencode
./install.sh --runtime both --apply
./install.sh --runtime both --apply --backup
./install.sh --runtime both --components skills,template --dry-run
./install.sh --runtime claude --components all --apply
```

`--runtime` is mandatory and accepts `claude`, `opencode`, or `both`. The
default is a read-only preview; `--dry-run` makes that explicit. `--apply`
enables writes; it cannot be combined with `--dry-run`. `--backup` is valid
only with `--apply`. `--components` is optional and defaults to `agents`;
specify a comma-separated list of distinct names `agents`, `skills`, and
`template` in any order, or `all` alone for all three. Invalid, empty,
repeated, or mixed `all` values and duplicate flags fail without writing.
`--runtime` remains mandatory even for template-only selection, although the
template is runtime-independent. The nine agent names
are athena, heimdall, hermes, iris, nemesis, odin, saga, themis and thor.

Agent destinations are `$HOME/.claude/agents` and `$HOME/.config/opencode/agents`.
The shared `review` and `retro` skills are copied as
`$HOME/.claude/skills/<name>/SKILL.md` and/or
`$HOME/.config/opencode/skills/<name>/SKILL.md`. Runtime selection controls
copied paths, not skill isolation: OpenCode also supports Claude skill paths.
See the [OpenCode skills documentation](https://opencode.ai/docs/skills) and
[Claude Code skills documentation](https://code.claude.com/docs/en/skills).
Those documented locations do not prove effective discovery or runtime loading.

The PR template is copied once, including for `both`, to the personal neutral
store `$HOME/.local/share/pantheon/templates/pull-request.md` for manual use.
This does not install it into a project or enable GitHub auto-discovery.
When OpenCode destinations are selected (agents or skills with runtime
`opencode` or `both`), a nonempty `XDG_CONFIG_HOME` differing from
`$HOME/.config` is rejected. Template-only selection and Claude-only selection
allow a custom value; this does not add custom XDG support for OpenCode paths.
Backups always use
`$HOME/.local/state/pantheon/backups`, ignoring `XDG_STATE_HOME`.

Preflight checks every selected component and runtime before any write: missing or unsafe
sources, unsafe destination or backup path components, and differing existing
files without `--backup` block the whole plan. Symlinks are not accepted in
source files, destination files, or path components used for writes. Identical
files are left alone, and reinstalling identical bytes creates no backup.
Other files and unselected runtimes are left alone.

For each replacement with `--backup`, the old bytes go to a private file
(`600`) under a unique private directory (`700`):
`$HOME/.local/state/pantheon/backups/<id>/<runtime>/<agent>.md`,
`<id>/skills/<runtime>/<name>/SKILL.md`, or `<id>/template/pull-request.md`.
These paths are outside both agent and skill discovery trees. To restore manually, inspect the
reported backup and copy the desired file back to its corresponding destination
yourself; this overwrites that destination. There is no uninstall or automatic
rollback. An actual I/O error can leave a partial installation, a backup, or a
temporary file; the installer reports completed entries, the pending entry and
backup directory, and exits nonzero. Preflight is not atomic: concurrent
malicious changes between checks and writes (TOCTOU) are not prevented.

## Update and test

To use a version later, manually select an available trusted Git tag in a clean
checkout (for example `git checkout vX.Y.Z` with an actual existing tag), then
run preview and reinstall with the commands above. The example is a schema, not
a claim that any tag or release exists. A future archive `VERSION` mechanism
is only a possible follow-up; archives are not supported by this installer.

Run the isolated fixture tests from this repository:

```bash
python3 -B -m unittest discover -s tests -p test_install.py -v
```

Tests use temporary homes and Git repositories under `/tmp/opencode`, including
a fixture-local Git identity; they do not install into your real home.
