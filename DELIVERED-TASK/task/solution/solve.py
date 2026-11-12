"""Reconstruct the seized command network and answer the link-analysis queries.

The register.pack container's block index was wiped and its fixed-size data
blocks shuffled, so stored order carries nothing. Each cell's ledger is the
fragments of a raw-DEFLATE stream: the reconstruction is the block selection and
ordering, starting at the catalog head block, whose inflated content has the
catalog byte length and SHA-256. Command is then a fixed-point accumulation: an
entity commands a cell once the directive weight it and the cells it already
commands send into that cell reaches the cell's recorded threshold.
"""
import hashlib
import json
import os
import struct
import sys
import zlib

DATA_DIR = "/app/data"
OUT_PATH = "/app/answers.json"
HDR = struct.Struct("<4sBHI")


def load_jsonl(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_pack(blob):
    magic, ver, block_size, count = HDR.unpack_from(blob, 0)
    off = HDR.size
    blocks = []
    for _ in range(count):
        blocks.append(blob[off:off + block_size])
        off += block_size
    return blocks


def _feed(dec, chunk):
    d = dec.copy()
    try:
        out = d.decompress(chunk)
    except zlib.error:
        return None, None
    return d, out


def recover_record(blocks, head, want_len, want_sha):
    """Depth-first, inflate-pruned reassembly starting at the head block."""
    M = len(blocks)
    result = {"content": None}
    d0 = zlib.decompressobj(-15)
    try:
        first_out = d0.decompress(blocks[head])
    except zlib.error:
        return None

    def dfs(dec, produced, path):
        if result["content"] is not None:
            return
        if dec.eof:
            if len(produced) == want_len and \
                    hashlib.sha256(produced).hexdigest() == want_sha:
                result["content"] = produced
            return
        if len(produced) > want_len:
            return
        for j in range(M):
            if j == head or j in path:
                continue
            nd, out = _feed(dec, blocks[j])
            if nd is None:
                continue
            path.append(j)
            dfs(nd, produced + out, path)
            path.pop()
            if result["content"] is not None:
                return

    if d0.eof:
        if len(first_out) == want_len and \
                hashlib.sha256(first_out).hexdigest() == want_sha:
            result["content"] = first_out
    else:
        dfs(d0, first_out, [])
    return result["content"]


class Network:
    def __init__(self, entities, records):
        self.entities = [e["id"] for e in entities]
        self.cells = [e["id"] for e in entities if e["kind"] == "cell"]
        self.alias = {}
        self.tau = {}
        self.inw = {}
        for cell, rec in records.items():
            self.alias[cell] = rec["alias"]
            self.tau[cell] = rec["tau"]
            self.inw[cell] = {s: int(w) for s, w in rec["in"]}
        self._commands = None

    def commands_map(self):
        if self._commands is not None:
            return self._commands
        commands = {A: set() for A in self.entities}
        changed = True
        while changed:
            changed = False
            for A in self.entities:
                cur = commands[A]
                for C in self.cells:
                    if C == A or C in cur:
                        continue
                    acc = self.inw[C].get(A, 0)
                    for D in cur:
                        acc += self.inw[C].get(D, 0)
                    if acc >= self.tau[C]:
                        cur.add(C)
                        changed = True
        self._commands = commands
        return commands

    def directives(self, frm, to):
        w = self.inw.get(to, {}).get(frm)
        return None if w is None else int(w)

    def alias_of(self, cell):
        return self.alias.get(cell)

    def commanders(self, cell):
        cm = self.commands_map()
        return sorted(A for A in self.entities if cell in cm[A])

    def commands_of(self, src):
        cm = self.commands_map()
        return sorted(cm[src])

    def apex(self, cell):
        cm = self.commands_map()
        commanded = set()
        for A in self.entities:
            commanded |= cm[A]
        return sorted(A for A in self.entities
                      if cell in cm[A] and A not in commanded)


def main(data_dir=DATA_DIR, out_path=OUT_PATH):
    entities = load_jsonl(os.path.join(data_dir, "entities.jsonl"))
    queries = load_jsonl(os.path.join(data_dir, "queries.jsonl"))
    with open(os.path.join(data_dir, "catalog.json")) as fh:
        catalog = json.load(fh)
    with open(os.path.join(data_dir, "network.pack"), "rb") as fh:
        blob = fh.read()

    blocks = parse_pack(blob)
    records = {}
    for r in catalog["records"]:
        content = recover_record(blocks, r["head"], r["size"], r["sha256"])
        if content is None:
            raise RuntimeError("failed to recover record for {}".format(r["cell"]))
        records[r["cell"]] = json.loads(content.decode("utf-8"))

    net = Network(entities, records)
    answers = {}
    for q in queries:
        qid, t = q["query_id"], q["type"]
        if t == "directives":
            answers[qid] = net.directives(q["from"], q["to"])
        elif t == "alias":
            answers[qid] = net.alias_of(q["company"])
        elif t == "commanders":
            answers[qid] = net.commanders(q["target"])
        elif t == "commands":
            answers[qid] = net.commands_of(q["source"])
        elif t == "apex":
            answers[qid] = net.apex(q["target"])
        else:
            raise ValueError("unknown query type: " + t)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(answers, fh)


if __name__ == "__main__":
    main(*sys.argv[1:])
