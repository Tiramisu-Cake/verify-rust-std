# B3 T1 — детерминированное сравнение моделей perf-набора main ↔ B3 v4

2026-11-15. Одна стадия подготовки. Это верификация корректности, не security-работа.
Основания: отчёт аудитора `b3p/AUDIT-REPORT-B3-PERF-RU.md` (t0 `73479a2054`, §4 ответы 2/4/9, §5 T1) и поправки планера
(ниже, обязательны). Владелец одобрил подготовку T1; **запуск — только координатор**.
Локальные cargo/rustc/Kani/CBMC/builds запрещены (только Python/git/static). Без push/CI/PR/issue.

## Цель

Установить, меняет ли B3 вход CBMC на штатном perf-профиле: A = upstream `0aac16ef62da9e9d5645782d458593e5d78143ba`,
B = B3 v4 `3d9a1809388f74c62ea9fb7320e123db0b8b37fa` (parent A; 17 файлов, `codegen/typ.rs` + `tests/expected/zst-union-*`).
Не измерять память, не решать SAT, не пытаться воспроизвести потерю раннера.

## Требования к дизайну (аудитор + планер)

1. **Один job, один раннер ubuntu-24.04, один абсолютный путь** для исходников и target всех плеч. Порядок:
   сборка A → A1, сборка B → B1, сборка A заново → A2. A2 генерирует модели заново (чистый target/кэш Kani-артефактов),
   не берёт A1. Скрипт сравнения и обвязка живут вне переключаемого дерева.
2. **Workload = ровно штатный perf**: тот же `scripts/kani-perf.sh`-путь (release build, копирование overlays,
   `compiletest --suite perf --mode cargo-kani-test`) — все 15 строк с их selectors, cfg/features, flags и полный
   инвентарь harnesses. Не подменять общим `cargo kani --tests`, если он не эквивалентен строке; эквивалентность
   доказать по исходникам compiletest/kani-perf и записать в CI-REQUEST.
3. **Сравнивать вход CBMC, а не только codegen.** `--only-codegen` останавливается после linking, до per-harness
   goto-instrument/DFCC. Нужны для каждого harness: финальная модель, которую получил бы CBMC (после всех шагов
   kani-driver), metadata, фактический argv backend и sha256 бинарников `cbmc`/`goto-instrument`/solver.
   SAT не запускать: допустим, например, CBMC-shim в PATH, который пишет argv и sha256 входа и завершает без
   решения, или штатный механизм Kani, дающий тот же результат, — выбрать и обосновать; если Kani после shim
   отчитывается ошибкой, это ожидаемо и не маскируется (`|| true` запрещён, exit каждого вызова в журнал,
   `PIPESTATUS` при конвейерах). Дополнительно сохранить sha256 linked `*.symtab.out`/`*.out` (уровень codegen).
4. **Воспроизводимость.** Закрепить все Cargo.lock (Kani workspace и каждого perf-крейта, включая s2n-quic,
   где lock в `.gitignore`): разрешить один раз на A1, сохранить и использовать в B1/A2 с `--locked`/`--offline`.
   Записать пути и sha256 компиляторов/драйвера каждого плеча, `rustc -Vv`, `cbmc --version`, образ раннера,
   `MemTotal`, `nproc`, `df`.
5. **Сравнение.** По именам: сначала A1 = A2 (воспроизводимость), затем A1 vs B1. При различиях — diff таблиц
   символов (`goto-instrument --show-symbol-table`), затем функций, для отличающихся файлов; в artifact.
6. **При A1 ≠ A2** вывод о B3 откладывается: классифицировать различия; нормализация — только объяснённых
   несмысловых полей, с A/A-проверкой нормализатора (0 различий) и обоснованием каждого поля.
7. **Положительный контроль** в том же job: B3-reproducer (`tests/expected/zst-union-arm` или минимальный
   из `zst-union-edge-*`) тем же путём сравнения: ожидается A1 = A2 ≠ B1 ровно в wrapper-типе
   `tag-<union>::<arm>`. Если контроль не различает — T1 недействителен. Отдельная сборка старой базы не нужна.
8. **Интерпретация** (в RESULT-template): A1=A2=B1 → «различий моделей указанного perf-профиля не обнаружено»
   (без обещания отсутствия ресурсных регрессий); отличия только в zero-width wrapper → перечень = census,
   **не считать автоматически безвредными** (они меняют обработку byte operations), решение координатора;
   отличия вне обёрток → анализ аудитора §3 неверен, PR не подавать; A1≠A2 → п.6.
9. Caps: job ≤ 240 min, без retry, `always()` upload artifacts (журнал, хэши, lock-файлы, diff, argv), bounded stdout.

## Где делать

- Worktree от `/root/kani-fix-zst-b3` (содержит A и B): `git worktree add /root/kani-b3-t1 3d9a180938` (диск занят,
  новые клоны не делать). CI-only commit поверх **A** (`0aac16ef62`): удалить все stock workflows, добавить свой
  workflow (push trigger `uninit-ci/b3-t1**`) и скрипты под `.github/b3-t1/`. Исходники Kani в commit не менять.
  Автор per-command Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By.
- Research: t0 `research/challenge-8/kani-k1/kani3300/b3p/t1/` — DESIGN.md (как выполнены пп.1–9, эквивалентность
  workload), CI-REQUEST.md, RESULT-template.md, synthetic tests скриптов сравнения (Python, без сборок).
  Commit в t0 с `[skip ci]`, без push.

Финал: `READY <kani CI sha> <t0 sha>` или `STOP <причина>`.
