# BACKING — COMPLETE: B принят; dispatch STOP по памяти

База `e5a0d8dd511730f374e2f757c8ac37f733062842`.
Library SHA `bff6e4863e4f69cfbd3b3f0cda4cc01e9d9f3c22` (новые opt-in backing-блоки).
Source `740d22674ca200f3270fb298651302019d347828`.
Build `b07fdcd8-fbd8-401e-9948-9e5f9e7201ad`, request `backing-matched-20261031`.
GCB SUCCESS; summary COMPLETE/gate true; Kani exit1 ожидаем из-за трёх negative controls.
measurement, k1-standard4, jobs1, controls=true, timeout600; Kani pin 9461e07a неизменён.
Своих builds 1/2; стоимость по ledger $0.2970, reserved $0 из $3; CAP_USD=73.96 сохранён.
Резервная сборка не нужна: пропусков/ошибок контролей нет, регресс dispatch — результат пилота.
Список UUID/request/source/расходов: [backing/builds.json](backing/builds.json).

В именах опущен `slice::sort::shared::smallsort::verify::`.
M=merge::backing, O=merge::opt_split, D=network::backing.
G=`MaybeUninit<[T;48]>`; S=`[MaybeUninit<T>;48]`; новый B/dispatch использует adapter.
RSS — индивидуальный CBMC VmHWM GiB; checks — failed/total; A строки — исторический reuse G2.

| Гармоника | Backing | Статус | VT GCB, с | RSS | Covers | Checks |
|---|---|---|---|---|---|---|
| O::stable_direct_u64_n8 (old B) | S | SUCCESS | 292.46835 | 7.928 | 1/1 | 0/405 |
| M::stable_direct_u64_n8 (new B) | G | SUCCESS | 214.31592 | 1.508 | 1/1 | 0/407 |
| D::dispatch_safety_stable_bytes17_n32_old | S | SUCCESS | 127.42941 | 1.643 | 1/1 | 0/378 |
| D::dispatch_safety_stable_bytes17_n32_new | G | SUCCESS | 134.57643 | 2.432 | 1/1 | 0/352 |
| O::stable_contract_u64_n8 (old A, G2) | S | SUCCESS | 349.38107 | 8.029 | 1/1 | 0/447 |
| O::general_contract_u64_n8 (new geometry A, G2) | G | SUCCESS | 221.69978 | 1.860 | 1/1 | 0/447 |

B: RSS ниже на 80.975% (в 5.256 раза), VT ниже на 26.72%; сумма VT пары 506.78427 с.
Adapter/домен приняты review, new SUCCESS, cover SATISFIED, все контроли сработали: B принят
как bounded кандидат для переноса. Это изменение fixture, не универсальная теорема о backing.
Dispatch: RSS вырос на 47.990%, VT на 5.61%; сумма VT пары 262.00584 с. Кандидат отвергнут.
Пилот не обосновывает общий выигрыш aggregate backing для всех гармоник.
Все новые normal-return/pre-access covers SATISFIED, по 1/1 у каждой из 7 гармоник.
Сумма VT 7 entries 774.49541878 с; Kani wall с компиляцией 854.82 с (14:14.82).
Полный build: 22 минуты по округлённому платному ledger, $0.2970; это не сумма VT.
CBMC max 7.928 GiB, driver max 0.736 GiB; sampled simultaneous sum RSS 8.359 GiB, OOM none.
Метод: kernel VmHWM, sampling 2 с; сумма RSS процессов не равна физической RAM.

Три контроля M::, каждый FAILED на единственной нужной проверке, cover 1/1:

- stable_value_corruption_control_u64_n2: 4.9353704 с, 1/409 (69 unreachable).
  Summary локализует placeholder на count-assert assert_sorted_and_probe_preserved, merge.rs:846.
  Sortedness-assert :844 прошла: oracle достигнут, других FAILED нет; flip сохраняет ключ x>>1.
  Terse lane выводит только FAILED checks; отдельной строки SUCCESS для :844 нет.
