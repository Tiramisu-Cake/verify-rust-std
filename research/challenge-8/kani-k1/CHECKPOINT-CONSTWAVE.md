# CONSTWAVE — перед G1

Дата: 2026-10-31. Worktree `/root/verify-rust-std-kani-constwave`.
Ветка `experiment/kani-k1-constwave-20261031`; исходный HEAD `0d0e585912`.
Library commit: `a9daab85b05e5e18c7b06dd657bb384def842eaa`.
Frozen library tree G1/G2: `3b06bd6d60eec19d3c7ff1a0133f8c8191f20980`.

## Окно и лимиты

- Первая записанная отметка подготовки T0: `2026-10-31 10:07:45 UTC`.
- Консервативный конец работы: `14:30 UTC`; закрытие до `15:00 UTC`.
- Перед dispatch записать фактическое время, остаток и `k1g.sh budget` повторно.
- G1: measurement/jobs=1/controls=true, 12 entries, timeout600; envelope 150 мин, $2.025.
- G2: diagnostic/jobs=3/controls=true; только const из прошедших пар G1, максимум 6.
- G2 envelope `count*10+30` мин, максимум 90 мин/$1.215. Закрытие: резерв 30 мин.
- Не запускать сборку без полного envelope + резерва закрытия в остатке окна.
- Максимум 2 сборки/$3.30, суммарный полный envelope $3.24; CAP_USD не менять.
- Проверка бюджета до review: 120 builds, used $64.2030, reserved $0, cap $73.96.
- Свои build UUID: G1 `3b1d1233-bff3-42fc-87af-21d1e083cfb0`; G2 нет.
- G1 запущен: фактическая стоимость пока неизвестна, резерв $2.025.
- G1 request_id: `constwave-g1-measurement-pairs-20261031`; G2 ещё не создан.

## Кандидат и source audit

`verify/merge.rs`: только 112 добавленных строк, 5 private helper-ов, 6 opt-in гармоник.
Новые блоки рядом с исходными helper-ами; все gated `kani_smallsort_controls`.
Ordinary items, controls, `scratch_view`, импорты, общие oracle/probe и макросы не менялись.
Остальные файлы library и их dependencies побайтово прежние; новые имена уникальны.
`CONSTWAVE-SOURCE-AUDIT.py` проверяет insertion-only diff и каждый старый fn/macro item,
точное равенство копий после оговорённых замен, cfg, wrappers и donor M9.
Совпадение helper-а M9 проверено с `7fd3d250a1`, изменён только guard на 6/7/8.
Aggregate → const у stable_direct сохраняет размер/alignment и mutable slice interface;
это другая fixture-геометрия, старый PASS на неё не переносится.

- Base merge.rs SHA256: `26c0ac36fd2f0fc7a48a09971c9b0829b444a3656fb69caafec3e9927c56c9d7`.
- New merge.rs SHA256: `370a4de78ddcc1f6d7e85951a1e91d4aca29d593cc8fb9a028c85fe9c55eac36`.
- Python source audit: PASS; request validator: 12 harnesses accepted.
- Предписанный rustfmt `--check --edition 2024 --config-path ...`: exit 0.
- Строки Rust ≤100, `git diff --check`: PASS.
- Компиляция и отсутствие новых warnings в обеих cfg пока не установлены;
  локальные rustc/cargo/Kani/CBMC не запускались по условиям задания.

## Продолжение

1. Дождаться GO после PRE-BUILD REVIEW; до GO сборок нет.
2. Проверить library tree и бюджет/окно, записать dispatch T0 и резерв закрытия.
3. Dispatch G1 через `research/challenge-8/kani-k1/tools/k1g.sh`.
4. Записать UUID/request_id, выполнить `k1g.sh watch UUID`, завершить ход.
5. После уведомления: summary/peaks/check-tooling/log-grep/log-lines (≤200 строк).
6. Решать по каждой паре: статус/VT/RSS/covers/checks; TIMEOUT RSS цензурирован.
7. В G2 включить только const SUCCESS с covers и не хуже своего baseline;
   MISSING не позволяет утверждать no-regression. Малые RSS-разницы не устойчивый эффект.
8. При достаточном окне/бюджете опубликовать research-only G2 request и запустить;
   library tree прежний, watch и завершение хода. Иначе G2 NOT_RUN.
