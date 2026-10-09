# O26 nested Drop proof-order TEST

## Problem and exact obligation

The canonical nine-body `select_unpredictable` translation verifies the outer
body (source lines 135–225) before its local generic
`<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop` body (lines
165–170). An outer ownership failure therefore prevents observation of the
actual nested body proof. VeriFast `-focus` cannot isolate it: the nested lines
lie in the outer function's inclusive source span, and focus leaves the global
dead-code check unsatisfied. This TEST changes only verification order.

The nested obligation remains generic in `T`: its mutable borrowed `self`,
`full_borrow_content`, nominal `own`, `inner: *mut T` field, padding and
lifetime resources, normal and unwind outcomes, and leak/dead-code checks must
all discharge against the unchanged source and contracts. Its actual MIR has
five locals and four blocks; block 2 calls the qualified generic
`drop_in_place<T>` with `Move(_4)`, normal target 3 and `Continue` unwind.
The same-unit generic pointer-drop callee must prove before this call can use
its summary. This is independent of the pointer-specialized outer contract.
Any optional inner-cell and thread resources in the generated generic contract
remain unchanged; this TEST creates or discards none of them.

## TEST rule and trust boundary

After the existing 20-patch profile and two reviewed refresh patches, make a
separate copy of the production translator. The TEST patch may run only for
the exact canonical verified source SHA-256
`1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6`,
decoded nine-body unit SHA-256
`10cf6e4d2a462082d456135078a77ea6670358f1ad15e0d81901104e8a102b43`,
and nested body-8 snapshot SHA-256
`e0508d6cfb436bc1bcd04737ad74e37b357d17e9ec3c2a226ee961f7036eae9a`.
The complete nine DefPaths, source locations, and AST declaration inventory
must match. All ADT/trait/predicate/ghost/signature declarations stay ahead of
all bodies. Seven prefix bodies keep their order. Move only the single nested
body declaration from after the outer body to immediately before it; preserve
every declaration's serialized bytes, location and module path. Refuse any
duplicate, missing, unexpected or reordered declaration. This is an explicit
trusted frontend TEST change, not a production profile or kernel theorem.
The inventory prints each body’s qualified name directly from its decoded MIR,
alongside the separate AST module/function key and full serialized AST hash.

The production source, std source, runtime, contracts, normal and unwind posts,
compiler/exporter/refiner/parser, kernel, ownership model, and target CFG do
not change. No Freeze/Copy premise, fabricated owner chunk, focus flag,
dead-code exemption or source-body stub is admitted.

## Cloud controls and verdict

Before TEST proof, compare source/original SHA, full NORMAL and readonly MIR,
refinement, complete nine-body snapshots and the production translator SHA
`0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a`.
Record the exact applied TEST diff and translator hash. A negative wrong source,
unit, body, declaration count or order must fail at its intended certificate
gate; setup/compiler failures are inconclusive. An AST duplicate/missing-body
negative remains pending unless an isolated Cloud mutation can demonstrate
the intended gate without altering the production source.

Run the complete unfocused verifier. The diagnostic positive requires seven
prefix proof headers in their original order, then the actual nested Drop
header, then the outer header. Inspect the full nested normal/unwind/return,
resource, leak and dead-code record. A nested-success prefix followed by an
outer failure is diagnostic only. Acceptance of any whole function requires
full verifier exit 0, complete controls and separate profile review. The
historical 20 and refreshed 22 profiles are never silently replaced.
