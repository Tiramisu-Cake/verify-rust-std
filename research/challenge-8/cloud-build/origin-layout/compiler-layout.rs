// Cloud-only compiler/target fact observation, not a VeriFast proof.
use std::mem::{align_of, size_of, ManuallyDrop};

fn layout<T>() -> [usize; 2] { [size_of::<T>(), align_of::<T>()] }

fn main() {
    let unit = layout::<()>();
    let md_unit = layout::<ManuallyDrop<()>>();
    let scalar = layout::<u64>();
    let md_scalar = layout::<ManuallyDrop<u64>>();
    let units = [(), ()];
    let scalars = [0u64, 0u64];
    let unit_stride = (&units[1] as *const () as usize).wrapping_sub(&units[0] as *const () as usize);
    let scalar_stride = (&scalars[1] as *const u64 as usize).wrapping_sub(&scalars[0] as *const u64 as usize);
    assert_eq!(unit, [0, 1]);
    assert_eq!(md_unit, [0, 1]);
    assert_eq!(scalar, [8, 8]);
    assert_eq!(md_scalar, [8, 8]);
    assert_eq!(unit_stride, 0);
    assert_eq!(scalar_stride, 8);
    println!("{{\"unit\":{:?},\"manually_drop_unit\":{:?},\"u64\":{:?},\"manually_drop_u64\":{:?},\"unit_array_stride\":{},\"u64_array_stride\":{},\"classification\":\"COMPILER_FACT_DIAGNOSTIC_NOT_PROOF\"}}", unit, md_unit, scalar, md_scalar, unit_stride, scalar_stride);
}
