//! Opt-in N2 forwarding contract for the blanket Stable entry with a key-rewriting comparator.
//! Keys are arbitrary after any comparison, so no order is promised: the contract states only
//! the tag multiset (independent u8 probe) and the frame. Not a contract for an arbitrary FnMut.

use super::super::super::StableSmallSortTypeImpl;
use super::{always_true, canonical, canonical_guard, pair_region};
use crate::cell::Cell;
use crate::mem::MaybeUninit;
use crate::ub_checks::same_allocation;
use crate::{kani, ptr, slice};

// Same meaning as the network.rs TaggedKey: comparisons may rewrite key; tag is the identity.
#[derive(Clone, Copy)]
struct TaggedKey {
    key: u8,
    tag: u8,
}

fn any_tagged() -> TaggedKey {
    TaggedKey { key: kani::any(), tag: kani::any() }
}

fn same(x: TaggedKey, y: TaggedKey) -> bool {
    x.key == y.key && x.tag == y.tag
}

// Canonical comparator, the body of network.rs `mutating_key_order`: reads both values, writes
// arbitrary keys, keeps both tags and returns an arbitrary bool.
fn cellwrap_key_order(a: &Cell<TaggedKey>, b: &Cell<TaggedKey>) -> bool {
    // SAFETY: both initialized Cell payloads must be readable before either write.
    let (left, right) =
        unsafe { (crate::ptr::read_volatile(a.as_ptr()), crate::ptr::read_volatile(b.as_ptr())) };
    let left_key: u8 = kani::any();
    let right_key: u8 = kani::any();
    a.set(TaggedKey { key: left_key, tag: left.tag });
    b.set(TaggedKey { key: right_key, tag: right.tag });
    kani::cover(
        left_key != left.key && right_key != right.key,
        "cellwrap comparator changes both keys",
    );
    kani::any()
}

// wrap.rs `stable_region` for this element type: the pair stays exclusive of nonempty scratch.
fn tagged_region(v: *mut Cell<TaggedKey>, scratch: &[MaybeUninit<Cell<TaggedKey>>]) -> bool {
    pair_region(v)
        && (scratch.is_empty()
            || !same_allocation(
                v as *const Cell<TaggedKey>,
                scratch.as_ptr().cast::<Cell<TaggedKey>>(),
            )
            || {
                // SAFETY: both nonempty regions are live and in the same allocation.
                // MaybeUninit<Cell<TaggedKey>> and Cell<TaggedKey> have identical layout.
                let d = unsafe { scratch.as_ptr().cast::<Cell<TaggedKey>>().offset_from(v) };
                if d >= 0 { d as usize >= 2 } else { d.unsigned_abs() >= scratch.len() }
            })
}

// Reads only the two initialized pair elements; only this scalar is captured in old().
fn pair_tag_count(v: *const Cell<TaggedKey>, probe: u8) -> usize {
    // SAFETY: the wrapper requires establish a readable initialized two-element span.
    let v = unsafe { slice::from_raw_parts(v, 2) };
    (v[0].get().tag == probe) as usize + (v[1].get().tag == probe) as usize
}

// Cell is !Freeze: the blanket Stable entry ignores scratch and runs insertion from index 1.
#[kani::requires(tagged_region(v, scratch))]
#[kani::requires(canonical(cmp, cellwrap_key_order))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 2))]
#[kani::ensures(|_| old(pair_tag_count(v, probe)) == pair_tag_count(v, probe))]
unsafe fn cellwrap_stable(
    v: *mut Cell<TaggedKey>,
    scratch: &mut [MaybeUninit<Cell<TaggedKey>>],
    cmp: fn(&Cell<TaggedKey>, &Cell<TaggedKey>) -> bool,
    probe: u8,
) {
    if !canonical_guard(canonical(cmp, cellwrap_key_order)) {
        return;
    }
    // SAFETY: the requires establish exactly two initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, 2) };
    let mut is_less = cmp;
    <Cell<TaggedKey> as StableSmallSortTypeImpl>::small_sort(v, scratch, &mut is_less);
}

