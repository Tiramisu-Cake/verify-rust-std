# S1-03 cost

R8 ≤600 s/root **не установлен**: 4 TIMEOUT, а ~327 s Cell — только exported verification time, не full instrumentation wall. Group RSS нельзя присвоить root.

| Group | Roots | Group wall s | Sum exported VT s | Compile boundary upper s | Sampled group peak KiB |
|---|---:|---:|---:|---:|---:|
| production-u34 | 15 | 3183.94 | 3100.759 | 32.706 | 8194328 |
| production-u4 | 3 | 26.41 | 0.311 | 25.879 | 1933140 |
| production-u5 | 3 | 36.088 | 5.654 | 27.005 | 2693768 |

Production-u34: четыре stock600s timeout дают ~2400 s; две Cell — ~653.35 s. Вместе это ~3053.4 s, ≈95.9% group invocation wall3183.94 s. Это установленное доминирование *строк*, а не SAT solving стадии. Модели по1.84–1.94 s, legal activation6.37/35.37 s, snapshot5.42 s, остальные <0.2 s. Fixed inputs у legal activation отличаются от symbolic smoke; их времена не измеряют отдельно цену ensures.

Что export НЕ сообщает: variables/clauses, GOTO/SSA размер, symex/solver/preprocess split, per-property costs, root process-tree RSS, full per-root wall. Число свойств не размер формулы. Размер JSON export также не размер формулы. Для timeout checks=null; нельзя приписать им число checks от успешного companion. Поэтому утверждение «доминирует конкретно snapshot/PFC/SAT» было бы неподтверждённым.

Статическая причинная гипотеза (не profiler conclusion), exact source f22f84f:

- Cell default (`smallsort.rs:31-50`, `90-107`) вызывает insertion. Freeze stable/general (`54-71`, `128-151`, `241-313`) добавляет отдельный scratch, symbolic prefix `n+16`, raw pointers, копирование половин, insert_tail, bidirectional_merge/CopyOnDrop. При N<=3 ветки sort4/8 не исполняются, но general memory CFG остаётся.
- Copy u8 (`160-185`, `332-392`) выбирает network implementation, однако N<9 не выполняет сети9/13: region insertion и early return `no_merge`; stack MaybeUninit<[T;32]> и pointer setup присутствуют в source, их остаток после оптимизации не измерен. Нельзя объявлять причиной исполняемую 9/13 сеть.
- KeyLess — закрытый stateless `value()<value()` (`sorting_model.rs:21-62`), общий всем трём exact типам. Snapshot — owned `[u8;32]`, loop только до фактической длины (`65-89`). Post — order loop + вложенный multiset count O(N²) (`91-120`), общая модель для Cell/u8/NonCopy. На N<=3 семантически до9 count пар; это не означает, что symex сразу исключил остальные unwind-итерации.
- PFC smoke (`sorting_entry_smoke.rs:32-95`) содержит old(snapshot) в actual ensures плюс независимый caller post и canaries, n0/n1 checks, 11 covers. Несколько одинаковых по смыслу проверок и symbolic slice addresses могут усиливать symex. Model-only~1.9s показывает, что checker сам по себе в другом fixture дешёвый; это не matched ablation и не доказывает стоимость PFC.

Unwind34 vs необходимый: loop-факты при N<=3 малы (snapshot<=3, post i/j<=3, insertion<=2 outer и<=2 shifts; general halves<=2, merge<=1 paired round). Но34 также выбран для snapshot CAP32 guard root; глобальная замена всех34 на4/5 была бы ошибкой. Все smoke/activation имеют `#[kani::unwind(34)]`: изменение CLI default само по себе их не снижает. Для fixed-N кандидата разумно проверить source-derived bound отдельно, начиная с34; меньший bound допустим только с enabled unwinding assertions и их SUCCESS, covers и unchanged domain. Конкретный минимальный unwind и выигрыш пока UNKNOWN.

Предложение без ослабления:

1. Light model/corruption/control + оба legal companions; затем исправленные actual activation variants. Cell и четыре тяжёлые строки — после них; отдельные explicit groups, чтобы grouping по variant/unwind не склеил их назад. Все23 сохраняются.
2. Изолировать каждую тяжёлую строку; это улучшает attribution/не даёт одной большой группе скрыть export, само по себе solver-time не уменьшает. Jobs1/max_parallel1/root timeout600/checks неизменны.
3. Следующий source experiment — split symbolic N на точные0/1/2/3 с теми же arbitrary bytes/KeyLess, exact target/PFC, scratch geometry/canaries/post. Принимать исходную строку только по полной union всех четырёх cases. Covers распределить по применимости, union обязан сохранить все11 meaningful obligations; невозможные N-covers в отдельном N нельзя молча считать SAT/удалить из aggregate. Старые unsplit roots до квалификации replacement не удалять. Это отдельный новый source pin/review, не выполнено здесь.
4. Source-preserving измерение formula/symex/solver metrics и root full wall/RSS в будущем runner/exporter. Не отключать assertions/covers/frame/validity/unwind для ускорения; не сокращать input values до маленького алфавита и не подменять actual callee summary.

Envelope: текущая phase4500 не выдерживает conservative ten-group proposal `10*900+23*600+10=22810 s` (до setup1800/closeout900). Это upper envelope, не прогноз. Reordering не исправляет fit и увеличивает возможное число compilation stages. Нужны owner-approved bounded stage allocation либо отдельно подтверждённые меньшие compile/root bounds с reserve. Не начинать следующий group, если его полный authorised envelope не помещается; оставшиеся NOT_RUN сохранять. S1 cap исчерпан; никакой dispatch этим пакетом не разрешён.
