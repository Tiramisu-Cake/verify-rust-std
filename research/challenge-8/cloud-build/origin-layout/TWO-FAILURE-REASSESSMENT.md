# Two compile-only failures: reassessment before Build 3

Observed 2026-10-10 13:56 UTC; mandatory threshold reached. New Build1
b5dacec7 (293 seconds) refused the effective translator source pin before any
candidate compiler. Component e163 is a delta on 8cb; Cloud uses f760 plus the
six frozen baseline patches and tracked-MD/span/unit/guard. The static pin
update had conflated these trees. Full ten-patch Git/text replay now checks
the baseline checkpoint and all twelve final source pins before dispatch,
records EFFECTIVE-SOURCE.json and corrects all three analogous mismatches.
Independent review confirms differences are the frozen baseline contribution.

Build2 101982de (464 seconds), exact8cbb5c2f, archive177d5d27: exporter,
schema-derived decoder and translator compile exit0. Console exit1 starts
with the actual pinned cxx_frontend/stubs/dune rule failing:
`capnp compile: -I CAPNP_INCLUDE: no such directory`. No OCaml Error appears;
full console compilation is still unconfirmed. The direct Dune preflight
mirrored the Rust CAPNP_INC_DIR and Z3_DLL_DIR variables, but its static review
had not inspected all full-console dependency rules. Copying the baseline's
Dune objects does not guarantee that generation remains unchanged after a
new root/environment/schema. No object cache identity or compile PASS is
inferred from that copy.

Checking method changed before Build3: inspect every `%{env:...}` reference in
the pinned src/**/dune tree. The complete set is CAPNP_INC_DIR (Rust),
CAPNP_INCLUDE (C++ stub generation), Z3_DLL_DIR (linking), and optional
OCAMLOPT_CCLIB_FLAGS. Export both Capnp include variables to the same real
VFdeps-pinned include directory, validate its capnp subtree and retain an
environment receipt. Z3 uses actual findlib resolution; optional link flags
remain inherited as with WITHOUT_LABLGTK=yes. No schema generator, dependency,
module or semantic code is stubbed or disabled. Reuse remains limited to the
existing dependency-tracked source copy; fresh compilation is required.

Keep four explicit serial compiler targets and full console linkage. Preserve
actual prior stage codes on failure (old short failure manifest lost them).
No further bridge/Drop/domain implementation is needed to fix this runner
environment issue, so splitting the semantic candidate would not isolate its
cause. Existing development remains intact. New target proof, len1 interface,
caller and glue are NOT_RUN. Next authorized Build is compile-only on the same
e163 component and identical effective source hashes, after static/script
review. Only a confirmed full compile permits activation of bridge-minimal.
