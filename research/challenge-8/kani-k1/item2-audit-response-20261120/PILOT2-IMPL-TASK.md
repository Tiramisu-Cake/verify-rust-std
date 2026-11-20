# Кампания 2 q-пилота: замена представления порогов на маску u32 (воркер, 2026-11-21)

Основание: анализ кампании 1 `PILOT-RUN1-ANALYSIS.md` (486ae15ad8), §4 — решение координатора: реализовать ровно эту замену. Остальное (корни, argv, unwind36, V34, 600 с, 6 GiB, tool) не менять.

## std

Worktree `/root/verify-rust-std-ch8-q-pilot-v1`, ветка `experiment/ch8-q-pilot-v1`, новый коммит поверх `5544e01921d5c67c21d4ab919e8f76b43f884d92`.

- `library/core/src/slice/sort/shared/smallsort/verify/sorting_q_model.rs`: массивы пороговых битов span/prefix/target → owned `u32` (бит i = `value[i] >= q`), скан длин 0–17 с 17 константными смещениями под `if i < len` (без цикла с символьной границей); order-stat через `count_ones` и `M(n) ^ M(n-c)`, `M(n)=(1<<n)-1`; insert Pre `((P<<1) & M(len-1) & !P)==0`; insert post — `before` при b=1, `(before<<1) & M(len)` при b=0. Удалить DP `at_least`. Все guards длины/адресов/fat slice, inactive dispatch, q-frame, байтовый хвост sort13 — как были, проверки длины до любых сдвигов и чтений; биты выше активной длины — нули.
- Харнессы и контроли (`sorting_q_pilot.rs`, `sorting_q_controls.rs`) менять только если они напрямую читают старые массивы; все метки ролей, covers (включая Q_ABSENT, tails 1..16) и контроль P-5c сохранить.
- Эквивалентность старой и новой семантики показать локально: Python-модель обеих формул для всех длин 0..17 и всех масок (2^17 для order-stat и insert) — полный перебор; плюс граничные len 0,1,2,17 и q 0/255 статически.
- rustfmt check-only: `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt` с `LD_LIBRARY_PATH=/root/rustfmt-toolchains/nightly-2026-11-19/lib`.

## control

Worktree `/root/kani-ch8-q-pilot-control-v1`. Новый коммит с parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7` (как и прежние; текущий HEAD `0bf2794faa`): тот же workflow (уже с GITHUB_ENV), runner, тесты; в `CI-REQUEST.json` только новые std sha/tree и SHA-256 изменённых std-файлов. `event_ref` оставить `refs/heads/uninit-ci/ch8-q-pilot-v1`. Локально: `run.py validate` с синтетическими GitHub metadata, `check-source` на новом std, `test_run.py`.

## Ограничения и handoff

Без cargo, rustc, Kani, CBMC, CI и пушей. Коммиты `[skip ci]`, автор/коммитер Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By. Handoff `PILOT2-IMPL-HANDOFF.md` в этом каталоге: SHA/tree/parent обоих коммитов, request sha256, результаты перебора эквивалентности, diff-сводка, проверки. Коммит в g0 `[skip ci]`.
