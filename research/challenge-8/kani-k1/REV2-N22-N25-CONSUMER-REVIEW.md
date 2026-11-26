# REV2 N22–N25 consumer · независимое ревью R1

**NO-GO** · ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26 · кандидат: Std `2f73485a5d`, Control `e3dcce70be`, tree `a5aab1d9c4`, trigger `1e5b5b397c`, handoff g0 `ca3e7862f2`.

Содержание пакета ревьюер признал корректным; единственный блокер — авторство, исправление которого меняет все пины. После исправления ожидается GO на том же содержании.

## Блокирующее

1. **Автор коммитов.** Std `2f73485a5d`, Control `e3dcce70be` и trigger `1e5b5b397c` записаны как `root <root@03ohba7t.vm>`; все предшественники — `Tiramisu-Cake <igkharin@gmail.com>`. Проверено координатором. SHA Std заморожен в `request.py` (OVERLAY/BUNDLE_SHA256) и CI-REQUEST, trigger уходит в публичный форк. Исправление меняет Std SHA, bundle, хэш request, control tree, `CH8_REV2_N22_N25_CONSUMER_TRIGGER_TREE` и trigger.

## Неблокирующее

2. **Запас VT/RSS у `N25-ACTUAL-BITS`.** Прецедент N20/N21 — 42–47 с VT, 2,13–2,41 GiB. N25 добавляет 4 бита, S13 на 45 пар и 12 пар merge. Изменений не требуется; следить в разборе.
3. **`ch8-cal1/request.py:455`** читает `bindings.get("historical_blobs", {})`. Ключ закреплён `SOURCE_BINDINGS_DIGEST`, но строгое `bindings["historical_blobs"]` лучше.
4. **Формулировка covers путей.** `LEFT/RIGHT_ALL_TAIL_SHIFTS`, `RIGHT_S13_PREFIX13_INVERSION`, `ODD_*_REMAINDER` (`rev2_n22_n25_consumer.rs:77-83, 105-106, 127-133, 155-156`) — предикаты входной маски, не наблюдатели внутри сети. Задание это допускает (путь проверен офлайн, ревьюер воспроизвёл). В admission указать, что путь привязан офлайн-аргументом, а не cover.

## Проверено и признано корректным

- Std diff: три файла, восемь plain Proof с `unwind(36)`, один helper на длину, actual вызов без stubs/Replace/loop contracts/предположений; контроль `v[1] ^= 1` после covers, перед тем же постом; runtime, `ptr/mod.rs` и опоры побайтно прежние; `rustfmt --check`, `git diff --check` чисты.
- Собственная транскрипция ревьюера (25 пар S9, 45 пар S13 из исходника): маски контролей совпадают с таблицей задания; сдвиги вставок N25 `[9,9,9]`/пусто, N24 `[9,9,9]`/`[9,9,9]`, N23 `[9,9]`/`[9,9,9]`, N22 `[9,9]`/`[9,9]`; центральные остатки N25 (11,1,0,12)→S+11, sentinel `0xfff` (0,12,12,0)→S+24; N23 (8,3,2,9)→S+8, sentinel `0x7ff` (0,11,11,0)→S+22; 20 000 случайных байтовых и битовых входов на длину сортируются верно; covers 7/6, 5/5, 7/6, 5/5.
- Source bindings: все координаты handoff и blobs совпадают, включая исторические `32129c1`, `217b8ef`, `86ea7aa`; source-check и тест column+1 есть; хэши индексов четырёх запусков совпадают.
- Композиция: переносы опор по таблице задания, пороговый перенос (0-1 принцип), префиксная индукция L11 (строки 701–767), ранговая индукция merge с обоими нечётными остатками и `left_rev=S−1`, copy-back 425:9. Пробелов сверх объявленных внешних переносов нет.
- Control: pin tree, порядок roster, outcome/exit, сроки (starts 3000…4435 с, слоты до 4640, аттестация 4760, cutoff 5055 = 84:15, upload 5480, план 6020), measure 1825 с при шаге 32 мин; `test_supervisor.py` blob `df63a457…`; YAML и 8 shell-блоков; 116/116 тестов на шкалах 1/5/60 с; bundle проверяется против `dab03cf510`; trigger — тот же tree, sole parent `467af9cb`.
- Сообщения коммитов: `[skip ci]`, без решётки перед цифрой.

Не запускалось: cargo, rustc, Kani, CBMC, CI, нативный compile, discovery, замеры.

## R2 после FIX1 — **GO**

Кандидат: Std `8fe1b01f0a85ee60118d1813d6b74645e4594213` (tree `f754c01d0e`), Control `fd941d949379ac437b9071cf9a1e636ae72aee5b` (tree `f4d42df994425e251022feeedcfd89e608b3d17a`), review-trigger `8a8bddf892` (тот же tree, sole parent `467af9cb8d`), handoff g0 `5fc356ec55`. Блокирующих замечаний нет.

- Автор и коммиттер Std, Control, trigger и g0 `44221a0453`/`5fc356ec55` — Tiramisu-Cake; все 16 Std-коммитов `dab03cf510..8fe1b01f0a` — Tiramisu-Cake; сообщения с `[skip ci]`, без решётки перед цифрой.
- `git diff 2f73485a5d 8fe1b01f0a` пуст, tree тот же; rustfmt и `git diff --check` чисты.
- Дельта Control `e3dcce70be..fd941d9493` — ровно 4 файла: CI-REQUEST (overlay и bundle SHA), `request.py` (OVERLAY/BUNDLE_SHA256, обязательный `historical_blobs` до вызова git), `test_run.py` (различающий тест), bundle. `git bundle verify`: prerequisite `dab03cf510`, единственный head `8fe1b01f0a`.
- SHA-256 пересчитаны независимо: request `a21b91c9…`, bundle `7768ed33…`, roster `ccc8db59…`, bindings `6fb605dd…`; совпадают с `ROSTER_DIGEST`/`SOURCE_BINDINGS_DIGEST`.
- `test_supervisor.py` blob `df63a457…`; 117/117 на шкалах default/1/5/60 с (`python3 -I -B`, клон trigger); YAML и 8 shell-блоков валидны.

Неблокирующее: локально suite на штатной шкале шёл 71 с при таймауте шага 90 с (на шкалах 1/5/60 — 37–44 с; в handoff 28–44 с). Вероятно, нагрузка машины; при таймауте `pins` учитывать это.
