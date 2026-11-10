//! Verification-only sort model, specialized by element and comparator type.
//! Snapshot callers supply an initialized readable slice region, never scratch storage.

pub(crate) type U64Cmp = fn(&u64, &u64) -> bool;

pub(crate) fn canonical_less_u64(a: &u64, b: &u64) -> bool {
    a < b
}

#[derive(Clone, Copy)]
pub(crate) enum SortEntry {
    Stable,
    Unstable,
    Freeze,
}

#[derive(Clone, Copy)]
pub(crate) struct SortSnapshot {
    pub(crate) len: usize,
    pub(crate) valid: bool,
    pub(crate) vals: [u64; 3],
}

pub(crate) trait SortModel<T, F> {
    fn enabled(entry: SortEntry, cmp: &F, len: usize) -> bool;
    fn snapshot(base: *const T, len: usize) -> SortSnapshot;
    fn sort_postcondition(pre: SortSnapshot, base: *const T, len: usize) -> bool;
}

impl<T, F> SortModel<T, F> for () {
    default fn enabled(_entry: SortEntry, _cmp: &F, _len: usize) -> bool {
        false
    }

    default fn snapshot(_base: *const T, _len: usize) -> SortSnapshot {
        SortSnapshot { len: 0, valid: false, vals: [0; 3] }
    }

    default fn sort_postcondition(_pre: SortSnapshot, _base: *const T, _len: usize) -> bool {
        true
    }
}

fn snapshot_count_u64(snapshot: SortSnapshot, value: u64) -> usize {
    let mut result = 0;
    let mut i = 0;
    while i < snapshot.len {
        result += usize::from(snapshot.vals[i] == value);
        i += 1;
    }
    result
}

impl SortModel<u64, U64Cmp> for () {
    fn enabled(entry: SortEntry, cmp: &U64Cmp, len: usize) -> bool {
        let supported = match entry {
            SortEntry::Stable => len == 2 || len == 3,
            SortEntry::Unstable => len == 2 || len == 3,
            SortEntry::Freeze => len == 2 || len == 3,
        };
        supported && *cmp as *const () == canonical_less_u64 as *const ()
    }

    fn snapshot(base: *const u64, len: usize) -> SortSnapshot {
        let mut result = SortSnapshot { len, valid: false, vals: [0; 3] };
        if len != 2 && len != 3 {
            return result;
        }
        result.valid = true;
        let mut i = 0;
        while i < len {
            // SAFETY: callers provide len initialized readable u64s in the active slice.
            result.vals[i] = unsafe { *base.add(i) };
            i += 1;
        }
        result
    }

    fn sort_postcondition(pre: SortSnapshot, base: *const u64, len: usize) -> bool {
        let post = <() as SortModel<u64, U64Cmp>>::snapshot(base, len);
        if !pre.valid || !post.valid || pre.len != post.len || pre.len > 3 || pre.len < 2 {
            return false;
        }
        if !(post.vals[0] <= post.vals[1] && (post.len == 2 || post.vals[1] <= post.vals[2])) {
            return false;
        }
        if pre.len == 2 {
            return (post.vals[0] == pre.vals[0] && post.vals[1] == pre.vals[1])
                || (post.vals[0] == pre.vals[1] && post.vals[1] == pre.vals[0]);
        }
        let mut i = 0;
        while i < pre.len {
            if snapshot_count_u64(pre, pre.vals[i]) != snapshot_count_u64(post, pre.vals[i]) {
                return false;
            }
            i += 1;
        }
        true
    }
}
