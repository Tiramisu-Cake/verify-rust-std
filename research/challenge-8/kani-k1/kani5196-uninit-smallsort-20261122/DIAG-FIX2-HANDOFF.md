# Kani 5196 diagnostics goto-cc fix handoff

Run `45158321038` stopped during tool attestation because the `goto-cc` first line advertised the pinned CBMC release `6.11.0` and the emulated GCC release `13.3.0`. The updated check requires at least one version attached to `goto-cc` or `cbmc-` on the first stdout line and requires every such version to equal the CBMC pin. The trailing GCC version is outside that comparison. CBMC and `goto-instrument` still use the existing whole-line release check.

The tests use the six observed first lines by default. They cover the exact GCC-style banner, a mismatch in either labeled release, a GCC-only banner, empty output, a release appearing only on the second line, malformed releases, and preservation of the raw setup receipt. The diagnostic request refreshes the SHA-256 entries for the parser and the two changed test files.

## Local Git identities

| Item | Value |
| --- | --- |
| Worktree | `/root/kani-ch8-kani5196-diag-control-20261123` |
| Control branch | `ch8-kani5196-diag-control` |
| Control head | `0334677b1333c5686914a0d0014a9b0b9edfbea8` |
| Shared control and trigger tree | `ce8c13e5d5b8dde79fff7766e1230def7bcb1352` |
| Trigger branch | `ch8-kani5196-diag-trigger2` |
| Trigger commit | `4f638ad9619729a6df1fd65077c86e6b7931b295` |
| Sole trigger parent | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

The trigger uses a CI-enabled message matching the convention of prior trigger `57c4eeb7a9`. The control and handoff commits use `[skip ci]`. The new commits are local. Live attestation and diagnostic roots await an authorized run.

## Validation

The exact commands from **Validate frozen control and run synthetic tests** ran from the parent of a clean, depth-three `control` checkout of the trigger. The environment used `PYTHONDONTWRITEBYTECODE=1` and the workflow's expected repository, push event, ref, run attempt, and trigger SHA.

```bash
python3 control/ch8-kani5196-diag-control/diagnostic.py validate
python3 -m unittest discover -s control/ch8-kani5196-diag-control
```

Frozen validation passed for the trigger's event and sole parent, changed paths, all 35 payload hashes, and all five fixtures. All 25 diagnostic tests passed.

The shared control and inherited supervisor suites also passed from the control worktree.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ch8-kani5196-control   # 27 tests passed
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s ch8-q-pilot-control  # 14 tests passed
git diff --check ccfcecba64 HEAD
```
