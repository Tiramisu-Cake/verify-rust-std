# KANI3300 P1G — финальный targeted native gate части 1 (15 upstream fixtures)

**Выдано координатором 2026-11-11, ночной GO владельца.** Runtime **Codex**, одна стадия. Пакет подготовлен в P1:
`kani3300/p1/NATIVE-GATE-HANDOFF.md`, `RUN-REQUEST.json`, `kani3300-part1-build.patch` (sha `b30758e5…`), `TEST-MANIFEST.json`.

- Worktree **/root/verify-rust-std-kani3300-u3**, ветка experiment/kani-k1-kani3300u3-20261111 (head после этого задания).
- Установить `kani3300/p1/RUN-REQUEST.json` как корневой `research/challenge-8/kani-k1/RUN-REQUEST.json` побайтно (stage
  `kani3300-p1g`, если поле stage/request_id требует — новый request_id `kani3300-p1g-*`, тогда пересчитать SHA и отметить),
  проверить identities из handoff (pin f046, tree `10c032ab…`, KT2 `3bb5445d2a`), `kani_k1.py validate` + preflight, commit
  `[skip ci]`, push, `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- Cap **$0.80**, резерв $0.6075, одна сборка, без repair. После GO: dispatch, `k1g.sh watch BUILD`, конец хода.
- Приёмка — по handoff: все 15 native PASS; positives с `--require-success`; negatives — собственная диагностика и полный golden.
  Не ослаблять goldens. Evidence — bounded `k1g.sh summary/native/native-field`.
- **RESULT-KANI3300-P1G.md** в `kani3300/p1/` (≤ 20 строк): identities, таблица 15 selectors, итог (PASS / что упало и почему).
- Запреты: raw logs/archives/credentials; локальные cargo/rustc/Kani/CBMC; push в Kani-репозитории; Actions/PR/issue.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.

Маркеры `REVIEW REQUEST <sha>` / **KANI3300 P1G ЗАВЕРШЁН**, одна стадия, затем стоп.
