# Current acceptance

A/B/C completed,772/3600s charged,2828 remaining; no active build.
[Final acceptance and scope](ACCEPTANCE.md). The entries below retain the
chronological states and historical failures; superseded pending/active statements
are not current instructions.

# Cloud Build migration evidence

Checkpoint: 2026-10-09; phase still in progress. A is accepted for infrastructure;
B stopped at source access, and C has not run. No new actual Rust proof claim.

All evidence prefixes are
`gs://smallsort-ci-evidence-504462351565/cloud-build/<BuildID>/`.
VPS downloads verified archive SHA256, every included file, external metadata,
submitted config hash, input SHAs and upload receipt for the four available
archives below. Missing initial evidence is recorded explicitly.

| Lane | Build ID | Final / original exit | Conservative seconds |
| --- | --- | --- | ---: |
| Initial smoke setup | 7bda20f0-cef7-4ff4-8c21-697374572b34 | FAILURE; upload127, no archive | 39 |
| Storage success | fd0020bd-967d-4e4b-ac20-83c578733389 | SUCCESS /0 | 47 |
| Managed error | 63862150-33e7-4b9d-b692-1231f9c34520 | FAILURE /42 | 54 |
| Internal timeout | 6604590a-f626-4ca0-81da-71f3d9091e25 | FAILURE /124 | 59 |
| B source preparation | 3e4c62e0-744b-4278-b10e-fc74f599dbe7 | FAILURE /128 | 81 |

Total280/3600, remaining3320. Charges are ceil(createTime–finishTime), including
queue, preparation, execution and upload; API execution intervals are separate
in [the ledger](BUDGET.json). Two rejected API requests created no Build and cost
zero seconds. Historical GitHub budgets and owner setup smoke are separate.
Machine API: E2_STANDARD_2; observed nproc2, MemTotal8147688kB, Ubuntu22.04.5,
x86_64. Per-stage time/RSS files will be produced by B/C once source loading works.

| Build | Infrastructure SHA | Input proof SHA | Archive SHA256 |
| --- | --- | --- | --- |
| fd0020bd | ac74f00c27207a0f23660b6a4de2e625dbec050e | 89e0a36f8df67bb2f66cf0564f497a0a4bad4aac | dbbc6c7d8294ca6d5360e7807ec2c0c12e50b6997e4540b371b869f9620c387e |
| 63862150 | ac74f00c27207a0f23660b6a4de2e625dbec050e | 89e0a36f8df67bb2f66cf0564f497a0a4bad4aac | d7416a4a8223dfca3dc76beb6166fcf1f1a0272ed658adc1dbf326c070387ab5 |
| 6604590a | 0de62646ddfdc36a8f2254a555f9a35cba94b000 | 89e0a36f8df67bb2f66cf0564f497a0a4bad4aac | 1e103e19acedf068ed84b8ee95812fdbc2ea9e19675dbd010b1c4e81841b044c |
| 3e4c62e0 | f694acddad88d4c353850f3a170adb7adb30bdb0 | a0cfd30e066acbaf1b5406cd9773f54388cc45be | c474f40ca1209292cfafbb1f7424a8d2c58bb22e2b1fdda0e395dcf1e532b995 |

All A proof-acceptance flags are false; only the success probe has smoke_success.
The error and timeout logs preserve their causes and upload never overrides the
failed final verdict. B has incomplete proof evidence because no tools/fixtures
ran. Its full preparation stdout/stderr and original Git failure are retained.

B comparison: frozen stock fixtures at
`a0cfd30e066acbaf1b5406cd9773f54388cc45be`, historical run37694000195. Planned
matrix retains stock u32/raw pointer positives, false posts, unwind/cleanup and
dead-code controls, including historical INCONCLUSIVE generic-forget limits.

C comparison: constructor fixtures at
`1378f0ffc8342233349fae3df5a938c4a021c8d7`, historical accepted O3 run37700450091.
Historical O3 runner applies the same two patches: S6 candidate
20f7d07ac9bdaca7c46f737b89925dfac3f4cef66c3f5d48aa9634ac949dbc1c, then CFG
593d09405379974ffbc475c2e0b65d648d8a6913f55b765dd0c3bebdc0922781.
Only the constructor matrix is selected, not the whole eight-stage S6 gate:
16 source/proof cases, nine typed MIR admission mutations, ten native controls,
stock/patched false-post and pointer-frame controls. Actual callee stays NOT_RUN.

Pinned VF source f76012fb518703b1d98e243ac4f487f16877cfcb, nightly2026-09-25
compiler f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f, std base
cd371e035c7e573760c43bf934d53e8118ee3e7d. New source-built console hashes will
be recorded separately; byte identity with GitHub binaries is not assumed.

The pinned-input archive fallback is prepared pending explicit owner approval
because it changes the requested public Git fetch route. It transfers committed
source objects only, checks original commit/tree/blob identities and source-file
hashes, and needs no credential export or cloud resource changes. See
[commands and second-direction requirements](README.md).

## Continuation authorization

