# PROF-OFF-02 acceptance v2 — handoff

Одна стадия от g0 `7a416079bbf17cdd8b64d5e01c2f10171e1baac6`.
Весь новый материал находится в этом каталоге. Содержащий пакет g0 commit
указан в итоговом READY; control/runner не менялся:
`112fcc9ada67ee2bb8e1712d47983d6717487b78`.

Итог: **9 ACCEPTED / 0 PENDING / 53 UNKNOWN** по batch policy;
8 positive relation rows + 1 negative accepted. Secondary PENDING reasons
сохранены в JSON: 43 generated-wrapper bindings, 1 frame oracle, 5 consumer
leaf dependencies. Все 1710 unreachable occurrences имеют UNKNOWN role;
205 successful unsupported occurrences связаны по 15 exact IDs с assert(false).
Все 62 historical snapshots воспроизведены точно; старые receipts не изменены.
Proof credit NONE; source-reported bounded observations, без B2/full-domain claim.

`ACCEPTANCE.md` содержит таблицу всех строк, `ACCEPT.json` — все IDs/reasons,
`SOURCE-MAP.json` — source hashes, qualified paths, covers→obligations.
`classifier_v2.py` — отдельная версия, runner не патчится.
`UNSUPPORTED-LINKS.json` / `TOOL-SOURCES.json` фиксируют stock source chain;
`UNREACHABLE-REVIEWS.json` намеренно не содержит выдуманных exemptions.

Воспроизведение только Python/JSON/Git (ZIP остаётся вне репозитория):

```sh
cd /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-profiles/off-ci-batch/run-43784551069/accept-v2
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_classifier_v2.py
PYTHONDONTWRITEBYTECODE=1 python3 reclassify_v2.py \
  --zip /tmp/ch8-prof-off-intake-w11/artifact.zip \
  --control /root/kani-ch8-prof-off-intake-w11 \
  --source /root/verify-rust-std-ch8-profiles-w11 \
  --output /tmp/prof-off-accept-v2-reproduced.json
```

31 новых synthetic tests и 42 прежних runner/service tests PASS;
189/189 cover source windows проверены по pinned source. Independent review
GO (Luna HIGH), замечаний нет; exact candidate/packet identities — в REVIEW.json.

Review packet имеет отдельный source-only candidate, побайтно совпадающий с
semantic inputs delivery; generated ACCEPT.json проверяется отдельным exact
replay/SHA из-за лимита diff 524288 байт. REVIEW-IDENTITIES.json фиксирует оба
commit, все semantic hashes и исключённый generated receipt; packet/spec рядом.
Финальные изменения validation/review/handoff metadata не меняют semantic inputs.

G0 используется параллельно другими заданиями. Commit `f0a223506f` также захватил
уже staged файлы E-02 из общего index; их содержимое этим заданием не менялось,
история сохранена. Review и claims этого пакета относятся только к accept-v2;
завершающий commit ограничен этим каталогом.

Дальнейшее admission требует exact unreachable-condition/location bindings,
generated-wrapper specialization binding и независимого frame oracle binding.
Эта стадия не разрешает новый run, изменение exporter или обход JSON-ограничений
чтением raw logs. Пять consumers не обходят leaf gate по одному Kani SUCCESS.

Push / CI / публикаций / ledger / local cargo-rustc-Kani-CBMC: 0.
