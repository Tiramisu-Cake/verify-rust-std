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
- Свои build UUID: **нет**, dispatch не выполнялся. Стоимость пилота: $0.
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
