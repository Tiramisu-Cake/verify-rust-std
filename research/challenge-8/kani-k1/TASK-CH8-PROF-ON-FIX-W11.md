# TASK — worker11: обходы A/B/C в profiles source + пакет PROF-ON-02 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: твой анализ [gaps/ANALYSIS.md](kani3300/ch8-profiles/on-ci/gaps/ANALYSIS.md) (g0 b3b88d659a) — принят координатором.
Source profiles `9fa2f7f977` (P′), твоя work-ветка профилей.

1. Реализовать поверх `9fa2f7f977` (новый коммит, без force):
   A — array literal вместо from_fn/.map/kani::any для массивов (все затронутые места, не только 3 из наброска —
   найди все пути к array_assume_init в 62 строках по stdout artifact);
   B — sort4: четыре thin modifies targets; merge len4: отдельный merge4_profile + его proof_for_contract,
   consumer stub_verified(merge4_profile); общий merge 2..=32 не трогать;
   C — общий closure factory для comparator во всех matching leaf/consumer.
   Каждая новая/изменённая строка: oracle, binding (accept-v4), covers. Domain не сужать.
2. Посмотреть w0-a1/polyiter/ANALYSIS.md: есть ли такой же harness-only обход PolymorphicIter для
   freeze_noncopy_n2 и rejects_always_true; если да и он не ослабляет — включить, иначе оставить BLOCKED_TOOL.
3. CI-пакет PROF-ON-02 на kani-хосте: обе ветви в одном dispatch, если возможно — OFF на 0aac16ef62
   (регрессия принятых 62 + новые строки) и ON на SEL1 14bc57fdb9; batch runner, те же caps. Если одним
   dispatch нельзя — обоснуй, ON первым. Review (независимый), synthetic tests на изменённые пути.
4. g0 kani3300/ch8-profiles/on-ci/fix/: SOURCE (sha/tree), CI-REQUEST, REVIEW, HANDOFF. Коммиты [skip ci],
   author Tiramisu-Cake <igkharin@gmail.com>. Перечисли, какие ветки координатор пушит.
   Последней строкой READY <source> <control> <g0> или STOP <причина>.

Код компилятора не писать (WIP 0). Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
Не пересекайся с worker15: он делает intake run 43798838603 в .../run-43798838603/accept/.
