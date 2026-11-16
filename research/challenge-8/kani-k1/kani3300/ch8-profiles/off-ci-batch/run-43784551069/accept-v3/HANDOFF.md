# Profiles OFF acceptance v3 — handoff

Одна стадия от g0 `28a11b9b7af6d76c951df6518323af4a72b84919`.
Control `112fcc9ada67ee2bb8e1712d47983d6717487b78`, source
`9fa2f7f97760584f38738909625c064006d8a936` не менялись.

Результат: **19 ACCEPTED / 43 PENDING / 0 UNKNOWN**.
62/62 per-row stdout полны и связаны с exact harness через runner receipts;
1710/1710 unreachable exact ID/status/location/function разобраны явными rules.
43 wrapper bindings, 1 frame oracle и 5 consumer leaf gates остаются PENDING.
Source-reported bounded observations; proof credit NONE; B2/full-domain не установлен.

Файлы: ACCEPTANCE.md — все 62 строки; ACCEPT.json — полная replayable классификация,
stdout hashes/coordinates и причины; UNREACHABLE-ROLES.md / ROLE-RULES.json — таблица
семейств; classifier_v3.py / reclassify_v3.py — isolated offline analysis.
V2 и все historical receipts/source/tool/ledgers сохранены.

Воспроизведение (ZIP остаётся вне репозитория):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_classifier_v3.py
PYTHONDONTWRITEBYTECODE=1 python3 reclassify_v3.py \
  --zip /tmp/ch8-prof-off-intake-w11/artifact.zip \
  --control /root/kani-ch8-prof-off-intake-w11 \
  --source /root/verify-rust-std-ch8-profiles-w11 \
  --output /tmp/prof-off-accept-v3-reproduced.json
```

25 новых synthetic tests + 31 прежний policy test PASS. Independent Luna HIGH
review GO, без замечаний; REVIEW.json и REVIEW-IDENTITIES.json фиксируют exact
candidate `6cad5ca196d3e68ecc50f52a89bea5f2dddc66f2` и packet/spec identities.
Reviewer повторил offline replay; generated ACCEPT.json совпал побайтно, SHA256
`947e1bb9c615d61007fc97ada6a732c098fd69c5d9085268fe5310999b0d4396`.
Пакет source-only исключает параллельные задачи g0 и большой generated receipt;
semantic files равны delivery commit `199f34743b483dc9f4e0476870d37ea136768312`.
Последние doc-правки только фиксируют завершённое review и форматируют таблицу.
Containing g0 commit указан последней строкой ответа READY.

Дальнейший шаг требует отдельного задания: exact generated-wrapper specialization
binding и независимый predeclared frame oracle. Consumers не обходят leaf gate.
Эта стадия завершена; новый run, публикация, изменения runner или ledger не разрешены.

Push / CI / публикаций / ledger writes / local cargo-rustc-Kani-CBMC: 0.
