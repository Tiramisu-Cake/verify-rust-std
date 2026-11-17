Независимый W14 review по task `831f87be704575dee4ace8f834312b5c95d43f99`.

Вердикты: **U APPROVE; PFC APPROVE; S1-08 CHANGES_REQUIRED**.
Composer w11 **NOT_REVIEWED**: exact committed delta для этого review не выдан.
Новые source/control runtime, compiler/rustfmt/exporter/verifier/full runner и CI
**NOT_RUN**. Это review компонентов, без admission, dispatch GO или B1/B2 credit.

**W14-S108-01 — P2 / MEDIUM, обязательные negative IDs содержат старые closure spans.**

Локализация: `s1-08/EMBEDDED-CI-REQUEST.json:258,294`, такие же поля в
`s1-08/CI-REQUEST.json` и control `9ccd882ef...:ch8-s1-control/CI-REQUEST.json:258,294`.
Генератор `s1-08/prepare_package.py:75–81` обновляет `oracle.line` и file SHA,
но оставляет source-derived координаты внутри `oracle.property_id` прежними.
`verify_package.py:85–93` воспроизводит эту же ошибку и сообщает PASS.

В source `99e8456d...`, `sorting_model_controls.rs`, closure descending перемещён
`100:32–100:48 → 95:32–95:48`, effectful — `106:21–106:37 → 101:21–101:37`.
Тексты closures совпадают с parent; в новых строках 100/106 closures уже нет.
Оба обязательных oracle ID по-прежнему содержат старые координаты. Это отличается
от намеренно исторических IDs в `ROLE-MAP.legacy_s107`: negative oracle задаёт
точную будущую failure identity, а не справочную запись прошлого запуска.

Pinned producer сохраняет полное instance name/closure type в property identity
(`kani_middle/mod.rs:26–37`, `cbmc_output_parser.rs:132–139,182–227`);
decoder не переносит source spans (`rich_evidence.py:150–175`).
`negative_oracle.matches` требует точный ID (`negative_oracle.py:29,56–59`).
Поэтому failure правильного нового instance не удовлетворит зафиксированному oracle.
Это fail-closed потеря обязательного control, не обнаруженный ложный proof PASS.

Воспроизведение: `PYTHONDONTWRITEBYTECODE=1 python3 validate_review.py` из этого
каталога; `VALIDATION.json#/finding_reproducer`. Для каждого из двух случаев
проверяются старый/новый exact source, затем один и тот же synthetic failure
принимается oracle с перенесёнными координатами и отклоняется committed oracle.
S1-08 compiler output не наблюдался; relocated IDs в reproducer явно synthetic.
Одновременно read-only `verify_package.check` возвращает PASS на дефектном пакете.

Минимальная правка original owner: связать оба exact negative IDs с новым source
instance (либо сохранить исходные closure spans в source), регенерировать embedded
и внешний request, control/payload/patch identities и добавить regression именно
для координат внутри generic closure type. Не заменять точные oracles wildcard,
description match или утверждением, что исторический ID уже наблюдался на S1-08.
После нового committed source/control/package pin нужен delta-review.

**U: основание APPROVE.** Exact component `16e36c4a2c244bb23ae71c80e5aa6db5f95e5338`.

Самостоятельно сопоставлены original unresolved set, rich properties, экспортные
UNREACHABLE buckets, request rows/groups, source/variant receipts и pinned Git
source. Все 187 records покрыты шестью узкими function/site/operation rules:
abs_diff 50, alignment 25, multiple 12, allocation 18, fmt 28, active_post 54.
Старые 226 allowed checks и два negative-return covers не получают нового credit.

Проверенные premises:

- `usize::abs_diff`, `uint_macros.rs:3215–3227`: на 64-bit используется ветка
  размера !=1; `self<other` даёт `1≤other-self≤MAX`, иначе `0≤self-other≤MAX`.
- `const_ptr.rs:1474–1480`, `uint_macros.rs:3932–3934`: прошедший
  `count_ones()==1` align ненулевой; `align-1` не underflow.
- `uint_macros.rs:3913–3918`, `ub_checks.rs:147–150`: нулевой divisor обработан
  отдельной веткой, `%` и `/` выполняются только при divisor≥1.
- `fmt/mod.rs:815–823`: shift RHS равен 1. Предел overflow — RHS>63, не потеря
  старших битов LHS (`rvalue.rs:275–297,328–339`, pinned stock tool).
  Для этого generated safety check не нужна предпосылка `s.len()≤MAX/2`.
- `sorting_model.rs:66–70,91–121`: после guard `n=before.len=values.len≤32`.
  Первый loop начинает с i=1, body только при i<n: `0≤i−1<i<n`, `i+1≤n`.
  Outer/inner loops начинают с 0; body indices<n≤32, increment≤n.
  На inner header `0≤old_count,new_count≤j`; прибавление 0/1 сохраняет
  `count≤j+1≤n`. Base/step проверены для всех n=0..32 и всех таких states.
  При n=0/1 первый loop не индексирует slice. Вызовы Project не меняют длины.

