# E2 prepared result — SOURCE-REPORTED / NOT_RUN

READY 19588e0afa9994a0e892f7f93a72534bdc061452
Tree: b16a7d8b5368d1c90a5ddad2ecb4ee4d65b8f2e5. Base C0: 478aad601fc5a45b142d6a8a2ae85594add9a0e6.
Clone /root/kani-fix-3300-e2, branch fix/kani-3300-e2. Clean committed tree; author and committer Tiramisu-Cake <igkharin@gmail.com> through git -c. No push.

Four immutable subrange/relocation controls now use three-slot comparisons to avoid scalar-sized raw_eq transmute lowering, preserving offset 1, exact bounds, relocation-bearing storage and a real hole. No golden changed. Actual retained raw_eq/MIR must be checked in CI.

Named immutable statics now register the exact original allocation mask with existing M1 reset-completion seeding. Qualification requires Freeze, the existing type domain, immutable relocation-free allocation, exact size and matching declared emitted type/lifetime/const/nonextern/nonTLS properties. Named/promoted allocation aliases require exact allocation equality; anonymous storage validation remains strict. The unchanged static legal/hole pair distinguishes initialized zero from None. No broader subrange or relocation admission is introduced.

Python identity/scope/fixture maps PASS, git diff --check PASS, approved scratchpad rustfmt PASS (rustfmt 1.11.0-nightly (c1070d6938 2026-09-28)); independent Luna HIGH source review found no blocker. Source changes are exactly two backend files and four fixtures, listed and hashed in STATIC-CHECKS.json. All kani_middle/runtime/driver/schema/script/JSON subtrees and inherited controls retain C0 identities.

Local cargo/rustc/Kani/CBMC/Miri/builds/CI NOT_RUN; no Cloud spend. These are source claims, not proof credit. Static legal/hole success and exact failure localization need coordinator CI. Subrange/relocation legal may expose a conservative falseFAIL after the unrelated transmute failures are removed; their expected SUCCESS remains unchanged and their holes are unqualified until legal and exact failure sets pass. No final-export/M3 qualification is claimed. See CI-REQUEST.md.
