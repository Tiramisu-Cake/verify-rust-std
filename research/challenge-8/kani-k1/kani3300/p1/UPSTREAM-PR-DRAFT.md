Refs #3300

With `-Z uninit-checks`, a pointer to `MaybeUninit<T>` must permit reads of storage while preserving the
initialization state of its payload. This change carries byte initialization state through raw pointer operations,
exact transmute conversions and ordinary MIR argument/return transfers, so a later typed read still checks the bytes
required by T. Partial writes, resets and copies preserve the distinction between data, padding and unwritten bytes.

The implementation recognizes the standard wrapper by language item. It handles `MaybeUninit<T>` behind raw pointers,
`MaybeUninit<T>` to T or `ManuallyDrop<T>`, T to `MaybeUninit<T>` and matching flat array conversions, arrays/slices
of slots, static repeats, and ordinary calls/normal returns with a MIR body. Array aggregate and local-repeat transfer
is restricted to the explicitly checked nonoverlapping operand shapes. Payload types must have supported layouts.

The argument buffer uses flat bool/usize fields inside the existing marked memory-initialization state. Argument
selection remains nondeterministic; index zero is reserved for a deterministic return transfer. Return sources are
captured as live object IDs and offsets and copied without querying a dead stack pointer. The existing DFCC exception
applies to verifier-private state; the user outside-modifies write remains checked by the included frame control.

Unsupported boundaries remain: nested/arbitrary unions, compound storage containing slots, `typed_swap` of storage,
`select_unpredictable`, and function-pointer/no-MIR transfers of shadow-carrying values. This PR does not close #3300.

PFC compatibility is limited. On the tested v2, the isolated MaybeUninit roundtrip PFC roots with `modifies` and
uninit checks report OOM. The clean positive comparison did not finish within its time limit; the U1 comparison is
INCONSISTENT/UNVALIDATED. Neither an already-existing upstream OOM nor a regression from a passing clean baseline has
been established. MU-free clean/U1 successes do not establish v2 PFC compatibility. The OOM repros are retained in
the research handoff and excluded from this upstream test selection. The specific mechanism and actual peak memory
remain unknown; this is a Kani-reported OOM, not independent measurement of memory exhaustion.

Manual/native validation performed before packaging:

| Build ID | Tested identities and relevant result |
|---|---|
| `d5d15c41-1c07-4f9f-a6ff-16c25fae00e1` | f046 baseline, patch SHA256 `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467`, applied tree `b9c36ac5ed550e39d26e1d1d77000052e62a9bb4`: 20/20 native selectors PASS, including the initialized fixture (eight successful harnesses). Older U1 production. |
| `45287677-98cb-4dc4-b98d-7ccae4782f5f` | Final production `81dd85bfce67226e283fdd9a156932e32ece080b`, patch SHA256 `f3f8a82c2c22798361bf51bf6186aa60cadb1de68d0aa15b15ad62d601138c1c`, tree `c5b24f0b0da999d1deb9758215790382fe5e3be4`: 17 PASS / 3 ERROR. Thirteen selected fixtures passed here. Errors were the PFC pair and frame golden naming mismatch; no full-run PASS is claimed. |
| `9f964706-4b89-4340-a1ee-022aa23ecbe9` | Test commit `0ab9cc703aed799f6f73d826b60281a4632ab585`, unchanged final production, patch SHA256 `d9417e68ec3ee9c8c27bb8e7ac829e2af712c4d124ac59078416ab34feebd85c`, tree `4de67d7ead14bdc4060d2b08060e7ee7651625bb`: 7 PASS / 2 ERROR; corrected user-frame golden and four selected regressions PASS, both isolated PFC-on roots report OOM. |

These used Kani 0.68.0 / CBMC 6.11.0 on standard4. Negative native PASS means the intended failure matched its golden;
positive fixtures additionally required successful verification. Retained bounded reports do not contain complete
literal failed-property lists for every passed selector; these finite outcomes do not establish a general theorem.

The proposed test selection contains 15 fixtures: initialized, wrap-positive, review-positive, wrap-padding,
wrap-source-read, plain argument-buffer negative, clause-PFC negative, user-frame negative, partial-copy, alias-reset,
and the five adversarial argument/return, overwrite, overlap, local-repeat and ZST-reset controls.
Six goldens were converted to stable `Failed Checks:` matches for checks emitted inside core, preserving failure/count
requirements. All new Rust files were formatted with Kani's `rustfmt.toml` and their declared editions.

The packaged commit `c39cc1121cdb287d9d77c38b87cff6c84c2c8046` is based on main
`bf9c58e662fd65c64381ef2ac97a6397ffc0693a`. Its production is byte-identical to final v2.
The packaged test context and adapted goldens have not been executed, and compatibility with the newer main is untested.
A final targeted native gate on f046 is prepared separately; it has not been authorized or run.

This contribution was prepared with AI assistance from OpenAI Codex and GPT-6 Luna.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.
