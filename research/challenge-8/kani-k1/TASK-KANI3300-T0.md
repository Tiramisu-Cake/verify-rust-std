# KANI3300 T0 — дизайн bounded трассировки контекст-зависимого ложного uninit на `IndexRange::len`

**Выдано координатором 2026-11-11, GO владельца; рамки — планер (`kani3300/cmp4/PLANNER-AFTER-CMP3-ANSWER.md` п.3–6 и
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-3300-SCOPE-ANSWER.md` п.6, 8 — прочитать).**
Только чтение и дизайн, без сборок, Cloud $0. Runtime **Codex**, одна стадия.

## Вопрос

С production CMP2 (patch sha `46ad585f…`) в наборе CMP3 из 9 roots шаги 1–3 (`IndexRange::zero_to(2).len()`, core
`ops/index_range.rs:57`) дают ложное «Reading from an uninitialized» (`kani3300/cmp3/RESULT-KANI3300-CMP3.md`). В CMP4 тот же
шаг в наборе из 4 roots проходит и на clean f046, и на CMP2 (`kani3300/cmp4/RESULT-KANI3300-CMP4.md`). Причина UNKNOWN.
Гипотезы: (а) delayed-UB/points-to по всему codegen unit инструментирует общий `len`, а shadow локала из константы не
выставлен; (б) иная. Этот blocker закрывает путь к PR «union как поле struct/union», поэтому нужна локализация, а не обход.

## Рабочее место

- Worktree **/root/verify-rust-std-kani3300-t0**, ветка **experiment/kani-k1-kani3300t0-20261111** (от CMP4 `57bb987c6b`,
  содержит CMP3/CMP4 evidence). Писать только `research/challenge-8/kani-k1/kani3300/t0/`.
- Kani (только `git show`/`git grep <sha>`): CMP2 `b1f0105c03` в `/root/kani-fix-3300-cmp`; clean `f046b70644`
  (`/root/kani-src-f046b70644`). Tooling base KT2 `3bb5445d2a` (`k1g.sh`, lane-скрипты) — только чтение.

## Что спроектировать

1. **Что именно трассировать** (по п.4 планера): фактический MIR присваивания/borrow для шагов 1 и 4 (instance, place),
   решение relevance / delayed-UB (какие функции инструментированы и почему — в 9-root и в 4-root), цели points-to,
   object+offset, порядок Set/Copy/Get по shadow до отказа. Какие из этих данных Kani уже умеет выдавать (существующие
   debug-dump, `--keep-temps`, флаги/env компилятора) — найти в исходниках, с файл:строка.
2. **Минимальный диагностический патч Kani** (если существующего мало): немутирующий, включается только env/флагом,
   отдельно от production CMP2, фильтр по имени функции, ограниченный объём вывода. Наброском: файлы, точки вставки,
   формат строк. Не менять семантику инструментирования.
3. **Как вывести результат bounded** через существующий интерфейс (`k1g.sh summary/native/native-field`) или какое
   минимальное расширение tooling нужно (оно потребует отдельного review и тестов tooling). Raw logs/archives не читать.
4. **Пакет экспериментов** (≤ 2 сборки, ориентир cap $1.40): один library/fixture hash; 9-root набор CMP3 vs 4-root набор
   CMP4 (и/или clean vs CMP2) — какое сравнение минимально отвечает на вопрос. Что считать подтверждением гипотезы (а),
   что — опровержением, что оставит UNKNOWN. Узкий фикс — не в этой стадии.

## Результат

`kani3300/t0/DESIGN-TRACE.md` (≤ 60 строк: что трассировать, существующие средства, патч-набросок, bounded вывод,
пакет и критерии) и `kani3300/t0/TASK-DRAFT-T1.md` (selectors, cap предложением). Коммит `[skip ci]` (автор Tiramisu-Cake
через `-c user.name/-c user.email`), push без force. Маркеры `REVIEW REQUEST <sha>` / **KANI3300 T0 ЗАВЕРШЁН**, затем стоп.

## Запреты

- Никаких сборок/dispatch/Cloud, локальных cargo/rustc/Kani/CBMC; raw logs/archives/credentials не читать.
- Не трогать другие worktree и клоны Kani (только чтение). Никаких Actions/PR/issue/комментариев. Без `git stash`.
- Это верификация корректности инструмента Kani и стандартной библиотеки Rust, не security-работа. Отвечай кратко.
