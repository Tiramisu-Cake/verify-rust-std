# PR02 automatic-harness entry reset — source review

Reviewer: independent Codex reviewer, Luna High. Scope: source candidate only; CI package delta review remains pending. No local compilation, Kani/CBMC, build, or CI was run.

## Identity and packet

- Baseline: `932fb8395a58f8c86c0d702ba2cae835823b2962`
- Candidate: `f695f653efaa1f7ac6774a079104de8cc0ff81fc`
- Candidate tree: `ae00c4f05316e1129d7ce911417c627fda1dc9ea`
- Diff SHA256: `397a82bb213e53993c1b818287358764d610efd50a00634b64ff98e078804cbb`
- Spec SHA256: `05c4f424a1ec69559a3a20968fa9444a52684788cc66f0444922b9b681aed392`
- Packet SHA256: `182ae0994b7cf915215047e550b3078e5b161619865aaf4616e2c398b82eb2ad`
- `smallsort-session review check` returned `PACKET_VALID_NOT_REVIEWED`, 16 files, proof credit `NONE`; this confirms packet identity only.

## Findings

No source blocker found.

- In `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs:81-103`, the added recognition is exactly `KaniFunction::Intrinsic(KaniIntrinsic::AutomaticHarness)` through `KaniFunction::try_from(instance)`. The existing `kanitool::proof_for_contract` and `kanitool::proof` attribute checks remain intact. `UninitPass::is_enabled` at lines 46-52 still gates this path on Uninit being enabled. The transform invokes `inject_memory_init_setup` once at lines 60-64; that helper inserts one initialization call before the first statement/terminator at lines 111-145.
- The reset is placed at the generated harness wrapper entry. `BodyTransformation::new` runs `AutomaticHarnessPass` before `UninitPass` (`kani-compiler/src/kani_middle/transform/mod.rs:116-145`); the automatic pass clears and builds the wrapper and its contract setup/arguments before Uninit instrumentation (`kani-compiler/src/kani_middle/transform/automatic.rs:2385-2402, 2446-2507`). Therefore the inserted call precedes wrapper setup and the target/model call, including the formatting branch's early return from the automatic pass. The intrinsic matcher does not select the target/callee.
- The immutable-allocation finalizer's fatal missing-reset behavior remains unchanged (`kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs:279-291`). No finalizer weakening or unconditional reset materialization was introduced; the pass is gated by Uninit and by the generated harness intrinsic identity.
- The seven fixtures under `tests/script-based-pre/autoharness_entry_reset/` cover the required zero-argument typed immutable byte-array return (`seed_only`), argument plus seed, no seed, contract seed, initialized read companion, uninitialized read negative, and Uninit-off case. The fixture sources use APIs already available in the PR02 baseline slice; no fixture relies on heads 3–7. The two read fixtures use offset 3, so they distinguish the last-byte witness from a fixed zero-offset read.
- Each fixture's `config.yml` uses the repository's `script: run.sh` / `expected: expected` script-based-pre form. Commands use `kani autoharness ... --output-format=regular`; the negative script explicitly captures and checks exit status 1. Expected output patterns are consistent with existing regular-format script-based-pre fixtures. The Uninit-off command omits `-Z uninit-checks`.
- `git apply --check` of the full baseline-to-candidate patch passed against exact C2 final `8e299aa6243bc5f06a29c51e98aafa9564478220` (`/root/kani-fix-3300-c2-slices-w15`) and exact SEL1 `14bc57fdb99960240c4944845a3d985c8af4dcf7` (`/root/kani-fix-3300-sel1-c2-w14`). No conflict context difference was reported.

## Recommendation

Source candidate: **GO for source scope**. This is not a GO for the complete task: inspect the separately prepared CI-only package as a required review delta before whole-task acceptance. No CI or proof result is inferred here.
