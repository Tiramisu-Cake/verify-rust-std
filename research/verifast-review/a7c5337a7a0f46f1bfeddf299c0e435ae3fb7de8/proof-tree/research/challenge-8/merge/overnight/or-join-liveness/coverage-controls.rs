// CALIBRATION ONLY. No EXPECT_DEAD oracle is registered until a Cloud run
// establishes exact stage, predecessor and dead-code location for each case.
// These functions do not match the bidirectional_merge origin gate; they
// check that unrelated real statements and source break/continue stay visible.

// CASE_BEGIN dead_real_return
pub unsafe fn dead_real_return(flag: bool) -> i32
/*@ req flag == false; @*/
/*@ ens result == 7; @*/
/*@ on_unwind_ens false; @*/
{
    if flag {
        return 8; // TARGET: unreachable real return must remain dead
    }
    7
}
// CASE_END dead_real_return

// CASE_BEGIN dead_panic_body
pub unsafe fn dead_panic_body(flag: bool) -> i32
/*@ req flag == false; @*/
/*@ ens result == 7; @*/
/*@ on_unwind_ens false; @*/
{
    if flag {
        panic!("dead panic control"); // TARGET: unreachable real panic body
    }
    7
}
// CASE_END dead_panic_body

// CASE_BEGIN dead_source_break
pub unsafe fn dead_source_break(flag: bool) -> i32
/*@ req flag == false; @*/
/*@ ens result == 7; @*/
/*@ on_unwind_ens false; @*/
{
    loop {
        /*@ inv flag == false; @*/
        if flag {
            break; // TARGET: source break lowered to Goto remains covered
        }
        break;
    }
    7
}
// CASE_END dead_source_break

// CASE_BEGIN dead_source_continue
pub unsafe fn dead_source_continue(flag: bool) -> i32
/*@ req flag == false; @*/
/*@ ens result == 7; @*/
/*@ on_unwind_ens false; @*/
{
    loop {
        /*@ inv flag == false; @*/
        if flag {
            continue; // TARGET: source continue lowered to Goto remains covered
        }
        break;
    }
    7
}
// CASE_END dead_source_continue
