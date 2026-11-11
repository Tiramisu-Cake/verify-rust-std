# KANI3300 T1b A — RESULT
Build `c2bec5fd-c0dd-4749-bdb0-99ac0c81a59c`; Cloud FAILURE, summary RUNNER_ERROR, gate=false; Kani exit отсутствует.
Head `0f399a76b758de89d9ddd60cfea1f4f22d0904c6`; request SHA256 `b4bdf24b8808c48c366974bd0acb3740f129f21c4fb209c9ea5dc4177dc54398` — MATCH.
Исходный Kani pin f046b70644e113be0df9c22c2e6ea44a65a57566; actual applied tree UNKNOWN (build identity неполна).
Класс: SETUP_COMPILER_E0282_PROOF_NOT_RUN. Диагностическая delta не скомпилировалась; verify не запускался.
`compiler_interface.rs:118:13`: E0282 `type annotations needed` у `let instances = items`; новый вызов `.iter()` на строке135 требует тип.
Статическое ревью пропустило вывод типа. Предложенная правка: `let instances: Vec<Instance> = items`; НЕ применена.
Все verdicts ниже — NOT_RUN вследствие отказа обязательного build до verify; structured harness rows=0, checks/covers отсутствуют.

| Root suffix (общий префикс uninit_probe::) | Verdict |
|---|---|
| cmp3_index_range_len | NOT_RUN |
| cmp3_polymorphic_sized_len | NOT_RUN |
| cmp3_polymorphic_unsized_len | NOT_RUN |
| cmp3_manually_drop_unsized_len | NOT_RUN |
| cmp3_into_iter_len | NOT_RUN |
| cmp3_into_iter_next | NOT_RUN |
| small_sort_general_with_scratch_u8_n4 | NOT_RUN |
| pincheck_calibration_uninit_read_u8 | NOT_RUN |
| pincheck_calibration_init_read_u8 | NOT_RUN |

diagnostic_trace: producer NOT_RUN; state/complete/omitted/key records UNKNOWN, не ноль и не пустая полная trace.
`trace-field state/complete/omitted 0 1` и `records 0 20`: exit2, `outer Kani build identity missing`.
Ни одной ключевой trace-записи получить нельзя; raw fallback/обход identity guard не применялся.
Brief: exit1 HTTP404; bounded summary/setup excerpt/rows и trace-field ошибки сохранены в `evidence/c2bec5fd/`.
Стоимость по coordinator ledger: **$0.0810**, резерв после terminal **$0.0000**; исходный резерв$0.7695/cap$0.80.
Одна попытка из одной использована. Повторов, пакета B, новых сборок и исправления source/tooling нет.
Checks/assertions исходной программы не выполнялись; contrast/причина KANI3300, concrete object/offset/R остаются UNKNOWN.
Результат не даёт independent B1/B2 proof credit. Следующая правка/Build требует отдельного задания/GO; текущая стадия завершена.
