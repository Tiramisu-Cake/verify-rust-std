# CC2 — worker14
Source: 9631aaf89e869624fbfc8cd22d327ce194eb779d.
Tree: 2d75492ae172087535c7a9f2723fd7a42b0d0666.
Base: accepted CC1 b2e1a392ad27bd21758473bc208ff66c2d7d0405.
Clone: /root/kani-fix-3300-cc2; branch fix/kani-3300-cc2; reference unchanged.
SETTER-MAP prepared before patch; exact dynamic/model binding remains UNKNOWN.
Added tracked ordinary argument-slot entry setters with existing Sized data masks.
Pointer/ref setters address representation storage only; pointees stay untouched.
Union/MU transfer and nested unsupported boundaries are retained.
Pending entry setters survive statement-free bb0.
Existing source checks, normal-edge return and copy setters remain in place.
Added9 isolated roots: scalar/ref/wrapper, ordinary/SimpleCheck capture-free,
paired initialized payloads, ref/raw holes, caller-read preservation and padding.
Original captured/mode inputs and all8 strong oracle inputs/expectations unchanged.
Python static audit13/13 PASS; existing Python oracle checker21/21 PASS.
Scratchpad rustfmt and git diff --check PASS.
Rust typecheck, compiler/verifier execution and CI: NOT_RUN.
Independent semantic review: PENDING_COORDINATOR; author static review recorded.
Exact new failure sets, selected setters/masks/Move/reachability/order: UNKNOWN.
CI-REQUEST:19 bounded invocations; coordinator owns review/GO/transport/binaries/caps.
No cargo/rustc/Kani/CBMC, push, CI or raw evidence access by worker; Cloud $0.
CC3 nonzero capture layout is not implemented or issued.
Original ordinary/SimpleCheck qualification is not established; Part1 remains NO-GO.
READY 9631aaf89e869624fbfc8cd22d327ce194eb779d
