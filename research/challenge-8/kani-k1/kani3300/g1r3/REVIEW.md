# KANI3300 G1R3 — независимое статическое ревью

- Baseline: `02b734151ada1dd0d216b0db329776eb522d2d67`; candidate: `6bb067476116704763502763984b225014dce221`; candidate tree: `03f3d79d0317436040c3b10b0e094a88ce99092c`.
- `smallsort-session review check`: `PACKET_VALID_NOT_REVIEWED`, 13 files, proof credit `NONE`; packet SHA256 `185f984304631b2ff50078790d562e31f16807463319e82c9e565470eca90209`. Нормализованный spec SHA256 `f8a7045a7e838a34e35ccc6a8cd360b7936c6703cccdeb0de856f2296f74d89d` (raw `REVIEW-SPEC.json`: `0dfad465816af258b2052dc63d758d75ac9b16e4cf54058675fe02ccbc1a5775`). Diff SHA256 `d87cf7aa909a79db7dd266a15c79fc7ecd230e23f834d59cd50faaba26377f39`.
- Sweep reviewed: `SWEEP.md` SHA256 `7764b6a06425734f092e0724e1a96788523ea63f683392aa86808534f02b8809`; Rust source manifest SHA256 `e2b1672ac9a31b71b821c006a0ad3a7f32b93a17c807f4e319f4ee431185a9ff`.

## Findings

No static findings in the scoped candidate. Its only two changed paths are the specified negative fixture and ManuallyDrop golden. The four `std::mem::forget` wrapper calls become direct intrinsic calls; all four moved-from `u32` reads remain, and the negative golden remains byte-identical with 70 expected failures. In the pinned Kani source, the intrinsic Forget call has a no-effect model plus `Operand::Move` storage invalidation (`uninit_visitor.rs:604–622,1112`); moved non-union fields are invalidated at their source (`:175–188`). The union type contains `ManuallyDrop<NonCopyWord>`, not a nested union. Pinned core `mem::forget` does construct `ManuallyDrop`, so bypassing that wrapper removes the identified G2 guard path. The ManuallyDrop golden changes only the property owner to `std::mem::ManuallyDrop::<U>::new.unsupported_construct.1`; diagnostic, failure, harness, and summary are retained.

The 23-fixture G1 sweep's wrapper/rejection controls match source inspection: remaining `ManuallyDrop` payloads are non-union types; zero-length array forget and explicit ManuallyDrop/niche/unaligned/volatile rejection cases remain controls. No additional unintended std/core wrapper path found.

A3 static metadata matches the request: exactly two selectors, full P1+G1 production, selected sources/goldens/helper pinned to the candidate, native pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, package B untouched, timeout 5 minutes, proposed cost `$0.4725` within `$0.4760`, Cloud spend `$0`. Applied inventory records 12 paths; production source diff against `3d085249c9c6c49a9c2e5747e2167d629748fb70` is empty. These checks establish package consistency only.

## Limits

Static review only. Compiler/Kani/native run is `NOT_RUN`; expected negative and ManuallyDrop outcomes remain unobserved, and no proof credit is established. This report is not a GO or dispatch authorization.
