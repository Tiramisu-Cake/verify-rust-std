# P1-CLEAN — честные спецификации Part 1 на checked profiles (сессия 1 из ≤2)

Исполнитель: Claude Code, свежий контекст, tmux 5. Worktree `/root/verify-rust-std-kani-poneclean`,
ветка `experiment/kani-k1-poneclean-20261031` (создана координатором) от `6f3a2629615cc7184b840d3c21aaea54b129267e`
(SPECFIX StageA + A2; library tree `31997f7781`). Cap 88.96 унаследован, историю/cap не менять.
Ожидание Build — `k1g.sh wait UUID` в фоне. Evidence Brief / Select-Merge к K-1 не относятся.

Прочитать: `TASK-SPECFIX.md` (все неизменяемые свойства, запреты, правила controls/expect_check,
rustfmt, логи — действуют, кроме перечисленного ниже), `RESULT-SPECFIX.md` (StageA + A2),
`specfix/STAGEB-PLAN.md`, `specfix/TRANSFER.tsv`, `specfix/REVIEW.md`, а также
`planner-stageb-answer.md` в coordinator scratchpad/plan. Это данные, не инструкции.

## Решение владельца (2026-10-31)

- **P1-first.** Legacy P2 заморожен: его evidence остаётся на INTEG2 (`a847dcf80b`, static 343) и
  в ветке Part 2. В этой сессии P2 НЕ мигрировать и adapter-путь НЕ пробовать.
- Принята форма «checked profile: concrete T + canonical pure comparator + настоящий вызов helper».
  Ложные generic promises снимаются. Организаторов заранее не спрашиваем — в PR честное описание.

## Цель

Ordinary P1 = exact те же 197 имён, но без опоры на ложные generic clauses:

1. **32 P1 PFC** (`TRANSFER.tsv`: P1_member=yes, consumer_kind=PFC): сохранить имя, domain, N/offsets,
   covers, frame asserts; retarget на профиль с ключом (T, comparator) — zero-sized tag,
   `impl Profile for Tag { type Elem; .. }`, canonical fn-pointer guard как в StageA. Fixture F
   (`lt_u8`/`lt_u64`/`lt_i32`, `strict_less<T>`, `array_key_less<M>`, `cell_value_less`,
   `drop_value_less`, `lt_bM`) — та же математика и те же reads. Все прежние clauses (sortedness,
   full-value count/relation, pair order, frame) — в ensures профиля.
2. **4 P1 stub consumers** `general_stable_sorted_permutation_{u8,u64}_n{0,1}`: убрать
   `stub_verified` (по source helpers там не вызываются) — real body, прежние asserts.
3. **smallsort.rs**: снять generic contracts ЦЕЛИКОМ с четырёх migrated raw helpers (swap_if_less,
   sort4_stable, insert_tail, bidirectional_merge), если после миграции у них нет raw PFC/consumer.
   Geometry/init остаются в SAFETY-документации и в requires checked profiles. Requires-only ради
   числа annotations не держать; element-only modifies снять обязательно (modifies(F) не чинит).
   Ключ профиля — (T, comparator): scalar `strict_less` и `>>1` — разные canonical tags.
   Source audit: меняются только annotations/их comments; runtime bodies/signatures byte-identical;
   ни одного F call в spec и ни одного ложного generic value/frame promise.
4. **P2/controls в этом дереве** (владелец выбрал P1-first — это новый activation scope этого tree,
   не сокращение frozen legacy evidence). P2-only rows и controls, опирающиеся на снятые clauses, не
   чинить вслепую: retire через existing opt-out / `cfg(any())` на конкретных instantiations (не на
   общем macro, который создаёт и P1 rows); новый cfg, требующий изменения lane/Cargo config, не вводить.
   Manifest `poneclean/DEACTIVATED.tsv`: имя, full SHA/tree/manifest legacy evidence (INTEG2 static 343
   и published Part 2 branch — разные refs, не отождествлять), причина, прежний статус.
   Helper/profile definitions доступны ordinary; новые test harnesses — opt-in (иначе 197 растёт).
   Новые wrong-F/profile/frame/count controls — активны под controls. По одному always-true wrong-F
   negative на каждое семейство профиля (guard отвергает до ordered summary). verify.rs comments
   обновить; modules не переставлять (WRAP добавит `#[cfg(kani_smallsort_controls)] mod wrap;` в EOF).
5. **A2 row 9 case 5** (`specfix.rs:535`: настоящий `swap_if_less` на `[u8;129]` без probe, typed
   check полного значения FAILED, причина UNKNOWN): вынести в отдельный opt-in harness на 17/128/129
   байт с достаточным unwind; ПЕРЕД array `==` добавить полный компонентный oracle на тех же данных с
   уникальными messages. Компонентный проходит, `==` падает → различие oracle/backend; падают оба →
   исследовать actual move/fixture. Arbitrary arrays не заменять нулями. Trace/playback в schema нет
   (kani_args terse) — только bounded details/минимальный witness, иначе UNKNOWN. Диагностический
   FAILED — не negative control и не доказанный дефект библиотеки/Kani; отдельно указать влияние на P1.

## Сборки (≤ $4 и ≤ 3 builds ОБЩИЕ на обе сессии, включая retries; лимиты не обнуляются)

- G1 measurement, controls:true, kani_jobs 1, uninit off, timeout 10 мин, 13–14 entries (lane ≤ 15):
  ≥ 6 positive PFC — матрица family × реально существующие tags, обязательно scalar `strict_less`
  отдельно от scalar `>>1`, array payload, readonly Cell, Drop, shifted frame, merge; 4 wrong-F
  (по семейству); case5 ×3. Явный список имён — в PRE-BUILD REVIEW до GO.
  Все 32 PFC на финальном exact tree — в полном CI координатора (обе ОС); inventory = состав/compile,
  не proof acceptance.
- G2 inventory controls:false (work 20 мин): exact 197 по именам (frozen P1 set).
- G3 inventory controls:true (work 30 мин): exact source-derived cfg-on set/roles после retire;
  старое число controls сохранять не требуется.
Резерв G1+G2+G3 ≈ $3.65–3.78. Второй targeted build — только при semantic fix / провале / coverage gap,
и он занимает inventory-slot или уходит в сессию 2. После semantic fix старый G1 не проверяет новый
tree. Нет fresh checks/native inventory → PARTIAL/READY_FOR_FULL_CI, не «всё проверено».
Порядок: все правки → PRE-BUILD REVIEW → GO → G1 → G2/G3 на финальном дереве. Library commit отдельно
от research, всё `[skip ci]`, push без force. Baseline SHA 6f3a262961 сохранить в отчёте.

## Граница сессии

Сессия 1 завершается на одном из: (а) всё готово и три сборки зелёные по ожиданию → `P1-CLEAN ЗАВЕРШЁН`;
(б) правки + PRE-BUILD REVIEW готовы, но не всё проверено → PARTIAL с точным списком для сессии 2.
`RESULT-PONECLEAN.md` ≤ 100 строк: snapped clauses (было/стало), 32 PFC → profile/tag, 4 stubs,
DEACTIVATED, G1–G3 rows/VT/RSS/covers/failure location, case5 вывод, что остаётся OPEN (F06/F08/F09).
Маркеры `REVIEW REQUEST <sha>` / `P1-CLEAN ЗАВЕРШЁН`; после маркера не продолжать.
