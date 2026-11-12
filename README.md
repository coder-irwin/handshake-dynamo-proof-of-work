# Project Dynamo (Handshake AI) — Proof of Work

Record of work delivered on the Handshake AI / Project Dynamo engagement:
designing, building and verifying evaluation tasks used to benchmark frontier
AI models, and peer-reviewing other contributors' submissions against the same
standard.

| | |
|---|---|
| Tasks submitted | 37 |
| **Tasks accepted** | **37** |
| Delivered task repositories | 24 |
| Peer reviews performed | 79 |
| Technical domains covered | 11 |
| Method documents authored | 37 |
| Build case studies written | 75 |

---

## What the work involved

Frontier AI labs need to know what their models genuinely cannot do. That
requires evaluation tasks a state-of-the-art model reliably *fails* — while
remaining completely fair, provably solvable, and unambiguously gradeable.

The difficulty is not in writing a hard problem. It is in writing a hard
problem that survives adversarial audit. A task that is hard because it is
ambiguous is worthless, because the model's failure says nothing about
capability. A task the model fails because of a broken fixture or an unpinned
dependency is noise dressed as signal. A task with any exploitable shortcut is
solved instantly and the work is lost.

So every deliverable had to be, at the same time:

- **defeating** to the benchmarking model — a task the model solves is rejected
- **provably solvable** — a reference implementation scoring exactly 1.0 in the
  sealed environment, under the same limits
- **null-failing** — a run producing no output must score below 1.0
- **deterministic** — no unseeded randomness, clock dependence, network access,
  or reliance on set or dict ordering
- **unambiguous** — two competent engineers reading the brief produce identical
  output
- **shortcut-free** — no exploitable path to the answer

Each submission cleared **13 automated gates**, and was probed against **30
named soundness failure modes** before being submitted.

---

## Contents

| Path | What it is |
|---|---|
| [`PROOF-OF-WORK.md`](PROOF-OF-WORK.md) | The engagement record in full: the standard applied, the 13 gates, the pass@5 difficulty bar, and all 30 soundness probes grouped into their five families |
| [`DELIVERED-TASK/`](DELIVERED-TASK/) | One complete accepted deliverable |

### The delivered task

| | |
|---|---|
| Category | Security · Digital Forensics |
| Benchmarked against | Opus-4.8, Terminus-2 agent harness |
| Expert time estimate | 6 hours |
| Scale | 34 entities, 22 packed records, 160 shuffled blocks, 80 graded queries |
| Reference implementation | 190 lines, runs in ~0.5 s |
| Verifier | 134 lines |
| Build history | 12 commits, several complete redesigns |

Reconstruct structured records from a packed binary evidence container whose
block index was wiped and whose fixed-size blocks were shuffled, then answer
link-analysis queries over the reconstructed graph.

Difficulty is layered deliberately. The first layer is a recovery problem whose
container format is not disclosed in the brief; the container holds roughly 1.5x
more non-empty blocks than the records require, so the obvious counting
heuristic cannot partition them. The second layer is analytical: the queried
relationship is a fixed-point accumulation, and the network is authored so that
most nodes sit above any single inbound edge but within reach through an
intermediary. Computing it from direct edges only — the natural first reading —
is wrong on **52% of all graded queries and 75% of the closure queries**,
measured, even once the records are recovered correctly.

Fairness holds throughout: every fact needed is present in the inputs, the
reference implementation recovers all 22 records and answers every query inside
the sealed environment, and all weights and thresholds are integers, so each
graded answer has one determinate value and the verifier needs no tolerance.

The full design rationale — difficulty, solution and verification each set out
in detail — is in [`DELIVERED-TASK/task/task.toml`](DELIVERED-TASK/task/task.toml).

---

## Domains delivered

Security · debugging and repair · data querying and databases · data science and
reporting · data processing and ETL · machine learning and AI · model training
and ML infrastructure · mathematics and formal reasoning · file and media
operations · build, dependency and release management · regulated knowledge work
and business operations.

---

## Not included

The programme's own grading rubric and diversity taxonomy, and the CI run
artefacts from the submission. Those belong to the client.
