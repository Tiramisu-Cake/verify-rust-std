// Generated native-contract controls for slice as_mut_ptr pointer projection.
use core::mem::MaybeUninit;

fn slice_projection<T>(v: &mut [T]) {
    let p = v.as_mut_ptr(); // CONTROL_PROJECTION_CALL
    //@ assert p == strip_pointer_metadata(v as pointer) as *T; // CONTROL_TARGET_ASSERT
}

fn maybe_uninit_projection<T>(v: &mut [MaybeUninit<T>]) {
    let p = v.as_mut_ptr(); // CONTROL_PROJECTION_CALL
    //@ assert p == strip_pointer_metadata(v as pointer) as *std::mem::MaybeUninit<T>; // CONTROL_TARGET_ASSERT
}

fn wrong_pointer_projection<T>(v: &mut [T]) {
    if 0 < core::mem::size_of::<T>() {
        let p = v.as_mut_ptr(); // CONTROL_PROJECTION_CALL
        //@ assert p == (strip_pointer_metadata(v as pointer) as *T) + 1; // CONTROL_TARGET_ASSERT
    }
}

fn unrelated_raw_destination<T>(v: &mut [T], rawdst: *mut T) {
    let _p = v.as_mut_ptr(); // CONTROL_PROJECTION_CALL
    //@ assert *rawdst |-> ?x; // CONTROL_TARGET_ASSERT
}
