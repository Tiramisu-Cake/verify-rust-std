#![feature(register_tool)]
#![register_tool(rr)]

fn g1_unregistered() {}

#[rr::verify]
pub fn g1_n1() {
    g1_unregistered();
}
