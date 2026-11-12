# dynamo/reconstruct-command-network

Digital-forensics link analysis over a **recovered** evidence container. A
covert coordination network's directive ledger was seized inside a packed
container (`/app/data/network.pack`) whose block index was wiped and whose
fixed-size data blocks were then shuffled. Each cell's ledger — its alias, its
command threshold `tau`, and its inbound directives — survives in the pool, and
`catalog.json` pins each ledger by exact byte length, SHA-256, and the pool
index of its first (`head`) block. The agent rebuilds every ledger, then answers
five query types over the reconstructed directive graph, writing
`/app/answers.json`.

## Why it is hard (two layers)

1. **Recovery.** The blocks of a ledger are fragments of a raw-DEFLATE stream,
   and the pool also holds non-zero **decoy** blocks belonging to no ledger
   (~1.5x the real fragment count), so the non-empty set cannot be partitioned
   by counting. The container format is **not disclosed** in `instruction.md`:
   the solver must discover that the blocks reconstitute each ledger through an
   inflate-validated reassembly search keyed only by the catalog length and the
   digest of the *decompressed* content. A face-value or stored-order read
   recovers nothing (fast, not a hang).

2. **Recursive closure.** `command` is a fixed-point accumulation: an entity
   commands a cell once the directives it *and every cell it already commands*
   send into that cell reach the cell's `tau`. The network is authored so most
   cells sit above any single inbound edge but at/below the threshold reachable
   through a commanded intermediary. A **direct-only** reading (the natural
   first take) recovers the ledgers correctly yet gets the closure wrong:
   measured wrong on **52% of all graded queries** (75% of the `commanders` /
   `commands` / `apex` queries), fast.

Reconstruction is unique (each ledger's recovered content is pinned by SHA-256).
Oracle recovers all 22 ledgers and answers all 80 queries in ~0.5s.

## Verification

`/app/answers.json` is graded by per-group SHA-256 digests baked into
`tests/expected.json` (computed once from `solution/solve.py`, overlaid only at
verify time, never in the agent image). Answers are grouped by type (≤20 per
group), so individual answers are not recoverable from a digest (joint answer
space ≫ 2^45). pytest is pinned
(`--rootdir=/tests --confcutdir=/tests --noconftest -p no:cacheprovider`), and
`answers.json` is rejected if it is a symlink or aliases the digests file.

## Layout

```
task/
├── task.toml
├── instruction.md
├── environment/
│   ├── Dockerfile               # python:3.13-slim + pytest
│   └── data/                     # agent inputs only
│       ├── entities.jsonl
│       ├── network.pack          # the packed, shuffled evidence container
│       ├── catalog.json
│       └── queries.jsonl
├── solution/
│   ├── solve.sh
│   └── solve.py                  # inflate-pruned reassembly + command closure
└── tests/
    ├── test.sh
    ├── test_outputs.py
    └── expected.json             # baked per-group digests (verify-time only)
```
