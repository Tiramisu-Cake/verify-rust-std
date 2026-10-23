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
