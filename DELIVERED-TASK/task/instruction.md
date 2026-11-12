# Reconstruct a seized command network and answer the link-analysis queries

A covert coordination network was recovered from a device seized during a
takedown. Its directive ledger was kept in a packed evidence container whose
block index was wiped and whose fixed-size data blocks were then shuffled. Every
block's bytes and every ledger's catalog entry survived intact, so the ledger
can be rebuilt, but the container can no longer be read in stored order.
Reconstruct the network, then answer the analysis queries.

The parties are **cells** and **agents**. A cell keeps an inbound *directive
ledger* and can be issued directives; an agent only issues directives and keeps
no ledger of its own. Both cells and agents can issue directives to a cell.

## Inputs

`/app/data/entities.jsonl` — one party per line: `{"id": ..., "kind":
"cell"|"agent"}`.

`/app/data/network.pack` — the packed container: a fixed header followed by the
ledger's data blocks.

- Header: 4-byte magic `RLNK`, then `version` (1 byte), `block_size` (2-byte
  little-endian), and `block_count` (4-byte little-endian). The header is
  followed by `block_count` blocks of `block_size` bytes each, laid out
  back-to-back with no padding between them.
- A block holds `block_size` raw bytes and nothing else — no identifier, no
  length, no ordering field.
- The blocks are shuffled. Their stored order carries no information: blocks of
  different cells are interleaved arbitrarily, adjacent blocks are unrelated,
  and some blocks belong to no cell at all.

`/app/data/catalog.json` — `{"block_size": ..., "records": [ {"cell": ...,
"size": ..., "sha256": ..., "head": ...}, ... ]}`, one record per cell:

- `size` — the exact byte length of that cell's recovered ledger content.
- `sha256` — the SHA-256 of that content.
- `head` — the pool index of the cell's **first** block (0-based, among the
  `block_count` blocks).

## Rebuilding a cell's ledger

Each cell's ledger content is recovered from a set of the pool's blocks, taken
in a particular order that begins at the cell's `head` block. Which further
blocks belong to a ledger, and the order among them, are not recorded anywhere —
not by adjacency in the pack and not by any field in a block. The correct
reconstruction of a ledger is the one whose recovered content is exactly `size`
bytes long and has SHA-256 equal to the catalog `sha256`; no other selection or
ordering of blocks reproduces that content.

A recovered ledger is a JSON object:

```
{ "alias": "Kestrel 41" | null,
  "tau": 27,
  "in": [ ["a0007", 18], ["c0031", 12], ["a0010", 0], ... ] }
```

- `alias` — the cell's operational alias, or `null` if it has none.
- `tau` — the cell's **command threshold** (a non-negative integer), described
  below.
- `in` — its inbound directives: each `[from_id, weight]` means `from_id` issued
  `weight` authenticated directives to this cell, where `weight` is a
  non-negative integer. A `from_id` appears at most once in a ledger. A `weight`
  of `0` is a real recorded contact that carried no directive.

## Command

An entity A **commands** a cell C when the number of directives C receives
directly from A, plus the directives C receives from every cell that A already
commands, is **at least** C's threshold `tau`. Apply this repeatedly, starting
from no assumed command relationships, until nothing new can be added. No entity
commands itself, and only cells (never agents) can be commanded.

## Queries

`/app/data/queries.jsonl` lists the questions, one per line: `query_id`, `type`,
plus fields per type.

- `directives` (`from`, `to`): the integer directive weight `from` issued to the
  cell `to`, or `null` if `from` is not among that cell's inbound entries.
- `alias` (`company`): the cell's alias, or `null`.
- `commanders` (`target`): every entity that commands the cell — a JSON array of
  ids sorted ascending, `[]` if none.
- `commands` (`source`): every cell the entity commands, sorted ascending, `[]`
  if none.
- `apex` (`target`): the entities that command the cell and are not themselves
  commanded by any other entity, sorted ascending, `[]` if none.

## Deliverable

Write `/app/answers.json`: a single JSON object mapping every `query_id` from
`/app/data/queries.jsonl` to its answer in the format above. This is the
normative output schema; key order does not matter.
