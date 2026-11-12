# Project Dynamo (Handshake AI) — Proof of Work

Record of work delivered on the Handshake AI / Project Dynamo engagement.
One complete accepted deliverable is included in `DELIVERED-TASK/`.

---

## Engagement

Designed, built, verified and submitted evaluation tasks used to benchmark
frontier AI models, and peer-reviewed other contributors' submissions against
the same standard.

| | |
|---|---|
| Tasks submitted | 37 |
| Tasks accepted | **37** |
| Delivered task repositories | 24 |
| Peer reviews performed | 79 |
| Technical domains covered | 11 |
| Method documents authored | 37 |
| Build case studies written | 75 |
| Status | Complete; engagement on hold |

Domains delivered: security · debugging and repair · data querying and
databases · data science and reporting · data processing and ETL · machine
learning and AI · model training and ML infrastructure · mathematics and formal
reasoning · file and media operations · build, dependency and release
management · regulated knowledge work and business operations.

---

## The standard each deliverable had to meet

Every task had to be simultaneously:

- **Defeating** to the benchmarking model — a task the model solves is rejected
  outright and the work is lost
- **Provably solvable** — a reference implementation scoring exactly 1.0 in the
  sealed environment, under the same limits
- **Null-failing** — a run producing no output must score below 1.0
- **Deterministic** — no unseeded randomness, no clock or network dependence, no
  reliance on set or dict ordering
- **Unambiguous** — two competent engineers reading the brief produce identical
  output
- **Shortcut-free** — no exploitable path to the answer

### Gates cleared per submission

13 automated gates. The two decisive ones:

**Soundness.** The environment builds, the reference implementation scores
exactly 1.0, and a null run scores below 1.0.

**Difficulty.** The grader attempts the task five times; at least 3 of 5 must be
*valid* failures with at least one "good valid" failure, assessed on a
seven-dimension per-attempt rubric. A failure caused by a crashed container, an
exhausted timeout or a malformed fixture does not count.

### Soundness probes applied per task

30 named failure modes in five families, applied before submission and when
reviewing others' work:

**A — Reference implementation (6):** oracle fails its own verifier · reports
rather than repairs · hardcoded answer · privileged access · undocumented
assumption · edge-case or tie-break bug.

**B — Contract coherence (6):** ambiguous rule with no tie-break · internal
contradiction · missing definition, field or data · requirement enforced but
never stated · hidden-knowledge dependency · unstated data-anomaly policy.

**C — Verifier rigour (6):** partial or stub output accepted · over-permissive
tolerance · guessable held-out coverage · truth recomputed from agent-writable
inputs · NaN/Infinity bypass · scoring-contract mismatch.

**D — Fixtures and determinism (5):** degenerate fixture a no-op passes ·
unparseable fixture · unpinned dependency · nondeterminism · unseeded build-time
randomness.

**E — Anti-cheat and isolation (7):** oracle or answers readable · immutable-input
integrity unenforced · reward-plumbing exploit · exposed secrets · symlinked
output path · unsafe archive extraction · non-self-contained oracle.

---

## The included deliverable

`DELIVERED-TASK/` — accepted.

| | |
|---|---|
| Category | Security · Digital Forensics |
| Benchmarked against | Opus-4.8, Terminus-2 agent harness |
| Expert time estimate | 6 hours |
| Scale | 34 entities, 22 packed records, 160 shuffled blocks, 80 graded queries |
| Reference implementation | 190 lines, runs in ~0.5 s |
| Verifier | 134 lines |
| Build history | 12 commits, several complete redesigns |

**Design.** Reconstruct structured records from a packed binary evidence
container whose block index was wiped and whose fixed-size blocks were
shuffled, then answer link-analysis queries over the reconstructed graph.

Difficulty is layered deliberately. The first layer is a recovery problem whose
container format is not disclosed in the brief; the container holds roughly 1.5x
more non-empty blocks than the records require, so the obvious counting
heuristic cannot partition them. The second layer is analytical: the queried
relationship is a fixed-point accumulation, and the network is authored so most
nodes sit above any single inbound edge but within reach through an
intermediary. Computing it from direct edges only — the natural first reading —
is wrong on 52% of all graded queries and 75% of the closure queries, measured,
even after the records are recovered correctly.

Fairness holds: every fact needed is in the inputs, the reference implementation
recovers all 22 records and answers every query inside the sealed environment,
and all weights and thresholds are integers, so each graded answer has one
determinate value and the verifier needs no tolerance.

**Verifier design.** Confirms the output is a real regular file, not a symlink
and not aliasing the digest file. Holds ground truth only as grouped SHA-256
digests computed once from the reference implementation, and recomputes nothing
at verification time. Answers are grouped so individual values are not
recoverable from a digest. `pytest` is pinned with `--rootdir`, `--confcutdir`,
`--noconftest` and no cache provider, so a `conftest.py` planted anywhere in the
working tree cannot affect the verdict.

The full design rationale — difficulty, solution and verification — is recorded
in `DELIVERED-TASK/task/task.toml`.

---

## Not included

The programme's own grading rubric and diversity taxonomy, and the CI run
artefacts from the submission. Those belong to the client.

The included task is a live evaluation instrument; its validity depends on
models not having been exposed to it. Not for redistribution, publication, or
use as training or evaluation material.
