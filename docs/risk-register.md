# Risk register (demo drawing-review system)

**Status.** Living engineering register for design-review practice.  
**Not** a conformity assessment or safety case. Owners below are demo roles only.

| ID | Risk | Severity (demo) | Likelihood | Existing control | Residual | Owner | Re-evaluate when |
|---|---|---|---|---|---|---|---|
| R1 | Auto-approval of a defective drawing | High | Low if HITL enforced | Reviewer decision required; no auto-release path in API contract | Medium if operators bypass UI | Product / process | Any request to remove HITL |
| R2 | Hallucinated LLM rationale trusted as fact | Medium | Medium when LLM on | Gateway + treat model output as untrusted; heuristic backends for fields | Medium | Integrator | Enabling LLM backend in a real namespace |
| R3 | Leak of drawing content via logs/metrics | High | Low with current defaults | Hash/size/timing logs only; vLLM request logging off in examples | Low | Platform | Changing log level or adding prompt traces |
| R4 | Supply-chain / wrong model revision | Medium | Medium | `lineage` + image git SHA + config hash; pin revisions | Medium | Integrator | New weights or quantisation |
| R5 | Quality regression after model change | Medium | Medium | Eval Job + `gates.yaml` fail-closed | Medium | MLOps | Every weight or prompt change |
| R6 | Over-trust of synthetic gate scores | Medium | High if misread README | Explicit “synthetic set” wording in model/data cards | Medium | Candidate / reader | Before citing scores externally |
| R7 | Network lateral movement from API pod | Medium | Low with NP | NetworkPolicy sketches; non-root; RO root FS | Medium until live-applied | Platform | First cluster apply |
| R8 | GPU OOM / latency SLO breach under load | Medium | Medium | Measure before commit; sibling vLLM T4 bench for method | Medium | Integrator | New model size or concurrency |
| R9 | Prompt injection via drawing text / OCR | Medium | Medium | Tool outputs untrusted; no shell/network tools in this service | Medium | Security | Adding agent tools that mutate state |
| R10 | Mis-stated deployment or review posture | High (reputation) | Medium if marketing copy | README and evidence distinguish stubs, schema checks, and local apply | Low if wording held | Candidate | Any public claim change |

## Qualification stub (fill per deployment — leave blank publicly)

- System: drawing-review assist (demo)
- Finality: human-assisted review
- Excluded uses: autonomous certification / flight decision
- Provider / deployer: _organisation-specific_
- Safety function link: none claimed in this repo
- Regime: _legal/safety validation required — not asserted here_
- Date / revision: align with git tag of the deployed image

## Rollback (exploitation)

1. Confine: disable route or scale consumers.
2. `kubectl rollout undo` or pin previous image digest / PVC weights.
3. Re-run health + gate eval before reopening traffic.
4. Capture versions/events without drawing content.

Related: [`docs/mlops.md`](mlops.md), [`docs/runbook.md`](runbook.md).