Правила относятся только к этим arithmetic/bounds assertions: ни порядок, ни
multiset equality/returns самого `active_post`, ни caller/PFC origin не исключены
из proof. Variant patches меняют только production target `smallsort.rs`, не
зависимости safety rules. Full source/anchor hashes, exact function instance,
operation description/site и same-run sets проверены. Tests действительно входят
ниже hash gate: direct premise mutations и classify для каждого record, а также
coherent rehash mutations. Повторённый replay совпал с committed U.json.
Assurance: pinned source-local safety argument + source-reported property identity;
ни sorting relation theorem, ни независимая compiler-origin provenance не присвоены.

**PFC: основание APPROVE.** Exact component `013f288ca5111c0587e087567d2ec4182856be1d`.

Проверены все 22 chains, шесть impls и два false-ensures mutants. Полное
demangling raw symbols независимо повторено `c++filt -i -s rust`; проверены T,
trait, full module path и `KeyLess<T>`, а не terminal method name. `Cell<u8>`
не Freeze через UnsafeCell; u8 Copy+Freeze; NonCopyByte содержит u8 без Copy impl.
Это выбирает stable/unstable default для Cell, Freeze stable/unstable для u8,
Freeze non-Copy и Freeze+Copy impls соответственно.

Clauses в `smallsort.rs` проверены по selected source impl, включая оба requires
stable Freeze и `modifies(v,scratch)`. Requires **assumed**, ensures **asserted**,
modifies **enforced** sole DFCC contract; diagnostic raw-symbol pair сам по себе
не clause proof. Ensures expression, line, полный check-wrapper stem и SUCCESS
(либо exact sole FAILURE у двух mutants) сопоставлены с rich properties.
SUCCESS frame write-site и clause allocation checks сохранены.

Producer `proof_for_contract`/resolver/manual metadata, contract mode и вложенные
check/modifies closures прочитаны в stock `0aac16ef...`. Дополнительно проверен
`transform/contracts.rs:380–407,457–525,565–585`: выбранный target исполняет
SimpleCheck, при `--no-assert-contracts` остальные contracts идут Original,
вызовы из clauses исполняют original bodies. Modifies роль следует producer
`find_modifies`, не номеру closure. Exact native JSON pointer/hash, attributes,
raw symbol и manual target-definition links согласованы с экспортом и source.

Обе exact variant patches заменяют только ensures выбранного impl, source SHA,
marker/oracle и same-instance production companions совпали. Request/argv/cfg/
checks/unwind/native invocation/source-under-test/binary snapshots сохранены;
original→projection digest distinction не скрыта. Normalization ограничена
whitespace clauses и local `core::` prefix, не generics/модулями/номерами closures.
Clause/native/symbol/config/variant mutations проходят ниже outer hash checks.

Assurance строго **bounded source-reported Profiles v4, trust pinned stock
compiler**. Независимые AST/MIR/DefId/instance-origin fields не требуются и не
присвоены. Native directory invocation ID не объявлен compilation provenance.
Это не blanket helper exemption, caller-only proof или общий threshold theorem.

**S1-08: остальная проверенная граница.** Package `8ea1c1d...`, std `99e8456d...`
(parent `5be85699...`), control `9ccd882e...` (parent `9208b373...`), tool `0aac16ef...`.

Независимая token canonicalization двух полных файлов подтвердила ровно 23
rewrites: smoke8/exact_n8/positive7. Сохранены operands и их sequence, short
circuit, guards/assumptions, initialized backing/scratch geometry, N0..3,
comparator/types и covers. Старый assert вычислял cond один раз и при false
переходил в panic; новый вычисляет тот же cond и constant string. Hook выдаёт
assert(cond);assume(cond), старый panic — assert(false);assume(false).
Путь после успешно пройденных checks совпадает; новых assumptions без checks нет.
`prove_safety_only` не включён. Constant-message allocation/extraction и удаление
reachability prefix проверены в producer; future descriptions не выданы за observed.

127 mappings сверены с исходным obligation inventory: 111 новых labels на 21
scheduled root и 16 сохранённых semantic bindings, из них три полных helper sets.
Исторические helper closure coordinates сохранены только как historical evidence;
fresh semantic re-audit обязателен. Проверены 54 supplemental sites и applicability:
N0/N1 guards сохранены, fixed N2/N3 не требуют conditional SUCCESS. Четыре legacy
symbolic roots остаются вне 35 scheduled rows. Все 113 required covers и companions
сохранены; из восьми negative oracles два имеют finding выше.

Проверены 21 manifest digest, payload/source hashes, producer source hashes,
embedded/external request и ROLE-MAP exact bytes. Source/control patches независимо
reconstruct соответствующие exact trees. Reviewed control parent имеет то же tree,
что выполненный S1-07 control. Реальный ancestor chain требует depth5; Git-fixtures
для shallow checkouts прошли. Runner byte-identical parent после замены двух std
pins; decoder/export/native capture/final snapshots/location exceptions/checks/
flags/caps и отсутствие admission внутри runner сохранены. Error/timeout/partial/
missing/null/wrong-type/NOT_RUN/source-stage-target mismatch synthetic cases прошли.

Команды/результаты: [CHECKS.json](CHECKS.json). Самостоятельные проверки и finding:
[validate_review.py](validate_review.py), [VALIDATION.json](VALIDATION.json).
Числа tests являются наблюдениями проверок, не доказательством сортировки.
