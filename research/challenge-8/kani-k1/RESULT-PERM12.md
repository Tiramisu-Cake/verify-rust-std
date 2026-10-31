# PERM12 — optimization STOP, proof/evidence PARTIAL

G1 закончен; FF/FT/TF приняты, TT TIMEOUT. Полный partition theorem не закрыт.
Сумма VT только трёх завершённых cases663.645851s уже превышает predeclared gate600s.
G2 NOT_RUN по STOP G1; jobs3 admission OPEN. Retry/дальнейшее дробление не выполнялись.

T0 guard2026-10-31 12:40 UTC, deadline17:40 UTC (20:40 MSK), closing reserve30min.
Точное время начального prompt не записано; первый clock12:46:38 UTC, guard консервативный.
GO Claude Code получен для `d3c7db7b0108e030500960c41a302783b2401fc6` до dispatch.
G1 start12:51:49.062621 UTC, finish13:41:04.387997 UTC, закрытие внутри окна.
UUID: `cf13853e-f3f0-4e0e-b4aa-cadc631e2c4b`; Cloud Build FAILURE, Kani exit1.
Request_id=`perm12-g1-measurement-20261031`, request SHA=`d3c7db7b01` (полный в session).
Request SHA256=`5494af1c33010249b3439d2455a3e9a83e027a46fac3b637cd686463e49fc5cc`.
Собственная стоимость USD0.6750, reserved0, builds1/2, остаток USD1.3250 из USD2.
G1 envelope100min/USD1.350 соблюдён; G2 envelope70min/USD0.945 не резервировался.
Средств на G2 достаточно, но G1 gate запрещает его запуск; бюджет не является причиной NOT_RUN.
Ledger/guards: [session](perm12/session.json), [dispatch guard](perm12/g1-dispatch-guard.json),
[own budget](perm12/evidence/g1.budget.txt). Активных собственных builds/reservations нет.

База `e0ff82577d` (полный SHA в manifest), original library tree:
`c522edd42ae67c385e1ee42a1c4d1bffb611c90b`.
Cap SHA=`92d89e7a8bca371e9b4a48175d08322d3f24a2e4`, CAP_USD88.96, история сохранена.
Source SHA=`e01ed338d746601dd12eb50d937805db32f085dd`.
Frozen G1 library tree=`521e2b4bd57c83c321f03445ff10f8d12c93fb24`.
Ветка `experiment/kani-k1-permtwelve-20261031`; library/source commit отдельно от research.
[Manifest](perm12/manifest.json) содержит exact namespaces, source, request/bound file hashes.
G1 measurement/jobs1/controls on/timeout10min/uninit off; root RUN-REQUEST сохранён исторически.
G2 diagnostic/jobs3 draft содержит только4 cases, не установлен и не dispatched.

| Entry (network::, новые в perm12::) | Status | VT,s | failed/total | covers | CBMC peak,KiB |
|---|---|---:|---|---|---:|
| insertion_permutation_u64_n12 | TIMEOUT | NA | UNKNOWN | UNKNOWN | 148220 |
| trace_unpartitioned | TIMEOUT | NA | UNKNOWN | UNKNOWN | 165632 |
| ff | SUCCESS | 14.510511 | 0/141 | 2/3 | 74944 |
| ft | SUCCESS | 269.278470 | 0/141 | 2/3 | 128512 |
| tf | SUCCESS | 379.856870 | 0/141 | 2/3 | 145496 |
| tt | TIMEOUT | NA | UNKNOWN | UNKNOWN | 131680 |
| value_corruption_control | FAILED | 3.9003792 | 1/141 | 3/3 | 120056 |

