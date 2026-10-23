# Network N7 — RefinedRust G1 через образ в Artifact Registry: указания владельца (2026-10-24)

N6 закрыт INCONCLUSIVE на setup-границе: унаследованный пакет требовал offline-образ с замороженным deb/vendor-контекстом и registry, которых не было, а dispatcher не имел прав читать Artifact Registry. **Решение владельца 23.10 (вечер):** образ RefinedRust кладём в Google Cloud, все эксперименты ставим там. Инфраструктура подготовлена владельцем вручную:

- репозиторий `us-central1-docker.pkg.dev/smallsort-ci/smallsort-tools` (Docker; там уже лежат `evidence-processor`, `reports-mcp` Evidence Brief);
- `smallsort-builder@` — `roles/artifactregistry.writer`; `smallsort-dispatcher@` — `roles/artifactregistry.reader` (чтение с VPS проверено 2026-10-23 ≈20:55Z).

Критерии выхода, пины RR/компилятора/std и границы — те же, что в [N6-OWNER-DIRECTIONS](N6-OWNER-DIRECTIONS.md) (GO_G2 / STOP_RR / INCONCLUSIVE; RR frontend не патчить; proof credit 0; индекс не меняется). Перенесённый и перепривязанный на cd371e0 пакет из N6 (`network/rr/g1-minimal`, `g1`, `RESULT-IDENTITIES.json`, `PACKAGE-PROVENANCE.json`) переиспользуется.

## Что изменилось по сравнению с N6

1. **Online image build разрешён.** Cold Build собирает образ внутри Cloud Build с включённой сетью: `ubuntu@sha256:5ec03bb3…`, архивы nightly-2026-08-28 с `static.rust-lang.org` по уже записанным SHA-256, `git clone` RefinedRust на `332d945f` с проверкой tree `b33bcccb…`, crates с crates.io строго по `rr_frontend/Cargo.lock` (SHA-256 `b66b9e28…`, `--locked`). Offline-gates N6 (deb snapshot, vendor.tar, cargo-config SHA) для G1 **отменены**; вместо них freeze = digest образа + SHA-256 бинарников `rustc/cargo/cargo-refinedrust/refinedrust-rustc` + список apt-пакетов и Cargo.lock, записанные в evidence cold Build. Dockerfile.candidate адаптировать соответственно (убрать обязательные `DEB_BUNDLE_SHA256`/`VENDOR_TREE_SHA256`/`CARGO_CONFIG_SHA256`), новых semantic-изменений RR не вносить.
2. **Push в registry.** Cold Build пушит `us-central1-docker.pkg.dev/smallsort-ci/smallsort-tools/refinedrust-g1` (поле `images` конфигурации Cloud Build или явный `docker push` под builder SA). Полученный digest записать в профиль N7 (`cloud-build/network-rr/RR-G1-PROFILE-20261024-N7.json` → `image_build.image_digest`) и в `freeze.json` пакета; warm-recipe ссылается только на `@sha256:` digest, не на tag.
3. **Warm G1** запускает шаг `execute` в этом образе вместо `ubuntu@sha256`. Поддержка образа per-lane реализуется **branch-local** в собственном клиенте (`cloud-build/control.py` своей ветки, lane `network-rr-g1`), по мотивам `dispatcher.proposal.patch`, но без изменений coordination.py, чужих lanes, IAM и shared transport; обязательный independent review перед первым submit.
4. **Machine type.** Для cold Build допускается до `E2_HIGHCPU_8` (branch-local опция той же lane; ledger считает секунды, не vCPU). Warm — прежний `E2_STANDARD_2`. Если cold не укладывается в 1740 с даже на 8 vCPU, записать точное место остановки и STOP: разбивать сборку на несколько Builds в этом задании не нужно.

## Режим окна и бюджет

Расширенное окно (deadlines T0+4320 мин / +60 мин только для tooling), Cloud budget 5400 с: cold 1740/1800 (одна попытка плюс одна repair при setup-ошибке), warm G1 1200/1260 (до двух попыток). Timeouts не урезать; та же конфигурация не повторяется. После каждого terminal Build сразу коммить и пушь учёт ledger и CHECKPOINT/STATUS. Review один раз на semantic candidate; progress примерно каждые 2 часа; спорные моменты по CORE «Решения без владельца». Закрытие по цели, бюджету или настоящей границе.

## Порядок

1. Профиль N7 заполнить exact pins; обновить Dockerfile и cold/warm recipes под online-маршрут; service-тесты error-path для нового image/registry кода клиента; один independent review; регистрация phase/lane/ledger через собственный клиент.
2. Cold Build → digest → профиль/freeze → delta review (только pins) → warm G1 Build → Brief → классификация первого причинного отказа (compiler compatibility / frontend admission или missing library spec / selected unsupported feature / generated obligations UNPROVED).
3. `network/rr/RR-G1-RESULT.md` переписать итогом N7: вердикт, identities (image digest, Build IDs, Brief file/index), первый причинный отказ, список недостающих specs, для GO_G2 — оценка G2. N6-результат сохранить как историю.
4. В конце проверить Select `task-history/select-callee-r24/` на `PUBLISHED` P2; W7/W8 остаются ограниченными.

Отдельно, не в этом задании: тот же репозиторий подходит для образа stock VeriFast 26.09, чтобы убрать setup из каждого Build N13/R7.
