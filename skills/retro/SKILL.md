---
name: retro
description: Evidence-based sprint or delivery retrospective proposing verifiable quality improvements.
---

# Retro

Use this opt-in after delivery, on request for a sprint or delivery or for a
verified escape; do not run it automatically for every task. A `NOTRUN` scenario
is not a verified escape.

## Scope and evidence

Define the sprint or delivery, period, baseline, runtime, and completed gates
when available. Identify sources and state what is unknown, inaccessible, or not
run. If necessary data is missing, request the minimum needed or report the limit.

Separate observed facts, evidence and its limits, and causal hypotheses. Do not
invent defects, escapes, results, success, or metrics.

Read and apply relevant target-repository rules and its twin map when available;
cite sources without duplicating their rules. Do not assume CI or another control
exists or covers a case without evidence.

## Selection and candidates

Select a few verifiable escapes and explain their priority by consequence or
observed repetition, without inventing statistics. An exhaustive code review or
general refactor list is not this retrospective's objective.

For each candidate, connect the escape and causal hypothesis to evidence and find
the relevant existing source, rule, or check. State whether it already covers the
case, whether a gap remains, or whether this could not be determined. Consider
relevant variants or twins and known CI limitations. Do not propose duplicates
when an existing control effectively covers the case.

For executable behavior, propose a deterministic check of the observable result
when appropriate. For prompts, documentation, or configuration, propose an
appropriate contractual rule or check without manufacturing software tests. For
each proposal, explain what it would and would not check, excluded variants, and
missing evidence.

## Result and limits

Report scope, sources, limits, selected verified escapes, hypotheses identified
as such, and improvement candidates in relation to existing controls. “No verified
escapes” and “insufficient evidence” are valid results; the former does not
guarantee absence of defects.

If evaluating effectiveness is proposed, first define a future comparison with
baseline, criteria, and permitted data. Do not claim a proposal improved quality
without real comparable observations.

Retro does not replace review, its refutation rules, or its gates. Nor does it
replace Athena or require an exercise or Mati's learning as a quality gate.

## Authority and privacy

Actions are proposals, not authorization to execute them. A proposed mutation
returns to Odin and follows the applicable protocol: Themis, Mati's explicit
initial approval, Thor, Heimdall, Mati's final approval, Nemesis or objective N/A
when appropriate, and Saga.

Retro does not edit files, run tests, create tickets, automatically write to the
vault or Engram, or publish results. It does not create a permanent record or
additional file on its own. Odin may manage a sanitized summary under the existing
memory protocol; this skill grants no new authorization.

Use only permitted sources and data. Do not incorporate private cases or publish
information without applicable authorization and privacy review.