У трёх SUCCESS5 unreachable checks, у control4; других reported failures у них нет.
Точные safety/unwinding/count результаты TT и baseline неизвестны; TIMEOUT не даёт proof credit.
Positive covers2/3, один unreachable: source объясняет его веткой CORRUPT=false;
movement/end остаются двумя достижимыми covers. Terse evidence не перечисляет их IDs отдельно.
Control covers3/3, включая post-flip/pre-checker. Постоянные case-bit covers не используются.
Control failure description: `assertion failed: count_matching_values(pre, probe) ==
count_matching_values(v, probe)`; file `network.rs:1518`, function `perm12::check_permutation`.
Это ровно intended full-value count failure; phase/OOB/safety/unwind failures не сообщены.
Исторический expect_check=`This is a placeholder message` НЕ совпал с actual description.
Semantic negative control наблюдён; request acceptance=false, matcher/gate не переписаны.

Сумма4 case VT=NA из-за TT; известная нижняя граница663.645851s>600s на63.645851s.
Максимум завершённых case VT379.856870s (TF); максимум всех4 UNKNOWN из-за TT.
Сумма/максимум harness wall=UNKNOWN: точных per-harness wall нет в bounded интерфейсе.
Whole Kani wall2536.14s (включая compilation), Cloud start-to-finish2955.325376s.
Whole time-v single-process max1673140KiB; sampled total RSS peak1902820KiB.
Sampled max CBMC165632KiB, driver77084KiB; максимум CBMC четырёх cases145496KiB (TF).
RSS sampling2s, OOM dmesg=none_seen не является абсолютным отсутствием OOM; swap0.
Exact per-harness wall недоступен, wall subgate UNKNOWN; savings/speedup=NA при обоих TIMEOUT.
Итоговый gate STOP независимо от wall: TT не принят и уже3 cases превышают cost ceiling.

[Evidence](perm12/evidence/g1.summary.md): parser COMPLETE7/7 rows, gate/expectation/measurement=false.
COMPLETE описывает отчёт, theorem/evidence остаются PARTIAL; aggregate false не стирает3 SUCCESS.
Summary build success — успех Kani build stage; terminal Cloud status FAILURE записан отдельно.
[Rows](perm12/evidence/g1.rows.txt), [result context](perm12/evidence/g1.result-context.txt),
[peaks](perm12/evidence/g1.peaks.0.txt), [derived metrics](perm12/measurements.json).
check-tooling UUID full cap SHA прошёл; [tooling](perm12/evidence/g1.tooling.txt).
Actual build/request IDs и SHA256 согласованы с manifest; summary Kani commit:
`9461e07af7ec929f050aa4192f29363c9be07779`, source toolchain `nightly-2026-10-12`.
Lane/flags/bound files неизменны; controls подтверждён machine/summary, uninit off summary.
Unwind25/begin9 подтверждены frozen source; actual runtime compiler version отдельно не выведен.

[Source audit](perm12/source-audit.json): appended opt-in network::perm12 — единственное library change.
Ordinary projection/старые items/imports/macros/cfg побайтно сохранены, dependency sources те же;
новые private names не меняют resolved dependencies старых items. runtime/oracle/merge/correct не менялись.
Новый closure F/instances явны: [simulation/fullness](perm12/COVERAGE.md) приняты coordinator review.
Для любых input/probe исходный trace выбирает case первых2 bool; свежие suffix choices повторяют
reads/branches/moves/count. Обратное включение есть; normal trace имеет уникальный prefix.
Ошибки до2-го comparison не исключаются; phase==2 только post-return assert, без assume.
Максимум30 comparisons на tails9/10/11, per-loop unwind25 сохранён, каждый insert loop<=11.
Fixture без sortedness/alphabet/value restrictions; real sort и parent full-value count, probe any u64.
Control: тот же unpartitioned adapter, real insertion, flip v[0]^=1, cover, тот же checker.
Source equivalence не тождество Kani instance и не machine proof unchanged baseline.
3/4 cases дают PARTIAL; исходное bounded obligation OPEN. B1 не превращается в B2/general theorem.
Linux16GiB jobs1 не доказывает Mac/fullCI/jobs3. P1/P2/submission не расширялись.
Prescribed rustfmt/static audit/validator прошли до G1; локальных proof runs/raw logs обходов нет.

Передача координатору: готовый опубликованный package; TT/base proof OPEN, matcher mismatch явен,
wall metric unavailable, jobs3 NOT_RUN. Рекомендации покрытия исходного theorem/экономии нет.
