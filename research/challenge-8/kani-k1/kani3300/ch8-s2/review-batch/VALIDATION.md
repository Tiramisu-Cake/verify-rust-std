PASS_STATIC_SYNTHETIC_ONLY. Detailed commands, exact inputs and results are in
VALIDATION.json; independently generated receipts are package-validation.json
and independent-checks.json. All43 service/error/selection tests passed in5.764s.
Pilot diagnostics passed with30 source anchors,598 small-alphabet inputs,
1869 paired transitions and372 CAP32 fixtures; these are diagnostic counts only.

Source/control patches replay to the exact trees. Shallow7/4/2, typed YAML,
bounded payload, source hashes and manifest pass. Independent checks also compare
all18 batch and7 pilot files to their committed blobs, verify45 network pairs,
unchanged runtime bytes after8 attrs,11 exact roots and RSS sampler partitioning.

No cargo/rustc/Kani/CBMC/rustfmt/full runner, CI, push, reservation or ledger write.
Actual compilation, PFC, consumers, witnesses, covers, negative controls and cost
results are NOT_RUN. B1/B2 and independently established proof credit NONE.
