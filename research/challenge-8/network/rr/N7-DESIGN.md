# N7 online image and lane design

Defect/applicability: the N6 candidate cannot dispatch an offline image with
unassigned deb/vendor/context inputs. The owner explicitly replaces those gates
with a network-enabled Cloud-only image build and supplies the existing registry.
The own Network client currently knows only N13 stages and always executes
Ubuntu. Add exact N7 phase admission and stage/image selection only for
network-rr-g1. Preserve all existing N13 stage envelopes and configurations.

Invariants: stock RR332d945f/treeb33bcccb, compiler nightly2026-08-28 archive
hashes, source cd371e0, generic signatures, runtime bytes, ghost-strip equality,
ownership/normal/unwind/cleanup requirements, p0-before-target and proof credit0.
No coordinator/IAM/shared transport changes; all source is pinned-objects.
Cold1740/1800 E2_HIGHCPU_8, warm1200/1260 E2_STANDARD_2, disk100, report240.
Warm uses an exact registry digest after cold receipt and pins-only delta review.
Only N7 permits cold attempt plus one explicitly recorded setup repair and two
warm attempts, with no unchanged config retry. New code validates types/stage,
image repository/digest, profile/source pins and ledger identities fail-closed.

Freeze: image digest, binary SHA256s, apt list, locked RR/core Cargo inputs.
The owner retires offline deb/vendor/config gates. Warm uses --locked online
Cargo access with exact source Cargo.lock; no compiler/tool installation on VPS.
Image construction and generation remain Cloud-only. Receipt collection and
collector SUCCESS never establish safety or sorting/proof credit.

Controls before first submit: synthetic success/error/timeout/partial/missing/
null/wrong-type/NOT_RUN and source/stage/target mismatches; preserve original
exit/exception/snapshot. Check existing N13 configuration and test suite for
unchanged admission/envelopes, Python/shell syntax and committed exact closure.
One independent Luna HIGH review covers connected cold/client/warm candidate;
pin-only freeze delta returns to that reviewer. Missing output is UNKNOWN/NOT_RUN,
never a target refusal. Terminal accounting/checkpoint commit+push precedes next
Build or repair.

Static executor compatibility correction before submit: the resolved Google
Docker builder source uses Ubuntu20.04 (Python3.8/Git2.25), while unchanged exact
source transport requires Git's --object-format support. Use the already pinned
Ubuntu executor for cold and install docker.io client in the Cloud bootstrap;
this preserves the shared transport bytes. Cold-only bootstrap cap180s, within
the unchanged1500s work/240s reporting envelope; image Dockerfile pins unchanged.
No local installation and no extra Cloud Build is introduced.

First cold Build efd32c5f terminal EXPIRED before any step status/timing, billed
297s including queue, execution0. Brief404; exact waiting cause UNKNOWN. Before
semantic repair record: reduce cold resource request to allowed E2_STANDARD_2
and jobs2, retaining1740 timeout/60 queue/240 report and immutable source/tool
pins. This is the single setup-error repair, not a frontend or source change.
Source preservation/control invariants unchanged; synthetic config tests must
distinguish allowed2/8 CPU requests, refuse unsupported/cross-stage shapes, and
retain old N13 config. No raw audit or proof inference from missing Brief.
