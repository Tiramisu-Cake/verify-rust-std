# E-02 intake — READY, draft only

Одна стадия `TASK-CH8-E02-INTAKE-W15.md`; вход g0
`32e297ea0c02a07612e2a1c6c99f7a3ae40e25ad`.

[RESULT.md](RESULT.md): классификация всех 24 invocations и границы evidence.
[ISSUE-DRAFT.md](ISSUE-DRAFT.md): финальный английский draft с выполненным
primitive MRE, upstream source links и disclosure; не опубликован.

`primitive_write` — чистый upstream repro: ON ровно один shadow assigns failure
в `mem_init.rs:93`, OFF SUCCESS; no-write/no-loop ON/OFF SUCCESS.
SEL1 воспроизводит тот же failure на `:120`. Прежний MaybeUninit MRE
на upstream останавливается раньше на union limitation и заменён в draft.
Код draft совпадает с выполненным primitive fixture после удаления только
двух устаревших подготовительных комментариев; harness/cover/атрибуты сохранены.

Read-only `gh` поиск дубликатов выполнен; точного совпадения не найдено.
Подготовка issue завершена, публикация остаётся отдельным действием владельца.

E-S остаётся OPEN: OFF — offset-address guard, false control загрязнён тем же
failure; ON — unsupported `integer_max` из `len.max(1)`, covers unreachable.
Для OFF следующий отдельный этап — получить структурированный witness
`len/index/orig_ptr/new_ptr` и проверить 52-bit offset boundary при object-bits12.
Для ON — отдельная семантически эквивалентная замена `len.max(1)` на ветвление
в экспериментальном генераторе с controls, без новой shadow модели и без CAP.
Ни один из этих шагов здесь не запускался и не авторизует новый dispatch.

Проверены artifact digests, tool/source/request/rows identities, 24 receipts и
24 exports; raw logs не читались. Статическая сверка draft и `git diff --check`
пройдены. Только документы; локальных cargo/rustc/Kani/CBMC, push, CI,
публикаций и ledger операций нет. Прежние evidence/ledgers не изменены.
Independent B1/B2 proof credit NONE; общие E/Q/H obligations не закрыты.
