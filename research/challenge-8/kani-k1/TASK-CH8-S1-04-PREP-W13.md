# TASK — worker13: запускаемый пакет S1-04 (подготовка; dispatch только после GO владельца)

Это верификация корректности, не security-работа. Отвечай кратко.

Основание: твой intake S1-03 (g0 `f6c8c7cb36`, `kani3300/ch8-s1/run-43784240498/`: RESULT, COST, S1-04 proposal,
runner-fix.patch). Владелец утром решает о бюджете/окне S1; к этому моменту пакет должен быть готов к запуску.

1. Source experiment из COST.md п.3: на S′ разделить symbolic N тяжёлых строк на точные N=0/1/2/3 с теми же
   arbitrary bytes/KeyLess, exact target/PFC, scratch geometry/canaries/post; исходная строка принимается только по
   union всех четырёх cases; covers распределить. Только verification-код (`verify/`), runtime smallsort не менять.
   Новый std commit на S′ (`f22f84f316`), локально, [skip ci].
2. Runner: fix `source_identity_drift` (porcelain whitespace, source_before до overlay), исправленные oracles negatives
   по property ID/location, порядок групп: light/model/corruption/companions → activation → Cell → тяжёлые
   (каждая тяжёлая N-строка отдельной группой или малыми группами — обоснуй против compile-overhead ~30 s/группа).
3. Envelope: реалистичная оценка (из S1-03 измерений) и варианты: один job vs matrix по группам (max-parallel 1 или 2),
   чтобы всё уложилось; укажи, сколько dispatch это займёт.
4. Synthetic tests, review. g0 `kani3300/ch8-s1/s1-04/`: CI-REQUEST, REVIEW, ENVELOPE.md, HANDOFF.
   Последней строкой `READY <std> <control> <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
