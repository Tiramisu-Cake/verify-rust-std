# ARRAYREPRO (A1b) — отдельный крейт: наблюдение D1 вне std, на pin и на main Kani

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-arrayrepro`, ветка
`ci/kani-array-select-repro-20261101` от upstream `c0bd09c354` (без нашей library). GCB/k1g.sh не используются.
GO на запуск CI даёт координатор. Evidence Brief / Select-Merge не относятся.

Прочитать: `RESULT-CASEFIVE.md` разделы CASE5-2 и A1 ARRAYFACTOR, `arrayfactor/reproducer.rs`, `arrayfactor/REPRODUCER.md`
и `verify/merge/casefive.rs` в ветке `experiment/kani-k1-arrayfactor-20261101` (`git show`); образец workflow —
`.github/workflows/k5-standalone-repro.yml` и каталог `k5-standalone/` в ветке `ci/k5-standalone-repro-20261029`
(`git show`; прецедент K-5: сборка Kani из исходников на pin и на main, один прогон).

## Вопрос

Воспроизводится ли наблюдение D1 вне std (обычный `cargo kani`), на pin `9461e07af7` и на текущем main Kani;
какое значение фактически читается; влияет ли решатель.

## Постановка

1. Крейт `array-select-standalone/` (вне `library/`), гармоники только под `#[cfg(kani)]`:
   - D1 дословно по форме (`[u8; 1]`, `select_unpredictable`, `ptr::read`), F2 (`if`), F5 (символический порядок
     индексов), D2 (`u8`), F7 (`x = [1]`, `y = [2]`, отдельные asserts по ветвям);
   - W — witness-строка: при `c` дополнительно `kani::cover(got[0] == y[0], ...)` и
     `kani::cover(got[0] != x[0] && got[0] != y[0], ...)` до asserts — читается ли значение другого элемента
     или произвольное.
   Все covers до asserts, literal `kani::assert` с уникальными сообщениями. Код примера не менять между версиями.
2. Workflow `.github/workflows/array-select-repro.yml` по образцу K-5: `on: push` только этой ветки (+
   `workflow_dispatch`), матрица ubuntu-latest × {pin `9461e07af7ec929f050aa4192f29363c9be07779`, `main`}, Kani из
   исходников, `cargo kani --output-format=terse` по всем гармоникам; дополнительно для D1 — запуск с
   `--concrete-playback=print` (значения контрпримера) и с другим решателем (`--solver minisat` или атрибут), если
   версия поддерживает. Job никогда не падает от ожидаемых FAILED; сводка в job summary; outputs — artifact.
3. Перед push — PRE-BUILD REVIEW с полным текстом крейта и workflow. Push ветки запускает CI один раз (2 job).
   Повтор — только при инфраструктурном сбое и только с GO. Никаких issue/публикаций вне форка.

## Итог

`ARRAYREPRO-RESULT.md` в корне ветки ≤ 40 строк: Kani SHA обеих версий, таблица гармоник × версия
(status/failed checks/covers), значения concrete playback для D1, влияние решателя, вывод: воспроизводится ли вне
std; исправлено ли на main; что остаётся UNKNOWN. Маркеры `REVIEW REQUEST <sha>` / `ARRAYREPRO ЗАВЕРШЁН`.

## Уточнения (обязательны, приоритет над текстом выше)

- Вызывать `scripts/cargo-kani` именно из собранной в job версии Kani (как K-5), не из PATH; корневой
  `rust-toolchain.toml` не менять.
- Playback: `.../scripts/cargo-kani -Z concrete-playback --concrete-playback=print --harness <D1> --exact
  --output-format=terse`, последовательно, с явными timeouts. На main проверить поддержку флагов; ошибки CLI
  отделять от результата harness.
- Решатель: D1 с явным `--solver cadical` и `--solver minisat` при прочих равных флагах; playback — отдельный опыт.
- print экспортирует конкретные входы `kani::any`, не `got`. Для численного `got` — отдельная W-гармоника:
  `let observed: u8 = kani::any(); kani::assume(observed == got[0]);` затем прежний value assert и playback W;
  проверить, что W сохраняет сбой; не называть её D1.
- Классифицирующие covers: условия `c && x[0] != y[0] && got[0] == y[0]` и `c && x[0] != y[0] && got[0] != x[0]
  && got[0] != y[0]` — в ОТДЕЛЬНЫХ гармониках по одной cover (terse даёт только агрегат).
- Не маскировать compile/driver/backend ERROR, unsupported, timeout и пропавшие строки: сохранять rc и разобранные
  outcomes; зелёный job означает собранный отчёт, не SUCCESS proofs. D2 — обязательный скалярный контроль.
- main: до GO зафиксировать полный SHA (на момент проверки `744b3e84d6eb68fd5456826997568666791bd355`,
  toolchain nightly-2026-10-23) и в workflow использовать его, а не `main`; записать версии Kani/rustc/CBMC.
- Формулировка вывода: «не воспроизводится в указанной конфигурации main», а не «исправлено»; standalone
  использует sysroot сборки Kani, PASS вне std не отменяет in-tree FAILED.
- Отчётный коммит — с `[skip ci]` или path filters workflow только на crate/workflow, чтобы не было второго CI;
  push-run не дублировать dispatch. `fail-fast: false`, `permissions: contents: read`, job timeout как в K-5.
- Ветка: только upstream-база + минимальный crate (`publish = false`, собственный `[workspace]`), workflow,
  README с командами и короткий RESULT. Без library, toolchain и штатных workflows; большие outputs — artifacts.
