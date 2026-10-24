//! Kani K-1 experiment harnesses (research/challenge-8/kani-k1/EXPERIMENT.md).
//!
//! File ownership: `merge.rs` belongs to the K1-merge agent, `network.rs` to the K1-network agent,
//! `smoke.rs` to the coordinator. An agent edits only its own file here and the contract attributes
//! of the functions assigned to it in `smallsort.rs`.

mod merge;
mod network;
mod smoke;
