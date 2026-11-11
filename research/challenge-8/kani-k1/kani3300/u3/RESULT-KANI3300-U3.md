# RESULT-KANI3300-U3
PRE-BUILD: native NOT_RUN, приёмка открыта; пакет готов к review/GO, Builds не запускались.
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; candidate `8bfb7c7c908fe58668214089a0fc7d1b5ccfe378`.
Patch SHA-256 `22b82d251006b83384cce1da644ca8842cd0fdb4ee98ed4c701d8817c5372a08`; request SHA-256 `5fc7589cac51486d987a4036479cb322d96b7f5b173dbfa7e6c432718ab64709`.
Tooling `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`; branch `experiment/kani-k1-kani3300u3-20261111`.
(a) exact T/array N + size; один SetStorage data-mask T, padding=false; typed read checks и Copy source сохранены.
Move: каждый uninit padding destination byte сохраняет false witness; составные поля/union не добавлены.
(b) buffer внутри marked MEM_INIT_STATE; user frame checks прежние; Store/Load 1..N/return0, reset/match-clear.
Return lifetime: object ID/offset сняты до Return, Load не использует dangling source pointer; no-MIR fail-closed.
Full IntoIter: NOT_RUN; ожидается Unsupported union-as-field, конкретное следующее препятствие ещё UNKNOWN.
U1T RESULT прочитан из fetched `51971120af391c3db80ff2797f43ea083ce42167`: 7/12 PASS source-reported, 5 ERROR/UNKNOWN.
False SUCCESS не установлен/не исключён; 14 файлов U1T перенесены без изменений, ожидания сохранены.
v2−U1: production 2 files +111/−13; tests включая U1T 36 files +636/−0.
Статика PASS: fresh apply/tree identity, validate, rustfmt 36 .rs, diff-check, allowlist, U1T blob identity.
Luna HIGH readiness review: concrete findings нет; native/следующее review после PASS не заменяет.
Все строки ниже — ожидания, фактический статус каждого selector NOT_RUN. Префикс `uninit/`, суффикс `/main.rs`.
| Selector | Ожидание |
|---|---|
| maybe-uninit-wrap-u3-positive | 6 SUCCESS: scalar/array Copy, zero/ZST, padded Move/array |
| maybe-uninit-wrap-u3-padding | FAILURE/uninit u8 padding |
| maybe-uninit-wrap-u3-source-read | FAILURE/uninit u64 typed source |
| maybe-uninit-wrap-u3-intoiter | FAILURE/Unsupported union-as-field |
| maybe-uninit-buffer-u3-positive | 4 SUCCESS: plain/PFC, clauses, nested/2 args/return0/stale |
| maybe-uninit-buffer-u3-plain-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-pfc-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-clause-plain-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-clause-pfc-negative | FAILURE/uninit u16 |
| maybe-uninit-buffer-u3-frame-negative | FAILURE/Check that *outside is assignable |
| maybe-uninit-buffer-u3-no-mir-unsupported | FAILURE/Unsupported shadow-carrying args without MIR |
| maybe-uninit-review-positive | 7 SUCCESS, U1T unchanged |
| maybe-uninit-review-argument-return | FAILURE/uninit u16, U1T unchanged |
| maybe-uninit-review-padded-manually-drop | FAILURE/uninit Padded, U1T unchanged |
| maybe-uninit-assume-init | FAILURE/uninit u8 |
| maybe-uninit-partial-copy | FAILURE/uninit [u8;4] |
| maybe-uninit-reset-alias | FAILURE/uninit u8 |
U1T NOT_RUN: review-overwrite-copy, review-overlap-copy, review-repeat-local, review-reset-zst (все с maybe-uninit-).
Остальные selectors U1, отсутствующие в request, также NOT_RUN; полный перечень в NOT-RUN.json.
Расход $0, reservation не создан; proposed $0.540 / cap $0.90; repair только с новым GO и actual+reserve≤cap.
Далее: после native PASS review координатора; diagnostic replay U1/U2,U6,U7–U9 отдельным GO.
Следующий scope: compound storage fields для U8/U9, затем select_unpredictable с alias/init controls; credit пока нет.
