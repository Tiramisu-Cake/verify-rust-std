# Merge receiver localization — CLOSED / BLOCKED

Сессия от checkpoint `ce2bc9d67ce83b2439fb17177487b462267c36e1`.
Собственный worktree `/root/verify-rust-std-merge-origin`, branch
`merge/incoming-origin-20261009`, owner `merge`. Start2026-10-11T08:17:34Z,
main09:17:34Z, finishing09:47:34Z (11:17:34/12:17:34/12:47:34 МСК).
Закрыта раньше main deadline после точного receiver blocker; новая сессия
автоматически не начинается. Policy revision c7ca8c467aecf10a4b53039372ee97714f854ee3
прочитана; local adoption1b9e3df3182d13e5adf7d2e5d04afcfbc1851f14, docs совпадают
с origin/main. Старый checkpoint и ledger сохранены в archive.

## Первое точное обязательство

Fresh Build `846517a9-5a8b-4a18-827c-3f74fa148903`, proof=infra
`c8962f4b8e10a8a1b457826272d101631fd23d97`, archive
`d5a86538d2ace52897d8974697eab0c3af6ad99627143874d35d30ed836e9527`.
После actual tail.read/constructor и полного physical field/padding frame158,
source/MIR/AST/refinement PASS, assertion159:42–44 отказывает:
`Cannot prove ref_origin(gap_guard_addr) = gap_guard_addr.`
Helper-call160 в этом case НЕ достигнут. Это полученный proof refusal direct-address
receiver route, не setup/binding error и не тест недостижимого кода.

Raw Cloud **FAILURE / INCONCLUSIVE** сохранён: classifier ожидал общий текст
Cannot prove equality. Узкая правка matcher читает те же неизменные логи,
проверяет точный symbol/expression/span, frame execution и все admission gates;
saved replay классифицирует4/4. Это **не новая сборка и не новый proof**.
Wrong alias/RHS/start/end column, missing frame и AST mutations отказаны в
изолированных service tests. Полный archive/inventory/config/inputs и text-log
index/chunks проверены;12 fresh effective trusted hashes совпадают с профилем.

## Receiver resource ledger

Полный abstract borrow package не принципиально отсутствует: close FBC,
begin_lifetime и borrow(k,P) могут его построить из constructor state.
reborrow_ref_mut возвращает r с FBC(t,r) и ref_origin(r)==r, но не r==physical g;
regular function нельзя просто вызвать как ghost lemma. Actual mutable Ref
в frozen lowering даёт AddressOf(g), без создания token/reborrow result.
create_ref_mut/end_ref_mut дают только physical ownership/end-token возврат,
не origin fixedpoint. ref_origin(g) сохраняет адрес/геометрию, но не переносит
permissions/FBC на другой provenance. Existing byte/points_to rules сохраняют
pointer index. Подстановка отсутствующего token/receiver premise не выполнена.

Rust explicit destructor call не является допустимым runtime edge (E0040).
Actual Drop terminator ведёт через generic drop_in_place; его post не возвращает
CopyOnDrop CURRENT effect. Source-bound receiver/body dispatch остаётся отдельным
неполученным interface obligation, не заменённым raw-pointer helper.
[Ledger](RECEIVER-RESOURCE-LEDGER-20261011.md),
[bindings](RECEIVER-RULE-BINDINGS-20261011.json),
[точный qualification receipt](RECEIVER-QUALIFICATION-20261011.json).

## Статусы и supplied premises

Общий frozen profile: experimental-merge-qualified-guard-onecell-v1,
SHA256 `0b8cf55b0e7b5a1d0e0595b1483726459cb1d2f40264311e2014d3580ad189b8`,
**NOT_ACCEPTED / NOT_FOR_INTEGRATION**. Effective base f76012fb + ordered10 patches,
component df6b3fbf,12 trusted hashes и зависимости — EFFECTIVE-SOURCE.json,
LEN1-QUALIFICATION-20261011.json; tool/std/trusted semantics не менялись.
Concrete-u64/x86_64, len==1; не whole insert_tail.

