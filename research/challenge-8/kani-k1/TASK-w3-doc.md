# Задание W3-DOC: черновик таблицы требований и пакета раскрытия (R8 L1-10, §7)

- **Runtime:** Codex, чистая сессия.
- **Worktree и ветка:** `/root/verify-rust-std-kani-l1u`, ветка `experiment/kani-k1-uninit-20261027`. Работа W3-L1u на ней закончена, новые файлы кладутся рядом.
- **Норматив:**
  - [W3-RULES.md](W3-RULES.md) — общие правила, включая раздел «Этапы»;
  - план R8 §1, §6 и §7.
- **Сборок нет, бюджет $0.** `k1g.sh dispatch` не вызывать.
- **Чистая комната:** код и ветки PR #576, #678, #694, #701 не открывать. Из того, что известно о конкурентах, пользоваться только аудитом автора плана (ред. 5, §2).

## Что сделать

**1. `research/challenge-8/kani-k1/W3-REQUIREMENTS.md`** — таблица требований М на русском.

- **Строки:** все требования A1…I5 из `REQUIREMENTS-INTERPRETATION-2026-10-24.md` §2.
- **Колонки:**
  - требование (ID и кратко);
  - уровень (М / В / К);
  - **статус** — ровно одно из: «закрыто», «частично», «раскрыто», «в работе», «не начато»;
  - **основание** — гармоники, job CircleCI или build Cloud Build, вердикт R9; для довода — где он записан;
  - что остаётся.
- **Без процентов.**
- **Каждое «закрыто» и «частично»** опирается на измерение с gate true (или на явный довод) и на R9 GO/GO_WITH_NITS.
- **То, что ещё делают W3-L1 и W3-L2**, получает статус «в работе» со ссылкой на пункт R8.
- **Отдельный раздел «Опорные результаты»:** по маршрутам, длинам и типам. Что именно доказано и на каком lane — CircleCI 13 GiB, Cloud Build 16 GB или 32 GB. 32 GB в зачёт CI не идёт.

**2. `research/challenge-8/kani-k1/W3-DISCLOSURE-DRAFT.md`** — пакет раскрытия, **на английском**: он пойдёт в PR.

- **Структура:** ред. 4 §4 с поправками ред. 6 §5 и R8 §7.
- **Минимум разделов:**
  - **scope:** функции, маршруты, длины до порога;
  - **type matrix (C3);**
  - **comparator model:** variant (A), CD-2, ветка `panic_on_ord_violation` отрезана, достижимость подтверждена `cover`;
  - **reductions and premises:**
    - structural permutation argument для `sort9`/`sort13`;
    - перенос K-9s на размеры аллокаций;
    - shift invariance K-8r;
    - B4 выше 20;
  - **what is not checked:**
    - uninit — U-1 unsupported на pin `9461e07a`, точный текст ошибки;
    - aliasing;
    - unwind и `CopyOnDrop`;
    - ZST `read_volatile` (kani#5072);
    - латентный цикл ZST network (rust-lang/rust#165041);
  - **trust ledger:**
    - флаги CI, `--no-assert-contracts`, `ub_checks()` под Kani = false;
    - `stub_verified` и правило R4;
  - **controls and mutants:** где лежат, как воспроизвести (`cfg kani_smallsort_controls`);
  - **extended layer:** контракт слияния N20/24 на 32 GB как дополнительное свидетельство вне CI;
  - **CI resources:** раздел-заготовка, заполнит L1 этапа C.
- **Каждое утверждение** — со ссылкой на job или build, либо помечено TODO с указанием, кто его закроет.

## Источники

Читать через `git show <ветка>:<путь>`, ничего не вливать.

**План и требования** (`origin/docs/evidence-brief-policy-20261017`, каталог `research/challenge-8/`):
- `REQUIREMENTS-INTERPRETATION-2026-10-24.md`;
- `CH8-PLAN-R8-2026-10-27.md`;
- `CH8-MINIMAL-PLAN-R4-2026-10-26.md` §4;
- `CH8-MINIMAL-PLAN-R6-2026-10-26.md` §2 и §5.

**Отчёты** (база `origin/experiment/kani-k1-base-20261024`, каталог `research/challenge-8/kani-k1/`):
- `REPORT-K1-2026-10-26.md`;
- `REPORT-W1-2026-10-26.md`;
- `REPORT-W2-2026-10-27.md`;
- `EXPERIMENT.md` §5, §5a, §5b.

**Итоги агентов:**
- на этой ветке уже есть `RESULT-merge.md`, `RESULT-network.md`, `RESULT-ext.md` (волны 1–2, ночь, расширенный слой) и `RESULT-w3-l1u.md` (Z-1, U-1);
- текущее состояние W3-L1 и W3-L2 — `origin/experiment/kani-k1-assembly-20261027:research/challenge-8/kani-k1/RESULT-w3-l1.md` и `origin/experiment/kani-k1-correct-20261027:research/challenge-8/kani-k1/RESULT-w3-l2.md`. Перед концом этапа перечитать.

Читать по разделам: RESULT-файлы длинные, искать нужные места через `grep -n`.

## Конец

- `REVIEW REQUEST <SHA>` на коммит с обоими файлами. Ревью сделает координатор.
- После вердикта исправить.
- Раздел передачи в этом TASK не нужен: итог — сами два файла.
- Строка `W3-DOC ЗАВЕРШЁН` в конце `W3-REQUIREMENTS.md` (в начале строки), push, остановка.
