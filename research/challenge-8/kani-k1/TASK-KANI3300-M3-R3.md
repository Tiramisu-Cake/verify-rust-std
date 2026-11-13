# KANI3300 M3-R3 — откат nested-aggregate guard, поддержанный M3 companion (ISSUED 2026-11-13 → worker14)

Это верификация корректности, не security-работа. Локально только Python/static и scratchpad rustfmt; без cargo/Kani/CBMC; push/CI — координатор.

## Решение (координатор + планер)
Guard M3-R2 (30655f306, a221d00cf, 88c532d6c) слишком широкий: quick 43494738738 expected 202/16 — B1 unresolved-calls диагностика
заменена, новые boundary-тесты ловят существующий 'union as a field', ordinary-and-pointers-legal ложные FAIL, Cell<MU> → aggregate Unsupported.
Откатываем guard целиком. Лог: /root/kani3300-h1-ci/m3-r2.log.

## Стадия
1. Новый clone `/root/kani-fix-3300-m3r3` из /root/kani-fix-3300-m3, ветка `fix/kani-3300-m3r3` от **aac27ed95** (не от 88c532d6c).
2. M3 companion в поддержанной форме: top-level MU return, Move, repair, проверки returned=42/source=23 и negative без reinit.
3. Tuple-return сохранить отдельным тестом как **known false positive**: точный текущий отказ (golden из r1 лога m3-r1.log, harness
   move_return_reinit_legal: `std::mem::transmute_neo::<MaybeUninit<u8>, u8>.safety_check.1`, 'Reading from an uninitialized pointer of type `u8`'),
   комментарий «семантически должен быть SUCCESS; nested aggregate shadow transfer не реализован»; не засчитывать как обнаружение UB.
4. Документировать в docs/src/reference/experimental (там же, где граница Replace/Recursive) отсутствие shadow transfer для by-value агрегатов
   с вложенными MU/union-слотами. Не утверждать, что такие пути всегда fail-closed.
5. ordinary-and-pointers-legal из M3-R2 в стадию не переносить, если без guard он не нужен; если переносишь — ожидание только по реальному поведению
   на aac27ed95 (пока NOT_RUN — пометь как требующий CI).
6. B1 (unresolved-calls) и closure-zst goldens не трогать.
Research — только в g0 `kani3300/m3-final/`, не в docs/dev Kani. Коммиты автор Tiramisu-Cake <igkharin@gmail.com> через -c. Финал `READY <source-sha>`.
