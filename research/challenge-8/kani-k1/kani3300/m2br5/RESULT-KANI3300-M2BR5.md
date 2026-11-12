# KANI3300 M2-B/R5
Status: two reviewed SOURCE_READY_NOT_COMPILED diagnostics; NOT_RELEASE_CANDIDATE.
Research planner e6f888e604 fetched; ff-only confirmed before preparation.
Historical m2br4@df374dfdaa2959a59910d6a53424298784adc0b3 unchanged.
Fresh clone /root/kani-fix-3300-m2br5; root branch exact R1 1cd96e354ec45346b61c245554a50a8af8cb5ce7.
R5-01 bcc1a2af3fe13599b88acabc78c33e1394407dc5: U Hbuf + R1 Hcopy/GLUE.
R5-02 899ffb5f26b79e89cec1b7cc537d54be494ab390: R1 Hbuf + adapted U Hcopy + explicit R1 GLUE.
Both direct R1 children; only mem_init.rs changed; exact patches/trees/hashes in manifest.
All8 unified hunks/18 atomic changes mapped; no uncovered executable changes.
R1/R1 reconstructs exact R1; U/U without GLUE reconstructs exact U/V02 runtime.
U/U-with-GLUE hash recorded in memory only; shared GLUE remains an unresolved factor.
Source audit checks14 markers/13 model functions, signatures/arities/fields/constructors/unsafe/reset closure.
Pinned rustfmt/diff checks and isolated-index patch-to-tree reconstruction passed; no compilation claim.
Legacy lifetime/frame/return0/reset and arithmetic/false/full-span losses are explicit.
Frozen str resolver generic-arity caveat and usize→u64 bound disclosed; no compiler repair.
One independent Luna High review: READY_FOR_COORDINATOR_BUILD, no actionable findings.
R4 A/B/C build/killed outcomes remain coordinator-reported; actual C changed else and count.
V02 is a converted/FAILED endpoint, not PASS; full failure inventory/retained paths UNKNOWN.
CI-request: only R5-01/P1 then R5-02/P1, sequential build/inventory→solver by coordinator.
Second-step decision tree prepared, unexecuted; no third/fourth candidate or history rerun.
Build/solver NOT_RUN; no production fix, causal conclusion, equal-obligation relief or proof credit.
Cloud$0; dispatch0; local cargo/rustc/Kani/CBMC/Miri/build0; diagnostic pushes0.
Release/M1/M2/S3/work14 unchanged; P2/M3/integration held; no diagnostic release cherry-pick.
STOP after research publication; no further stage activation.
