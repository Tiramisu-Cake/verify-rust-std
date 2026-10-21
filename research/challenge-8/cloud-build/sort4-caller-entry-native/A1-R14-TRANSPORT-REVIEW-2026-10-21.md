# R14 source transport review

**Result: GO for the encoder-only change.** Reviewed `cloud-build/source-input.py` and the unchanged bounded transport suite. The diff only changes the XZ encoder filter to LZMA2 preset `6 | PRESET_EXTREME` with `pb=0`. It retains the standard XZ envelope and codec tag, and leaves schemas, decoder, memory/output caps, and dependencies unchanged. The suite exercises the compact encoder through its bounded XZ decoder and verifies exact UTF-8/binary content and restored Git object closure.

Source-closure review: `make_payload` still obtains each selected commit/tree/path closure through `repo_record`, pools identical object records without dropping paths, and serializes the same inner shared-object payload before compression. The reviewed diff does not alter path selection, object identity, recipe validation, or restore checks. Existing decoder checks still enforce the 128 MiB XZ memory limit, 64 MiB decoded limit, EOF/trailing-byte rules, and strict envelope/codec validation.

Validation: `python -m unittest test_source_input_transport -v` from `research/challenge-8/cloud-build` passed all 6 tests; `git diff --check -- research/challenge-8/cloud-build/source-input.py` passed. No compiler, verifier, preparer, or proof pipeline was run. The full committed-candidate static restore and exact byte/config checks remain separate integration gates.

Reviewed source SHA-256: `07884dc4da4651112303c273c2e8b5961172cf177275a40fe616a905ffe8816c`.
Reviewed patch SHA-256 against the current worktree base: `496384e9b9a84ab6af994a758b9910107613ba3257607687d2f25af58446d184`.
