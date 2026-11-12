#!/bin/bash
#
# Runs inside the SHARED environment image. Harbor overlays tests/ at /tests only at verify
# time; ground truth (expected.json) stays under tests/, never in environment/. pytest flags
# are pinned so the verifier ignores any agent-planted conftest/cache/rootdir under /app.
set +e
pytest \
  --rootdir=/tests \
  --confcutdir=/tests \
  --noconftest \
  -p no:cacheprovider \
  --ctrf /logs/verifier/ctrf.json \
  /tests/test_outputs.py -rA
rc=$?

if [ $rc -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
