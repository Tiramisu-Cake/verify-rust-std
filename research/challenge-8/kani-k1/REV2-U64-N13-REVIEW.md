# REV2 u64 N13 · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **NO-GO.** Пины: Std `79030c96c86f6bae0ef3498e3323a5ba919925c0`, Control `027f81e0712d` / tree `794c9c5bb687`, review-trigger `87888742f89b`, handoff g0 `4c8b2e5441`.

1. **Blocker.** `rev2_u64_n13.rs:74`: `v[14..] == before[14..]` на `[u64]` идёт через `BytewiseEq` → `compare_bytes` (`slice/cmp.rs:146`) → `BuiltinFn::Memcmp` на пине `9834c96`. Побайтовый цикл на 160 байт при `#[kani::unwind(36)]` даёт FAILURE unwinding assertion в обоих S13 корнях; у CORRUPT появляется второй отказ. Тот же риск отмечен в `verify/network.rs:120`. Исправление: поэлементный frame (как в swap-корне), затем пересчёт якорей, bindings, roster, bundle, request, Control и trigger.
2. Nit. `test_results.py`, фикстура `U64_N13_ROWS`: `ptr::copy::<u64>` на `ptr/mod.rs:672:13`, в исходнике и handoff — `682:9`. Выровнять.

Проверено и в порядке: реальные тела в plain Proof; индексы листа 78 пар; covers; 8192 маски без усечения; ожидаемая маска и контроль `0x0001 → 0x1000 → 0x1001`; `u64_less` = `strict_less`; 45 пар `smallsort.rs:612–656`; маршрут N13 и пороговый аргумент; Std-дельта 3 файла; SHA-256 request `ac3d0a81…`, roster `4d174160…`, bindings `208f5b04…`, bundle `dc662c54…`; trigger tree/parent; авторы; Actions variable; часы; suite 124/124.

## R2 · FIX1

Независимое повторное ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO**, замечаний нет. Пины: Std `4d6dd509956dff820a596ff1af9c0aae347aca26` / tree `b0dc6d6286`, Control `ed62c6a5c94bc2b676d2b9cdb698fcbc7dc3ad79` / tree `71b1cbd433b47a9ccc6a26ef33aa1f8e2c6c9a7b`, review-trigger `b0c84653de`, request `2200182a…baeb`, bundle `1e3fff44…b3da`, handoff g0 `10aafc6341`.

- Blocker R1 устранён: frame из 21 скалярного сравнения; в модуле нет сравнений срезов/массивов, самый длинный цикл 34 итерации; `count_ones` → `ctpop` без цикла; `any::<[u64; 34]>` без цикла.
- Дельта от R1: Std +6/−1 только frame; Control — request (overlay, bundle, дайджесты, сдвиг строк), фикстура (nit R1), selectors/исходы/covers/лимиты прежние.
- SHA-256, roster `7aae46a6…`, bindings `44cb323b…`, 338 якорей, bundle (prerequisite `dab03cf510`, HEAD `4d6dd50995`), авторы и сообщения сверены. Suite 124/124.
- Оговорка: перед запуском `CH8_REV2_U64_N13_TRIGGER_TREE` → `71b1cbd433b47a9ccc6a26ef33aa1f8e2c6c9a7b`.
