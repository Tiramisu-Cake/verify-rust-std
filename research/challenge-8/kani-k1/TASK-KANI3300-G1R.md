# KANI3300 G1R — repair после G1A: ошибки компиляции, пересборка пакетов A/B

**Выдано координатором 2026-11-11.** Основание: `kani3300/g1/RESULT-KANI3300-G1A.md` (build `e35ca11d`, FAIL на сборке,
2× E0308 `MachineSize` вместо `usize`, все selectors NOT_RUN, $0.0675). Runtime **Codex**, одна стадия, Cloud **$0**.
Задание G1 (`TASK-KANI3300-G1.md`) и правки планера остаются в силе.

## Что сделать

1. В `/root/kani-fix-3300-g1` (ветка `fix/kani-3300-g1`) исправить
   `uninit_visitor.rs:321/324` и `:614/617`: размер — `shape().size.bytes()` (как в `ty_layout.rs:140–213`). Отдельный
   production-коммит поверх `45d0300e05`, автор Tiramisu-Cake через `-c user.name/-c user.email`; не пушить. Семантику не менять.
2. **Компиляционный sweep всего production-diff `657c2b245..HEAD`** (rustc не запускать): для каждого нового/изменённого вызова
   stable_mir/rustc_public API и kani_core сверить сигнатуры и типы по исходникам на pin f046b70644 (и toolchain
   nightly-2026-10-23, если доступен исходник): `MachineSize`/`usize`/`u64`, `Option`/`Result`, ссылки vs значения, move из
   заимствований, `match` exhaustiveness, неиспользуемые переменные/импорты (CI Kani собирает с `-D warnings`), видимость,
   generic-параметры в `mem_init.rs`. Каждую найденную проблему исправить тем же коммитом; список проверенных мест —
   в `kani3300/g1r/COMPILE-SWEEP.md` (≤ 40 строк, файл:строка → вывод).
3. Пересобрать пакеты A и B (тот же состав selectors, тесты не менять): новые build patches/SHA, applied trees, preflight,
   `git apply --check` на чистом f046. В A **`harness_timeout_minutes` ≤ 24**, чтобы резерв `(work + 30) × $0.0135` ≤ $0.7325
   (суммарный G1 ≤ $0.80 с учётом $0.0675). B — без изменения бюджета (отдельный GO владельца).
4. Независимое ревью дельты repair + sweep (свой ревьюер).

## Результат

`kani3300/g1r/`: `COMPILE-SWEEP.md`, `PRE-BUILD.md` (≤ 30 строк: новый Kani SHA, дельта, identities A/B, резерв A),
`RUN-REQUEST.json`/`RUN-REQUEST-B.json` + патчи. Коммит `[skip ci]`, push без force.
Последней строкой `PRE-BUILD REVIEW <полный research sha>`, стоп. Dispatch — только после GO координатора.

## Запреты

- Никаких сборок/dispatch/Cloud в этой стадии; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.

Маркеры `PRE-BUILD REVIEW <sha>` / **KANI3300 G1R ПАКЕТ ГОТОВ**, одна стадия, затем стоп.
