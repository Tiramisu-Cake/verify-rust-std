use rapx_applicability::zst::Z;

fn main() {
    println!(
        "target={} zst.size={} zst.align={} u64.size={} u64.align={}",
        std::env::consts::ARCH,
        core::mem::size_of::<Z>(),
        core::mem::align_of::<Z>(),
        core::mem::size_of::<u64>(),
        core::mem::align_of::<u64>(),
    );
}
