---
name: review
description: Read-only change review with causal evidence and independent refutation.
---

# Review

## Preparation

Identify the change, its boundaries, declared risks, and available evidence. Read
the target repository's review rules and twin map where they exist and are
accessible; apply their rules without copying them here. Record sources, absences,
permissions, and evidence limits. Do not invent a map or assume a CI control exists
or covers a case without evidence.

Report the runtime, roles, and models actually used, their capabilities, and their
permissions. Do not assign default models or automatically substitute an unavailable
role. If required independence, context, or permission is missing, declare the
affected review blocked or inconclusive; do not simulate it.

Report changed files and added and removed lines, plus actual cost if available;
otherwise state that it is unknown. If the change exceeds 400 added plus removed
lines or 10 files, partition review by coherent areas and retain an integration
pass across areas. This is an organizational heuristic, not automatic risk
classification.

## Review

In normal mode, one reviewer inspects the change and its relevant connections.
For changes declared risky or critical, adversarial mode uses two independent
judges instead of the normal reviewer for that objective; it does not add a third
normal review. Both record their conclusions and disagreements. Risk classification
comes from context and applicable rules, not size alone. Judges do not replace the
refuter.

Follow relevant values from origin to consumption: document units, transformations,
and assumptions, and check causal endpoints with file and line. Apply the twin map
and review relevant counterparts. State limitations when a chain cannot be followed.

Propose findings supported by behavior and observable consequences. For each,
state the consequence if true, severity according to that consequence — not
probability — and file-and-line evidence at both relevant causal endpoints. If
evidence is missing, do not present it as confirmed fact.

Exclude observations about style or names alone, speculative hardening, and controls
effectively covered by CI, unless an applicable rule or evidence shows an uncovered
behavioral problem. A review without findings is valid, not a guarantee that no
defects exist.

## Refutation

For each candidate whose consequence would block delivery, an independent refuter
in a separate context attempts to disprove it using accessible evidence. Record:

- `corroborado` (corroborated): survives refutation with sufficient evidence;
- `refutado` (refuted): evidence disproves the candidate;
- `latente` (latent): risk depends on a condition not established;
- `inconcluso` (inconclusive): evidence or capability is insufficient to decide.

Only `corroborado` blocks on that finding. Do not publish a refuted finding as a
result. Communicate relevant limits of latent and inconclusive candidates without
presenting them as confirmed defects. If independent refutation cannot be performed,
do not claim corroboration.

This rule does not remove or replace independent authorization, evidence, or scope
gates. A review does not authorize changes or replace Heimdall's technical gate or
Mati's final approval. Odin coordinates read-only under the applicable protocol.

## Result and measurement

Report scope, sources, size, known or unknown cost, actual roles and models, mode,
limits, and publishable findings with evidence and verdict. Identify unreviewed
areas and unresolved disagreements. Do not infer coverage, effectiveness, or
runtime parity from one execution.

Quality improvement requires a before/after comparison with defined cases and
criteria, permitted data, and real observations. Without an adequate suite or
baseline, state that effectiveness is unmeasured. Do not import private cases or
publish information, history, or results without applicable authorization and
privacy review.
