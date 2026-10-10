/*@
// C3-only candidate helpers. These are not wired into a preparation runner and
// have not been parsed or verified. The existing split-four and join-four
// lemmas must precede these declarations in the same proof unit.

lem selected_four_limits<T>(base: *T, c1: bool, c2: bool)
    req [?f]base[..4] |-> ?xs;
    ens [f]base[..4] |-> xs &*&
        0 <= (c1 as usize) &*& (c1 as usize) <= 1 &*&
        0 <= ((!c1) as usize) &*& ((!c1) as usize) <= 1 &*&
        2 <= (2 + (c2 as usize)) &*& (2 + (c2 as usize)) <= 3 &*&
        2 <= (2 + ((!c2) as usize)) &*& (2 + ((!c2) as usize)) <= 3 &*&
        pointer_within_limits(base + (c1 as usize)) == true &*&
        pointer_within_limits(base + ((!c1) as usize)) == true &*&
        pointer_within_limits(base + (2 + (c2 as usize))) == true &*&
        pointer_within_limits(base + (2 + ((!c2) as usize))) == true;
{
    // All four source-derived offsets are bounded in each case while the
    // array resource is available. This helper can run before the actual
    // `.add` expressions, so their own pointer-limit obligations are covered.
    if (c1) {
        if (c2) {
            assert c1 as usize == 1;
            assert (!c1) as usize == 0;
            assert c2 as usize == 1;
            assert (!c2) as usize == 0;
            interior_pointer_limits::<T>(base, 4, c1 as usize);
            interior_pointer_limits::<T>(base, 4, (!c1) as usize);
            interior_pointer_limits::<T>(base, 4, 2 + c2 as usize);
            interior_pointer_limits::<T>(base, 4, 2 + (!c2 as usize));
        } else {
            assert c1 as usize == 1;
            assert (!c1) as usize == 0;
            assert c2 as usize == 0;
            assert (!c2) as usize == 1;
            interior_pointer_limits::<T>(base, 4, c1 as usize);
            interior_pointer_limits::<T>(base, 4, (!c1) as usize);
            interior_pointer_limits::<T>(base, 4, 2 + c2 as usize);
            interior_pointer_limits::<T>(base, 4, 2 + (!c2 as usize));
        }
    } else {
        if (c2) {
            assert c1 as usize == 0;
            assert (!c1) as usize == 1;
            assert c2 as usize == 1;
            assert (!c2) as usize == 0;
            interior_pointer_limits::<T>(base, 4, c1 as usize);
            interior_pointer_limits::<T>(base, 4, (!c1) as usize);
            interior_pointer_limits::<T>(base, 4, 2 + c2 as usize);
            interior_pointer_limits::<T>(base, 4, 2 + (!c2 as usize));
        } else {
            assert c1 as usize == 0;
            assert (!c1) as usize == 1;
            assert c2 as usize == 0;
            assert (!c2) as usize == 1;
            interior_pointer_limits::<T>(base, 4, c1 as usize);
            interior_pointer_limits::<T>(base, 4, (!c1) as usize);
            interior_pointer_limits::<T>(base, 4, 2 + c2 as usize);
            interior_pointer_limits::<T>(base, 4, 2 + (!c2 as usize));
        }
    }
}

lem split_selected_four<T>(base: *T, t: thread_id_t, c1: bool, c2: bool)
    req base[..4] |-> ?xs &*& foreach(xs, own::<T>(t));
    ens *(base + (c1 as usize)) |-> ?a_current &*&
            <T>.own(t, a_current) &*&
        *(base + ((!c1) as usize)) |-> ?b_current &*&
            <T>.own(t, b_current) &*&
        *(base + (2 + (c2 as usize))) |-> ?c_current &*&
            <T>.own(t, c_current) &*&
        *(base + (2 + ((!c2) as usize))) |-> ?d_current &*&
            <T>.own(t, d_current) &*&
        pointer_within_limits(base + (c1 as usize)) == true &*&
        pointer_within_limits(base + ((!c1) as usize)) == true &*&
        pointer_within_limits(base + (2 + (c2 as usize))) == true &*&
        pointer_within_limits(base + (2 + ((!c2) as usize))) == true;
{
    selected_four_limits::<T>(base, c1, c2);

    // Split the actual array/foreach permissions, then expose them at the
    // source expressions. The four cases above establish that each expression
    // normalizes to a distinct physical slot from this split.
    split_four_owned_cells::<T>(base, t);

    // Keep a second explicit case walk at the dynamic points-to boundary. This
    // makes the bool-cast normalization obligation local to this helper.
    if (c1) {
        if (c2) {
            assert c1 as usize == 1;
            assert (!c1) as usize == 0;
            assert c2 as usize == 1;
            assert (!c2) as usize == 0;
            points_to_limits(base + (c1 as usize));
            points_to_limits(base + ((!c1) as usize));
            points_to_limits(base + (2 + (c2 as usize)));
            points_to_limits(base + (2 + ((!c2) as usize)));
        } else {
            assert c1 as usize == 1;
            assert (!c1) as usize == 0;
            assert c2 as usize == 0;
            assert (!c2) as usize == 1;
            points_to_limits(base + (c1 as usize));
            points_to_limits(base + ((!c1) as usize));
            points_to_limits(base + (2 + (c2 as usize)));
            points_to_limits(base + (2 + ((!c2) as usize)));
        }
    } else {
        if (c2) {
            assert c1 as usize == 0;
            assert (!c1) as usize == 1;
            assert c2 as usize == 1;
            assert (!c2) as usize == 0;
            points_to_limits(base + (c1 as usize));
            points_to_limits(base + ((!c1) as usize));
            points_to_limits(base + (2 + (c2 as usize)));
            points_to_limits(base + (2 + ((!c2) as usize)));
        } else {
            assert c1 as usize == 0;
            assert (!c1) as usize == 1;
            assert c2 as usize == 0;
            assert (!c2) as usize == 1;
            points_to_limits(base + (c1 as usize));
            points_to_limits(base + ((!c1) as usize));
            points_to_limits(base + (2 + (c2 as usize)));
            points_to_limits(base + (2 + ((!c2) as usize)));
        }
    }
}

lem join_selected_four<T>(base: *T, t: thread_id_t, c1: bool, c2: bool)
    req *(base + (c1 as usize)) |-> ?a_current &*&
            <T>.own(t, a_current) &*&
        *(base + ((!c1) as usize)) |-> ?b_current &*&
            <T>.own(t, b_current) &*&
        *(base + (2 + (c2 as usize))) |-> ?c_current &*&
            <T>.own(t, c_current) &*&
        *(base + (2 + ((!c2) as usize))) |-> ?d_current &*&
            <T>.own(t, d_current);
    ens base[..4] |-> ?xs &*& foreach(xs, own::<T>(t));
{
    // These four cases restore the physical index order expected by the
    // existing join_four_owned_cells contract. Each delegated join consumes
    // the actual points-to and own resources in that case.
    if (c1) {
        if (c2) {
            assert c1 as usize == 1;
            assert (!c1) as usize == 0;
            assert c2 as usize == 1;
            assert (!c2) as usize == 0;
            join_four_owned_cells::<T>(base, t);
        } else {
            assert c1 as usize == 1;
            assert (!c1) as usize == 0;
            assert c2 as usize == 0;
            assert (!c2) as usize == 1;
            join_four_owned_cells::<T>(base, t);
        }
    } else {
        if (c2) {
            assert c1 as usize == 0;
            assert (!c1) as usize == 1;
            assert c2 as usize == 1;
            assert (!c2) as usize == 0;
            join_four_owned_cells::<T>(base, t);
        } else {
            assert c1 as usize == 0;
            assert (!c1) as usize == 1;
            assert c2 as usize == 0;
            assert (!c2) as usize == 1;
            join_four_owned_cells::<T>(base, t);
        }
    }
}
@*/
