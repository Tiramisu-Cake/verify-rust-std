# KANI3300 U1 — PRE-BUILD repair 1

Первая сборка `6f8c5b75-42e9-4b2b-bfea-95826896d247` на `5de1d66706ccbe00a15087b2c8ace509ab6bab0e` остановилась с E0599 при компиляции `kani-compiler`. Bounded summary указывает на отсутствие trait `rustc_public::CrateDef` для вызова `AdtDef::def_id`. Native stage зависит от успешного build; результаты всех 20 selectors отсутствуют.

Repair добавляет `CrateDef` к существующему импорту в `check_uninit/ty_layout.rs`. Diff локального Kani относительно предыдущего пакета равен одной строке +1/−1. Тесты, golden, selectors и таймауты совпадают с первой попыткой.

- Ветка `experiment/kani-k1-kani3300u1-20261111`, stage `kani3300-u1`, owner `k1-merge`, tooling `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`.
- Пин Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, локальный commit `546bcf30379b9b2894f94b1305d5277cc5b4574c`.
- SHA-256 patch `306851ac5dd4f28a11778dfc49e878a5bb62fd7c35a2ad7ad0419053b9504467`.
- Request `kani3300-u1-repair1-20261111-03`, SHA-256 `69d892414672163b0d4969c13292c0141d9b5e97ada72dd7d0221c10199062cc`.
- Tree `b9c36ac5ed550e39d26e1d1d77000052e62a9bb4` после применения к свежему пину совпал с локальным коммитом Kani.
- PASS для validate, prepare-kani/apply-check, rustfmt и diff-check. Production +548/−150 в 7 файлах; tests/golden +328 в 22 новых файлах.
- 20 selectors, `harnesses: []`, job 20 мин, selector timeout 150 с. Девять negative selectors требуют uninit-диагностику из собственного вывода и соответствующий golden.
- Расход первой попытки $0.0675. Repair reservation $0.6750, суммарный максимум $0.7425 из $0.90. Подготовлен единственный разрешённый repair.
- `check-tooling` первой попытки подтвердил совпадение lane files и request/patch hashes с опубликованным пакетом, общий exit 1 сообщил `tree=None` после compile failure. Полная build identity ожидается после успешной сборки.

Статическая сверка U0 и поддержка повторения массива из 20 слотов описаны в исходном PRE-BUILD. Прямой `select_unpredictable` остаётся непроверенным. Native-результаты и проверка unexpected SUCCESS ожидаются после GO точного repair packet.
