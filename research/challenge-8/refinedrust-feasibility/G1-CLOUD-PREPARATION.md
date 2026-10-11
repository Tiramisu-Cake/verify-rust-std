# G1: Cloud admission design

2026-10-11. **READY FOR TECHNICAL REVIEW; NOT DISPATCH READY; NOT_RUN.** Текущее разрешение — только документы, Cloud budget/charge **0/0**. Пакет уточняет G1 из [EXPERIMENT-PLAN](EXPERIMENT-PLAN.md) по [G0 на `60272e31ae4d1780dea05da525c345b0c6534799`](https://github.com/Tiramisu-Cake/verify-rust-std/commit/60272e31ae4d1780dea05da525c345b0c6534799). G1 теперь строго frontend admission/diagnostic: foundational Rocq replay из прежнего плана отложен и не входит в PASS. Generic recovery, assumption closure и G2 остаются NOT_RUN. Для текущего задания эта acceptance definition заменяет прежнюю строку G1; старый план сохранён как история, без второго конкурирующего PASS gate. Его прежние warm G1/G2 3600 s и cold 7200 s здесь не действуют и не наследуются.

## Input freeze

| Input | Exact identity / gate |
| --- | --- |
| Source/policy snapshot | `c7ca8c467aecf10a4b53039372ee97714f854ee3`; policy-change `5bf53668a4afa51c302e599be91a2dbc4b24042d`. [AGENTS](https://github.com/Tiramisu-Cake/verify-rust-std/blob/c7ca8c467aecf10a4b53039372ee97714f854ee3/AGENTS.md), WORK-POLICY, AGENT-RUNBOOK, Cloud README/v2 protocol |
| Source closure | library tree `4ae912b9caf2e477a2b0caef084fb349c878f0fd`; library/Cargo.toml blob `87df966bb6b874faa0358c6d626954d76b384890`, Cargo.lock `940c8dd662869d6fc2eaa1aaa532f3052769c009`, core/Cargo.toml `66452e569f7782f957624f5045a9b0489997981e` |
| Actual SmallSort | blob `e555fce440872898e47fd5114f32eb15401d07df`, SHA256 `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`; [guard L295–309, helper L542–578](https://github.com/Tiramisu-Cake/verify-rust-std/blob/c7ca8c467aecf10a4b53039372ee97714f854ee3/library/core/src/slice/sort/shared/smallsort.rs#L542) |
| Callee blobs, relative to core/src | mem/manually_drop.rs `ca008a82ee6f09bbd429f2ef40f5e33f17ebf69b`; mem/maybe_dangling.rs `a5f77e667f9757c56e7ff088a928e3041440f68c`; ptr/mod.rs `50d2396728ee411f9e958239322c4419cee6b307`; ptr/const_ptr.rs `a51e1a4fc29814ff1dd13ffcf2f4e71a766084c3`; ptr/mut_ptr.rs `6e6e72eb03fbf20f593866213e89fce1879b0bd1` |
| RR frontend/logic/specs | [development `332d945fafa14bf55c0c8390cb35ec4b0c012cff`](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/tree/332d945fafa14bf55c0c8390cb35ec4b0c012cff), unpatched; rr_frontend/Cargo.lock SHA256 `b66b9e281478be8263eab9ba210964cdd8f1db92535b7b81305f50dea03682aa` |
| Compiler | nightly-2026-08-28; `1.100.0-nightly (e457a7b0d 2026-08-27)`; [full rustc source SHA `e457a7b0d326d67b4322ef0d11bd715cfaeda48f`](https://github.com/rust-lang/rust/commit/e457a7b0d326d67b4322ef0d11bd715cfaeda48f). Future Cloud rustc -Vv must independently match |
| Official distribution manifest | [2026-08-28](https://static.rust-lang.org/dist/2026-08-28/channel-rust-nightly.toml), SHA256 `a10ff685d2159307e414d29c1a1f97e576c77c59ebe93c4c13d075fc7e088d4b`; metadata only, archives not downloaded on VPS |
| Proof/harness SHA | **UNASSIGNED**: future published own ghost annotations, controls, config and evidence collector; G0 docs SHA is not executable proof input |
| Infra SHA / recipe | **UNASSIGNED**: separately reviewed dispatcher-compatible registration/entrypoint/recipe. Own policy base contains docs, not a registered RR client |
| OCI digest | **UNCONFIRMED**: no audited compatible RR image found in inspected repository evidence; no registry inventory assertion. Freeze digest and complete dependency/build receipts before admission |

Last three rows block submission, not review. Do not fill them with branch names, mutable tags or historical VF SHAs. Source remains fixed even if future infra comes from a separately reviewed commit.

## Environment closure

Prefer a frontend-only immutable Linux x86_64 OCI image, assembled in separately authorized Cloud setup from pinned OS digest, exact Rust archives and RR frontend Cargo build with --locked. Freeze crate checksums/vendor inventory, system packages/linker, arguments and resultant image digest. Include cargo, rustc, rustc-dev, llvm-tools-preview and target rust-std from [RR toolchain](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/rust-toolchain.toml). rust-src may provide diagnostic sysroot identity, never replacement actual core. No image/toolchain pulls or extra full checkout on VPS.

Official xz SHA256 receipts, x86_64-unknown-linux-gnu (rust-src target-independent):

| Archive component | SHA256 |
| --- | --- |
| rustc | `b41f2e026eae47d66d67b9199c31084e470a05166c78d6770e8a838f8e98331f` |
| cargo | `1fb253af555a7edd3758bc3a00ddf262f6d5114a21e43e7c5d8207ea34887cb7` |
| rustc-dev | `f6a29511f80d08ff780a566b63ee54775d8f875b33716202035641748e40be71` |
| llvm-tools-preview | `88967a1ad48a1784e558fe8324b693322d3e49c498554712e20339ceb7516d00` |
| rust-src | `6e6713037291a3880e3c9b3c5949a516d5064250541bfb88cb20226285c50a91` |
| rust-std | `73c5854230a3424379137953e835ce0c83d0282929214722e43831bebd547ce3` |

Future setup validates manifest/archive checksums and executable versions. Actual Cargo closure includes contracts tree `f05daf8f588874108a5e92b07b3bfad8f21996ea`, portable-simd `dad7d5af24b99d85aa32eddac4e664b026fb9bef`, stdarch `775ec65ed2e85db47b020f9b5bfacdc7182dc306`, root/workspace config and locked registry inputs actually required. Future recipe enumerates paths/modes/hashes. Missing configuration/path dependencies fails before compilation. No bootstrap/full std tests.

Rocq/Iris are not executed in G1. Committed RR .rrlib metadata is input, not replay. Later proof profile, if approved: OCaml 4.14.2+flambda, Rocq core 9.2.0/std 9.1.0, Equations 1.3.2+9.2, Dune >=3.23.1; stdpp `729c671ed573749588f699138e306dbae880f3e1`, Iris `4a6add171278417fec6da7c490fe487e502326f0`, iris-contrib `0ed8e45b554b2c7f7b9102818bc3ee27d8fa18b8`, lifetime `0a062fb1eb68f9a6ac38412347117b294fc7746b`. Do not add cold proof-stack costs to G1 or mix with Nix closure. Alternative flake.lock SHA256 `eeee3f5cd5f21378c0d146d92b1dd06135b8043f25d323436ef1c26974d6bad1`; actual Nix derivation closure would require separate review.

## Actual-source route

Stock [cargo-refinedrust](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/refinedrust_frontend/src/bin/cargo-refinedrust.rs#L54) wraps Cargo check without per-DefId CLI selection. [register_drop_glues](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/translation/src/lib.rs#L1831) scans crate ADTs even with register_all_adts=false. Thin extracted crate cannot be exact positive: its ManuallyDrop comes from newer compiler sysroot; text equality alone does not establish DefId/layout/MIR identity.

Minimal exact route: disposable pinned library/core checkout, ghost-only attributes registering generic insert_tail, CopyOnDrop::drop, ManuallyDrop::new/Deref and MaybeDangling::new/as_ref plus required ADTs/callees. Record actual recursive callee closure, including pointer methods/compiler glue. Strip annotations and require original signatures/bodies byte-equal; archive original and annotated source. Retain generic bounds/runtime. No only_spec replacement for ordinary wrappers, blanket skip attributes or new frontend rules.

First native core compatibility on RR nightly, then RR admission. Repo nightly-2026-02-05 differs from RR nightly-2026-08-28. Future candidate, **NOT_TESTED**: `cargo refinedrust -- --manifest-path library/Cargo.toml -p core`. Implementation must freeze target/profile/features, lock behavior, internal-core settings (including whether RUSTC_BOOTSTRAP is required), exact command and executable capability. Direct-core build failure is STOP, not permission to invent bootstrap pipeline or swap source.

Use explicit RR_CONFIG/output/log directories and pinned lib_load_paths. [rrconfig](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/rrconfig/src/lib.rs#L68): find_stdlib=false, register_all_adts=false, skip_unsupported_features=false, dump_debug_info=true, dump_borrowck_info=true, generate_linking_requirements=true, panic_abort_mode="conservative", compiler -Cpanic=unwind; retain overflow/validity checks. run_check=false means generation only; no_verify=false, admit_proofs=false, trust_debug=false. Generated obligations remain unproved. Record effective config/allowlisted environment (overrides exist), no post-generation hook/ambient specs. Confirm stock dump formats before dispatch; absent required artifact is INCONCLUSIVE, not reason to patch logging semantics.

## Evidence, controls, verdicts

Collect submitted config/certificates, original/runtime/ghost-strip hashes, image/RR/compiler/component receipts, complete ordered logs, timing/peak RSS/disk, MIR/borrow dumps/Radium/specs/linking obligations and hashed file inventory. For selected bodies record crate identity, DefId/source span, MIR blocks/callee edges and Radium definitions. Compiler-generated glue requires actual resolved callee map, beyond user Drop method.

| Required observation | Diagnostic obligation, not proof |
| --- | --- |
| First comparator before read/guard | Real unwind edge without nonexistent guard |
| Late comparator after shift/updated dst | Borrow-end obligations, actual Drop terminator/glue/CopyOnDrop body and resume unwind |
| Normal exit | Actual guard Drop/copy; ManuallyDrop temporary suppresses payload T Drop |
| Generic FnMut | Selected call spec, unwind condition/post, framed lender/borrow obligations; True post is not CURRENT recovery |
| read/copy | Syntypes/layout; value Copyable versus Rust T:Copy; initialized/uninit bytes, scalar versus ArraySynType(T,1); alignment/provenance/nonoverlap/ZST obligations |
| Callee closure | Classify translated actual body, compiler intrinsic, RR shim/spec or unsupported. Ptr shim is modeling boundary, not source callee proof |

P0: independent tiny own frontend fixture with MIR/Radium output. P1: all actual generic target bodies and relevant glue. N1: separate unregistered-callee fixture, expected UnknownProcedure at intended call ([calls.rs L265](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/blob/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/translation/src/body/function_translation/calls.rs#L265)). N2: saved metadata certificate with wrong source hash/missing required cleanup; collector rejects named correspondence gate, without modifying actual runtime. Freeze exact fixtures/stages/locations in future harness commit. Unrelated errors do not satisfy N1. Ownership/alignment proof negatives are G2.

PASS: P0 and intended N1/N2, all P1 bodies, complete source→MIR→Radium/callee/cleanup correspondence, complete evidence and explicit unproved spec/resource inventory. INCONCLUSIVE: setup/OOM/timeout, missing dumps or unrelated whole-core registration/spec failure before the selected target is observed. STOP: compiler/source incompatibility, unsupported selected type/operation, erased cleanup or new trust requirement. STOP / LIBRARY-SPEC: actual selected callee has no binding/spec (including target UnknownProcedure); this establishes a library admission gap, not semantic impossibility. Distinguish missing spec from unsupported semantics. No admission PASS establishes CURRENT recovery, scalar/array lemma, transitive assumptions or actual safety.

## Lane, resources and budget proposal

Design only: stable owner refinedrust-feasibility, phase RR-G1-ADMISSION-<approved-date>, lane refinedrust-g1-admission; own absolute ledger/state under this directory. None registered/created. Future smallsort-cloud-recipe-v1 recipe binds entrypoint and exact infra_paths/proof_paths/modes/hashes; existing dispatcher submits pinned objects with --no-source and explicit proof/infra SHAs. New owner/phase/lane/image provider contract needs separate reviewed implementation. Inspected dispatcher hardcodes Ubuntu execution digest and E2_STANDARD_2: proposed RR OCI digest, machineType and diskSizeGb need explicit reviewed support; cold image build/push additionally needs a recipe and authorized repository permissions. Existing dispatcher is retained, but these features are not already available. Runtime examples inspected at `ac6a1c4ebe84ee05302f4cc5829ff1075e99d822` and `984d8007c0b2250b8a7a2c3b9bd37e6f32aaa249`; neither selected as future infrastructure.

Preserve [v2 protocol](../cloud-build/PARALLEL-BUILDS.md): at most two project-wide queued/running/unresolved Builds, one per stable owner/ledger, including setup. Client/live incompatibility STOP; no manual coordinator edits, peer aliases or direct alternate submit. Existing explicit project/account/configuration and evidence bucket from [Cloud runbook](../cloud-build/README.md). Cold phase uses same owner, separate authorized ledger; admission waits for terminal reconciliation.

Propose default-pool E2_HIGHCPU_32 (32 vCPU/32 GB), disk 100 GB, Cargo/frontend jobs 2, >=40 GB free workspace. Planning minimum 16 GiB; peak use unknown. This is an intentional memory-for-CPU tradeoff pending quota/region review, a resource candidate rather than a measured minimum; only two jobs are used. Observed E2_STANDARD_2 ~7.8 GiB is no RR compatibility evidence. [Google machine configuration](https://docs.cloud.google.com/build/docs/optimize-builds/increase-vcpu-for-builds) and [schema](https://docs.cloud.google.com/build/docs/build-config-file-schema) describe explicit resource configuration; provider availability/exact config require review.

Warm one-attempt timeout **1200 s**, reservation **1260 s**. Cold frontend image one-attempt timeout **1740 s**, reservation **1800 s**, separately authorized. Combined ceiling 3060 s if needed. These are caps, not measured completion predictions. [Published default-pool price](https://cloud.google.com/build/pricing) $0.0624/min gives execution-only estimates $1.25 warm/$1.81 cold, excluding registry/storage/egress and work outside attempts. Google queue is unbilled but conservatively charged by project ledger. Recheck price/location before approval. No retry or cold proof environment included; overruns/unresolved state require reconciliation, not duplicate submission.

Recommendation: review bounded diagnostic design, separately authorize implementation/freeze gates. Execution is not ready while image/executable inputs are absent. G1 success would locate actual exceptional resource obligations and support a new G2 decision; it would not justify migration/Tool Application.
