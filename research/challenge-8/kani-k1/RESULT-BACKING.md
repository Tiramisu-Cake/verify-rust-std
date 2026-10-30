# BACKING — PARTIAL: кандидат подготовлен, сборки NOT_RUN

База `e5a0d8dd511730f374e2f757c8ac37f733062842`.
Library SHA `bff6e4863e4f69cfbd3b3f0cda4cc01e9d9f3c22`.
GO координатора получен после двух правок; новый build ещё не отправлен.
Своих builds 0/2; spent $0, reserved $0 из $3; planned envelope 100 мин / $1.35.
Request `backing-matched-20261031`: measurement, k1-standard4, jobs=1, controls=true, timeout 600 с.
Список UUID/request_id и окно: [backing/builds.json](backing/builds.json).
Сборки и итоговая приёмка остаются невыполненной частью задания.

В именах ниже префикс `slice::sort::shared::smallsort::verify::` опущен.
M=merge::backing, O=merge::opt_split, D=network::backing.
G=`MaybeUninit<[T;48]>`; S=`[MaybeUninit<T>;48]`; новый B/dispatch использует adapter.
RSS — CBMC GiB.
Checks записаны как failed/total; численные G2 строки — reuse, не новые результаты.

| Гармоника | Backing | Статус | VT GCB, с | RSS | Covers | Checks |
|---|---|---|---|---|---|---|
| O::stable_direct_u64_n8 (old B) | S | NOT_RUN | — | — | — | — |
| M::stable_direct_u64_n8 (new B) | G | NOT_RUN | — | — | — | — |
| D::dispatch_safety_stable_bytes17_n32_old | S | NOT_RUN | — | — | — | — |
| D::dispatch_safety_stable_bytes17_n32_new | G | NOT_RUN | — | — | — | — |
| O::stable_contract_u64_n8 (old A, G2) | S | SUCCESS | 349.38107 | 8.029 | 1/1 | 0/447 |
| O::general_contract_u64_n8 (new geometry A, G2) | G | SUCCESS | 221.69978 | 1.860 | 1/1 | 0/447 |

Reuse A: source `c81c10e3061e07bb83c732d81413632ada757d2c`,
build `0e44427c-18bd-4de4-95b2-e8730abec632`, request `opt-split-n8-20261030`.
Стоимость G2 $0.3645 историческая, в расходы BACKING не входит; A сумма VT 571.08085 с.
Источники: [OPT N8](opt/n8.results.json), [summary](backing/reuse-a.summary.md),
[tooling](backing/reuse-a.tooling.txt). RSS — VmHWM CBMC; это не физическая RAM всей машины.
G2 matched A не доказывает новый adapter/trait caller, новые имена или SHA.

Контроли нового backing, все NOT_RUN; PASS/FAILED ещё не установлены:
- M::stable_value_corruption_control_u64_n2: flip payload сохраняет ключ;
  настоящий oracle: count-assert merge.rs:846; expect_check="This is a placeholder message".
  После build нужен location :846 в summary и SUCCESS sortedness-assert :844 в bounded логе.
- M::unsorted_halves_control_u64_n4: корректная память, keys [3,0|1,2];
  отказ requires `merge_inputs_are_sorted` у stub_verified merge, --no-assert-contracts сохранён.
- M::allocation_bounds_control_u64: cover перед ptr::write через view+48 за allocation;
  нужен именно located Kani object-bounds check, не Rust indexing/compile/unsupported failure.

Adapter получает borrow живого caller-holder, сохраняет provenance/offset0/alignment/layout,
возвращает только `&mut [MaybeUninit<T>]` длины 48 с lifetime borrow. Holder не трогается
во время view, не alias с v/dst; нет assume_init, ссылки на uninit T или assume о памяти.
B совпадает с O::stable_direct_u64_n8 кроме backing/view: any values/probe, lt_u64, oracle,
trait-вход, unwind34 и cover одинаковы. Private opt_split helper не вызывается.
A reuse допустим для merge-части B: при N8 обе sort4 пишут prefix8 offset0, tail uninit;
merge получает отдельный initialized v как dst, тот же F/probe/frame. A any dst покрывает
все значения/корреляции caller; PFC ограничивает sorted halves прежним requires.
Dispatch: обе стороны stable-only, тот же arbitrary comparator с volatile reads,
panic stub super::assume_order_violation, any from_fn, unwind65 и normal-return cover.
С прежним pair-harness/macOS 509 с новая пара не сравнивается.

Проверки: rustfmt --check exit0; Python request validator exit0; static audit PASS.
Старые файлы — точные префиксы; добавлены только opt-in backing-блоки, 144 строки.
[Обоснование](backing/REVIEW.md), [аудит](backing/static-audit.json).
Локальные Rust/Kani/CBMC не запускались. Covers/failed checks новой сборки неизвестны.
Изменение counts при иной инициализации допустимо, но ещё не измерено.
Приёмка требует SUCCESS new, covers SATISFIED, три точных отказа и снижения matched RSS;
суммы VT, wall/цена и статус old TIMEOUT должны фиксироваться отдельно после GCB.

Другие кандидаты с литералом stable scratch (код не менялся), по приоритету:
1. network::dispatch_safety_fixed — bytes16/17 N31/32, DropValue и прочие stable-пары.
2. merge::general_route_properties — general_stable_direct/sorted_permutation u64/u8 N6+;
   opt_split::stable_direct_u64_n6 и stable_contract_u64_n6/n8.
3. merge::stable_general_u64_safety_body/all_upper_routes_safety_body — N2..32;
   merge_scratch48_length_body — stable contract geometry.
4. merge::drop_route_properties — DropTaggedValue N8/16; correct::general_stable_stub N13..15.
5. types::trait_properties — DropKey N7..9; Cell fallback и assembly ZST — низкий приоритет.
Это список гипотез по исходникам, не прогноз измеренного выигрыша.

Fixture 48 slots ≠ любой backing: production driftsort использует stack 4096 байт/heap,
возможна длина >48. Нет нового generic-backing/E1/uninit результата. Pin 9461e07a сохранён.
Linux GCB jobs1 не подтверждает macOS/jobs3; macOS UNKNOWN; нужен полный CI организаторов.
