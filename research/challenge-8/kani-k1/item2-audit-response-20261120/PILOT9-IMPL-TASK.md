# Кампания 9. Пакет для qualification N17 и границы network без merge

Подготовить **одну** кампанию с одним setup/build и последовательными exact roots. Перезапустить P‑1, P‑3 и plain N17 с контролями на одном новом std pin. В том же пакете проверить ветки N0/1, N2, N8, N9, N12, N13 и N16. Runtime std сохраняется побайтно. Результаты оцениваются офлайн по [QUALIFICATION-CHECKLIST.md](QUALIFICATION-CHECKLIST.md).

## Std

База `1b82e2a9a70f0712986fab263c5e336e6edef3ca`, tree `8d66a57644630c07fb19e0948b48c3e3e2fc8441`, worktree `/root/verify-rust-std-ch8-q-pilot-v1`. Один новый commit поверх базы. Дельта только в `smallsort/verify/sorting_q_pilot.rs` и `sorting_q_controls.rs`. Переиспользовать существующие P‑1, P‑3, N17, N17-control и оба false-OR controls с прежними телами, атрибутами, метками, q-доменами и моделями. Новые корни доступны в normal cfg, под `#[cfg(not(kani_smallsort_q_controls))]`.

Во всех новых positives дать независимые `kani::any()` для `[u8; 34]` и `q: u8`, сохранить `before=v` и доказать активность модели `u8/KeyLess<u8>`. Вызывать реальную `small_sort_network(&mut v[1..1+n], &mut f)`. Подготовить `qmodel::order_target` перед вызовом, затем проверить `qmodel::order_post` на всём активном срезе, `f.q()==q` и byte frame для всех индексов вне среза. Для N0/1 дополнительно проверить `v == before` для всего backing. N0/1 — один exact harness, `n` получается из произвольного bool и даёт ровно длины 0 и 1. Остальные длины литеральные. Обычные проверки памяти, overflow и unwind сохраняются. Сводки ограничены указанными листьями. Реальные sort9, sort13 и insertion loop остаются в графе. Контрактный `requires(len==17)` у sort13 относится к его активной контрактной обвязке. N13 и N16 исполняют `Original` при `--no-assert-contracts`.

Метки новых positives уникальны по selector. Для N2 и длин больше двух сохранить шесть условий N17, с префиксами `N02_PLAIN_`, `N08_PLAIN_`, `N09_PLAIN_`, `N12_PLAIN_`, `N13_PLAIN_`, `N16_PLAIN_`: `MIXED_THRESHOLD`, `THRESHOLD_TIES`, `Q_ZERO`, `Q_MAX`, `Q_ABSENT`, `USEFUL_RETURN`. `Q_ABSENT` смотрит только на логический вход, `USEFUL_RETURN` расположен после вызова и проверок. Для N0/1 задать пять covers с префиксом `N01_PLAIN_`: `LEN0_RETURN`, `LEN1_RETURN`, `Q_ZERO`, `Q_MAX`, `Q_ABSENT`. Последний требует `n==1 && before[1]!=q`, чтобы пустой вход не давал свидетельство отсутствия q. Для общей проверки `v==before` использовать `N01_PLAIN_UNCHANGED`. `ACTIVE`, `QPOST`, `Q_FRAME` и `OUTSIDE_VALUE_FRAME` также маркировать префиксом своего корня.

Добавить два normal-control по образцу N17-control. N02 покрывает схему только с `insert_tail`, N13 — только со `swap_if_less`. Они используют тот же actual маршрут, fixture, Replace и q-oracle, что соответствующие positives. После возврата для all-zero активного входа и q=1 заменить только `v[1]` на `u8::MAX`. Сохранить q/outside frame и три covers `ALL_ZERO_INPUT`, `Q_ONE_CORRUPTION_PATH`, `USEFUL_RETURN` с префиксом своего контроля. Единственная ожидаемая failure — `N02_CORRUPT_QPOST` или `N13_CORRUPT_QPOST`. Оба корня используют `q:any`, условие мутации выделяет достижимый путь. Существующий N17-control покрывает схему с обоими verified stubs. Ветку N0/1 независимо проверяет равенство всего backing и по одному post-call cover на каждую длину.

## Roster и ресурсы

Общий префикс exact selector — `slice::sort::shared::smallsort::verify::`. В колонке Replace перечислены все verified stubs. Ordinary stubs пусты у всех. `PFC swap` и `PFC insert` обозначают `proof_for_contract(swap_if_less)` и `proof_for_contract(insert_tail)`.

