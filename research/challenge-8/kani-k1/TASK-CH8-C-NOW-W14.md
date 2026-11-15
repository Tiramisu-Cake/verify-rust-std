# TASK — worker14: C-сейчас, статический frame/shared-span inventory (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

## Контекст

План пункта 1 v2, §9 «C-сейчас» ([PLAN-CH8-ITEM1-REMAINING-v2.md](PLAN-CH8-ITEM1-REMAINING-v2.md)).
Собственную alias-модель не делаем; #5040/RFC 0016 — upstream-дорожка. Твой B census (B-01) уже
запущен координатором на kani-форке (run 43774504122); его intake — следующая отдельная стадия.

## Что сделать (только статика, без compiler changes и без CI)

Источник: production std `872d5a43380752786415bc00d2a12ce0e930cb37` (S1 head
`75a4d1ea6eb60c63c27c1b18e662740d93bafb08` для новых contracts), read-only worktree.

1. Инвентарь всех shared spans SmallSort: merge source/dst, callback inputs (`is_less` `&T`),
   local ManuallyDrop/scratch, gap guards. Для каждого edge: real body или stub/summary, заявленный
   frame (modifies), disjointness requires, captured/global effects, использования после вызова.
2. Таблица proven / gap: какие write-confinement утверждения уже следуют из доказанных modifies +
   disjoint requires (с точными root/harness именами и SHA), какие нет. Отдельно три trait entries
   и pin с #4908/#5116 (что есть на 0aac, что нет).
3. Спроектировать (не запускать) два негативных контроля и legal companions из §9:
   write-then-restore в merge source вне dst frame; transient write за callback `&T` внутри outer v
   frame; legal disjoint external callback state/UnsafeCell; local-temp/ref lifetime reuse.
   Для каждого: ожидаемый исход, oracle, что значит неожиданный PASS (documented alias gap).
4. Черновик точной формулировки Limitations #752 о том, какие write sets/disjointness доказаны
   (без «all immutable mutations checked»).
5. STOP C по §9 — записать, если сработал.

Выход: g0 `kani3300/ch8-c-now/` (INVENTORY.md, CONTROLS-DESIGN.md, LIMITATIONS-DRAFT.md, HANDOFF.md),
коммит `[skip ci]`, author `Tiramisu-Cake <igkharin@gmail.com>` в команде. Последней строкой:
`READY <g0-sha>` или `STOP <причина>`.

## Ограничения

Без push/CI/публикаций/ledger, без правок smallsort.rs (это область 13). Без локальных
cargo/rustc/Kani/CBMC. Raw logs не читать.
