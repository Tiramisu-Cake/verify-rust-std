# M2-A source/mode/site map — PREPARED / AWAITING_CI

This is source inspection at exact M2 `5f7f2b7364135a0a8b7cfd86c43b4491a8911bac`, not observed MIR or a causal diagnosis. Source hashes and coordinator-reported observations are in INPUTS.json. No new compiler/solver ran. Historical M2 records remain unchanged.

## Mode and wrapper axes

`kani-compiler/src/kani_middle/transform/contracts.rs:406,566–585` sets `assert_contracts = !no_assert_contracts`; the checked target takes SimpleCheck (this target has no recursion attribute) before Replace/Assert/Original. Thus source-predicted modes are:

| Root/configuration | Target dispatch | Clauses/frame retained by source |
| --- | --- | --- |
| Original ordinary, function-contracts, default | Assert | Body-wrapper and asserted ensures; modifies adds no Assert-body wrapping |
| Original PFC, function-contracts, default | SimpleCheck | Check closure, modifies wrapper, asserted ensures and DFCC frame |
| Decorated ordinary, function-contracts, no-assert-contracts | Original | Original body; ensures/frame checking removed from this probe |
| PFC plus no-assert-contracts (DEFERRED) | SimpleCheck | Check has priority; flag does not disable PFC |
| Undecorated ordinary, with/without contracts flag | No decorated target mode | Same original body, body/root assertions only |

Actual selected/transformed roots, wrapper instances and emitted modes are UNKNOWN until C01/C02 inventory. `assert.rs:43–58,63–100` constructs a body_wrapper and appends asserted postconditions; `check.rs:23–75,83–106,140–158` uses the modifies wrapper and appends ensures. `shared.rs:143–159` lifts only explicit old expressions and applies the result closure. The M2 ensures has no `old`; an old-copy explanation has no source binding. Generated copies/captures still need actual MIR binding independently of old.

## Six original equality sites

Coordinates are in `tests/expected/uninit/transfer-qualification/legal-pair.rs`. Each row needs its own two-operand record; sharing RHS spelling does not establish allocation sharing. Ordinary body may be emitted in a generated wrapper.

| Root | Site | LHS source candidate | RHS source candidate | Actual MIR/CheckAs/property |
| --- | --- | --- | --- | --- |
| legal_ordinary_transfer | body:30 | `value: [u8;3]`, stack assume_init return temporary | `[1,2,3]`, candidate promoted immutable referent | UNKNOWN for both operands |
| legal_ordinary_transfer | ensures:14 | `*out: [u8;3]`, referent after `*out = value` | Separate clause literal/promotion candidate | UNKNOWN for both operands |
| legal_ordinary_transfer | root:39 | `out: [u8;3]`, caller stack destination | Separate root literal/promotion candidate | UNKNOWN for both operands |
| legal_pfc_transfer | body:30 | `value` in Check/modifies wrapper | Body literal/promotion candidate | UNKNOWN for both operands |
| legal_pfc_transfer | ensures:14 | out referent through generated captures/wrapper | Clause literal/promotion candidate | UNKNOWN for both operands |
| legal_pfc_transfer | root:46 | Caller `out` after contract target | Root literal/promotion candidate | UNKNOWN for both operands |

For EVERY operand coordinator must return: source site and transformed instance/block → retained raw_eq/CheckAs specialization and operand number → origin alternatives/carrier/AllocId and pre-zero-fill Some/None mask → backend symbol → runtime object/base offset/extent → reset completion and matching seed (or complete mutable history) → last setter/transfer → read/property ID/status. AllocId is compiler-local, never a runtime object ID. If raw_eq is absent, record actual lowering; absence is not coverage. Property inventory alone has no reached verdict or runtime witness.

LHS body history candidate: slot MU<[u8;3]> → cast `*mut u8` → writes offsets 0,1,2 → assume_init normal return destination → `value` read. Ensures history additionally includes typed assignment to out and generated capture/copy paths. Root history includes the call's actual normal continuation. Each RHS needs its own immutable origin/seed binding, even if coalesced. Stack `[0;3]` initialization is a separate source object. None of these candidates is an observed runtime identity.

## Static transfer/reset rules to bind, not conclusions

