# Mode scope: source map; fixtures BINDING_PENDING / NOT_RUN

Owner decision from the issued task: Replace (`stub_verified`) and RecursiveCheck with shadow
transfers are not claimed as supported Part1 modes. This does not exclude ordinary recursion,
ordinary stubs, SimpleCheck or Assert. It does not prove every such input fails or is unsound.

Proposed public limitation (not applied after the prerequisite STOP):

> With `-Z uninit-checks`, Part1 support does not currently cover shadow transfers in
> Replace (`#[kani::stub_verified]`) or RecursiveCheck (`#[kani::recursion]` contract checking).

The base `docs/src/reference/experimental/contracts.md` has no limitation section yet; the
future patch should add one and use the actual `ContractMode` names. Do not label the runtime
outcome Unsupported without observed evidence. No mode guard/cut is proposed here.

## Existing source anchors

- `kani_middle/transform/contracts.rs::contract_mode:569` uses proof-for-contract metadata
  first: recursive target → RecursiveCheck, nonrecursive → SimpleCheck; then verified-stubs
  metadata → Replace; other contracts → Assert/Original according to configuration.
- `library/kani_macros/src/sysroot/contracts/replace.rs::initial_replace_stmts` havocs return
  through `kani::any_modifies`; `expand_replace_body` asserts requires and assumes ensures.
  The payload check may precede the ensures assumption; source alone does not fix the outcome.
- Existing macro/API examples read: `tests/expected/function-contract/simple_replace_pass.rs`
  (real `stub_verified` plus SimpleCheck companion) and `gcd_rec_simple_pass.rs`
  (actual recursive edge plus `kani::recursion` and proof-for-contract).
  Existing explicit unwind syntax was read in `gcd_replacement_pass.rs`.

## Source-level semantic expectations for future fixtures

Use `MaybeUninit::new(valid_u8)` and `MaybeUninit::<u8>::uninit()`; neither constructs an invalid
typed payload. A helper and return must carry actual by-value shadow storage. Reading the new
payload is legal; merely transferring uninit storage is legal; reading its payload is not.
Requires/ensures must be lawful under the source contract. Replace's demonic return must be
bound to the actual generated replacement and helper/return path before interpreting its checks.

RecursiveCheck needs a real recursive call with both base and recursive paths, reentry replacement,
and a small explicit bound. Reuse the payload contract in ordinary/SimpleCheck companions, while
recording the intentional recursion metadata difference. An attribute alone is not mode evidence.
Full transformed body/mode/transfer binding, per-root property inventory and lawful prefix are
pending. No new fixture or golden was staged after STOP; no failure is guessed from source.
An eventual particular SUCCESS must not be promoted to general mode qualification.
