# Isolated 26.10 strict-cut console: hosted diagnostic plan

The proposed [lifetime patch](verifast-strict-lft-cut-26.10.patch), SHA-256
`d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8`,
has only static review. This run tests the falsifiable scope/resource claim
from [BEFORE.md](BEFORE.md) on the current production patch stack; it does
not admit the cut into the accepted profile or claim actual sort4 proof.

`run-cut-isolated-console.sh` takes the exact already patched production VF
checkout, its full `git diff` evidence, the pinned release support home,
compiler sysroot, fresh evidence directory and deadline. It copies the
checkout into a distinct hosted temporary tree, checks that the production
tree changes only std spec/parser/translator and that the copied diff is
byte-identical, then applies the one pinned CUT patch. The CUT tree must
change exactly std spec/parser/translator/verifast kernel. It removes only
the copied console binary and builds a separate console; it does not write
the production source or cache. The new console must have a different hash.
Schema SHA-256 is `f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469`;
vfdeps archive SHA-256 is
`8d022c93d51a1d13ec1e782d767c60462405f6865d5ee416f82d6234e93ee580`;
the decoder generator is pinned to `capnpc-ocaml-decoder` revision
`2d6606d9b59cd0c88a66729f3f076c10c0c8e0b2`. The real exporter,
refinement checker and every effective `.rsspec` must match production;
exporter/refiner must also match the pinned stock release. Record source,
diff, binary, generated-decoder, schema and spec hashes plus build logs.
Static `git apply --check` of the CUT patch passed after the current
production 13th `verifast-actual-owner-fingerprint-probe-26.10.patch` on a
disposable f760+12-patch checkout; a future 14th component is not implicitly
covered and must pass the hosted overlay check on its exact source.

The first CUT matrix uses the reviewed exact isolated fixture template
SHA-256 `7cb5c8a8a2541da30af188c8731ee13276c59b206e5ed58a78e909852719359e`:
basic/early-return/direct-unwind/outer-`F` positives, ordinary unmarked
control and available source/resource negatives. It captures normal and
readonly complete MIR, original/verified sources, refinement, full proof
and first errors. A separate no-opt-in case must reject the marker before
proof. Every classification remains a candidate pending full log/MIR review.
The runner then runs the full fresh S6 matrix and the nine callback cases
directly through `probe.py --case all --unwind-matrix --enable-hrtb` on this
CUT console, with CUT opt-in absent. This avoids the tuple runner's three-file
cumulative-profile allowlist; callback source and FnMut spec pins remain in
`probe.py`. The callback summary must match its nine previously observed
stage classifications exactly. No verification or build runs locally.

The test is inconclusive if overlay application/build, source/schema/spec
identity, export/decode/refinement, body inventory, or an unrelated callee
fails. A green initial CUT matrix and regressions are still insufficient for
acceptance: unresolved-inference, live bounded heap, outer-variable escape,
source-file mutant and direct MIR ingress/reentry negatives are mandatory.
The complete actual sort4 body, operands, cleanup and resource protocol need
their own certificate and proof after this component is accepted.