- unsorted_halves_control_u64_n4: 0.6949606 с, 1/472, требует merge_inputs_are_sorted,
  smallsort.rs:842; корректные aggregate prefix/dst, stub_verified и --no-assert-contracts.
- allocation_bounds_control_u64: 0.07497778 с, 1/16; dereference failure: pointer outside
  object bounds, ptr/mod.rs:1981 в ptr::write::<u64>. Это raw write view+48 за всей allocation
  384 байта, не safe indexing. Compile/unsupported/uninit-read не выдаются за успех.
Контекст/check/location: [bounded log 2716..2805](backing/matched.checks.txt).

Adapter: borrow живого caller-holder, provenance/offset0/alignment/layout сохранены;
только &mut [MaybeUninit<T>] длины48 с lifetime borrow, без assume_init и ссылок на uninit T.
Holder не трогается при живом view; v/dst — другие локальные объекты, fake memory assumptions нет.
B: тот же stable trait-вход, any values/probe, lt_u64, oracle, unwind34 и cover;
private opt_split helper не вызывается. Dispatch: stable-only old/new, any from_fn,
volatile_reading_less, явный stub super::assume_order_violation, unwind65 и одинаковый cover.
Прежний pair-harness и macOS 509 с не использованы как baseline.

Reuse A — только G2 source `c81c10e3061e07bb83c732d81413632ada757d2c`,
build `0e44427c-18bd-4de4-95b2-e8730abec632`, request `opt-split-n8-20261030`.
G2 cost $0.3645 исторический, не расход BACKING; сумма VT A 571.08085 с.
Исходники и транзитивные helpers/oracle/probe/T/F/flags/pin совпадают с базой по static audit.
При N8 новый stable caller пишет sort4 в prefix8 offset0, оставляет tail uninit, merge получает
отдельный initialized v как dst; any dst из A покрывает любые значения/корреляции caller.
Те же lt_u64/probe/frame; PFC ограничивает sorted halves прежним requires. Поэтому A достаточно
для merge-части нового caller. A проверяет merge, не trait/adapter; G2 PASS не перенесён
на новое имя/SHA и не заменяет новое direct доказательство B или dispatch bytes17/N32.

B checks405→407, dispatch378→352; unreachable62→62 и 10→6. Представление fixture/adapter
меняет набор служебных проверок и устранённых ветвей; точное соответствие check IDs не заявлено.
Домен обоснован кодом; SUCCESS/равенство counts не служат самостоятельной приёмкой.
Rustfmt --check exit0, Python validator/static audit PASS; прежние файлы — точные префиксы.
Tooling/source/request/pin связаны summary/check-tooling; lane-файлы равны базе.
[Summary](backing/matched.summary.md), [peaks](backing/matched.peaks0.txt),
[metrics](backing/matched.results.json), [tooling](backing/matched.tooling.txt).
[Обоснование](backing/REVIEW.md), [static audit](backing/static-audit.json).

Другие кандидаты с литералом stable scratch, без изменения кода (выигрыш — гипотеза):

1. merge::general_route_properties: u64 direct/sorted-permutation N6..8;
   opt_split::stable_direct_u64_n6; stable_contract_u64_n6/n8 и merge_scratch48_length_body.
2. merge::stable_general_u64_safety_body/all_upper_routes_safety_body N2..32;
   general_route_properties u8; correct::general_stable_stub u64/u8 N13..15.
3. merge::drop_route_properties DropTaggedValue N8/16; types::trait_properties DropKey N7..9.
4. network::dispatch_safety_fixed для иных T/N — низкий приоритет после регресса bytes17/N32;
   types Cell fallback и assembly ZST — низкий приоритет, иной маршрут/геометрия.
Fixture 48 slots ≠ любой backing: production driftsort даёт stack4096 байт/heap, длина бывает >48.
Нет нового generic-backing/E1/uninit результата. GCB jobs1 не подтверждает macOS/jobs3;
macOS UNKNOWN; полный CI организаторов нужен. Локальные Rust/Kani/CBMC не запускались.
