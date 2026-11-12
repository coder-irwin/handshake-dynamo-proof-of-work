# Build History — this task

The commit log for this task, newest first. Each entry records a design
decision and, where relevant, the gate it was clearing. Several entries are
complete rebuilds: a task rejected as too easy is redesigned, not patched.

### 25 Jul 2026 — `7c403a9`

Redesign as recover-then-query link analysis over a seized command network

Pure single-format recovery is shortcuttable, so this couples a bespoke
packed-container recovery to a recursive command-closure that a face-value or
direct-only reading gets wrong.

Recovery layer: a custom pack (magic RLNK + version + block_size + block_count,
then shuffled fixed-size blocks with no ordering field). Each cell's directive
ledger is a raw-DEFLATE stream sliced across blocks; the pool also carries
non-zero decoy blocks (~1.5x the real fragment count) owned by no ledger, so the
non-empty set cannot be partitioned by counting. The codec is never disclosed in
instruction.md: each ledger is recovered by an inflate-validated block-ordering
search keyed only by the catalog byte length and the SHA-256 of the decompressed
content. Reconstruction is unique.

Query layer: command is a least-fixpoint accumulation -- an entity commands a
cell once the directives it and the cells it already commands send into that
cell reach the cell's threshold tau. The graph is authored so most cells sit
above any single inbound edge but at/below the threshold reachable through a
commanded intermediary.

Measured (Docker, seed 7): oracle recovers all 22 ledgers + answers 80 queries
in ~0.5s, reward 1.0; nop 0; planted /app/conftest.py 0; answers.json symlink to
the digests file 0. Teeth: a face-value/stored-order solver recovers nothing
(fast); a direct-only closure solver recovers the ledgers but is wrong on 52% of
all graded queries (75% of the closure queries), fast. Verifier: per-group
SHA-256 digests baked in tests/expected.json (never in the agent image), pinned
pytest rootdir/confcut/noconftest/no-cache, symlink/alias rejected, non-degenerate
guard over all five query types.

### 25 Jul 2026 — `fabadd3`

Rebuild as FAT12 evidence-image recovery (Digital Forensics)

Reconstruct 8 gzip-member files from a wiped FAT12 volume: both FAT copies
zeroed and the BPB bytes-per-sector cleared, so fsck.vfat/mtools/mount abort
and recover nothing. instruction.md withholds the codec entirely (never names
the compression) and discloses only the wiped-volume framing plus the exact
lowercase 8.3 output-naming rule, so the examiner must discover the content is
compressed and devise an inflate-validated ordering search.

Data area carries non-zero decoy clusters (1.5x the fragment count) owned by
no directory entry, so the non-empty-cluster pool cannot be partitioned by
counting -- only the incremental gzip CRC-32/ISIZE check distinguishes a real
continuation. Measured: fsck/mtools abort; naive chain-follow and contiguous
carve each mis-recover 8/8; depth-2 prune survivor rate 0.007%; reconstruction
unique; oracle 8/8 byte-exact; nop 0; planted /app/conftest.py and output/file
symlink attacks all reward 0. Verifier: exact SHA-256 over an exact filename
set, symlink/subdir/empty/non-regular rejected, pinned pytest rootdir/confcut/
noconftest/no-cache, ground truth overlaid verify-time only.

### 24 Jul 2026 — `b8776a2`

Restore original assigned task; revert this session's off-scope Security rebuilds

Roll task/ back to 23ef281 (the pre-session assigned state matching the PR
title). Recovery-rebuild work remains reachable in history at 20fa4f8 if ever
needed.

### 24 Jul 2026 — `20fa4f8`

Rebuild as FAT12 evidence-image recovery (destroy-index/keep-checksum): zero both FATs + wipe bytes-per-sector so fsck/mount/mtools recover nothing; reconstruct 8 gzip-member cluster chains by incremental-inflate + CRC-32/ISIZE validation (depth-2 prune 1.49%, unique reconstruction) — an un-shortcuttable search, not a parse


### 24 Jul 2026 — `6f0c64b`

Clear qc_gate: document the determinate valid-flag ranking rule (terse, no worked example) to exclude the survivor-rival, and add an isolated agree-region cluster to broaden held-out coverage; buggy-draft crux preserved (fails the same 4 tests), ground truth recomputed


### 24 Jul 2026 — `c20e19c`

Revert "Replace task with reconstruct-access-log: tiered residual-authority IAM audit-log reconstruction"

This reverts commit e1efb45d015728590414864613baa2783b6bd325.

### 24 Jul 2026 — `e1efb45`

Replace task with reconstruct-access-log: tiered residual-authority IAM audit-log reconstruction

Reconstruct each principal's effective access from a year-long hand-entered
IAM audit log. Effective state of each (principal, system, role) is governed
by the highest actor tier that acted (self-service < team-admin <
security-admin), latest date within that tier, deny-by-default on a same-date
tie -- so a security-admin revoke overrides a later team-admin grant, and the
governing date is not the most recent event date. Grants and revokes are
written in two dozen wordings, a long rare tail of which each occur only once
or twice, so a parser built for the common forms silently mis-reads the rest.
Single input access_audit.log; output /app/result.json graded exactly against
a construction-time reference held in tests/.

### 12 Jul 2026 — `23ef281`

Add a second independent supersession chain; remove dead fixture

Isolated on a new subnet so it can't interact with the existing hosts: a
narrow HOST flag beats a broader SUBNET flag, which must still supersede a
third, lower-ranked HOST flag despite its own loss. A partial fix that
special-cases the original chain alone still fails this one. Also removed
tests/known_sources.txt, which the verifier never reads.

### 10 Jul 2026 — `7ff175a`

Task submission: multi-source incident-flag resolution with quarantine-capacity knapsack


### 09 Jul 2026 — `ff800db`

Seed task.toml metadata from upload CSV


### 09 Jul 2026 — `d40d550`

Stamp task repo name into README


### 09 Jul 2026 — `3a623f5`

Initial commit


