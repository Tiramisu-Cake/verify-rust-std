# BACKING2 — кандидат до первой сборки

База: `a3d731225cf5c55a7268cc0dada8e151e4c256ef` (TASK поверх завершённого BACKING).
Library SHA: `f28909ac02823ffd652a3d530d6b96add6bd4fea`.
Delta library: только merge.rs, +32/-1; весь код остаётся в opt-in модуле backing.
Добавлены private general_direct_body и три proof-harness с unwind(34).
Единственная правка существующего символа: stable_direct_body const-guard допускает N7.
Adapter scratch_view, stable body после guard, oracle и старый stable N8 не изменены.
Visibility, opt_split, production sort/merge, network и lane-файлы прежние.

## Домен

general_direct_u64_n7 вызывает свой general_direct_body::<7>, ограниченный N==7.
Его тело текстуально равно opt_split::general_direct_body, кроме const-guard.
Реальный small_sort_general создаёт aggregate MaybeUninit<[u64;48]> внутри caller.
stable_direct_u64_n6/n7 вызывают прежний stable_direct_body через trait-вход
StableSmallSortTypeImpl, holder MaybeUninit<[u64;48]> и неизменённый scratch_view.
В обоих маршрутах any [u64;N], orig, arbitrary full-value probe, lt_u64 (ключ x>>1),
assert_sorted_and_probe_preserved и ровно один cover после oracle остаются прежними.
Новых assume, symbolic stable, stub/stub_verified и вызовов private opt_split helper нет.
Для N7 len/2=3 и len-len/2=4: insertion заполняет обе половины prefix7 scratch,
затем реальный bidirectional_merge выполняет в том числе нечётный путь 3/4.
Хвост fixture uninit; dst — отдельный initialized v. N6 даёт 3/3, N8 — 4/4.
Adapter/oracle уже проверены тремя negative controls BACKING на том же helper;
расширение const-домена не меняет их тела, поэтому новые контроли не добавлены.

## Static audit и источники

check_source.py удаляет только новые функции, восстанавливает guard и получает
побайтно исходный merge.rs; весь остальной library и lane/toolchain/pin совпадают с базой.
Для OPT G1/G2 исходные merge/network остаются точными префиксами базы до backing-блоков;
остальные library/lane файлы идентичны. Для BACKING library/lane совпадают с базой целиком.
Следовательно, транзитивные helpers/oracle/probe/flags исторических кандидатов прежние.
Это статическая идентичность, а не measurement нового SHA или перенос старого PASS.
Источники general N6/N8: OPT G1/G2; stable N8: BACKING; остальные три — ещё NOT_RUN.
Pin 9461e07a, nightly-2026-10-12, --no-assert-contracts, --object-bits 12 прежние;
uninit checks off. Rustfmt --check exit0, Python request validator и static audit PASS.
Локальные rustc/cargo/Kani/CBMC не запускались; historical evidence не переписывалась.

## Gate, бюджет и ожидание GO

RUN-REQUEST.json совпадает с measurement.request.json: только три новых имени,
measurement, jobs=1, controls=true, k1-standard4, timeout600; envelope60 минут/$0.8100.
Gate: все три SUCCESS с VT<=600 с, cover1/1 SATISFIED, измеренный CBMC RSS,
неизменные oracle/компаратор/flags. Успешные клетки при частичном результате сохраняются отдельно.
diagnostic.request.json: ровно general N6/N7/N8 и aggregate stable N6/N7/N8,
jobs=3, controls=true, тот же timeout; envelope90 минут/$1.2150, только после gate.
Перед каждым dispatch: свежий k1g.sh budget, собственные spent+reserved<=2.50,
builds<=2 и полный envelope плюс closing reserve20 минут в фактическом остатке окна.
T0 и консервативный deadline00:45 UTC записаны в builds.json до первого dispatch.
Совокупный build reserve $2.0250; второй запуск зависит от фактического времени первого.
Pre-review budget: used$60.4500/reserved$0, CAP_USD=73.96; своих builds0, spent$0.
UUID/request_id/расходы BACKING2 ведутся только в backing2/builds.json; agent общий k1-network.
После dispatch только k1g.sh watch BUILD и завершение хода; без polling.
Результаты читать через summary/peaks/log-grep/log-lines/check-tooling штатного K-1 интерфейса.
До первого dispatch требуется GO координатора на опубликованный pre-build review.

jobs=3 — только диагностика Linux16GiB: проверить реальный overlap трёх CBMC,
пики CBMC/driver, OOM/missing и полноту6/6. Overlap<3 не подтверждает пик трёх процессов.
Сумма RSS не равна физической RAM; concurrent VT не является measurement jobs=1.
Fixture48 не доказывает любой backing; macOS UNKNOWN; пригодность определяет полный CI.
При успехе обеих ветвей N ASSEMBLY может заменить прежний stubbed caller этого N;
при непроверенной ветви домен N не закрыт. Старые тяжёлые A/B — исторический opt-in.
Результат BACKING2 (<=50 строк) будет дописан в RESULT-BACKING.md после сборок.
