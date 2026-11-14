# Independent static review — SEL1 followup

## Reviewed identities

- Source baseline `46e46583ff112cae9c43aea1ba5dd6145e5e8387`.
- Source candidate `b6f1b08eb512ff9006aff7b4924c2e8f13930d70`, tree `c426f0cb9be59838d217d2ec68334cbcbd9721ac`.
- Review packet spec SHA256 `63e5a11fc18b341c9096bc794bdf000e6cef3e17148b6799873434fe7e51f13f`; diff SHA256 `66afd4a2960e45b54320c348c87f7ef925f52c15e8279a340596cab8c23ca358`.
- Replay baseline `c9619b15022fb43f1e961e01695e64875ad68fe9`; replay candidate `3bb04079537dc4611d5e214586a291966905e018`, tree `2fb160258eee2c8ede10ea71a3a5076632989342`.

## Source review

The classifier defect is addressed at the correct identity layer. It requires `InstanceKind::Intrinsic`, intrinsic name `select_unpredictable`, a fallback accepted by the shared `has_intrinsic_fallback` predicate (`!must_be_overridden()` and `instance.has_body()`), exact defining crate and DefPath segments `core::intrinsics::select_unpredictable`, the monomorphized `(bool, T, T) -> T` signature, non-variadic form, and `checked_body`. The canonical path test requires exactly two namespace segments and the exact module/item names, so a `std` re-export reaches the one core definition without admitting neighboring intrinsics or a printed-name alias.

The visitor still rejects unsized or unmasked payloads before transfer, uses existing typed-storage/typed-value masks, validates actual call argument and return types, and requires the existing paired transfer protocol. I found no change to body ownership, alias modeling, transfer sequencing, or F5/F6/F7 behavior in this candidate diff. The core/std direct-call assertion is present. The negative overwrite control is renamed to `overwrite_hole`, retains its exact one intended uninitialized-read failure, and the nested-layout expected output still asserts the select refusal and one-failure count without pinning `std` versus `core` spelling. The manifest still lists 29 selectors.

No blocking source correctness issue found by static inspection. New runtime outcomes remain `NOT_RUN`; this review grants no proof credit.

## Replay/package review

Replay commit `3bb04079537dc4611d5e214586a291966905e018` changes the source binding to the candidate commit/tree and keeps the pinned std overlay `6075e7ce17179f45642c9ffe8fe09e3ec9395726` and its library tree unchanged. The request retains the same six row IDs, flags, serial workflow, requested branch, and no-retry policy. Its diff is limited to the binding and accurate source-state descriptions.

The current `full-export/` file hashes match `REPLAY-CI-OVERLAY.json`; `make-ci-delta.py --repo /root/kani-fix-3300-replay-c1-w15 --check` passed and verified delta SHA256 `48d3ff171b9e59c764e91c6a416121e85163dfdec1f3d1a5643b09dda0cebf64`. The 29 service tests passed, and the 7 generator Python tests passed. Source and replay `git diff --check` were clean.

**Package metadata needs refresh before treating the package as candidate-bound.** `PACKAGE.json`, `VALIDATION.json`, `README.md`, and `RESULT.md` still describe replay candidate `c9619b15022fb43f1e961e01695e64875ad68fe9`, old source pin `46e46583ff112cae9c43aea1ba5dd6145e5e8387`, and delta SHA256 `cbcb31b360b872d6ed8e8440b0decf15d424cf47f9e6f5f82dff01bea435b27a`. Current full-export hashes and delta differ. `REPLAY-CI-OVERLAY.json` correctly records the followup source binding and says the earlier quick run failed while followup runtime is `NOT_RUN`, but its `delta_against` text still calls the old source binding. Update those package/report identities and hashes before relying on them as the final package record; the full-export and delta themselves reproduced successfully.

## Limits

I did not run compiler, Kani, CBMC, Miri, builds, or CI. The owner formatter wrapper was not present in this reviewer environment; the supplied `ROOT-CAUSE.md` records that its formatter and `--check` passed. Static review cannot establish runtime behavior or proof acceptance.

## Final replay binding clearance

Followup metadata correction reviewed against exact final identities: source `b6f1b08eb512ff9006aff7b4924c2e8f13930d70` / tree `c426f0cb9be59838d217d2ec68334cbcbd9721ac`; replay overlay `f44ddc4313651fc2fd946ea7f4be60280de47cb5` / tree `863c98b069708f7f915399e6e22534706f5d04fb`; std overlay `6075e7ce17179f45642c9ffe8fe09e3ec9395726`; cumulative delta SHA256 `34d97db9a04fdec19fa1b51e626deceb74144ad97d38a544418bfb3bf314262b`.

`CI-BINDING.json`, `PACKAGE.json`, `VALIDATION.json`, `README.md`, and `RESULT.md` now agree on the source/replay pair and delta hash. I checked all 31 `PACKAGE.json` file hashes; all match. Each of the seven `full-export/` files matches both the binding hash map and the corresponding blob in replay commit `f44ddc4313651fc2fd946ea7f4be60280de47cb5`. The source worktree remains at the reviewed source commit. The metadata-only replay followup changes only `scripts/kani3300-replay/REPLAY-CI-OVERLAY.json`; `git diff --check` is clean. The prior stale `delta_against` pin is corrected. Old source/candidate identifiers remaining in the previous review packet and prior-review file are historical review inputs, not current package pins.

Quick run `43605855700` is recorded as FAIL on the old source per supplied owner excerpts; followup source/replay runtime remains `NOT_RUN`. The owner formatter script and `--check` pass are recorded by the main agent; I did not run that script independently. No tests were repeated for this metadata-only clearance. No builds, pushes, or CI were run; no proof credit is implied.
