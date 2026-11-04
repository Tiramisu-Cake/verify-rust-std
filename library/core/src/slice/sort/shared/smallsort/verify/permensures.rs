//! Opt-in conditional full-value swap contracts and tag-permutation composition.
//! PFCs and consumers use exactly the same u8/function-item comparator and backing N.
//! Only swap_if_less is replaced by a verified summary. Insertion and merge execute real
//! bodies; only the explicit order-violation panic is cut, so claims concern normal return.

use super::super::{PairPermutation, UnstableSmallSortTypeImpl, swap_if_less};
use crate::{kani, ptr};

fn arbitrary_less(a: &u8, b: &u8) -> bool {
    // SAFETY: the helper must provide initialized readable references. Both reads are
    // observable; the result remains independent of the values and of every prior answer.
    unsafe {
        let _a = ptr::read_volatile(a);
        let _b = ptr::read_volatile(b);
    }
    let answer: bool = kani::any();
    kani::cover(answer, "permensures comparator true");
    kani::cover(!answer, "permensures comparator false");
    answer
}

fn model_is_active<F: FnMut(&u8, &u8) -> bool>(_: &F) {
    kani::assert(<F as PairPermutation<u8>>::has_model(), "permensures u8 model active");
}

fn exercise_swap<const N: usize>() {
    let mut v: [u8; N] = kani::any();
    let before = v;
    let a: usize = kani::any();
    let b: usize = kani::any();
    kani::assume(a < N && b < N);
    model_is_active(&arbitrary_less);
    // SAFETY: both positions are initialized, aligned and writable in this allocation.
    // Equal positions are intentionally included, as are both orders of distinct positions.
    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut arbitrary_less) };
    for i in 0..N {
        kani::assert(i == a || i == b || v[i] == before[i], "permensures swap frame");
    }
    kani::cover(a == b, "permensures equal positions return");
    kani::cover(a < b, "permensures increasing positions return");
    kani::cover(a > b, "permensures decreasing positions return");
    kani::cover(
        a != b && before[a] != before[b] && v[a] == before[b] && v[b] == before[a],
        "permensures distinct values exchanged",
    );
    kani::cover(true, "permensures swap returns");
}

macro_rules! swap_pfc {
    ($name:ident, $n:literal) => {
        #[kani::proof_for_contract(swap_if_less)]
        #[kani::unwind(40)]
        fn $name() {
            exercise_swap::<$n>();
        }
    };
}

swap_pfc!(swap_permutation_u8_backing4, 4);
swap_pfc!(swap_permutation_u8_backing9, 9);
swap_pfc!(swap_permutation_u8_backing13, 13);
swap_pfc!(swap_permutation_u8_backing17, 17);
swap_pfc!(swap_permutation_u8_backing18, 18);
swap_pfc!(swap_permutation_u8_backing24, 24);
swap_pfc!(swap_permutation_u8_backing32, 32);

fn cut_order_violation_panic() -> ! {
    kani::cover(true, "permensures order-violation boundary reached");
    kani::assume(false);
    unreachable!()
}

fn exercise_network<const N: usize>(corrupt: bool) {
    // Distinct identity tags fill the entire backing, with no payload or comparator model.
    // Arbitrary decisions can permute these tags independently of their numeric order.
    let mut v = [0u8; N];
    for i in 0..N {
        v[i] = i as u8;
    }
    model_is_active(&arbitrary_less);
    <u8 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut arbitrary_less);
    kani::cover(true, "permensures network returns before corruption");
    if corrupt {
        // N >= 2. A duplicate must remove one tag from the full N-bit mask.
        v[0] = v[1];
    }
    let mut mask = 0u64;
    for tag in v {
        kani::assert((tag as usize) < N, "permensures tag in range");
        mask |= 1u64 << tag;
    }
    kani::assert(mask == (1u64 << N) - 1, "permensures network tag mask");
    kani::cover(true, "permensures network mask checked");
}

macro_rules! network_consumer {
    ($name:ident, $n:literal) => {
        #[kani::proof]
        #[kani::stub_verified(swap_if_less)]
        #[kani::stub(super::super::panic_on_ord_violation, cut_order_violation_panic)]
        #[kani::unwind(40)]
        fn $name() {
            exercise_network::<$n>(false);
        }
    };
}

network_consumer!(unstable_network_permutation_u8_n17, 17);
network_consumer!(unstable_network_permutation_u8_n18, 18);
network_consumer!(unstable_network_permutation_u8_n24, 24);
network_consumer!(unstable_network_permutation_u8_n32, 32);

#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub(super::super::panic_on_ord_violation, cut_order_violation_panic)]
#[kani::unwind(40)]
fn rejects_network_corruption_u8_n17() {
    exercise_network::<17>(true);
}

#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub(super::super::panic_on_ord_violation, cut_order_violation_panic)]
#[kani::unwind(40)]
fn rejects_network_corruption_u8_n9() {
    exercise_network::<9>(true);
}