The owner has approved pinned Git-object delivery, replacing anonymous fork
fetch. The280-second account carries forward,3320 remaining at resumption.
Pre-dispatch Git/hash preparation checked original objects and bounded config
shape for B/C without any verifier, fixture generator or compilation on VPS.
Cloud restore validation and B/C acceptance remain pending the new builds.
The permanent workflow and remaining automatic Actions triggers are documented
separately. ChatGPT already reads the evidence bucket via SmallSort CI — Read Only;
new builds will publish full indexed text logs separately with <=8MiB objects.

## B confirmed — Cloud stock chain

Build `ce77c943-f657-47da-9dfa-4b6e16d3679e` SUCCESS,164 conservative seconds,
original proof `a0cfd30e066acbaf1b5406cd9773f54388cc45be`, infrastructure
`30fc3b42a2fb980b49174d459ec5cfbea778379b`.
Input config SHA256 f532b8cccd907fef8076a02ba80c7cd4784d8a312825870b6180afcff59d55e0;
source bundle SHA256 a1ab7bad2340b84cc556eecb08d5bf99ee658e4f86523f6720cac880de584b3f.
Cloud source certificate confirms both original HEADs, object IDs and selected
path hashes; no origin or missing-blob fetch is configured. Stock11 cases retain
four positives, four intended post/unwind negatives, two exact dead-code rejects
and the historical INCONCLUSIVE generic-forget positive. B acceptance is the
operational stock chain with its original limits, not a full generic forget proof.

Archive `evidence.tar.gz` SHA256
`dac3492bb16ff5501403449ddad5a404c989e928259360dac5f20f9c305d4ad6`;
separate text index SHA256
`6a62d9809e31d62b43235a3a12aaa063ab435287407f3ba1603174dd0ceb4d28`.
Archive and all separate text chunks downloaded and verified on VPS, including
lossless concatenation hashes. Prefix uses the full BuildID as above.
Usage444/3600, remaining3156. C remains pending, so full migration not accepted.

B independent artifact review confirms provider-only guard changes, all17
RSSpecs byte-equal pinned VF source, full11-case normal/readonly exports,
decodes and refinement exits0. False controls stop at exact expected obligations,
not setup. The two dead-code controls retain strict INCONCLUSIVE/raw intended
rejection separately. Exported fixture body comes from pinned repository source;
external std metadata comes from nightly sysroot, whose mem/mod.rs and ptr/mod.rs
files differ from repository files. This is the preserved historical trust scope,
not a rebuilt repository std or actual SmallSort proof. Peak measured B stage
RSS543236KiB (toolchain install); matrix5.04s/96020KiB, compiler39.24s, packages22.91s.
C active `d9e4538a-c6c0-4881-b422-de6ceae72d19`, sameinfra30fc3b42, proof1378f0ff,
config15db37f3bb8b331e06f747c51078d0430e17ecba827ef28c9aeec8269e83fc99,
timeout1500s. No semantic/fixture change; fullmigration acceptance remains pendingC.

## C confirmed — cold historical constructor source profile

Build `d9e4538a-c6c0-4881-b422-de6ceae72d19` SUCCESS,328 conservative seconds.
Infrastructure `30fc3b42a2fb980b49174d459ec5cfbea778379b`, original proof
`1378f0ffc8342233349fae3df5a938c4a021c8d7`, O3/run37700450091 comparison.
Config SHA256 `15db37f3bb8b331e06f747c51078d0430e17ecba827ef28c9aeec8269e83fc99`;
source bundle `5a36ec008dbc0db57bcf69efe616057bc93c54c82cb8d97a2e9500344bf78b1c`.
Cloud restore verified original commit/HEADs, selected object closure and path hashes.
Pinned source build applies exactly S6candidate20f7d07a thenCFG593d0940, builds
console cold and preserves all selected obligations:16source/proof,9MIR admission,
10native,4false/frame. Classifier CONSTRUCTOR_COMPONENT_ACCEPTED, exit0.
Independent full-artifact review confirmed expected refusals, source/profile identity
and unchanged kernel/parser. Actualcallee NOT_RUN; localcopy/def-path applicability
is not DefId equality, generic/ZST closure or full S6/O26/helper/sort4/merge proof.

Archive SHA256 `d2ef48f11744fd622520524e2ab859c479a400e17385ddcf982546b0f885d18c`;
text index `72007409313e1d94691b7e465ee214451ceb6d52391aa5d0bd576b30f6136f15`.
Complete archive plus all482 separate text files downloaded and SHA256/lossless
reconstruction verified on VPS. Largest text object149690bytes;8MiB cap preserved.
New source-built console SHA256
`f0d3c92651d98d91ceed57d58d93087bee0106a094b7efc1e956820c46132642`.
C compile53.49s/398136KiB/185%CPU; largest measured stage RSS546084KiB
(toolchain install);2CPUs, MemTotal8147688KiB. Historical permitted omission of
810 duplicate mutation-tool entries is explicitly inventoried; wrappers/MIR/logs
and original diagnostics remain. No binary reproducibility claim vs GitHub.

Cumulative772/3600,2828remaining, no active build. All A/B/C migration gates accepted
in the final report's scope. Further actual proof development not part of this phase.
Permanent Cloud workflow and second-direction handoff documented without resuming
that agent, altering its worktree, or changing automatic Actions triggers.