9. Итог `RESULT-CONSTWAVE.md` по TASK (≤100 строк), commit/push отдельно от library.
   Включить четыре рекомендации, карту слияния M9, ограничения и реальное jobs3 overlap.

Никакие Select/Merge/Evidence Brief процедуры не применять; результаты только через k1g.sh.
Соседний U8N9 не переносить. Pin/toolchain/flags/lane-файлы и submission/* не менять.

## G1 — GO и dispatch

GO координатора получен для `b87fa44877`, review пройден.
Dispatch T0: `2026-10-31 10:10:25 UTC`.
До закрытия 15:00 UTC осталось 289.6 мин; envelope G1 150 + закрытие 30
помещаются. G1 максимум $2.025; G1+G2 максимум $3.24 < $3.30.
Budget непосредственно перед dispatch: 120 builds, used $64.2030, reserved $0.
Build source SHA: `b87fa448770e07e51f498e4fe2320fbaab292ea1`.
Build UUID G1: `3b1d1233-bff3-42fc-87af-21d1e083cfb0`.
Request ID: `constwave-g1-measurement-pairs-20261031`.
Dispatch успешен; pool k1-standard4, общий used + reserved максимум $66.2280.
Следующий шаг: `k1g.sh watch 3b1d1233-bff3-42fc-87af-21d1e083cfb0`, завершить ход.
После уведомления читать результаты через k1g.sh; решение по G2 — по TASK.

## G1 — результаты и решение G2

G1 COMPLETE; build SUCCESS; 12/12 SUCCESS, Kani exit 0, failed checks 0.
Request sha256: `73088722be1ba8eb220fa975baa3f3a1f902905da9d5d6160dfd3b6e344b0af4`.
Kani pin `9461e07af7ec929f050aa4192f29363c9be07779`.
`check-tooling BUILD 0d0e585912cb1295c22d4f9e610386d00a88dc9f`: PASS, все шесть SHA.
12 CBMC processes имеют direct attribution и metadata_match_count=1; source/build IDs совпали.
G1 actual $0.3915; sampled sum RSS 5.10 GiB; simultaneous CBMC 4.41 GiB.
Linux 15.63 GiB, swap off; dmesg OOM none_seen. Verify wall 22:12.81 (с компиляцией).

| Пара | VT old → const, с | CBMC VmHWM old → const, KiB | ΔVT | ΔRSS |
|---|---|---|---|---|
| S6 | 43.307020 → 31.181812 | 873252 → 366672 | -28.00% | -58.01% |
| S7 | 80.345360 → 65.378990 | 983592 → 410520 | -18.63% | -58.26% |
| S8 | 202.350880 → 135.131290 | 1581664 → 770392 | -33.22% | -51.29% |
| G5 | 105.804320 → 37.682630 | 4713196 → 737488 | -64.38% | -84.35% |
| R16 | 77.376434 → 73.865230 | 1610096 → 1570976 | -4.54% | -2.43% |
| M9 | 185.722870 → 202.587140 | 1342312 → 1328556 | +9.08% | -1.02% |

S6/S7/S8 = stable_direct_u64_n6/n7/n8; G5 = general_stable_direct_u64_n5;
R16 = route_safety_all_routes_n16; M9 = merge_scratch48_contract_u8_n9.
Covers old/const: S6/S7/S8 1/1; G5 2/2; R16 4/4; M9 2/2.
Checks old/const: S6/S7/S8 0/407 → 0/405; G5 0/407 → 0/407;
R16 0/637 → 0/637; M9 0/440 → 0/440. Unreachable в каждой паре одинаковы.
S6/S7/S8/G5/R16 имеют VT и RSS не выше baseline, допускаются в G2.
Малые изменения R16 и RSS M9 не считаются устойчивым эффектом.
M9 не проходит no-regression по VT (+9.08%), в G2 NOT_RUN; общий итог PARTIAL.
G2 request_id `constwave-g2-diagnostic-jobs3-20261031`: только пять допущенных const.
G2 diagnostic/jobs3/controls=true; envelope 5*10+30 = 80 мин/$1.0800.
G1 actual + G2 reserve = $1.4715 < $3.30; это второй и последний build.
