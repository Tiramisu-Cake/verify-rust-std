# Шесть SmallSort rows — все NOT_RUN

Префикс selectors: `slice::sort::shared::smallsort::verify::`; полные exact argv в CI-REQUEST.json.

| ID / selector suffix | Geometry / unwind | Приёмка |
| --- | --- | --- |
| merge-raw-closure-on / helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0 | u64 len8; MU scratch48, src[32..40], dst[0..8];34 | SUCCESS,0 failures,5/5 covers, frame/readbacks |
| merge-profile-closure-on / replay_gateb_prime::merge_profile_closure_scratch48_u8_n9 | u8 N9 scratch48, обе подложки;34 | SUCCESS,0 failures,2/2 covers, ensures reached |
| sort4-closure-on / helper_contracts::sort4_safety_u64 | Check(sort4_stable), src4/dst4;16 | SUCCESS,0 failures,3/3 covers (comparator true/false и return) |
| swap-if-less-closure-on / helper_contracts::swap_safety_u64_backing4 | Check(swap_if_less), backing4;8 | SUCCESS,0 failures,6/6 covers (comparator true/false, a==b/a<b/a>b, return), frame/readback |
| raw-legal-on / replay_uninit_controls::sort4_raw_all_initialized_u64 | ordinary sort4 src4/dst4;16 | SUCCESS,0 failures,2/2 covers entered/returned |
| raw-negative-on / replay_uninit_controls::sort4_raw_hole_negative_u64 | та же geometry; только source[1] unwritten;16 | ровно один задуманный uninit-read source[1], никаких иных failures |

Negative reference: `sort4_stable::<u64,…read_less_u64>.safety_check.1`,
“Reading from an uninitialized pointer of type `*const u64`”, smallsort.rs:751:26.
Property/name/location binding надо подтвердить на source operation после freeze; drift только после review.
Requires/layout/frame/comparator/select Unsupported не заменяют intended negative.
Сохранять полный failed inventory, полезные SUCCESS/ensures/covers и unreachable. Unreachable return запрещает legal PASS.

Статически перепроверено на std70ba: smallsort.rs:751 содержит
`let c1 = is_less(&*v_base.add(1), &*v_base);` — чтение source[1] соответствует исходному oracle.
Exact test-only patch6075 и пять patched-file hashes не изменились. Generated property/name/trace остаются UNKNOWN до CI;
эта source-coordinate проверка не устанавливает связь с новым generated artifact.

Сравнение с C2 B′43683557088: merge572/1030 (0 failures), sort4 — одна select boundary760 и return UNREACHABLE.
После SEL1 обе merge должны сохранить obligations; sort4 должен стать SUCCESS с reached return.
SEL1 replay43611601987 — ориентиры: sort4 0/753, swap0/585, raw legal0/382, raw negative1/382,
merge0/572 и0/1030. Эти totals не golden: объяснить additions/removals/status/reachability, исключить lost safety obligations.
Concrete profile companion не доказывает generic merge_profile<P>. Bounded helper evidence, не всё SmallSort/T,N/#5104.
