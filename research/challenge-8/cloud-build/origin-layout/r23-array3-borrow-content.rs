/*@

pred r23_u64_array3_own(t: thread_id_t, a: [u64; 3]) =
    foreach(Array_elems(a), own::<u64>(t));

pred_ctor r23_u64_array3_fbc(t: thread_id_t, p: *[u64; 3])() =
    *p |-> ?a &*& r23_u64_array3_own(t, a);

lem r23_array3_fbc_to_content(t: thread_id_t, p: *[u64; 3])
    req r23_u64_array3_fbc(t, p)();
    ens r20_u64_array3_content(t, p as *u64)();
{
    open r23_u64_array3_fbc(t, p)();
    open r23_u64_array3_own(t, _);
    Array_to_array(p);
    close r20_u64_array3_content(t, p as *u64)();
}

lem r23_content_to_array3_fbc(t: thread_id_t, p: *[u64; 3])
    req r20_u64_array3_content(t, p as *u64)();
    ens r23_u64_array3_fbc(t, p)();
{
    open r20_u64_array3_content(t, p as *u64)();
    assert array::<u64>(p as *u64, 3, ?r23_elements);
    r9_drop_u64_owners(t, r23_elements);
    array_to_Array(p);
    assert *p |-> ?r23_array;
    r9_make_u64_owners(t, Array_elems(r23_array));
    close r23_u64_array3_own(t, r23_array);
    close r23_u64_array3_fbc(t, p)();
}

lem r23_array3_fbc_to_slice_content(t: thread_id_t, p: *[u64; 3], s: *[u64])
    req r23_u64_array3_fbc(t, p)() &*&
        strip_pointer_metadata(s as pointer) as *u64 == p as *u64 &*& s.len() == 3;
    ens <[u64]>.full_borrow_content(t, s)();
{
    r23_array3_fbc_to_content(t, p);
    r20_array3_content_to_slice(t, p as *u64, s);
}

lem r23_slice_content_to_array3_fbc(t: thread_id_t, p: *[u64; 3], s: *[u64])
    req <[u64]>.full_borrow_content(t, s)() &*&
        strip_pointer_metadata(s as pointer) as *u64 == p as *u64 &*& s.len() == 3;
    ens r23_u64_array3_fbc(t, p)();
{
    r20_slice_content_to_array3(t, p as *u64, s);
    r23_content_to_array3_fbc(t, p);
}

lem r23_array3_borrow_to_slice(k: lifetime_t, t: thread_id_t, p: *[u64; 3], s: *[u64])
    req full_borrow(k, r23_u64_array3_fbc(t, p)) &*&
        strip_pointer_metadata(s as pointer) as *u64 == p as *u64 &*& s.len() == 3;
    ens full_borrow(k, <[u64]>.full_borrow_content(t, s));
{
    produce_lem_ptr_chunk implies(r23_u64_array3_fbc(t, p), <[u64]>.full_borrow_content(t, s))() {
        r23_array3_fbc_to_slice_content(t, p, s);
    } {
        produce_lem_ptr_chunk implies(<[u64]>.full_borrow_content(t, s), r23_u64_array3_fbc(t, p))() {
            r23_slice_content_to_array3_fbc(t, p, s);
        } {
            full_borrow_implies(k, r23_u64_array3_fbc(t, p), <[u64]>.full_borrow_content(t, s));
        }
    }
}

lem r23_slice_borrow_to_array3(k: lifetime_t, t: thread_id_t, p: *[u64; 3], s: *[u64])
    req full_borrow(k, <[u64]>.full_borrow_content(t, s)) &*&
        strip_pointer_metadata(s as pointer) as *u64 == p as *u64 &*& s.len() == 3;
    ens full_borrow(k, r23_u64_array3_fbc(t, p));
{
    produce_lem_ptr_chunk implies(<[u64]>.full_borrow_content(t, s), r23_u64_array3_fbc(t, p))() {
        r23_slice_content_to_array3_fbc(t, p, s);
    } {
        produce_lem_ptr_chunk implies(r23_u64_array3_fbc(t, p), <[u64]>.full_borrow_content(t, s))() {
            r23_array3_fbc_to_slice_content(t, p, s);
        } {
            full_borrow_implies(k, <[u64]>.full_borrow_content(t, s), r23_u64_array3_fbc(t, p));
        }
    }
}

// Dispose only an expired logical lease after all physical content is restored.
// The physical array and element ownership are required and returned unchanged.
lem r23_dispose_dead_array3_borrow(k: lifetime_t, t: thread_id_t, p: *[u64; 3])
    req [_]lifetime_dead_token(k) &*& full_borrow(k, r23_u64_array3_fbc(t, p)) &*&
        r23_u64_array3_fbc(t, p)();
    ens [_]lifetime_dead_token(k) &*& r23_u64_array3_fbc(t, p)();
{
    leak full_borrow(k, r23_u64_array3_fbc(t, p));
}

@*/
