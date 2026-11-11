# KANI3300 U3 — пакет до GO

Статус BLOCKED_MISSING_DIAGNOSTIC_BINDING, native NOT_RUN. Пункты 3–4 AMEND требуют уточнения.
Пакет 52cd0b12353076194296d74d2f59808ace90aceb не диспатчить. Новый dispatch также запрещён без снятия blocker и GO.
План, PLANNER-U3-ANSWER.md и AMEND-U1T.md прочитаны целиком; ниже реализован только native v2 scope (a)/(b).

## Identities и вход U1T

- Research branch `experiment/kani-k1-kani3300u3-20261111`, исходный head `aa5a44ec237fdb3d36382478aac6e3b86fda5df7`.
- Kani `/root/kani-fix-3300-v2`, branch `fix/kani-3300-v2`, commit `3fd6f408e1d565ba65aaeb86c0c4ad0bbc57ab52`.
- Полный pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; U1 base `546bcf30379b9b2894f94b1305d5277cc5b4574c`.
- Tooling `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`, toolchain и все lane paths неизменны.
- Patch SHA-256 `f9187933ecd69858ae03762baa8dd57f5907e456e7457db7cba73092471ae111`; request SHA-256 `8cda1fa64a8b1c7dfce56c44f30fd5d84bce508e9d93cf03a426e188f9c912da`.
- Applied tree `d10fbe6d3089a4d015748544963824c1053e94d4` = дерево Kani candidate; patch включает новые файлы тестов.
- U1T fetched origin head `51971120af391c3db80ff2797f43ea083ce42167`, RESULT получен через git show,
  копия [INPUT-U1T.md](INPUT-U1T.md). Его build `ff0988c7-d2f2-4872-b4ea-be581d9de02f`: source-reported 7/12 PASS,
  5 ERROR/golden mismatch. Координатор уточнил: все пять Kani FAILED; FAILURE нужных uninit properties ещё не установлен.
- Тестовый commit U1T `647109cf6342474d899aa463315a37dac14fd831` перенесён; 7 Rust sources и 2 goldens идентичны,
  5 goldens исправлены по AMEND без изменения ожидаемых типов. Подробности/вопрос: [U1T-DIAGNOSTICS-AMEND.md](U1T-DIAGNOSTICS-AMEND.md).

## Семантика и инварианты

(a) Общий typed_storage_mask используется matcher transmute и handler assignment: только exact T→MaybeUninit<T>
или [T;N]→[MaybeUninit<T>;N], равный размер и поддержанная Sized data-mask T. super_rvalue продолжает обычный
обход чтения источника; raw-deref/union-field checks и delayed-UB typed-local checks остаются. После инструкции
выполняется единственный SetStorage по data-mask T, data=true / padding=false; обычный union setter не вызывается.
Типизированный перенос вправе отбросить padding, поэтому его нельзя благословлять. Copy не меняет исходный shadow:
его witness остаётся, а назначение получает собственную маску. Для Move каждый padding-байт живого назначения
остаётся false на пути исходного произвольного выбора tracked destination byte; data разрешена штатным typed read.
Пустая длина/ZST имеют пустую маску. Вложенные union и struct storage-формы не поддержаны. Полный стандартный
IntoIterator::into_iter([usize;2]) включён: ожидается явный Unsupported из-за union field, фактический результат UNKNOWN.

(b) ARGUMENT_BUFFER стал полем уже marked MEM_INIT_STATE. Existing DFCC shadow assignable object включает это
поле; ни user modifies, ни общие флаги/DFCC код не менялись. В buffer сохраняются номер/размер и числовые object ID /
offset, снятые пока source жив. Load #0 после return не вычисляет identity по dangling pointer и не разыменовывает
старый адрес. copy_by_id реализует прежний copy witness: ветка source→destination сохраняет bit и относительное
смещение; альтернативная ветка оставляет source witness и bless перезаписанный destination. Это ghost identity,
не вывод ownership из адресного равенства. Store arguments до Call, entry Loads 1..N; return Store 0 до Return,
caller Load 0 после Call. Match проверяет extent и очищает buffer; unmatched Load сохраняет выбор другому аргументу.
На harness entry buffer=None; entry Loads завершены до nested user calls. No-MIR shadow-carrying call без модели
получает Unsupported до Store, поэтому не оставляет stale transfer; Forget использует существующую no-effect модель.

## Controls, статика, бюджет

[RUN-REQUEST.json](RUN-REQUEST.json): 20 exact selectors, harnesses=[], whole job 10 min, selector 150 s.
Два новых positive selectors (6 wrap + 4 buffer harnesses), U1T positive (7 harnesses) требуют require_success=true.
Остальные требуют конкретную диагностику собственного вывода; U3 goldens связывают FAILURE и diagnostic
в соседних строках, а пять U1T goldens требуют Failed Checks: uninit, FAILED и Complete с failed harnesses. Frame-negative требует `Check that *outside is assignable`. Новые goldens — ожидания до Cloud,
goldens upstream pin не менялись; ровно пять добавленных U1T goldens изменены по AMEND. Пары plain/PFC и clauses, nested/two args/return0/stale и no-MIR включены.
Все пять обязательных U1T negatives + review-positive включены; padded-manually-drop — NOT_RUN.
[STATIC-CHECKS.json](STATIC-CHECKS.json): validate, fresh prepare-kani/git apply --check --index, tree identity,
diff-check, allowlist и U1T source identity — PASS. Все 36 Rust blobs прежние, поэтому прежний rustfmt PASS сохраняется. Full diffstat 3999 bytes, в лимите 4096.
Production v2−U1: 2 files +111/−13; tests с U1T: 36 files +631/−0. Полный patch: production 7 files +657/−161,
tests 58 files +959/−0. Tooling/lane diff против c98d7cee0d — пустой.
[REVIEW-U3-DELTA.md](REVIEW-U3-DELTA.md): исторический review candidate 8bfb7c7 без concrete findings;
production delta от него пустой. Изменены только пять goldens; нового semantic review этот test-only delta не требует.

Расход стадии $0; proposed reserve (10+30)×$0.0135=$0.540, cap $0.90. Ledger/reservation не менялись.
Не более одного repair только по факту, с новым GO и actual+reserve≤cap. Общий ночной cap $6.40 сохраняется,
актуальный общий ledger перед dispatch проверяет координатор; U1T $0.108 — входной source-reported расход другой стадии.
Без native PASS приёмка открыта; full IntoIter не даёт credit U8/U9. Следом — отдельный native-result review, затем
отдельный GO для diagnostic replay U1/U2,U6,U7–U9. Составные storage-формы и select — следующие отдельные scopes.

## Обязательное уточнение перед GO

[AMEND-U1T.md](AMEND-U1T.md) выполнен по пунктам 1–2. Статический trace пункта 3 находит механизм текста,
но не invocation/source location observed overlap property; пункт 4 не устанавливает foreign callee по одному счётчику.
Поэтому production fix не выдуман, недостижимость не заявлена. Координатору отправлен вопрос с точными bounded fields;
ответ ожидается. Подробности: [U1T-DIAGNOSTICS-AMEND.md](U1T-DIAGNOSTICS-AMEND.md). До уточнения пакет заблокирован.
