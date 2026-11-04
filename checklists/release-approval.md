# Release approval checklist (demo)

Fill one row per candidate promote. Digests / signatures / approvals are **different**
gates — do not treat a digest as a signature or a human approval.

| Gate | Question | Status for laptop-2026-11-04 |
|---|---|---|
| Content address | git sha recorded? | yes — see `releases/example-laptop-2026-11-04.json` |
| Image digest | registry `sha256:…` present? | **no** — null until GHCR push |
| Signature | image signed (cosign/etc.)? | **not done** in this demo |
| Eval gate | golden / kubeconform / tests pass? | yes — evidence under `docs/evidence/` |
| Human approval | named reviewer for promote? | **N/A** — public demonstrator, no prod traffic |
| Rollback plan | undo script + runbook linked? | yes — `docs/rollback.md` |

Template for a future live promote: copy this file, set Status column from real
commands only — never invent digests or signatures.