| Обязательство | Результат / binding |
| --- | --- |
| Receiver bridge | BLOCKED: fresh846517a9/c8962f4b origin refusal159:42–44; abstract full-borrow construction только static audit |
| Actual Drop body | SAVED len1 QUALIFIED_LEN1_COMPONENT_FRESH_PROOF_PLUS_SAVED_ADMISSION,1396ff47/d491b937; conditional strong-pre bounded body, не свежий method body этой сессии |
| Actual method call | NOT_RUN / NOT_PROVED; actual Drop DefId call не реализован |
| CURRENT recovery/full normal posts | FRESH_PASS только helper-positive846517a9/c8962f4b: call159/effect162/post170; actual method path NOT_REACHED |
| Return/free/leak | FRESH_PASS только helper-positive: helper78/caller172; actual method path NOT_REACHED |
| Compiler-generated glue | NOT_RUN / NOT_PROVED; предотвращение второго destructor call тоже NOT_RUN |
| Panic/unwind cleanup | NOT_RUN / NOT_PROVED; обычные unwind smoke не доказательство cleanup caller |

Len1 прежний статус не повышен; caller прежний
FRESH_PASS_BOUNDED_NORMAL_COMPOSITION_FRAGMENT_ONLY сохранён.
Три исходные original/verified source-пары побайтно совпадают с bc08afa0;
helper-positive и его before/after-effect false controls свежие в846517a9.
Actual-method nonvacuity, missing receiver/FBC, missing-source и simultaneous-two-effect
controls **NOT_RUN**: prerequisite receiver bridge заблокирован. Saved len1
source-quarter и simultaneous-effect controls — только component evidence1396ff47;
исторический close;close BAD_NEGATIVE_ORACLE и raw failures не удалены.

Supplied caller premises неизменны: valid initialized tail storage/held u64 owner,
thread token/currentThread/type_interp, positive size/isize bounds, alignment,
object limits/no-overflow. Receiver origin/full borrow/summary не добавлялись
как новые caller premises. CURRENT и поля/padding сохраняются в helper fragment.

Оба mandatory ordinary normal/unwind smoke groups **FRESH_PASS**846517a9/c8962f4b.
Guard21/span6 **REUSED / NOT_RERUN**, Buildb1da6f8e-7569-4070-b86d-857bce812c13,
proof7995fccfee6c0e29621c2cffcca94161c7e05729,
archivea47f1958ffa4a08b9d7147059fab95e21a65aebc35c3802cc3009ef8d7f2e1dc,
тот же profile0b8cf55b. Ни smoke, ни повторная классификация не повышают theorem.

## Учёт и следующий шаг

Новый счёт CLOSED: **458/3600** Cloud seconds create→finish, **3142 retired**,
без переноса старого/нового остатка. Build created08:30:08.312774449Z,
start08:30:09.640510921Z, finish08:37:45.571307Z; main deadline соблюдён.
BUDGET.json — authoritative. Own active/reservations/unresolved NONE,
request WITHDRAWN; peer reservation сохранена. Нет own ID/token для recovery.
Measured compile/case stages — qualification JSON; queue/setup/package/upload
отдельно не измерены, create→finish не выдаётся за время proof.

Минимальный следующий шаг: review существующего source-bound receiver creation
и actual-method dispatch rule владельцем VeriFast. Подготовлен локальный
[запрос с воспроизводимым case и controls](VERIFAST-RECEIVER-REQUEST-20261011.md),
внешне не отправлен. Патч trusted semantics самостоятельно не внедрялся;
повторного Build без новой гипотезы нет. Для исполнения нового bridge потребуется
review/решение о scope и новая сессия; эта завершена. Только собственная ветка
закоммичена/отправлена, upstream/baseline/foreign worktrees не менялись.