// Control-only mutant of `cellwrap_stable`: same contract and body, then one tag in the active
// pair is flipped after the real entry returns.
#[kani::requires(tagged_region(v, scratch))]
#[kani::requires(canonical(cmp, cellwrap_key_order))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 2))]
#[kani::ensures(|_| old(pair_tag_count(v, probe)) == pair_tag_count(v, probe))]
unsafe fn cellwrap_stable_tag_corruption(
    v: *mut Cell<TaggedKey>,
    scratch: &mut [MaybeUninit<Cell<TaggedKey>>],
    cmp: fn(&Cell<TaggedKey>, &Cell<TaggedKey>) -> bool,
    probe: u8,
) {
    if !canonical_guard(canonical(cmp, cellwrap_key_order)) {
        return;
    }
    // SAFETY: the requires establish exactly two initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, 2) };
    let mut is_less = cmp;
    <Cell<TaggedKey> as StableSmallSortTypeImpl>::small_sort(v, scratch, &mut is_less);
    let first = v[0].get();
    v[0].set(TaggedKey { key: first.key, tag: first.tag ^ 1 });
}

// Shared body of the positive root and the corruption control, laid out as `stable_cell_n2`.
macro_rules! cellwrap_n2_body {
    ($wrapper:ident) => {{
        let [left, a, b, right] = [any_tagged(), any_tagged(), any_tagged(), any_tagged()];
        let probe: u8 = kani::any();
        let mut v = [Cell::new(left), Cell::new(a), Cell::new(b), Cell::new(right)];
        let mut scratch = [MaybeUninit::new(Cell::new(any_tagged())), MaybeUninit::uninit()];
        let scratch_len: usize = kani::any_where(|n: &usize| *n <= 2);
        // SAFETY: this slot was initialized above; TaggedKey has no padding and get reads it all.
        let scratch_before = unsafe { scratch[0].assume_init_ref() }.get();
        // SAFETY: active pair in initialized backing4; separate valid scratch; canonical pointer.
        unsafe {
            $wrapper(v[1..3].as_mut_ptr(), &mut scratch[..scratch_len], cellwrap_key_order, probe)
        };
        kani::assert(same(v[0].get(), left) && same(v[3].get(), right), "cellwrap input frame");
        // SAFETY: the blanket Cell route does not write scratch; only the input may be modified.
        let scratch_after = unsafe { scratch[0].assume_init_ref() }.get();
        kani::assert(same(scratch_before, scratch_after), "cellwrap scratch frame");
        let tags = (v[1].get().tag, v[2].get().tag);
        kani::cover(scratch_len == 0, "cellwrap empty scratch returns");
        kani::cover(scratch_len == 2, "cellwrap unread uninit scratch tail returns");
        kani::cover(probe == a.tag || probe == b.tag, "cellwrap independent probe hits a tag");
        kani::cover(probe != a.tag && probe != b.tag, "cellwrap independent probe misses tags");
        kani::cover(a.tag != b.tag && tags == (b.tag, a.tag), "cellwrap tags exchanged");
        kani::cover(a.tag != b.tag && tags == (a.tag, b.tag), "cellwrap tags stay in place");
        kani::cover(true, "cellwrap stable Cell<TaggedKey> trait entry returns");
    }};
}

#[kani::proof_for_contract(cellwrap_stable)]
#[kani::unwind(16)]
fn cellwrap_stable_tags_n2() {
    cellwrap_n2_body!(cellwrap_stable);
}

// Same body against the mutant: its ensures (the shared tag-count line) must be the only failure.
#[kani::proof_for_contract(cellwrap_stable_tag_corruption)]
#[kani::unwind(16)]
fn cellwrap_tag_corruption_control() {
    cellwrap_n2_body!(cellwrap_stable_tag_corruption);
}

// Plain real-body call with another fn pointer: no PFC assumption hides it, so the shared wrap.rs
// guard literal must be the only failure; the wrapper returns before any sort or comparison.
#[kani::proof]
#[kani::unwind(16)]
fn cellwrap_wrong_comparator_control() {
    let mut v = [Cell::new(any_tagged()), Cell::new(any_tagged())];
    let probe: u8 = kani::any();
    kani::cover(true, "cellwrap invalid comparator reaches guard");
    // SAFETY: valid pair and empty scratch; only canonical identity is deliberately rejected.
    unsafe { cellwrap_stable(v.as_mut_ptr(), &mut [], always_true::<Cell<TaggedKey>>, probe) };
}
