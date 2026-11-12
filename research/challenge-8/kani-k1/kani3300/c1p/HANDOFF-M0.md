# C1-P → M0: requirements, NOT_RUN

Source read-only: `6134e42dd1c65dc980336e7d9455aba02d423edf`; production как `dc5f5a406749a73f1c3192e0b5338441e79508bb`.
Решение B: flat scratch сохраняется; полный raw_eq model обязателен. Это подготовка, не gate PASS.
1. Сначала D0-A: actual MIR/Instance/AllocId, оба operands → runtime object/offset/extent → witness → last setter/transfer.
2. M0 обязан отличать proved initialized, modeled false и unknown; неизвестное не превращать в true.
3. Immutable anonymous/promoted masks брать из referent Some/None bytes; учесть relocations, coalescing, offsets и runtime choice.
4. Не заключать по имени temporary, что setter отсутствует; подтвердить полный relevant trace и normal destination.
5. Normal-return ordinary T: только доказанная D(T); shadow return: реальная передача false и padding mask, без blanket bless.
6. Unwind/abort не получает normal-return setters/return0 consumption; ABI и реальный CFG должны быть установлены.
7. Raw whole-array copy сохраняет полный byte extent; typed transfer сохраняет D(T), unwritten data остаётся false.
8. Затем M1 → M2 → M3 одним model owner; C1 test activation только после M0 design gate по отдельному заданию.
9. Первая C1 очередь: 6 promoted drafts (direct/helper × legal/left-hole/right-hole), 3 whole-array-copy drafts.
10. Все 9 drafts — research-only, NOT_RUN; не объявлять compile-ready. Проверить retained raw_eq и copy::<[MU<u8>;3]>.
11. CONTROL-MATRIX.json: 25 obligations, 62 pinned/draft/spec inputs; existing bodies не скопированы, SHA-256 зафиксированы.
12. Использовать существующие left/right/padding, typed data/padding, Item-return, reset/overlap и frame/clause negatives.
13. Позже добавить specs dynamic choice/coalescing/offset/subrange и legal PFC/modifies; у каждой пары legal scalar observable и отдельный negative.
14. COMPILER-CONTROLS.md: genuine FnDef Err, bodyless kinds, Shim arg-only/return-only, by-value DST, union constant, intercepted return.
15. Недоступная legal MIR форма остаётся UNKNOWN; source FnOnce/FnPtr/tuple/Item не доказывает Shim. Framework здесь не создавать.
16. Идентичные singleton/AB/BA roots требуют actual specialization/cache/property binding; order-dependent cause пока UNKNOWN.
17. Empty/ZST не заменяет nonempty negative; сохранить counters/return0 pairing даже при extent=0.
18. При targeted CI требовать named JSON properties/reachability, не общий FAILED; ранний UB/Unsupported не закрывает byte-read negative.
19. Quick 43199156872 — только aggregate coordinator claim: known raw_eq legal FAIL; whole-Quick PASS и ABI coverage не установлены.
20. Source/model/guards/workflows не изменены; Cloud $0, никаких локальных compiler/verifier/build запусков.
21. STOP C1-P. M0/model/guards, C1 implementation и CI не начинать без следующего задания координатора.
