# H1 STEP1 — resource SUPPORTED; semantic gates BLOCKED
2026-11-13; worker15; research base047c7af09a; saved receipts only, local Python/source reading, no downloads/builds/verifier/CI/push.
INPUTS: coordinator-attributed run43393496999, CI-only2657d2bc3a, production4f64cc617c unchanged; upstream code bf9c58e662.
Earlier43392342927/43392900278 stopped before CBMC: Python3.10 SIGTERM-string test / strict version check; fixes1c492f014/2657d2bc3.
Actual version string `6.11.0 (cbmc-6.11.0)`; prior attempts/fixes recorded from task, not independently rerun.

| Case | First CNF variables / clauses | Sampled group RSS KiB (GiB) | Outcome |
|---|---:|---:|---|
| E8-P1 | 256060 / 585791 | 260792 (0.249) | 1/316 FAIL |
| D10-P1 | 850492 / 2064959 | 586400 (0.559) | 1/316 FAIL |
| D10-P2 | 850492 / 2064959 | 586876 (0.560) | 3/316 FAIL |
| C12-P1 | 3228220 / 7981631 | 1901724 (1.814) | 1/316 FAIL |
| C12-P2 | 3228220 / 7981631 | 1897728 (1.810) | 3/316 FAIL |
| B14-P1 | 12739132 / 31648319 | 6912520 (6.592) | RSS watchdog SIGTERM; verdict UNKNOWN |
| B14-P2 | 12739132 / 31648319 | 6913376 (6.593) | RSS watchdog SIGTERM; verdict UNKNOWN |
| A16-P1 | CENSORED / CENSORED | 6681028 (6.372) | RSS watchdog SIGTERM; verdict UNKNOWN |
| F12-P1 no-slice | 580817 / 6407436 | 896352 (0.855) | 1/316 FAIL |
| H16-P1 UF-always | 25257555 / 203206 | 6020132 (5.741) | 1/316 FAIL |

Exact separate P1(E,D,C,B)/P2(D,C,B) first-CNF fits: V=774·2^b+57916; clauses=1926·2^b+92735; every residual0.
Extrapolated b16:50782780 variables/126315071 clauses, not measured counts or RSS prediction; B14 first conversion finished, verdict did not.
Conditional64-bit lookup model admits D=S=6,Cret=0; STEP0 R1 proxy agrees, but4f64 read/version/cache/owner coverage remains UNKNOWN.
P1 has three completed verdict points; unchanged316-property inventories across E/D/C. F reduces V82.0%, clauses19.7%; simple_slice still applies.
H reaches solver/verdict with much smaller clause count; relative to extrapolated A: V0.4974,C0.001609. No matched H-negative/mode qualification.
By R3§2.6 plus PLANNER review: resource mechanism SUPPORTED conditionally, not uniquely confirmed; semantic relief/Part1 readiness not established.
B14/A16 outer receipts say RSS_LIMIT, signal15, limit6291456KiB; child CBMC records forwarded[15], exit15. No timeout/kernel-OOM evidence.
All seven completed P1/P2 arms fail on apply_closure Unsupported; P2 also fails ptr::read::<u8>.safety_check.1/.4 (same payload, two instrumentation layers).
P1 postcondition assertion is UNREACHABLE after Unsupported; P2 violates the literal one-failed-property oracle. Details/fix hypothesis: SEMANTIC-FINDING.md.
CBMC property observer hit capture cap; complete Kani regular inventories recovered/hash-checked: P1 305SUCCESS/10UNREACHABLE/1FAIL, P2 303/10/3.
CASES preserves all316 properties per distinct inventory, every arm, later CNF rounds, timings, argv, receipts/hashes; FIT preserves residuals/conditions.
GOTO bytes/complete bounded streams checked locally; common CBMC hash is receipt-reported. r3 contains10 cases, no build receipt; source→binary independent binding UNKNOWN.
Existing r2-build is failed setup; h1-tools untouched. Symbol/assigns/reached-write and general capacity gates remain UNKNOWN; no proof credit.
Next: separately authorized sized-ZST closure layout repair/repro and captured-closure controls; do not revert S3 or suppress required checks. No implementation here.
