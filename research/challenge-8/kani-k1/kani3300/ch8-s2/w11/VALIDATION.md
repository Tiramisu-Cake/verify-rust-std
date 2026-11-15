# Validation

- PASS: Git scope — ровно три новых verify/sorting_leaf*.rs относительно S1;
  smallsort.rs/verify.rs/S1 models и все существующие проверки не изменены.
- PASS: git diff --check исходного кандидата и research.
- PASS_SYNTHETIC_ONLY: check_package.py — 65 536 byte-pair fixtures, 512 binary
  fixtures sort9 и8 192 sort13 из текстуально извлечённых actual edges;
  distinct order/count/input corruption fixtures и34 same-allocation merge8 offsets.
  Это Python tests и source sanity, не Rust/Kani actual-body/contract proof,
  не MIR binding и не эмпирическая цена будущего CI.
- source candidate: 24e12a1e98d9dd8de4f272f3d4a6fb489ade5894; tree f67001e9fd160f052318bc3391fa0187d67e715e.
- patch leaf-source.patch sha256: f8443763660640258b3d5af790b65e22ba6ba351d4dccfd0a6b07e39cb43344b.
- P1/compiler/core manual Fn ABI/actual attrs/selected Replace/PFC/control property IDs:
  NOT_RUN; formal proof credit NONE. Никакие локальные Rust инструменты/CI не запускались.

Независимое static review exact candidate/spec/dependencies — REVIEW.json.
Никаких old verdict/ledgers/download_verified не изменено, builds/dispatch/push нет.
