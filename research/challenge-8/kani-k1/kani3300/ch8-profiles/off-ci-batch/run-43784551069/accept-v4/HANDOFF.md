# Profiles OFF acceptance v4 — handoff

Одна стадия TASK-CH8-PROF-OFF-ACCEPT4-W11.md от g0 `57ff224201`.
Результат: **62 ACCEPTED / 0 PENDING / 0 UNKNOWN** (53 positive / 9 negative).
Это bounded source-reported policy admission; independent proof credit NONE,
B2/full-domain proof не установлен. 19 reviewed v3 rows перенесены без изменения;
43 bindings (37 positive PFC, 5 Replace-consumers, 1 negative PFC) установлены по
pinned source chain + exact same-row properties. Frame oracle соответствует
predeclared semantic criterion; consumers проверены после accepted matching leaf.
Source/tool/control/runner/manifest/historical receipts/ledgers не менялись.

ACCEPTANCE.md — итоговая таблица; ACCEPT.json — полный receipt;
BINDING.md — механизм, поимённые specialization bindings, ограничения и минимальный
следующий export; reclassify_v4.py/test_binding_v4.py — offline replay и controls.
В v4 исправлена source mapping привязка merge cover.1/3 по literal description;
insert-tail assertion ordinals учитывают runtime arithmetic check. См. BINDING.md.

Replay из этого каталога (ZIP уже вне репозитория):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q test_binding_v4.py
PYTHONDONTWRITEBYTECODE=1 python3 reclassify_v4.py \
  --zip /tmp/ch8-prof-off-intake-w11/artifact.zip \
  --control /root/kani-ch8-prof-off-intake-w11 \
  --source /root/verify-rust-std-ch8-profiles-w11 \
  --output /tmp/accept-v4-reproduced.json
```

20 targeted tests PASS; independent review/validation receipts прилагаются после
проверки candidate. Полный compiler/verifier локально не запускался.
Существующего artifact достаточно для принятой batch policy; предложение следующего
export не означает необходимость/разрешение нового CI. Одна стадия завершена.
Push / CI / публикаций / ledger / local cargo-rustc-Kani-CBMC: 0.
Containing g0 commit передаётся последней строкой READY в ответе.
