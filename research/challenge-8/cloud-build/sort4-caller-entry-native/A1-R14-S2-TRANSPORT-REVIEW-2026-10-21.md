# R14 S2 source transport review

**Result: GO for the localized transport and packaging edits.** `source-input.py` changes only the standard LZMA2 filter's `lc` from its default to `4`, retaining the existing `utf8-xz-envelope-v1` XZ envelope, preset `6 | PRESET_EXTREME`, `pb=0`, dictionary, match depth, schemas, object closure, strict decoder, and size/memory limits. `package-evidence.py` removes only the docstring on the existing `check_archive_size`; the function body, call site, cap, and failure diagnostic are unchanged.

The source transport still serializes every selected commit/tree/path object from `repo_record`, then compresses the same payload. The XZ decoder remains capped at 128 MiB memory and 64 MiB decoded bytes and retains truncation, trailing-byte, codec/schema and object identity checks. The rationale records the same-payload lc=4 result at 571288 bytes (under unchanged 571567 source capacity), with exact decode equality; no source input is removed and no limit is raised. Final candidate static restoration/config validation remains required.

Validation: `python -m unittest test_source_input_transport -v` passed 6/6, including exact UTF-8/binary restoration, object closure, and corrupted/truncated/oversized rejection. `python -m unittest test-package-archive-limit -v` passed 1/1 at the inclusive archive-cap boundary and cap+1 failure. `git diff --check` passed. These are local synthetic transport/package tests only; no compiler, preparer, verifier, or Cloud Build was run.

Reviewed source SHA-256: `833313879260f2b626f731abc82d221ce0b9e817cd21d99c87c09e4939a7953d`.
Reviewed packager SHA-256: `1843505d2c9a9329c730ad468f89060c2846d332a03ecf5063b96cb83885dfd4`.
Reviewed two-file patch SHA-256 against current worktree base: `46fb620e824d6512d7dc945b34a28a6527c9d2e0472b11891546eaf977dd4e36`.
