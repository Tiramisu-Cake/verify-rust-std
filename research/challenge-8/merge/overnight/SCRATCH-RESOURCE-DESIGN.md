# Paired option-scratch resource frame

## Target and scope

This fixture isolates the stock typed resource needed to represent two
destination cells in the merge scratch array. A cell is the full
`points_to_<T>(p, option<T>)` chunk used by stock `array_<T>`; `none` models an
uninitialized `MaybeUninit<T>` cell and `some(v)` models an initialized cell
holding a model value of `T`. The fixture uses only this option-cell resource.
It never creates, transfers, or requires `<T>.own`, and never relates scratch
values to arbitrary byte strings.

The domain is generic, positive-stride, and excludes zero-sized `T`. A checked
whole-array predicate carries every option cell and an input list of logical
option values. Its two-hole form omits exactly the selected cells while
retaining every other cell in the recursive frame. Extraction returns the two
actual writable option-cell chunks. Restoration consumes those current chunks
and reconstructs the full array with exact list replacement. The list argument
is an input, not an output: it records the represented contents without a
predicate-precision claim.

## Exact contracts

For `n >= 2`, `0 <= i < j < n`, positive `size_of::<T>()`, and
`n * size_of::<T>() <= isize::MAX`, extraction transforms
`scratch_option_array(p,n,vs)` into the two-hole frame plus
`points_to_<T>(p+i,vi)` and `points_to_<T>(p+j,vj)`, where
`vi == nth(i,vs)` and `vj == nth(j,vs)`. The destination values may each be
`none` or `some(v)`; no source or owner resource is consumed.

Restoration takes that frame and the current destination chunks at `p+i` and
`p+j`. Its normal post is the full option array whose model is
`replace_two(vs,i,j,vi,vj)`, plus all non-hole cells. This accepts the option
values produced by the actual C1 copies and retains old `Some` values as
ordinary option models; a C1 byte copy does not create a `T.own` chunk. The
fixture functions also declare their complete normal frame and `on_unwind_ens
false` post. Panic behavior of the actual merge, including partial writes, is
not proved here.

The concrete `u32` case is restoration-only: its precondition supplies current
physical `Some(41)`/`None` hole resources and separately records old `None`/
`Some(73)` values in the saved list. Its body performs no write and does not
claim to model how a C1 copy produced those current values.

Every recursive predicate/lemma has a checked body. Index arithmetic is
ghost-only and follows the structural list traversal; the public cases use
valid interior indices. The unrelated frame is an ordinary initialized
`u32` pointsto plus its matching owner and must survive extraction/restoration.

## Trust boundary and decision matrix

No primitive, axiom, assumption, verifier patch, permission conversion, or
ownership bridge is introduced. This fixture establishes only the option
array resource algebra for later integration. It does not prove the allocator
postconditions, actual `merge_up`/`merge_down`, source loans, `CopyOnDrop`,
normal/unwind cleanup, or functional properties. Generic invalid bytes and
ZST behavior remain outside the domain.

| Case | Intended obligation | Evidence and next decision |
| --- | --- | --- |
| `scratch_option_extract_restore_old_values_and_frame` | Extract and restore arbitrary old `None`/`Some` destination values while preserving the unrelated frame | Full verifier/refinement/body/return/leak/dead/source gates; if green, retain as the basic resource component. |
| `scratch_option_restore_current_values` | Reconstruct the exact list after the two destination options have changed | Full positive gates; establishes list replacement from actual current slots without requiring a `T.own`. |
| `scratch_option_restore_concrete_u32_current_values` | Restore concrete current slot values `Some(41)`/`None` over saved list values `None`/`Some(73)` | Full positive gates; checks concrete option constructors and list replacement with supplied current cells, without modeling writes. |
| `scratch_option_duplicate_write_permission` | A single hole does not provide a second writable `points_to_<T>` chunk | Keep inconclusive until the hosted target diagnostic is observed, then pin exact rejection metadata. |
| `scratch_option_wrong_old_list_rejected` | Current option values that differ from the saved list cannot restore the old array | Keep inconclusive until the hosted target diagnostic is observed, then pin exact rejection metadata. |
| `scratch_option_does_not_create_owner` | An initialized option cell does not imply `<T>.own` | Keep inconclusive until the hosted target diagnostic is observed, then pin exact rejection metadata. |

The first hosted result determines whether the resource predicates/recursive
contracts work under the pinned stock verifier. A setup or unrelated helper
failure is not a negative result. A green fixture is only this option-resource
component; root must separately integrate it into the actual source proof.
