# S1-06: офлайн-приёмка v2

Run `43889560779`, вход g0 `44ee751dcfe192f11133099f85cb65348f51c1b6`.
**Qualified acceptance PENDING; independent B1/B2/general proof credit NONE.**
Этот receipt применяет два решения координатора от 2026-11-16:
exact location-only исключение и semantic success binding. Исторический `accept/`,
intake/collected/receipts, checkpoints и ledgers сохранены.

| Gate | Результат |
|---|---|
| Stock/rich inventory | 14/14 групп, 35/35 строк, 9986/9986 exact properties; 27 SUCCESS и 8 предобъявленных FAILURE. Неизвестных статусов, lost/duplicate IDs, посторонних failures нет. |
| Location | Применены 18 exact tuples / 2 ID, class `unreachable`, description `unreachable code`, status SUCCESS, original display `library/core/src/lib.rs:0:0`. Null file/line сохранены; checks не удалены. |
| 10 исторических incomplete groups / 26 rows | Inventory повторно согласован с разрешённым исключением, включая 8 полных строк light-controls. Старый intake failure сохранён отдельно от source proof verdict. Это не квалифицирует группы: after отсутствует. |
| Binary after | 4 группы имеют совпадающие fixed required before/after hashes; 10 групп / 26 строк остаются UNKNOWN. Source_after и текущий hash не использованы как замена. |
| Required success | 16/127 semantic bindings; 111 PENDING. Дополнительно разрешены три сообщения generic helper `inactive<T,F>`: сохранены exact SUCCESS IDs всех экземпляров и исходные callsites. Для `smoke!`, `smoke_exact_n!`, `positive!` одинаковые placeholders на одном callsite не позволяют выбрать конкретный ID. Ordinals не угадывались. |
| Required SAT covers | 113/113 exact ID/description/status, с source order после relevant assumptions/model operations либо actual call и caller post/frame checks. Это статический source/structured observation; SAT не доказывает полноту domain. |
| PFC | 22/22 source attributes связаны с конкретным macro/direct root и export target; selected impl → checked_with → modifies_wrapper → property chain остаётся PENDING для всех 22. |
| UNREACHABLE | Все 413 checks + 2 covers имеют отдельные записи site/role/domain/target/wrapper. Для 226 checks установлены допустимые source/domain ветки; 187 checks остаются UNKNOWN (133 dependency applicability, 54 post-predicate binding). Generated arithmetic/bounds checks не объявлены mandatory postcondition по одному имени `active_post`. Точные решения и причины — `unreachable_analysis.records`. |
| Два mutant return covers | Допустимы после exact predeclared sole failure в activation-default/override с успешным same-run production companion. Не дают positive vacuity credit; собственные и companion identity/binding gates сохраняются. |
| Negatives / unsupported | 8/8 exact predeclared sole-failure oracles с pinned source/patch. 76 unsupported records связаны с exact SUCCESS guard в том же harness/export; pinned producer генерирует assert(false), затем assume(false). Blanket veto не применялся. |
| Source/tool/config/checks | Source/variant SHA, source before/after, tool commit/tree, exact selectors/crate/argv, unwind, enabled checks, отсутствие stubs и truncation/timeout сверены. Config cfg связан статически с frozen runner, экспорт checks сохранён. |
| Replacement unions | Все четыре N0..3 unions содержат четыре совместимых same-run member; required covers union сохранён. Qualification PENDING до закрытия gates каждого member. Область — фиксированная fixture N0..3, не общий smallsort theorem. |

Нулевое число выявленных mandatory-unreachable assertions не устанавливает их
достижимость при UNKNOWN origin/applicability. PFC candidate sites и непустой
mangled symbol не заменяют binding; pinned producer экспортирует имя
modifies-wrapper. Source coordinates не устанавливают отсутствующую compiler
instance/expansion связь.

Квалифицировано **0/35** строк. Точные remaining gates даны отдельно для каждой строки и companion в
[ACCEPT.json](ACCEPT.json). Поля и измерения для w13 перечислены в
[MISSING-FOR-S1-07.md](MISSING-FOR-S1-07.md). Метаданные следует сохранить в том же
новом compilation/run; старые отсутствующие after не восстанавливаются задним
числом. Новый proof только ради binding не требуется; этот stage dispatch не
разрешает.

Replay (из любой директории):

```sh
python /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/s1-06/run-43889560779/accept-v2/replay.py
```

По умолчанию replay пересчитывает и сравнивает новый receipt; `--write` пишет
только `accept-v2/ACCEPT.json`. [INPUTS.json](INPUTS.json) фиксирует хеши входов;
source/producer читаются из pinned Git objects. Compact payload/projection hashes
пересчитаны; проверка исходных ZIP описана историческими integrity receipts,
оригинальные ZIP этим replay не переаудировались. Raw logs не читались;
cargo/rustc/Kani/CBMC, push/CI/публикации не выполнялись.

Проверка: повторный replay совпал с receipt; 19/19 fail-closed tests PASS.
Хеши receipt/алгоритмов и команды — [VALIDATION.json](VALIDATION.json).
