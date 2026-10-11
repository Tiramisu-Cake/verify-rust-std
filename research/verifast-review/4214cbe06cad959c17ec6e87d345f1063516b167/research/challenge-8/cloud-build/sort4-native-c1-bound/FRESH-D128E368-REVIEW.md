# Fresh native C4 bound candidate review

Build `d128e368-9a50-4c1a-8e74-64d71c51bfa0`, proof=infra
`aea868bfd3ac9519ae3a51112cd8af82d9b29171`; 466 Cloud seconds, cumulative
1631/3600. [Evidence index](FRESH-D128E368-INDEX.json). Collector reports
SUCCESS and complete delivery; verification is not accepted. Downloaded archive
SHA-256: `b0628ec500d606afbe059c50855601189298075b9a8a85ac45c0ee7b457fc663`.
The independently checked inventory contains 1041 entries.

All fresh ZST model gates and C1 prerequisites passed. The ZST model positives
and layout ZST/nonZST matrix reached VF0 with paired source/MIR/refinement;
its deliberate pre-guard, reachable-ZST-false, and missing-permission controls
failed at their intended assertions/resources. Native C1 positive binding and
its normal/unwind false controls passed their intended classifications; source,
extra-body, malformed, and mixed-environment controls refused as intended.
These remain experimental diagnostics without proof credit or an external
caller summary.

The C4 source pair is pinned and immutable: verified
`0f92a609c898df5271cbafd04cea688bf7b46c8b4786f8313b8ff99db995e9c4`, original
`9628df15e3a42643d671bd1e9f5684e0bdd81162e26ab8233ce704a9657942df`. Paired
normal/readonly full MIR and refinement passed for
`small_sort_general_with_scratch`; MIR hashes are
`b0da712d2b16c76d1baac91ae69c591ddeab308a2242e196fe876fd27e35e24d` and
`79c16a30be7b2921ccdaa35c66aac496f236d900130fff72a36b81524e50ef86`. The
pre-transform AST hash is
`65b9ddf282ab3b8d123bba3725600528936ff09e236c4261841d61f66cb5ae18`.

The C4 positive and all five intended false controls (normal plus four direct
unwinds) stopped before admission and post-transform AST at the same frontend
failure: `NATIVE-C4-BOUND: complete native AST/HRTB inventory`. They are
INCONCLUSIVE, not proof negatives. Source-hash, extra-body, malformed, and
mixed-environment controls reached their intended admission refusals. Default
off remained unadmitted but terminated with a parse error, not a semantic
negative.

The effective candidate tool retained HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb`,
kernel `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`,
translator `0f94a83db283d5373e82e2c11c1eb6fde1f0bef300d5bf67ecd40ad8339943b7`,
and verifast1 `bfbfb518fb9783afeeba9384e1431b6cd280c7da7713b9fdbfd15a8395b00207`;
the candidate console was rebuilt. No C4 proof credit, profile acceptance,
caller proof, or callable summary follows. Raw per-case logs and hashes are in
the downloaded archive under `allprooflogs/cases/sort4-c1-current-recovery/`.
