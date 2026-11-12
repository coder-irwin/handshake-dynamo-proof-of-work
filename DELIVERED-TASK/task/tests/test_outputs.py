"""Verify /app/answers.json against the query set per instruction.md.

Ground truth is never recomputed at verify time: each query group's answers are
canonicalized exactly as instruction.md specifies (integer/null, string/null, or
sorted duplicate-free id arrays) and their SHA-256 digest is compared against a
value in /tests/expected.json, baked once from the reference resolution. The
answers file must be a real regular file the agent produced, not a symlink
redirecting the verifier at another path.
"""
import hashlib
import json
import os

import pytest

ANSWERS_PATH = "/app/answers.json"
QUERIES_PATH = "/app/data/queries.jsonl"
EXPECTED_PATH = "/tests/expected.json"


def _load_queries():
    """Load the agent-visible query list."""
    queries = []
    with open(QUERIES_PATH) as fh:
        for line in fh:
            line = line.strip()
            if line:
                queries.append(json.loads(line))
    return queries


def _load_answers():
    """Load the agent's answers.json as a JSON object."""
    with open(ANSWERS_PATH) as fh:
        return json.load(fh)


def _load_expected():
    """Load the baked per-group ground-truth digests."""
    with open(EXPECTED_PATH) as fh:
        return json.load(fh)


def _query_types():
    """Map every query_id to its declared type."""
    return {q["query_id"]: q["type"] for q in _load_queries()}


def _canon_set(qtype, value):
    """Validate a set-valued answer is a sorted, duplicate-free JSON array of ids."""
    assert isinstance(value, list), "{} answer must be a JSON array, got {!r}".format(qtype, value)
    assert all(isinstance(v, str) for v in value), "{} array must contain only id strings".format(qtype)
    assert len(value) == len(set(value)), "{} array must not contain duplicate ids".format(qtype)
    assert value == sorted(value), "{} array must be sorted ascending by id".format(qtype)
    return value


def test_answers_file_is_a_regular_json_object():
    """answers.json must be a real regular file (not a symlink) holding a JSON object."""
    assert os.path.exists(ANSWERS_PATH), "/app/answers.json does not exist"
    assert not os.path.islink(ANSWERS_PATH), "/app/answers.json must be a regular file, not a symlink"
    assert os.path.isfile(ANSWERS_PATH), "/app/answers.json must be a regular file"
    assert os.path.realpath(ANSWERS_PATH) != os.path.realpath(EXPECTED_PATH), \
        "/app/answers.json must not alias the expected-digests file"
    answers = _load_answers()
    assert isinstance(answers, dict), "/app/answers.json must contain a JSON object at the top level"


def test_answers_cover_every_query_id_exactly():
    """The output must map every query_id in queries.jsonl and no others."""
    expected_ids = set(_query_types().keys())
    got_ids = set(_load_answers().keys())
    missing = expected_ids - got_ids
    extra = got_ids - expected_ids
    assert not missing, "answers.json is missing query_ids: {}".format(sorted(missing)[:10])
    assert not extra, "answers.json has unexpected query_ids: {}".format(sorted(extra)[:10])


def test_direct_lookup_answers_have_valid_shape():
    """directives answers are integers or null; alias answers are strings or null."""
    qtype_by_id = _query_types()
    for qid, val in _load_answers().items():
        qtype = qtype_by_id.get(qid)
        if qtype == "directives":
            assert val is None or (isinstance(val, int) and not isinstance(val, bool)), (
                "directives answer for {} must be null or an integer, got {!r}".format(qid, val))
        elif qtype == "alias":
            assert val is None or isinstance(val, str), (
                "alias answer for {} must be null or a string, got {!r}".format(qid, val))


def test_set_valued_answers_have_valid_shape():
    """commanders/commands/apex answers are sorted, duplicate-free JSON arrays of ids."""
    qtype_by_id = _query_types()
    for qid, val in _load_answers().items():
        qtype = qtype_by_id.get(qid)
        if qtype in ("commanders", "commands", "apex"):
            _canon_set(qtype, val)


_EXPECTED = _load_expected()
_GROUPS = _EXPECTED["groups"]


def test_expected_ground_truth_is_non_degenerate():
    """The baked ground truth must cover every query id across all five types."""
    assert len(_GROUPS) >= 5, "expected ground truth is degenerate (too few groups)"
    graded = set()
    for g in _GROUPS:
        graded |= set(g["query_ids"])
    all_ids = set(_query_types().keys())
    assert graded == all_ids, "graded groups must cover exactly the full query set"
    types = {g["type"] for g in _GROUPS}
    assert {"directives", "alias", "commanders", "commands", "apex"} <= types, \
        "every query type must be graded"


@pytest.mark.parametrize("group", _GROUPS, ids=[g["id"] for g in _GROUPS])
def test_query_group_matches_reference_resolution(group):
    """Each query group's canonicalized answers must match the baked reference digest."""
    qtype_by_id = _query_types()
    answers = _load_answers()
    obj = {}
    for qid in group["query_ids"]:
        assert qid in answers, "missing answer for {}".format(qid)
        val = answers[qid]
        if qtype_by_id[qid] in ("commanders", "commands", "apex"):
            val = _canon_set(qtype_by_id[qid], val)
        obj[qid] = val
    canon = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canon.encode()).hexdigest()
    assert digest == group["sha256"], (
        "answers for query group {} ({} `{}` queries) do not match the expected values".format(
            group["id"], len(group["query_ids"]), group["type"]))
