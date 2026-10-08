# O23 first-call temporary inventory (diagnostic certificate draft)

The selected `callback_positive<T,F>` fixture has unchanged verified source
SHA-256 `66bf5a6edc0188f560e72ac5a6a5636f2dcda47c65aa295ac21008fc7702e2d8`
and original source SHA-256
`9b41aef507c8c61ec786bfacc8e12ede656286213e393a0d07436a8879dc569e`.
O23 preserved complete NORMAL target-body SHA-256
`10356bf128753db09e17b968e859957121cb3f5a2684c3b608abd4152f150f76`
and readonly target-body SHA-256
`9fdee7643ff66e8f3a12fc37b489100b7280ded0489a20ab1da11c67f24032c4`.
These hashes are admission gates in `capture-relocate.py`; they are not
substitutes for reviewing the following MIR path obligations.

| Role | NORMAL local/type | Readonly local/type |
| --- | --- | --- |
| FnMut receiver | `_27`: `&'<erased> mut F` | `_7`: same |
| argument pair | `_28`: `(&'<erased> T, &'<erased> T)` | `_8`: same |
| first input-ref construction | `_29`, `_30`: `&'<erased> T` | `_9`, `_10`: same |
| second input-ref construction | `_31`, `_32`: `&'<erased> T` | `_11`, `_12`: same |

Each selected local has one `StorageLive` before the sole line-103
`core::ops::FnMut::call_mut`, and one `StorageDead` in its normal successor
(NORMAL block 21; readonly block 1), before the line-106 lifetime marker.
The normal call moves receiver and pair locals, has a plain destination
(`_26`/`_6`) and a direct `unwindAction = continue`. The direct unwind
does **not** execute those normal-successor `StorageDead`s; it leaves via
the existing return/unwind continuation. The candidate AST scope must
free its relocated declarations on that path without inventing Rust Drop.

The TEST overlay's frontend gate checks NORMAL local names/types and exact
source/cut coordinates. Its hosted gate checks both complete MIR bodies,
so any changed call, normal successor, cleanup, or use changes a hash and
stops before relocation. The overlay checks exactly six outer declarations
are removed and exactly one insertion into the strict block occurs. Its
`addresstaken=false` trace is only the declaration's initial flag.

Before acceptance, add targeted negative MIR mutations for a missing or
duplicated `StorageLive`/`StorageDead`, post-cut use, address escape,
changed local type, Drop/cleanup path and non-Continue unwind. For each,
require successful exporter encode/decode mutation and rejection at the
intended exact MIR gate before proof; source mutants need separate exact
source admission failures. No such negative matrix has run yet. The
actual `sort4_stable` first call has a different temporary set, including
raw pointers, and requires a separate certificate.
