/*@

pred_ctor r20_u64_array3_content(t: thread_id_t, p: *u64)() =
    array::<u64>(p, 3, ?current) &*& foreach(current, own::<u64>(t));

lem r20_array3_content_to_slice(t: thread_id_t, p: *u64, s: *[u64])
    req r20_u64_array3_content(t, p)() &*&
        strip_pointer_metadata(s as pointer) as *u64 == p &*& s.len() == 3;
    ens slice_full_borrow_content::<u64>(t, s)();
{
    open r20_u64_array3_content(t, p)();
    close slice_full_borrow_content::<u64>(t, s)();
}

lem r20_slice_content_to_array3(t: thread_id_t, p: *u64, s: *[u64])
    req slice_full_borrow_content::<u64>(t, s)() &*&
        strip_pointer_metadata(s as pointer) as *u64 == p &*& s.len() == 3;
    ens r20_u64_array3_content(t, p)();
{
    open slice_full_borrow_content::<u64>(t, s)();
    close r20_u64_array3_content(t, p)();
}

lem r20_array3_borrow_to_slice(k: lifetime_t, t: thread_id_t, p: *u64, s: *[u64])
    req full_borrow(k, r20_u64_array3_content(t, p)) &*&
        strip_pointer_metadata(s as pointer) as *u64 == p &*& s.len() == 3;
    ens full_borrow(k, slice_full_borrow_content::<u64>(t, s));
{
    produce_lem_ptr_chunk implies(r20_u64_array3_content(t, p), slice_full_borrow_content::<u64>(t, s))() {
        r20_array3_content_to_slice(t, p, s);
    } {
        produce_lem_ptr_chunk implies(slice_full_borrow_content::<u64>(t, s), r20_u64_array3_content(t, p))() {
            r20_slice_content_to_array3(t, p, s);
        } {
            full_borrow_implies(k, r20_u64_array3_content(t, p), slice_full_borrow_content::<u64>(t, s));
        }
    }
}

lem r20_slice_borrow_to_array3(k: lifetime_t, t: thread_id_t, p: *u64, s: *[u64])
    req full_borrow(k, slice_full_borrow_content::<u64>(t, s)) &*&
        strip_pointer_metadata(s as pointer) as *u64 == p &*& s.len() == 3;
    ens full_borrow(k, r20_u64_array3_content(t, p));
{
    produce_lem_ptr_chunk implies(slice_full_borrow_content::<u64>(t, s), r20_u64_array3_content(t, p))() {
        r20_slice_content_to_array3(t, p, s);
    } {
        produce_lem_ptr_chunk implies(r20_u64_array3_content(t, p), slice_full_borrow_content::<u64>(t, s))() {
            r20_array3_content_to_slice(t, p, s);
        } {
            full_borrow_implies(k, slice_full_borrow_content::<u64>(t, s), r20_u64_array3_content(t, p));
        }
    }
}

@*/
