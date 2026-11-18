![Pantheon banner depicting a gathering of mythological figures](assets/images/gods-banner.png)

# Pantheon

The word *pantheon* comes from the Latin *Panthĕon*, which in turn comes from the Greek *Pántheion*, meaning “of all the gods.”

Pantheon brings a team of specialized AI agents to Claude Code and OpenCode. Explore, build, review, and learn with a workflow designed around explicit human approval.

This repository contains agent profiles, two shared skills, and a pull request template. The installer copies selected files; it does not install either runtime, configure models, credentials or MCP servers, or verify that a runtime discovers or follows the profiles.

**Explore:** [Quick start](#quick-start) · [Agents](#agents) · [Workflow](#workflow) · [Skills and template](#skills-and-template) · [Validation](#validation)

## Quick start

Clone the public repository and preview the default agent installation without writing files:

```bash
git clone https://github.com/Maty910/pantheon.git
cd pantheon
./install.sh --runtime opencode
```

After reviewing the preview, explicitly apply all components for OpenCode:

```bash
./install.sh --runtime opencode --components all --apply
```

Existing files with different contents cause a conflict. To keep their previous bytes while replacing them, review the plan and add `--backup` to an apply command. See the installation details below for both runtimes, destinations, and safety limits.

<details>
<summary>Installation details</summary>

1. Use Linux with Bash, Git, and standard shell utilities (`cmp`, `cp`, `mkdir`, `mktemp`, `mv`, `chmod`). Python 3 is needed to run the tests. Install Claude Code and/or OpenCode separately.
2. Clone the repository as shown above and choose a trusted Git revision in a checkout rooted at the installer. Apply requires a valid HEAD, a clean tracked tree, and the installer and selected sources tracked and byte-identical to HEAD. Untracked extras are not copied. Tracked `assume-unchanged` or `skip-worktree` entries block apply. Gitless or archive installs are not supported.
3. Select `--runtime claude`, `--runtime opencode`, or `--runtime both`. The runtime is required even for the runtime-independent template. Preview is the default; `--dry-run` makes it explicit. Preview reports the source revision and tracked-tree state when known.
4. Select components with `--components agents,skills,template`, any distinct comma-separated subset, or `--components all`. The default is `agents`. For example:

   ```bash
   ./install.sh --runtime claude --components skills,template --dry-run
   ./install.sh --runtime both --components all --dry-run
   ```

5. After inspecting the plan, use `--apply` to write files. It cannot be combined with `--dry-run`. Add `--backup` only with `--apply` to replace differing files after saving their previous bytes. Identical files are left unchanged and do not produce backups.

   ```bash
   ./install.sh --runtime both --components all --apply --backup
   ```

Agents and skills go to `~/.claude/{agents,skills}` and/or `~/.config/opencode/{agents,skills}`. The template is copied once to `~/.local/share/pantheon/templates/pull-request.md` for **manual use**; this is not a GitHub auto-discovery location. Copies do not establish effective runtime discovery or access. OpenCode can also discover Claude skill paths; see the [OpenCode](https://opencode.ai/docs/skills) and [Claude Code](https://code.claude.com/docs/en/skills) documentation.

When OpenCode agent or skill destinations are selected, a nonempty `XDG_CONFIG_HOME` different from `$HOME/.config` is rejected. Backups use `~/.local/state/pantheon/backups` regardless of `XDG_STATE_HOME`. Apply reports the full source commit for that operation, but creates no persistent installation manifest.

Preflight checks all selected sources and destinations before writes, rejects unsafe symlinks and blocks differing files unless backup is requested. It is not atomic: an I/O error may leave a partial installation, and concurrent changes between checks and writes are not prevented. There is no automatic rollback or uninstall.

The public OpenCode profiles deny external-directory access by default; these are profile rules, not proof of runtime enforcement. No private path access is automatically enabled. Review permissions and the profiles before use.

</details>

## Agents

These tables introduce the team; their order is not the execution order. Each agent has a profile for both runtimes.

### Primary agents

| Agent | Mythological identity | Role | Profiles |
| --- | --- | --- | --- |
| Odin | God of wisdom and poetry; All-Father (Nordic) | Read-only architecture, coordination, and mentoring | [Claude](agents/claude/odin.md) · [OpenCode](agents/opencode/odin.md) |
| Thor | God of thunder; Odin’s son (Nordic) | Implements and validates approved scope | [Claude](agents/claude/thor.md) · [OpenCode](agents/opencode/thor.md) |
| Themis | Titaness of divine order and justice (Greek) | Defines pre-change contracts and TDD behavior | [Claude](agents/claude/themis.md) · [OpenCode](agents/opencode/themis.md) |
| Heimdall | Guardian of Bifröst (Nordic) | Performs the technical gate before final approval | [Claude](agents/claude/heimdall.md) · [OpenCode](agents/opencode/heimdall.md) |
| Nemesis | Goddess of retribution (Greek) | Adds post-final-approval regression tests or records justified N/A | [Claude](agents/claude/nemesis.md) · [OpenCode](agents/opencode/nemesis.md) |
| Saga | Goddess associated with storytelling (Nordic) | Delivery summaries and PR descriptions | [Claude](agents/claude/saga.md) · [OpenCode](agents/opencode/saga.md) |
| Athena | Goddess of wisdom, crafts, and strategic warfare (Greek) | Learning synthesis and teachback for substantial changes | [Claude](agents/claude/athena.md) · [OpenCode](agents/opencode/athena.md) |

### Supporting agents

| Agent | Mythological identity | Role | Profiles |
| --- | --- | --- | --- |
| Iris | Goddess of the rainbow; messenger of the gods (Greek) | Product discovery, prioritization, and planning | [Claude](agents/claude/iris.md) · [OpenCode](agents/opencode/iris.md) |
| Hermes | God of travel and boundaries; messenger of the gods (Greek) | Read-only codebase mapping and flow exploration | [Claude](agents/claude/hermes.md) · [OpenCode](agents/opencode/hermes.md) |

## Workflow

Odin coordinates; Iris and Hermes can help with optional product and code exploration before implementation. The intended delivery sequence is:

1. **Themis** defines the behavior or validation contract.
2. A **human gives initial approval** for the implementation and validation scope.
3. **Thor** implements and validates within that scope. Executable behavior follows RED → GREEN → REFACTOR; docs, prompts, and configuration use before-and-after contractual checks rather than invented software tests.
4. **Heimdall** reviews the implementation as a technical gate. For PR-bound delivery, Odin coordinates the [review](skills/review/SKILL.md) methodology within that gate when the required tool and independent roles are available; unavailable required capability blocks or limits the affected review. Rejected changes return to Thor and then to Heimdall.
5. A **human gives separate final delivery approval**.
6. **Nemesis** adds regression tests, or records justified N/A for non-executable artifacts. A further implementation delta requires a new technical gate and final approval.
7. **Saga** prepares delivery summaries and PR descriptions after regression validation or justified N/A.
8. **Athena** supports learning and teachback for substantial changes. Learning predictions are not approvals.

The user pushes and opens the PR manually after the applicable gates. The [retro](skills/retro/SKILL.md) skill is opt-in after delivery for a requested sprint or delivery retrospective or a verified escape; it proposes improvements rather than executing them. An unrun scenario is not a verified escape.

These profiles describe a workflow; their presence alone does not guarantee runtime enforcement.

## Skills and template

| Resource | Purpose |
| --- | --- |
| [review](skills/review/SKILL.md) | Read-only, evidence-based review with independent refutation of blocking candidates. |
| [retro](skills/retro/SKILL.md) | Evidence-based retrospective that proposes verifiable quality improvements without executing them. |

The [pull request template](templates/pull-request.md) is a manual aid for describing scope, validation, and risks. Copying it to the personal template store does not make GitHub discover it automatically.

## Validation

Run the installer fixture suite from the repository:

```bash
python3 -B -m unittest discover -s tests -p test_install.py -v
```

The [evaluation documents](evals/README.md) contain 12 declarative protocol scenarios. They were not run as part of this documentation change; their presence does not prove runtime behavior.

See the [changelog](CHANGELOG.md) and [MIT license](LICENSE).
