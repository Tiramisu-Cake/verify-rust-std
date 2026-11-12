# M2-B/S explicit type audit

Candidate `35fab624af19b8c724ddc9c80a7cc79289541459` vs exact5f7 changes only
`docs/dev/kani3300-m2bs-handoff.md`. Changed Rust expressions/APIs/imports: **none**.
There is no semantic candidate or new selector to compile. A future Rust delta requires a new per-expression
audit and reviewer continuation before coordinator build/fmt/clippy; this audit is not that future approval.
No rustfmt, cargo, rustc, Kani, CBMC or Miri was run. Compilation and -D warnings remain NOT_RUN.

## Inspected existing signatures and width boundaries (unchanged, not a full re-audit of M1)

| Existing expression/API | Source-bound types / conversion obligations |
| --- | --- |
| observe_immutable_origins | immutable_allocations.rs:80: (&mut GotocCtx, &MirConst)->(); anonymous_origins: (TyCtxt<'_>, &MirConst)->Vec<AnonymousOrigin>, tcx passed by value; source fn at anonymous_allocations.rs:33 |
| prepare_immutable_allocations | (&mut self, items:&[MonoItem])->(); Instance::body() result matched Some(body); visitor borrows &body; ConstantCollector stores Vec<MirConst>; no proposed API substitution |
| bind_immutable_allocation | (&mut self, key:AllocId, allocation:&Allocation, address:&Expr)->(); AddressOf object is borrowed Expr; Symbol identifier is dereferenced InternedString; key is compiler identity, no integer cast to runtime object |
| AnonymousOrigin mask | allocation.bytes iter borrows Option<u8>; Option::is_some->bool, collect Vec<bool>; u8 unsigned 8-bit; no payload deref/zero-fill conversion to true |
| pointer carrier checks | pointer_size/slot/carrier.bytes.len():usize (host pointer width, unsigned); checked_add both usize; end<=len both usize; read_partial_uint result offset:Option<u128>; offset==Some(0) RHS inferred Option<u128> |
| referent_extent | ->Option<usize>; slice count is checked TryInto<usize> from read_partial_uint u128; element size usize, checked_mul with count usize; failure None, no truncation; extent==Some(allocation.bytes.len()) compares Option<usize> on both sides |
| target_matches | pointer_width:u64 (unsigned64), cast to host usize compared with MachineInfo::target_pointer_width().bits():usize; existing cast unchanged; no claim that this cast is generally nontruncating on arbitrary hosts |
| descriptor.layout | Vec<(u64,u64)>; existing len as u64, n as u64; symbol.typ.sizeof(&SymbolTable)->u64, compares u64 with u64, never usize; casts unchanged and not newly justified for every host |
| seed extent bound | n:usize unsigned host width; n as u128 compared to unsigned_int_max().unwrap_or(u128::MAX):u128 unsigned128; both sides u128; target usize maximum checked before seed construction |
| emitted seed expressions | object/offset/value are backend Expr; explicit typ checks require size_t/size_t/c_bool; pointer_object()->Expr cast to object's size_t, eq both same backend type; pointer_offset()->Expr compared with int_constant(0,ssize_t), signed target pointer-width type; offset.lt(int_constant(n,offset.typ().clone())) compares size_t both sides, bool Expr result |
| constructors/index | Expr::int_constant<T:Into<BigInt>>(T,Type)->Expr, expr.rs:888; Type::array_of<T:TryInto<u64>>(T)->Type, typ.rs:987, checked conversion unwrap; mask.index(offset) produces c_bool Expr from array of c_bool; Stmt::assign targets value:c_bool; Rust n is usize, backend size_t is target width, not Rust u64 |
| unchanged C03 source | select(MaybeUninit<u8>,MaybeUninit<u8>,bool)->MaybeUninit<u8>; selected.assume_init()->u8; out:&mut[u8;3], value:[u8;3]; both sides of array equality [u8;3]; result:&u8, deref/result == literal7 both u8; && bool/bool |

Local declarations were read at the pinned files hashed in INPUTS.json; C03 standard-library signature audit
is inherited from exact M2-A SITE-MAP/INPUTS with its pinned Rust-source provenance, not a fresh compiler run.
Rust references and backend Expr are separate type levels. Generated closure types, actual lowered operand
specializations, installed compiler/sysroot identity and emitted widths remain UNKNOWN without CI receipts.
There are no new imports, unused bindings, arithmetic, comparisons or conversions to audit in this delta.
Existing code was not reformatted or changed to silence warnings. First subsequent semantic CI must build and clippy.
