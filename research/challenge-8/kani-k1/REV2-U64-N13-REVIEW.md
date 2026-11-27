# REV2 u64 N13 · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **NO-GO.** Пины: Std `79030c96c86f6bae0ef3498e3323a5ba919925c0`, Control `027f81e0712d` / tree `794c9c5bb687`, review-trigger `87888742f89b`, handoff g0 `4c8b2e5441`.

1. **Blocker.** `rev2_u64_n13.rs:74`: `v[14..] == before[14..]` на `[u64]` идёт через `BytewiseEq` → `compare_bytes` (`slice/cmp.rs:146`) → `BuiltinFn::Memcmp` на пине `9834c96`. Побайтовый цикл на 160 байт при `#[kani::unwind(36)]` даёт FAILURE unwinding assertion в обоих S13 корнях; у CORRUPT появляется второй отказ. Тот же риск отмечен в `verify/network.rs:120`. Исправление: поэлементный frame (как в swap-корне), затем пересчёт якорей, bindings, roster, bundle, request, Control и trigger.
2. Nit. `test_results.py`, фикстура `U64_N13_ROWS`: `ptr::copy::<u64>` на `ptr/mod.rs:672:13`, в исходнике и handoff — `682:9`. Выровнять.

Проверено и в порядке: реальные тела в plain Proof; индексы листа 78 пар; covers; 8192 маски без усечения; ожидаемая маска и контроль `0x0001 → 0x1000 → 0x1001`; `u64_less` = `strict_less`; 45 пар `smallsort.rs:612–656`; маршрут N13 и пороговый аргумент; Std-дельта 3 файла; SHA-256 request `ac3d0a81…`, roster `4d174160…`, bindings `208f5b04…`, bundle `dc662c54…`; trigger tree/parent; авторы; Actions variable; часы; suite 124/124.