| № | Root ID | Суффикс selector | Cfg / режим | Replace | Child, с | Граница маршрута или ожидаемый итог |
| ---: | --- | --- | --- | --- | ---: | --- |
| 1 | P-1 | `sorting_q_pilot::p1_swap_u8_v34_q_any` | normal / PFC swap | ∅ | 600 | `SUCCESS`, q:any, base 0–20, оба индекса <13 |
| 2 | P-3 | `sorting_q_pilot::p3_insert_u8_b01_rel1_16_q_any` | normal / PFC insert | ∅ | 600 | `SUCCESS`, q:any, base 1, relative tails 1–16 |
| 3 | N17-PLAIN-STUB-SWAP-INSERT | `sorting_q_pilot::n17_plain_stub_swap_insert` | normal / Proof | swap, insert | 600 | `SUCCESS`, sort13 × 45 swap, inserts 13–16 |
| 4 | N17-PLAIN-QPOST-CORRUPT | `sorting_q_controls::n17_plain_qpost_corrupt` | normal / Proof | swap, insert | 600 | `FAILURE` ровно `N17_CORRUPT_QPOST` |
| 5 | P-5a | `sorting_q_controls::p5_swap_false_or_q_any` | mutant / PFC swap | ∅ | 600 | `FAILURE` ровно role `swap_false_or_post`, split cover до swap |
| 6 | P-5b | `sorting_q_controls::p5_swap_false_or_q_fixed0` | mutant / PFC swap | ∅ | 600 | Native `SUCCESS`, фиксированный q=0 |
| 7 | N01-PLAIN | `sorting_q_pilot::n01_plain_no_merge` | normal / Proof | ∅ | 300 | `SUCCESS`, ранний возврат для N0 и N1 |
| 8 | N02-PLAIN | `sorting_q_pilot::n02_plain_no_merge` | normal / Proof | insert | 300 | `SUCCESS`, insert tail 1 |
| 9 | N08-PLAIN | `sorting_q_pilot::n08_plain_no_merge` | normal / Proof | insert | 600 | `SUCCESS`, inserts 1–7 |
| 10 | N09-PLAIN | `sorting_q_pilot::n09_plain_no_merge` | normal / Proof | swap | 600 | `SUCCESS`, sort9 × 25 swap, ноль вставок |
| 11 | N12-PLAIN | `sorting_q_pilot::n12_plain_no_merge` | normal / Proof | swap, insert | 600 | `SUCCESS`, sort9 × 25 swap, inserts 9–11 |
| 12 | N13-PLAIN | `sorting_q_pilot::n13_plain_no_merge` | normal / Proof | swap | 600 | `SUCCESS`, sort13 × 45 swap, ноль вставок |
| 13 | N16-PLAIN | `sorting_q_pilot::n16_plain_no_merge` | normal / Proof | swap, insert | 600 | `SUCCESS`, sort13 × 45 swap, inserts 13–15 |
| 14 | N02-PLAIN-QPOST-CORRUPT | `sorting_q_controls::n02_plain_qpost_corrupt` | normal / Proof | insert | 300 | `FAILURE` ровно `N02_CORRUPT_QPOST` |
| 15 | N13-PLAIN-QPOST-CORRUPT | `sorting_q_controls::n13_plain_qpost_corrupt` | normal / Proof | swap | 300 | `FAILURE` ровно `N13_CORRUPT_QPOST` |

Во всех строках tool `0aac16ef62da9e9d5645782d458593e5d78143ba` / tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`, CaDiCaL, `--object-bits 12`, unwind36, `--no-assert-contracts`, `--jobs=1`, empty extra `cbmc_args`, прежний regular/export-json и отдельный target dir для каждого root. `normal` = `kani_smallsort_sorting` + `kani_smallsort_q_pilot`. Только `mutant` добавляет `kani_smallsort_q_controls`. Профиль OFF для uninit/validity/extra pointer checks, loop contracts и quantifiers отсутствуют.

Номинальный local cap **10 GiB**, outer 12 GiB и резерв 2 GiB. Сохранить формулу effective cap из v8 и оба значения в receipt. 11×600 + 4×300 = **7 800 с child budget**. При job 180 мин, setup/build ≤30 мин от setup epoch и резерве завершения/upload 540 с остаётся номинально 11 мин на остальную работу. Latest start каждого корня считается от supervisor cutoff по его child timeout и 30 с headroom. Child timeout входит в argv и внешний cutoff, включая std compile. Если бюджет или cleanup не позволяют продолжить, сохранять первичную причину остановки и явные `NOT_RUN` для невыполненных корней.

## Control и handoff воркера

- В control взять дерево `f8399974170e0a85b0e20b7bc2290431fb47c357` из `/root/kani-ch8-q-pilot-control-v8`. Подготовить новый локальный кандидат `experiment/ch8-q-pilot-control-v9` с единственным parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7` и тем же pinned workflow/event ref. Дельта v8 → v9 ограничена roster и fixture expectations в `run.py`, `test_run.py` и request. Закрепить все selectors, per-root cfg/timeout/argv и std commit/tree/hash inventory. Request остаётся `READY`, `go=NOT_GRANTED`, `proof_credit=NONE`.
- Сохранить bounded raw runner. В артефакт входят exact identities, start/exit/signal/caps и фактический ресурсный профиль каждого корня, cleanup, PGID и component RSS, regular stdout/stderr и stock export. Caps из v8 16/1/8 MiB на файлы и 256 MiB суммарно. Форматы, resource guards и materialization fallback переиспользуются. Вердикты, ожидания контролей, qualification и решение о допуске относятся к офлайн-разбору.
- Локально сверить дельту std и старые harness bodies/attrs. Проверить совпадение literals, селекторов, cfg, наборов verified stubs и ожидаемых путей switch/insert по исходникам. Сделать rustfmt check-only для нового кода. Выполнить `validate` на commit с синтетическими GitHub metadata, `check-source` на чистых exact checkout и `python3 -m unittest -v test_run.py`. Проверить порядок и число корней, обе cfg, оба timeout, неизменные object bits/caps и latest start, отклонение дрейфа roster/профиля и существующие error paths. Сохранить разницу между подготовленным кандидатом и нативно проверенным корнем.
- Коммиты std/control и `PILOT9-IMPL-HANDOFF.md` в g0 оформить `[skip ci]`, `Tiramisu-Cake <igkharin@gmail.com>`, без Co-Authored-By. Handoff включает точные pins/trees и hash request/workflow, roster и проверки. Подготовка локальная. Cargo, rustc, Kani, CBMC, CI и push в эту задачу не входят. Для запуска потребуется отдельное ревью и GO координатора.

Охват сетки — только перечисленные длины, exact `u8/KeyLess<u8>`, V34/base1 до merge. Эта кампания сохраняет принятый маршрут P‑1/P‑3 → plain N17. [Итог пилота](PILOT-SUMMARY-AND-NEXT.md) · [Профиль кампании 8](PILOT8-IMPL-HANDOFF.md)
