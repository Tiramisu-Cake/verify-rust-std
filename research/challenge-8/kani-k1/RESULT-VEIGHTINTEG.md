# VEIGHTINTEG — результат
Build `03d45e6a-0553-414e-83ea-6f6c9ce87778`: Cloud SUCCESS, COMPLETE, gate true, Kani exit 0.
Source `91aeee2c62c3fc1e665fa7a44a5787c8283e54ab`; owner k1-merge, diagnostic, standard4.
Request `veightinteg-g1-20261105-02`; inventory=true, controls=false, jobs=1, 10 мин/корень.
Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`; request hash и bindings сверены.
`fa6a1d3142dd7463ffe35ab51e24a54c7ad470e6`: контракты реальных helpers и PFC/consumers.
`f351bbc1c61fe7397006d713db7e0e7de9c3bfb5`: permtags N9/N13 и маршруты типов.
`aa2a7347511350ae4a855352595d4bdd12d5ff48`: scratchgeom u64 N2/scratch18.
`4b4803b126638b7ece733076ceb7361b653c98b9`: только covers; исходные версии оставлены opt-in.
Cfg-off inventory **219 = 204 + 15**, точный набор; cfg-on **253**, opt-in **34** (статика).
Names SHA256: `359bfc09eceb2a8f9fcbee6617f7e4313b3d4c9b2e10094d65b90c58a33f101b`.

| Корень verify:: | Статус | с | Failed/total | Covers |
| --- | --- | ---: | ---: | ---: |
| permtags::network_u8_n13 | SUCCESS | 24.318867 | 0/559 | 1/1 |
| permtags::network_u8_n9 | SUCCESS | 14.063343 | 0/559 | 1/1 |
| permtags::tag_types_preserve_source_routes | SUCCESS | 0.060445 | 0/14 | 1/1 |
| realcontracts::insert_tail_safety_u64_tail1_to4_backing5 | SUCCESS | 38.1495 | 0/219 | 7/7 |
| realcontracts::merge_safety_u64_len2 | SUCCESS | 31.429583 | 0/284 | 4/4 |
| realcontracts::merge_safety_u64_len4 | SUCCESS | 45.406685 | 0/284 | 4/4 |
| realcontracts::sort4_safety_u64 | SUCCESS | 35.744152 | 0/293 | 3/3 |
| realcontracts::swap_safety_bytes17_backing4 | SUCCESS | 33.57819 | 0/402 | 6/6 |
| realcontracts::swap_safety_u64_backing4 | SUCCESS | 20.581472 | 0/229 | 6/6 |
| realcontracts::swap_safety_u8_backing13 | SUCCESS | 19.395584 | 0/219 | 6/6 |
| realcontracts::swap_safety_u8_backing4 | SUCCESS | 19.17471 | 0/229 | 6/6 |
| realcontracts::swap_safety_u8_backing9 | SUCCESS | 18.622524 | 0/219 | 6/6 |
| realcontracts::unstable_network_safety_u8_n13_stubbed | SUCCESS | 18.837992 | 0/387 | 1/1 |
| realcontracts::unstable_network_safety_u8_n9_stubbed | SUCCESS | 8.316227 | 0/387 | 1/1 |
| scratchgeom::stable_u64_min_scratch_n2 | SUCCESS | 5.838726 | 0/423 | 2/2 |

Строки verify: **3872 = 3453 ordinary/shared + 419 opt-in**; smallsort.rs **964 (+98)**.
CI: **333.518 с** фактически, 312.029 с по источникам; max 45.407 с; verify wall 7:48.51.
Статика/rustfmt/diff-check: PASS; тела 204+8 сохранены; tooling/pool/SHA PASS.
Covers **55/55**; unreachable из summary — прочие checks, не covers. Opt-in копии сохранены.
Диагностика только 15 новых корней; прежние 204 и 34 opt-in не перепроверялись.
Домены PFC/consumers совпали; tag-transfer условный; unwinding/uninit/validity не доказаны.
Verify/unused warning scan: no match; общий warning scan — ограниченная выборка.
Одна сборка, repairs 0; расход **$0.6480 / $3.00**, резерв $0; max RSS 1897304 KiB.
Владельцу решить: включать ли runtime-контракты и 15 новых ordinary-корней.
Evidence: [отчёт](veightinteg/evidence/verification-report.json), bounded-данные рядом.
