# R12 S2 no-F diagnostic classification rationale

The S2 `N-no-F` observation is a terminal synthetic translator refusal, not a
proof result. Its `no_F` mutation removes `F` from both compiler and HIR
generic arrays while retaining the `typeParams` and uses. The source guard now
checks the type-parameter identity table and can reject this representation
before the older generic-array mismatch. The saved observation reports one
diagnostic at `verified/lib.rs(35,8-18)`:
`A1 type parameter identity table mismatch`. The previous classifier recognized
only `A1 HIR/compiler method generic mismatch`, so it mislabeled this known
earlier guard as inconclusive. The bounded fix accepts either exact diagnostic
for `no_F`, but only with a terminal translator stage, nonzero exit, exactly
one diagnostic, and the exact `verified/lib.rs` diagnostic form. It does not
classify arbitrary errors, embedded text, or multiple diagnostics. The result
continues to carry no compiler, refinement, summary, or proof credit.

## Bounded Evidence references

Build `c08f6903-82db-43e4-91cb-fe7cfadca731`; audit file
`cc20cf422e3f3828330adb99a0a55222711961bbb855f3b12dfc360c537a3e96`, SHA-256
`73088ecc711c957d764fcb85254fdb1e9358dfb93281b5ef7b234b652ff6ac1d`, archive
SHA-256 `33763699e2b6dc344f21c63f2c69811be1bd81a0ede61443c6e61cb80d44714b`,
index SHA-256 `41aecd856fc2d402ad997af186add1dfa2bf99c46f0768a6ef770f21e99eca7d`.

Targeted request IDs:

- Info refresh: `3fe06b1acddeb1d454c553331f37de43d7bce43edd8f2420a567f8789e0fffa8`
- N-no-F details: `ff3346f6147428eacae3799154ab8a9d46f83d0240f67ceb1ab6d8797ccf4c77`
- N-no-F message: `f79303ab3e3f9f2e8a1649f2f175869ae62c742dd7b6b6779cfb94fbaeeb4f02`
- Classifier node: `bb09d400233a89cd7bdb05fb625740c1c76c0ac6aeb78a9d1941cfedd9927440`
- Transport node: `b5d1e8bfbab63f326571796bce1edf12601370f3bac0de9c25f0f79297f7d1f4`
- Mutation node: `453dcf891ed7cfc28472c2882dcbb551317d99501be94508a7760c51218dc565`

P-dispatch was inspected independently and remains outside this change:
pointer `2cf6ced646e27ee2d4c4ccd63b655b4dc33c17debe128078b7ccbab030da6e9f`,
raw node `31300c1caa417574eb815d8c4a7edf80a89dd1e3840632ced3c89807a9ddd7f0`,
structure `2730c8f70f5a645e5ba459604ecea20d2d216c9b13fea6d5245e45dc9df9e2fb`,
classifier `410748383ca4aeb9108044a19ecd60043cfc79a2463e864d6456b52af6aa528b`,
raw stage `ae56c384000cc9d65ccef3504d77c801c4e041d82140cae807fc3dfcae7366c0`,
verification stage `d3bc1010d1250de234b45257c18be56466eff0319ea1d35a77af796667b14e3c`,
proof AST `c1d442fdd41abaeebb9ee6283bab0013d0ed13e5515a0fbc899f8a86ebc0ea19`,
paired support `9131d83b478f2d0cff4c47092c51ab6add1f9e972a8850f099807e67fbe7e275`.
The bounded trace log has file ID
`be6c609e5d54b7649a2d9fac8e7cdb3f9bdc7ab3994a21d45bd707826a82b874`, SHA-256
`4a2f40e3e0288165aed212feb9547aa9603385c5c30f59bb6a751bcb25546c10`; its
catalogue, locate, and bounded-line requests were respectively
`f1fafdc13376428a044513842a36b9ebbb3a6930b204bf7ac868cd65e3569788`,
`8b1f5d24f334c634b8dbb21f429a0ada8d94cc53e1f8b8c32215490cffa80c4b`, and
`48751eb0eae7a43a90952d6984b87252dfb23ec3b624dccc71f0d4e786d93d81`.

The only failed targeted read was a single request for
`/observation_details/P-dispatch/raw/artifacts`; command used
`/usr/local/bin/smallsort-brief c08f6903-82db-43e4-91cb-fe7cfadca731 --file cc20cf422e3f3828330adb99a0a55222711961bbb855f3b12dfc360c537a3e96 --refresh --expect-sha256 73088ecc711c957d764fcb85254fdb1e9358dfb93281b5ef7b234b652ff6ac1d --pointer /observation_details/P-dispatch/raw/artifacts`;
exit 1, stdout empty, stderr exactly
`smallsort-brief: Reader HTTP request failed (HTTP 429)`. It was not retried.
The CLI help exposed no `--version` flag; the repository's applicable reader
guide identifies v0.11. Targeted responses used reader schema v2 and index
schema v8. The audit was limited to the above pointers and a bounded trace
excerpt; no raw archive/log download was performed. These source reports do not
establish parser-input binding or independent proof acceptance.
