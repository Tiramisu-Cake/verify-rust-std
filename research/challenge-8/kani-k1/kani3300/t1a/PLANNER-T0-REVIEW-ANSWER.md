Рекомендую T1a: сначала один A без trace и без нового tooling. Полный T1 сейчас избыточен относительно ещё не подтверждённого воспроизведения.
1. Существенная экономия: library tree 2121ff2d08 и уже выполненного CMP4-B head c8967c5a44e8f95b19f31761e55313d8488faea5 одинаков — 919cc3e2dc5fb19ea6e7f7be761914b949160a41.
   Diff между ними только в research-файлах. Сверить также production patch/applied tree, pin, toolchain, tooling и recipe/flags; при совпадении старый B использовать как source-reported baseline.
   Новый A: исходные 9 roots на этой library, неизменные CMP2/KT2/checks/таймауты, без diagnostic delta, --emit/--trace/--no-slice-formula и новых env.
   Резерв $0.7695, cap $0.80, одна попытка. Повторять B автоматически незачем; если его inputs нельзя надёжно сопоставить, тогда отдельный B: резерв $0.567, общий cap A+B $1.40.
2. A FAIL / сопоставимый B SUCCESS даст same-library contrast, но ещё не механизм и не доказательство детерминированной зависимости только от root set.
   A SUCCESS означает невоспроизведение исходного отказа в этом пакете: не писать constant-seed fix и не начинать дорогой runtime collector вслепую.
   Следующим объектом локализации тогда выбрать исходный failing CMP3 либо воспроизводимый native IntoIter fixture; не объявлять старый blocker исправленным.
   Сломанные controls/identities, Unsupported или timeout — отдельные результаты, не нужный contrast. Actual codegen order из порядка selectors не выводить.
3. Если contrast получен, T1b сузить до compile-time диагностики: unit/stubs/actual root order, cache hit/miss, creator/last writer и body/stage hashes,
   target-origin/relevance witnesses, выбранные и пропущенные MemoryInitOps и небольшой before/after MIR для step1/step4/IndexRange::len. Не запускать transformer повторно ради записи.
   Cache provenance сохранить: один transformer/cache действительно используется несколькими roots unit, а delayed-UB может обновлять cached body; причинность пока UNKNOWN.
   В первой итерации убрать CBMC runtime projection, op→CBMC symbol/object mapping и все изменения slicing/trace flags. Это существенно уменьшит код и риск изменения эксперимента.
   Цена сокращения честная: конкретные object+offset/R/Get и окончательная причина пропущенной инициализации останутся UNKNOWN, если их нельзя установить этим этапом.
4. --emit=mir/*.kani.mir полезны как подтверждение финального transformed MIR, но не заменяют cache/relevance provenance; points-to.dot перезаписывается между roots.
   Поэтому не выбирал бы большой dump-reader как первый шаг. Если понадобится, только filtered bounded extraction с root/stage binding, не чтение полных debug dumps/raw logs.
   Для T1b достаточно небольшого reviewed sidecar/summary reader; generic trace-field API и runtime parser можно отложить. Сохранить service/error-path tests, caps/omissions и исходные verdict/exits.
5. tmux 15 — готовить T1a сейчас, параллельно G1 в tmux 14. Общую инфраструктуру trace не реализовывать до результата A.
   T1b — отдельный уточнённый пакет после результата и review, с новым расчётом ledger; cap T1a не разрешает автоматически последующие trace Builds.
   Brief HTTP404/неполные bindings по-прежнему раскрывать; новый запуск без trace сам по себе не создаёт независимый proof credit.
