# Caller bridge checkpoint — STOP

Resumed789b0daffcdd3d1b49c83e979aec486542334b46 in own worktree
/root/verify-rust-std-select-night, branch research/night-select-sort4-cloud-2026-10-09,
git-dir /root/verify-rust-std/.git/worktrees/verify-rust-std-select-night.
Policy d389ff641194364e5eeda4ea4e66bedac4915a79. Phase started19:43:08UTC;
main ended20:43:08UTC; after main only already-started evidence/account/checkpoint.
No new Cloud job after main; no local compiler, extraction or proof execution.

Entry boundary before actual SmallSort254 sort4_stable reached in second/third
builds, supported by exact full-source certificate, normal/readonly typed MIR,
stock proof AST and execution locations. Original scratch check/abort branch
retained byte-identical; duplicated success filter uses same condition and no
writes intervene. First missing abort binding is avoided on continuing path.
The actual sort4 invocation itself is absent from this bounded fragment; whole
caller and actual c1 invocation integration are NOT_RUN. See [premise map](PREMISE-ORIGIN.md)
and [AST/CFG audit](SECOND-AST-REVIEW.md). Numeric duplicate filter compensates for
opaque generic inline const in MIR; no claim that constant#0/#1 are linked.

**No supplied c1 premise is eliminated as a completed, fully admitted native
caller theorem.** Third source-frame VC reaches source4/foreach CURRENT owners,
F/current F.own, thread/currentThread and rejoins source frame. Native return/leak
checks are observed, but raw VF1 rejects original abort statement and generated len<8 fallback return
as dead code. Checker stays enabled, no exemptions/assumptions added. This is
first strict complete-entry blocker. A sound exact path projection would require
certified source/MIR/AST transformation and independent controls; existing
specialized O26 select/unwind projections provide no generic entitlement.

Bridge additionally reaches native scratch MU array, opens four MU slots and
constructs optional dst array before incorrect predicate-form pointer-limit
assertion at verified126. It is corrected to bool==true in734af5d8449347148f04179dadbd4cdd64957699,
**NOT_RUN**. Exact identity call and type_interp assertions NOT_REACHED. T/F
interpretation is not supplied by native heap contract; existing real-function
produce_type_interp was reviewed but unused. Native selected path permits ZST
len8..15, so size>0 remains supplied/conditional. Generic MU wrapper/opaque owner
restoration is separately OPEN: no new(inner(old))==old law was assumed.

Narrow tool candidate prepared: [patch](../../caller-entry/verifast-slice-as-mut-ptr.patch),
[semantic card](SLICE-PROJECTION-SEMANTIC-CARD.md). Only exact slice as_mut_ptr name
joins existing typed metadata-stripping cast arm, preserving provenance and
creating no heap/owner/lifetime/type_interp chunks. Base f76012fb518703b1d98e243ac4f487f16877cfcb,
frozen O26 translator0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a;
patch SHA256f200a5812149bb2278ded1d1ccb27a104b3dec3c03c5e40c79e30409d0d06916.
Independent GPT-6 Sol review completed. Third native T/MU positives VF0+full
post/leak; wrong equality and unrelated raw-dst rights fail exactly as intended.
Range/duplicate-source controls also reach intended failures. Experimental pass
is **not profile/upstream/consumer acceptance**. No kernel/spec/ownership change.
Candidate is ready for VeriFast review, not integrated there by this agent.

Fresh builds (infra=proof exact SHA; all lane o26-sort4-caller-entry):

| Build | SHA | create→finish seconds | Result |
|---|---|---:|---|
| e97528f0-80a2-4e23-9b43-80601e06f3bb | 15056f9e820633fbe047f6a064eb2374076ce9ae |332| no slice as_mut_ptr binding, before boundary |
| c8ae2005-7b50-41fa-a926-0319bf9787e3 | f854de7235169cd7fc50ed43b2c96e7e6160ed50 |303| boundary reached; opaque const bound/name failures |
| 4a7eedc5-655f-44a0-b8df-9ba9b22f7dcd | 5e821db1310b006309e8cc7ad9c21142ac6d9b78 |299| projection controls PASS; source/frame strict dead-code VF1; bridge bool syntax VF1 |

Cloud SUCCESS denotes diagnostic packaging, never native proof PASS. Archives SHA256: firstfe8a5bcba9ed4640d9eada938ee4849e498d7bebf2e8311e43ffe35049bc489a,
second214d6c4ab212f1f9a4168e05aeac2df1dd16c03a86b0408627123803a7978679,
thirdbb2bca7d3a5577bb508c0437be579f017f6d91d4178b5978a73ab6bc0c139956.
[Exact final result](FINAL-TEST-RESULT.json), [raw-case summary](THIRD-RESULT.json),
[dead-code replay](THIRD-DEAD-CODE-REPLAY.json). Fresh
normal/readonly full-prefix MIR export/decode and ghost-pair refinement pass all
cases. Saved first hash audit and third dead-code classifier replay produce no
new proof. Trace-needle fix9be26c410b161ee8a861554b7eb2bf82d36f98ce and bool/classifier
fix734af5d8 have no fresh proof execution. Prior select e2b24967 and conditional
c1 normal/unwind results remain pinned/preserved without repetition; they do not
transfer to this entry unit/candidate. No c2 or new actual comparator execution.

Scope incident: worker temporarily touched two foreign infra files; immediately
restored exact original tracked bytes/removed own new file, final foreign status
clean. No foreign index/ref/build/ledger mutation. Details in semantic card.

Final account:934/3600 create→finish seconds;2666 unused closed/no carry. Own
all3 terminal, accounted, integrity-verified archives/index; active/unresolved/
reservations0, ready request withdrawn; existing coordinator v2/max2 unchanged.
Final source/diff checks and local static Python parsing PASS. No upstream push,
issue, PR or consumer pin was authorized or performed. Own checkpoint pushed.
Next task needs fresh authorization: close strict path-admission blocker with
sound exact correspondence, then same c1 bridge; retain full resource checks.
