# R23 fractional MIR layout overlay (candidate)

## Defect and applicability

The R23 fractional owner path reaches the complete source, decoded-unit, and
per-body hash checks, then refuses at the shared cleanup predecessor check.
The matching NORMAL MIR reports ten unwind-call predecessors to `bb28`; the
translator still expects the old nine-body `bb24`. The ten-edge count remains
ten. The same body has shifted typed locals and block positions in the owner
forget call, the pointer `drop_in_place` call, and the final `assume_init`
call.

This is a new overlay on top of
`verifast-r23-fractional-forget-26.10.patch`, and applies only when the existing
fractional source/unit/body row has passed its complete hash checks and the
ten-edge inventory. The overlay stores that admitted variant for downstream
checks; it does not create an alternate admission path. Legacy and default
nine-body coordinates remain as before. No source/runtime statements, ghost
annotations, profile row pins, or positive/negative row hashes change.

## Exact NORMAL layout witnesses

The exact row has 46 local declarations and 29 blocks (`bb0` through `bb28`).
The preserved ownership and unwind graph is:

- Ten call unwind edges target shared cleanup `bb28`.
- `bb18` prepares the forget call with the five statements `StorageDead(_34)`,
  `StorageLive(_35)`, `StorageLive(_36)`, `_45 = false`, and `_36 = move _28`.
  It calls `forget(move _36) -> _35`, with normal `bb19` and unwind `bb28`.
- Cleanup `bb28` switches on copied bool `_45` to `bb26`/`bb27`; `bb26` resumes
  unwind, while `bb27` drops `_28` to `bb26` and terminates if that drop unwinds.
- The pointer `drop_in_place` call is in `bb15`: `move _32 -> _31`, normal
  `bb16`, unwind `bb28`.
- The final `MaybeUninit::assume_init` call is in `bb24`: `move _41 -> _0`,
  normal `bb25`, unwind `bb28`.

## Invariants

- The R23 fractional variant must match the variant admitted by the full
  source, unit, and body hashes before the fractional layout flag is set.
- The 10 predecessor count, exact forget type/contract, drop-flag false write,
  guard move, normal successor, shared cleanup successor, and cleanup resume/
  drop/terminate path remain checked.
- The pointer drop retains its typed call, exact moved receiver and successors.
  The final `assume_init` retains its typed pointer-wrapper argument, result
  destination, and cleanup successor.
- The additional 46-local/29-block coordinates are accepted only under the
  already admitted fractional row. Existing nonfractional branches retain
  their prior coordinates and behavior.
- All existing source and row hashes stay unchanged. The patch adds no
  translation exemption, ownership bridge, or generic shape acceptance.

## Static controls and patch identity

The static synthetic tests check the exact new coordinate set, reject altered
coordinate tuples and legacy coordinates as fractional, require the existing
fractional admission flag, and inspect that the overlay leaves the default
nine-body branch and row hashes alone. They do not invoke an exporter, decoder,
compiler, verifier, source preparation, or Cloud.

Overlay base translator SHA-256:
`2d6f1950bd95b655560c767c54af8facfecde724f29a72c4218b65b6c6438c19`

Overlay translator SHA-256:
`cadaa80ab55e6fb3f53ccfcae1ab05dc953a2cb69a17616654d49dad6350478f`

Overlay patch SHA-256:
`68810eb486d494cb49e158a13eab55b19464fad1b724bd9025cf5960b6c5bc17`
