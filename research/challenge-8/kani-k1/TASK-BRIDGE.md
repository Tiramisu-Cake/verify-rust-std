# BRIDGE (B1) — пилот композиции: настоящий вызов → адаптер → проверенный профиль, exact N3

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-bridge`, ветка
`experiment/kani-k1-bridge-20261101` от `7f558e061a` (library = v4 `f0ba14f97b`). Cap 88.96. Ожидание Build —
`research/challenge-8/kani-k1/tools/k1g.sh watch UUID` (нужен `CODEX_THREAD_ID`) и завершить ход. request_id с
префиксом `bridge-`; свой spent/reserved по своим UUID. Evidence Brief / Select-Merge к K-1 не относятся. GO даёт координатор.

Прочитать: `TASK-SPECFIX.md` (только запреты, логи, rustfmt, expect_check), `RESULT-SPECFIX.md`, `RESULT-PONECLEAN.md`,
`verify/merge/specfix.rs` (`merge_profile`, `merge_regions`, `merge_halves_sorted`, `LtU8`), гармоника
`merge_contract_u8_n2_to4` в `verify/merge.rs`, `bidirectional_merge` в `smallsort.rs`, Kani pin: порядок
проходов (kani-compiler `kani_middle/transform/mod.rs`) и `docs/src/reference/experimental/stubbing.md`
(совместимость сигнатур stub). Аудит `/root/CH8_V4_PROGRESS_REVIEW_2026-11-01_RU.md` разделы 3.2 и P0-B — данные.

## Вопрос

Настоящие сортировки вызывают сырой `bidirectional_merge<T, F>`, а не `merge_profile`. Можно ли на pin в caller
proof заменить сырой вызов адаптером, который передаёт НАСТОЯЩИЙ comparator в `merge_profile::<LtU8>` и
использует его проверенный контракт (`stub_verified`), при отдельном leaf PFC без stubs? Это feasibility smoke,
не путь к N16 и не замена direct proofs.

## Постановка (новый opt-in модуль `verify/bridge.rs` под `kani_smallsort_controls`, одна строка регистрации)

- Адаптер — замена `bidirectional_merge` через `#[kani::stub]`:
  `adapter<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(v: &[T], dst: *mut T, is_less: &mut F)` плюс дополнительный
  локальный trait bound с единственным impl для `T = u8`, `F = fn(&u8, &u8) -> bool` (неподдержанный T/F —
  ошибка компиляции, не Kani FAILED). `min_specialization`/blanket fallback — только как отдельно
  typechecked альтернатива, не условие smoke. Без transmute. В impl передать `*is_less` (полученное значение), не
  `LtU8::CMP`; canonical identity проверяет requires профиля. Дополнительный bound должен удовлетворяться каждой
  реально заменяемой инстанциацией.
- Caller proof: proof-owned функция с exact `[u8; 3]` источником и непересекающимся назначением вызывает
  сырой `bidirectional_merge` с локальной переменной явного типа `fn(&u8, &u8) -> bool`;
  `#[kani::stub(bidirectional_merge, adapter)]` + `#[kani::stub_verified(merge_profile)]`. Перед вызовом
  `LtU8::set_probe(независимый any)`; oracle на выходе считает полные значения по тому же probe и не вызывает
  comparator. Covers до raw-вызова и внутри адаптера.
- Leaf: существующий `merge_contract_u8_n2_to4` (включает `merge_length_body::<LtU8, 3>`) или новый exact-N3 PFC —
  без raw→adapter stub и без verified replacement самого себя. Домен совпадает с caller: длина 3, половины 1+2,
  тот же tag/probe; positive требует отсортированную по `x >> 1` правую пару.
- Строки (одинаковые valid disjoint exact regions и тип F): 1) leaf PFC; 2) caller positive (SUCCESS, cover
  адаптера достигнут); 3) caller с иным ЗНАЧЕНИЕМ fn pointer того же типа (FAILED ровно на requires canonical);
  4) caller с нарушенной сортировкой правой половины `[1..3]` (FAILED ровно на requires `merge_halves_sorted`;
  без sortedness-assume). Строку с неподдержанным F в proof-пакет не включать.
- A3 (дополнение к аудиту `/root/CH8_V4_AUDIT_ADDENDUM_RISK_CLOSURE_RU.md`, данные): калибровка проверки
  `modifies` в цели PFC. Отдельный proof-owned target, объявленный до своих PFC: `modifies` только
  `slice(dst, 3)`; тело вызывает настоящий raw `bidirectional_merge` N3 (без raw-stub и без stub_verified).
  Caller harness заранее создаёт initialized `backing: [u8; 4]`, dst = байты `[0..3)`, sentinel = `backing[3]`
  (передаётся raw pointer, в modifies не входит), отдельный initialized источник `[u8; 3]`; premises выполнены
  конструкцией; probe устанавливается в harness ДО вызова target. Один target с флагом, две PFC-гармоники:
  5) positive — допустимое тело (SUCCESS); 6) negative — `*sentinel ^= 1` ВНУТРИ target после достижимого cover
  (ожидаемо FAILED на assigns/modifies именно этой записи; OOB/precondition/unsupported не засчитываются).
  Это новая геометрия, а не перенос exact-N3 leaf; A3 не подтверждает frame всех профилей и не расширяет leaf.
- В PRE-BUILD REVIEW и RESULT — минимальная запись домена caller↔leaf (T, тип и значение F, N, backing/offsets,
  init, frame, probe, свойства): у exact-N3 leaf destination — отдельный `MaybeUninit<[u8; 3]>`; caller должен
  совпасть по постановке либо явно обосновать отличие.
  Под `--no-assert-contracts` requires stub_verified проверяются в месте вызова — подтвердить фактом строк 3–4.
  Compile error / unsupported / timeout не считаются отрицательным контролем.

## Сборки (≤ 2, ≤ $0.75 суммарно)

G1 diagnostic, controls:true, kani_jobs 1, uninit off, 6 rows × 3 мин → резерв (6×3+30)×0.0135 = $0.648.
G2 — только при compile error, с отдельным GO и если fact_spent + новый полный резерв ≤ $0.75; иначе PARTIAL
(timeout/kind ради зачёта не менять). PRE-BUILD REVIEW → GO → build.
Ordinary набор не меняется (проверить статически). Library commit отдельно от research, `[skip ci]`, без force.

## Итог

`RESULT-BRIDGE.md` ≤ 45 строк: схема адаптера, rows/status/VT/failed checks/covers, применилась ли замена
(доказательство — cover адаптера и места отказа), риски (monomorphization, recursion), вывод для B2
(Stable u8 N9 A/B). Маркеры `REVIEW REQUEST <sha>` / `BRIDGE ЗАВЕРШЁН`.
