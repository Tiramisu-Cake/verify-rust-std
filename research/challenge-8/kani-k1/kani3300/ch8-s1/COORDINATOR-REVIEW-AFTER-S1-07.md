# Разбор S1-07: сначала исправить офлайн-классификацию

2026-11-16. Вход g0 `b84003a4fd`, run `43923266772`, std `5be85699b8`, stock tool `0aac16ef62`.
Основание: [receipt](s1-07/run-43923266772/accept/ACCEPT.json), [варианты w11](s1-07/run-43923266772/accept/POLICY-OPTIONS.md), pinned source. Повторный read-only replay совпал: 1/35 QUALIFIED, 34 PENDING; independent credit NONE. Этот разбор не меняет receipt, policy, source или budget и не разрешает CI.

## 1. UNREACHABLE: 187 записей имеют локальные аргументы для закрытия

Нынешний `s1-06/.../accept-v2/unreachable.py:124` безусловно оставляет dependency assertions UNKNOWN; для `active_post` требует origin конкретного caller. Для перечисленных generated safety checks можно обойтись доказательством безопасности операции при любом её исполнении. Это не blanket helper exemption и не утверждение достижимости Boolean sorting relation.

| Exact pinned site | Открытых записей | Аргумент, не зависящий от caller |
|---|---:|---|
| `num/uint_macros.rs:3222,3224` | 50 | `abs_diff`: ветка сравнения выбирает большее минус меньшее; unsigned underflow невозможен. |
| `ptr/const_ptr.rs:1479` | 25 | `is_aligned_to`: до `align - 1` неположительная/не power-of-two alignment отвергается panic; оставшееся `align >= 1`. |
| `num/uint_macros.rs:3916` | 12 | `% rhs` выполняется только в ветке `rhs != 0`. |
| `ub_checks.rs:148` | 18 | Деление на `size` только в ветке `size != 0`. |
| `fmt/mod.rs:820` | 28 | `s.len() << 1`: overflow check сдвига проверяет **правый операнд**, а не потерю старших битов. Константа 1 меньше разрядности usize. Pinned Kani `codegen/rvalue.rs:328–338` строит overflow flag из RHS; `uint_macros.rs:2057–2063,3558–3559` подтверждает семантику. Предпосылка о длине строки не нужна. |
| `verify/sorting_model.rs:97,100,106,111,112,113,118` | 54 | `active_post` сначала проверяет равные длины <= CAP=32; loop guards ограничивают индексы, первый цикл начинается с 1, счётчики и инкременты <=32. Аргумент одинаков для ensures, caller, canary и model control. |

Следующая офлайн-редакция должна проверять source SHA/context, exact site/class/description/status и сохранять каждый ID с аргументом. Не менять UNREACHABLE на SUCCESS. Не распространять решение на неизвестный site или саму обязательную post/frame/relation assertion. Отсутствие различения caller здесь не препятствует универсальному аргументу для арифметики; для роли самого contract clause оно остаётся существенным.

## 2. PFC: экспорт содержит больше связей, чем учитывает нынешний gate

Для **22/22 PFC** в rich properties найдены ровно две записи с exact `contract.contracted_function_name`: `single_top_level_call` и `no_recursive_call`, обе SUCCESS; каждая description повторяет тот же raw symbol дважды. Сверено по group/harness отдельно, включая activation mutants. Demangled symbol совпадает с полным function stem обеих property IDs во всех 22 строках; location относится к source modifies. Parent check-closure сохраняет assertions на соседних ensures sites с исходной clause description: SUCCESS у positives/legal companions, предобъявленный FAILURE у activation mutants. Это реальное same-run свидетельство enforce-contract wrapper, а не только непустое имя в metadata.

Аналогичный механизм уже использован в [Profiles v4](../ch8-profiles/off-ci-batch/run-43784551069/accept-v4/BINDING.md): pinned producer → raw symbol → demangled full instance → check/modifies roles → source clauses. Между тем текущий `accept/pfc.py:466` безусловно добавляет отсутствие compiler-resolved impl identity. Нельзя из отсутствия отдельного native поля заключать, что все связи вообще отсутствуют.

Следующий шаг — воспроизвести v4 mapping на S1-07 и отдельно проверить selected type/trait/impl, source clauses и exact property anchors. Pinned `codegen/contract.rs:19–52,98–124` устанавливает смысл raw symbol и путь checked_with → modifies_wrapper; manual target-definition link уже подтверждён. Поэтому v4-style bounded source-reported цепочка восстанавливается офлайн без замены PFC на caller-only statement. Пара служебных checks сама по себе ещё не закрывает все clause bindings. Source-reported binding в доверенной модели stock Kani и независимая проверка AST/MIR/compiler provenance — разные гарантии; вторую не присваивать первой. Если текущий gate трактуется как требование именно независимого compiler-origin trace, нужен выбор владельца: сохранить более сильный audit gate либо применять тот же source-reported уровень, что у Profiles. Здесь такое решение не принято.

## 3. Success messages: подтверждённый пробел наблюдаемости

111 сообщений относятся к 21 root: 18 entry roots по 5 обязательных ролей и 3 model roots по 7. В entry root каждая из пяти ролей получает один и тот же набор восьми SUCCESS placeholders; в model root семь ролей — один набор семи. Ordinal не устанавливает роль. Повторная обработка тех же сообщений уникального binding не создаст.

Минимальный source-кандидат: в положительных `smoke!`, `smoke_exact_n!`, `positive!` использовать `kani::assert` с константной меткой `root::role`, сохранив выражения, evaluation order, assumptions, domain и условные ветки. Проверить взаимодействие assertion/cover semantics; отрицательные panic-path fixtures, их oracles и controls не менять. Уникальная строка обычного `assert!` недостаточна: stock panic lowering может снова выдать placeholder. Обновить точную таблицу required messages; negative oracles не подбирать по новому FAILURE. В реализации соблюдать владельцев: entry integration — w13, model controls — w11. Это потребует нового source SHA и одного compatible run после review; сам patch ещё не подготовлен и dispatch не выдан.

## 4. Порядок следующей стадии

1. Новая отдельная офлайн-редакция: точные source-local U rules и перенос доказуемой части Profiles PFC mapping; synthetic fail-closed проверки и review. Старый receipt оставить неизменным.
2. По её остатку окончательно определить scope source-кандидата с role labels. Не тратить прогон на неизменённые metadata и не открывать compiler feature ради уже имеющихся связей.
3. После готового reviewed пакета — отдельный coordinator GO с точным бюджетом. Companion gates пересчитать из принятия named production rows; они не отдельная причина запуска.

113 required SAT covers, 8 sole-failure oracles, complete inventory, same-run snapshots, checks и прежний domain сохраняются. S1 остаётся smoke N0..3, не доказательством полного threshold16/32 Challenge 8.
