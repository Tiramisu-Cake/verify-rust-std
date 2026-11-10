//! Verification-only dispatch by both element and comparator type.
//! Callers supply an initialized readable region of `len` elements.

pub(crate) type U64Cmp = fn(&u64, &u64) -> bool;

pub(crate) fn canonical_less_u64(a: &u64, b: &u64) -> bool {
    a < b
}

pub(crate) trait PairModel<T, F> {
    fn enabled(cmp: &F, len: usize) -> bool;
    fn snapshot(base: *const T, len: usize) -> (u64, u64);
    fn pair_is_sorted(base: *const T, len: usize) -> bool;
    fn pair_permutation(base: *const T, len: usize, pre: (u64, u64)) -> bool;
}

impl<T, F> PairModel<T, F> for () {
    default fn enabled(_cmp: &F, _len: usize) -> bool {
        false
    }

    default fn snapshot(_base: *const T, _len: usize) -> (u64, u64) {
        (0, 0)
    }

    default fn pair_is_sorted(_base: *const T, _len: usize) -> bool {
        true
    }

    default fn pair_permutation(_base: *const T, _len: usize, _pre: (u64, u64)) -> bool {
        true
    }
}

impl PairModel<u64, U64Cmp> for () {
    fn enabled(cmp: &U64Cmp, len: usize) -> bool {
        len == 2 && *cmp as *const () == canonical_less_u64 as *const ()
    }

    fn snapshot(base: *const u64, len: usize) -> (u64, u64) {
        if len == 2 {
            // SAFETY: callers provide two initialized readable u64s when len == 2.
            unsafe { (*base, *base.add(1)) }
        } else {
            (0, 0)
        }
    }

    fn pair_is_sorted(base: *const u64, len: usize) -> bool {
        let post = <() as PairModel<u64, U64Cmp>>::snapshot(base, len);
        post.0 <= post.1
    }

    fn pair_permutation(base: *const u64, len: usize, pre: (u64, u64)) -> bool {
        let post = <() as PairModel<u64, U64Cmp>>::snapshot(base, len);
        post == pre || post == (pre.1, pre.0)
    }
}