`delayed_ub/instrumentation_visitor.rs:122` inserts relevant mutating/common-ancestor SetRef(true,After); `transform/body.rs:307,674` splits only normal Call targets. Do not repeat D0's established historical normal setter as proof for these new destinations. `ptr_uninit/uninit_visitor.rs:47,493,696,766,1145` preserves shadow indices 1,2/count2 for select(MU<u8>,MU<u8>,bool), snapshot-before-Move, callee entry loads and return0/count0. Numeric signature is model-local `Ty::to_index()` cast to usize (`check_uninit/mod.rs:691`), not a stable guessed ID.

`mem_init.rs:431,449,501` carries false source witnesses through selected argument/return branches; require the source-following `buffer_value && layout[relative_offset]` branch, not optimistic destination true. Bind any macro/hook copy only if the actual path includes it. `ptr_uninit/mod.rs:54,82,101`, `mem_init.rs:240`, `immutable_allocations.rs:162,210,308,326` require full reset → exact canonical seed → first effect. `contract.rs:129–176` and PFC entry clause-depth reset/private assigns must remain bound for PFC.

## Alternatives and targeted requests

Missing RHS seed, lost normal destination update, UntrackedDeref, generated copy/capture and a different lowering are competing hypotheses. Neither `[u8;3]` text nor both roots failing distinguishes them. First request C01/C02 is singleton retained MIR and property inventory with source/mode binding, no solver. If runtime object/setter history is unavailable there, request a bounded trace of an already identified property using the existing supported process; do not request a full global dump or restart the heavy original solver. A property-filtered trace is diagnostic only.

Out-pointer: request ALL Failed Checks (including `*const u8`), successful endpoint checks at offsets0/2 and intended false byte1 read; substring `u8`/matched golden does not qualify early pointer failure. Normal-abort: request true panic path and absence of executed normal setter/return0 store/load, plus false normal read7 success. Postcondition-hole: valid MU returned by false selection; first payload read remains `assume_init_read` in ensures. OOM provides no property verdict. These gaps stay OPEN.

## Explicit type/signature audit (source only)

Exact Rust source revision `7189d39d9` (M1 recorded nightly-2026-10-23 mapping) was read for mem/maybe_uninit.rs, ptr/mut_ptr.rs and array/equality.rs; hashes, URLs and declarations are in INPUTS.json. The CI-installed sysroot/binary identity is UNKNOWN. No compiler was run.

| Expression/API | Operand/result types checked |
| --- | --- |
| select(a,b,first) | `(MaybeUninit<u8>, MaybeUninit<u8>, bool) -> MaybeUninit<u8>`; 7/17 inferred u8 from this signature; true/false bool |
| MU<T>::new/uninit | `new(T)->MU<T>`, `uninit()->MU<T>`; select supplies T=u8; array slot explicitly T=[u8;3] |
| selected.assume_init() | Consumes MU<u8>, returns u8; byte/assert literal7 both u8 |
| slot.as_mut_ptr().cast::<u8>() | `&mut MU<[u8;3]> -> *mut [u8;3]`; `cast<U>(self)->*mut U`, U=u8 |
| data.write / data.add | `write(self,val:T)` on *mut u8 takes u8; `add(self,count:usize)->Self`; offset literals1/2 infer usize, never compared with u64 |
| slot.assume_init / assignment | Consumes MU<[u8;3]>, returns [u8;3]; `*out` is [u8;3] via `&mut [u8;3]` |
| body/root assert_eq | Array operands both [u8;3], borrowed by macro; scalar return/assert literal7 both u8; out initialized [0;3] inferred [u8;3] by target call |
| ensures original | result:&u8, `*result == 7` is u8==u8; `*out == [1,2,3]` compares [u8;3] with [u8;3]; `&&` joins bools |
| ensures scalar drafts | result:&MU<u8>; assume_init_read(&self)->u8; RHS17 inferred u8; no body payload read; root stores unread MU<u8> |
| array equality specialization | PartialEq<[U;N]> for [T;N], eq(&self,&[U;N])->bool; spec_eq(a:&[T;N],b:&[U;N]); BytewiseEq may use raw_eq; actual retained specialization UNKNOWN |

The undecorated draft removes only attributes/header flag; remaining Rust body/root bytes equal the decorated singleton. Scalar legal differs from the original scalar hole only in selected bool, root name and explanatory comment. No integer-width conversions, new bounds, assumptions or local lint suppressions were added. Compilation, lints and generated closure types remain NOT_RUN.
