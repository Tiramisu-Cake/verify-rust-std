# G1 remediation — independent review

2026-10-12, Europe/Moscow. Implementation target:
`217c939a54c3623b5e65c5359a35263982d451f8`.
Previous independent review: `07f0180d146ed1e1ce1d89ddba7102d5f4bb882d`.

**Phase 1 remediation: NOT CLOSED.** Старые конкретные false-positive controls
исправлены, но дополнительная независимая мутация выявила остаточный дефект R1:
qualified callee разбирается как другой bare binding. Это локальный дефект
scanner, а не наблюдённый полный false admission PASS: обязательные UNKNOWN
gates продолжают блокировать положительный verdict. Нужен один узкий fix и его
service regression. Безопасное частичное исправление R2 принято именно как
PARTIAL, без положительного continuation parser.

**Cloud G1: NOT READY.** R2 positive roles, R9 exact source contracts и actual
callee linkage остаются открыты; R4–R8 не переоценивались и не закрывались.
Runtime watchdog, native core, actual RR outputs и proof — NOT_RUN. Этот review
не является разрешением исполнения, квалификацией RefinedRust или доказательством.

## Изоляция и проверенные identities

Работа выполнена в `/root/verify-rust-std-g1-review`, ветка
`review/refinedrust-g1-independent-20261011`, HEAD до review — предыдущий review
`07f0180…`. Worktree/index отдельные. `git fetch origin` выполнен; origin —
`https://github.com/Tiramisu-Cake/verify-rust-std.git`. `git ls-remote origin`
подтвердил author branch на exact target и review branch на previous review.
Merge/cherry-pick чужой history не выполнялись. Worktree автора не редактировался;
target читался через Git objects, service files сохранены в собственный sandbox
`/tmp/g1-remediation-review-217c939`. Это копирование committed bytes как данных,
не std/proof source extractor. В review branch добавлен только этот документ.

Прочитаны актуальные AGENTS, WORK-POLICY, STATUS, PLAN, COMPLETION-PLAN,
AGENT-RUNBOOK, Cloud README/PARALLEL-BUILDS, research index, challenge/general
rules, G1 execution/cloud preparation/review документы и actual source.
Policy revision: `5bf53668a4afa51c302e599be91a2dbc4b24042d`, редакция 2026-10-10;
после fetch это также последнее изменение AGENTS/WORK-POLICY в origin/main.
Read-only `gh run list --repo Tiramisu-Cake/verify-rust-std --limit 5` вернул
пустой список; это не Cloud audit. Cloud budget/charge **0/0**, own Build/token
**NONE**; компиляция, RR, injector/extractor, proof, Docker, installation,
dispatch, production infrastructure и coordinator mutations не выполнялись.

Source pin `c7ca8c467aecf10a4b53039372ee97714f854ee3`; SmallSort blob
`e555fce440872898e47fd5114f32eb15401d07df`, SHA256
`32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.
RR pin `332d945fafa14bf55c0c8390cb35ec4b0c012cff`; compiler pin
`e457a7b0d326d67b4322ef0d11bd715cfaeda48f`; profile
`rr-g1-frontend-unpatched-v1`. Pins не заменялись.

Ниже `g1/` — `research/challenge-8/refinedrust-feasibility/g1/`, номера строк
относятся к implementation target, а не к старой копии в review-worktree.

## Результаты и минимальные следующие действия

| Item | Статус | Evidence / пройденные gates | Остаточный blocker | Минимальное действие автора |
| --- | --- | --- | --- | --- |
| R1 | **PARTIAL** | Shared scanner видит все 6 inline calls / 4 bindings в synthetic fixture; comments/strings исключены; missing binding, unrelated Definition, call outside recognized blocks, nested/multiple calls не дают admission PASS. Tests 233–281, 328–332; scanner 272–330; closure 705–732. | Qualified callee silently переименован в bare binding; repro ниже. Exact actual grammar ещё неизвестна. | Отклонять unsupported qualified callee без ложного bare binding (либо поддержать его только после exact contract audit); добавить negative для inventory и event scanner. Повторить service suite. |
| R2 | **PARTIAL** | Swapped continuations, normal-only cleanup, bypass Drop, map role substitution не дают PASS; missing late DropGlue даёт event NOT_OBSERVED. MIR cleanup учитывает bad exit, missing block, cycle и unsupported terminal; payload/projection Drop даёт STOP. Tests 283–326; code 583–587, 622–626. | Positive Radium continuation parser **NOT_IMPLEMENTED**. UNKNOWN — отказ от квалификации, а не доказательство неверности каждой мутации. | Получить exact writer/lowering contract; определить normal/unwind argument roles, полный cleanup CFG и добавить positive + targeted negatives до снятия UNKNOWN. |
| R3 | **PARTIAL** | Signal/timeout classifiers **VERIFIED**: interrupted controls/stages не получают credit, включая partial P0/N1 output и code 0/1 с timeout; collector пересчитывает их. service.py 23–72; evidence.py 107–115, 279–315. Timeout process-group fix статически проверен: run.py 103–145. | Runtime watchdog/process-tree gate **NOT_RUN**; статическая проверка не удостоверяет фактическое исчезновение всех descendants. | Сохранить NOT_RUN; в отдельно разрешённой Cloud-сессии проверить parent-exits-on-TERM + surviving child, bounded TERM/KILL waits и сохранение incomplete metadata/logs. |
| R9 | **OPEN** | Собственные pins/annotations/config прочитаны; exact access attempts ниже. Python syntax и собственный emitted-config parser проверены. | Pinned RR parser/writer/config/wrapper bytes не получены. Syntax, selection, flags semantics, output/resource forms не квалифицированы. | Предоставить маленький exact-SHA source bundle/tree listing с blob IDs/hashes; провести статический audit без смены RR версии. |
| R10 | **VERIFIED** в ограниченном local collector contract | Stage-dependent required artifacts, command/execution equality, raw log SHA256/length, effective config/environment/image/source archives, archived N2 byte binding и recomputation проходят negative gates. evidence.py 57–85, 89–214, 243–360; все 6 evidence tests PASS, дополнительные negatives ниже. | Это внутренняя целостность, не authenticity исполнения. External package/upload/API/OCI completeness не проверена и остаётся false; diagnostic completeness независима. | Использовать recomputed collector verdict; external completeness включать только после отдельного R4–R8 protocol review и реального transport evidence. |
| Actual callee linkage | **OPEN** | Missing/extra binding inventory — INCONCLUSIVE; все bindings на unrelated hash-bound Definition — UNKNOWN. Наличие Definition больше не даёт OBSERVED. correspondence.py 709–732. | Positive resolver отсутствует: DefId, substitutions, location parameters и bodies/specs не связаны actual output evidence. | Проверить exact linking writer/resolver и затем связать каждое emitted ребро с actual DefId/type instantiation/body/spec; не разрешать его guessed map. |

## R1: новый минимальный воспроизводимый дефект

Synthetic parser input; не утверждается, что pinned RR действительно выводит
такую форму. Именно unsupported form должна быть отвергнута, как заявлено
docstring scanner (`correspondence.py:273–278`). Команда в sandbox:

```python
from correspondence import _radium_calls, _radium_call
s = 'CallS Module.FnMut_loc []'
print(_radium_calls(s))
print(_radium_call(s, 'Module'))
print(_radium_call(s, 'Module.FnMut_loc'))
```

Получено:

```text
([{'binding': 'Module', 'arguments': [['.'], ['FnMut_loc'], ['[', ']']]}], '')
True
False
```

Причина: lexer делит qualified identifier на `Module`, `.`, `FnMut_loc`
(`240–243`), callee check принимает первый identifier (`294–295`), `_coq_term`
разрешает `.` как одиночный argument (`247–269`). Event scanner использует тот
же ошибочный result (`403–407`). В полной исходной RADIUM fixture замена только
первого `CallS FnMut_loc` на `CallS Module.FnMut_loc` даёт inventory из шести
calls и **пустой parse error**, с первым binding `Module`. Call count сохранён,
но callee identity неверна. Это не просто пропуск положительного resolver.

Expected при нынешнем bare-location-only contract: непустой error,
никакой `_radium_call(..., 'Module')`; full inventory INCONCLUSIVE. Поддержка
qualified syntax без source contract здесь не требуется. Hard UNKNOWN gates
`radium_output_contract`, normal/unwind roles и callee linkage не позволяют
этому дефекту стать полным admission PASS на target. Код автора не исправлялся.

## R2 и R3: что проверка устанавливает

`correspondence.py:622–626` не выводит роли из произвольного Goto и отсутствия
UnwindFreeAnnot. Swapped call продолжает синтаксически разбираться; обе role
проверки остаются UNKNOWN. Map с `radium_unwind_bb=1` тоже их не повышает.
Отсутствие mapped late DropGlue отдельно обнаруживается на event gate.
`admission_complete` требует только OBSERVED для **всех** checks (767–770).
Поэтому безопасный R2 fail-closed change подтверждён; positive correctness роли
и реального cleanup по нему ещё не установлена.

`run.py:109–134` создаёт новую session/process group; timeout ставит флаг,
посылает TERM, ждёт parent не больше двух секунд, затем **всегда** пробует KILL
группы, даже если parent уже вернул code; дополнительный wait тоже bounded.
ProcessLookupError обработан. Code None и отрицательный code остаются
неположительными; timeout не исчезает при code 0/1. Runner не импортировался и
не исполнялся. Это статический gate исправления прежней parent-exit ошибки,
не runtime watchdog PASS и не гарантия для descendants, покинувших эту группу.

## R9: доступ и минимальная source closure

Независимые способы доступа к точному pin:

- Web open для [exact rrconfig raw](https://gitlab.mpi-sws.org/lgaeher/refinedrust-dev/-/raw/332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/rrconfig/src/lib.rs), corresponding blob page и GitLab v4 raw-file API с `ref=332d945…`: каждый вернул inaccessible/Internal Error, source bytes отсутствуют.
- Прямой bounded curl к raw и API: `--connect-timeout 5 --max-time 12 --max-filesize 1048576`; оба exit 28, HTTP 000, bytes 0, connect timeout около 5 секунд. Это failure доступа, не отсутствие commit на upstream.
- `git cat-file -t 332d945…` в общей object database: object unavailable. Поиск имён RR/Radium/rrconfig под `/root` и `/tmp` нашёл лишь G1 candidate filenames; дополнительные wrapper/cache filename probes source не нашли. Это не доказательство отсутствия любой локальной копии с иным именем.

Не выполнялись clone/archive download, image pull или тяжёлая подготовка;
другая revision и July artifact не подставлялись. Нужны следующие небольшие
файлы **из этого pin**, с original paths, Git blob identities и SHA256:

| Contract | Минимальные исходники / необходимые символы |
| --- | --- |
| Wrapper/flags | `rr_frontend/refinedrust_frontend/src/bin/cargo-refinedrust.rs`, `refinedrust-rustc.rs`; `rr_frontend/rrconfig/src/lib.rs`; вызываемый frontend callback/driver selection и check/export entrypoint. Для первых трёх exact blob/hash/length уже перечислены в inputs.json. |
| Attributes/ADT | `rr_frontend/translation/src/spec_parsers/verbose_function_spec_parser.rs`; actual ADT/refined_by parser module; `rr_frontend/translation/src/types/translator.rs`. Нужны `verify`, `may_unwind_if`, normal/unwind spec, generic unit refinement, `?Sized`, transparent fields/lang items и const-method selection. |
| Call/continuation grammar | Actual Radium AST definitions и Display/writer для CallS, block maps, Program Definition/f_init/Final Obligation; вызывающий MIR call lowering; `rr_frontend/translation/src/body/mir_lowering/unwind.rs`; `theories/refinedrust/radium/lang.v`. Нужно удостоверить порядок/значение normal/unwind continuations и terminal forms. |
| Linkage/Drop | Writer/resolver для emitted location parameters, DefId/type substitutions, generated linking requirements; `rr_frontend/translation/src/traits/resolution.rs`; `rr_frontend/translation/src/body/drop_glue_translation/tx_impl.rs`; `theories/refinedrust/rust_typing/primitive/functions.v` для resource/unwind spec record. |

Exact filenames неизвестных writer/ADT/linking modules не выдумываются:
сначала нужен компактный pinned tree listing для их выбора, затем только
definitions и непосредственно вызываемые helpers. README и frontend Cargo
manifests связывают этот bundle с declared entrypoints; полный toolchain/vendor
или весь repository для этого статического review не требуется.

Нужно отдельно подтвердить, что `run_check=false` действительно исключает Rocq
execution, `no_verify=false` оставляет нужную translation, `admit_proofs=false`
не выдаёт skeleton/admitted text за proof, и config precedence не меняет профиль.
Наш collector сравнивает config bytes/values; это не проверка RR semantics.

Actual source contracts для дальнейшего linkage: все семь selected bodies
(insert_tail, CopyOnDrop::drop, ManuallyDrop::new/deref, MaybeDangling::new/as_ref,
compiler glue), полный recursive CallS closure, pointer sub/read/copy boundaries,
FnMut trait call и Drop glue с exact generic substitutions. Actual source
`smallsort.rs:542–577` устанавливает early callback до move, tmp/guard/len=1,
late callback и cleanup; `manually_drop.rs:161–185,273–278` и
`maybe_dangling.rs:73–91` задают actual wrappers/fields. Синтетические definitions
не удостоверяют provenance/ownership move, payload drop suppression, callbacks
или CURRENT normal/unwind posts; `may_unwind_if(True)` — diagnostic annotation.
До summaries нужны actual callee proofs той же source version; G1 admission
сама не доказывает ресурсные контракты и не открывает G2.

## Validation receipt

Перед исполнением прочитаны imports/entrypoints: tests импортируют stdlib,
service/evidence/correspondence и test fixture helpers; нет runner/compiler,
extractor, installer, network или dispatch imports. Временные synthetic archives
изолированы, реальные evidence и live coordinator не менялись.

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s research/challenge-8/refinedrust-feasibility/g1 -p 'test_*.py' -v
Ran 30 tests in 24.253s — OK
```

Первый запуск sandbox без `library/.../smallsort.rs` имел 17 setUp
FileNotFoundError и 13 успешных service/evidence tests. После сохранения exact
Git blob набор повторён полностью с результатом выше; setup failures не
приписываются implementation и не скрываются. Все тесты — synthetic service
tests, **не actual RefinedRust outputs/replay и не proof**.

Дополнительные независимые controls:

- R1: два inline calls, unterminated comment/string и duplicate block не дают
  usable inventory; nested CallS fail closed. Qualified callee control **FAIL**
  по expected rejection, точный repro выше.
- R3: 30 stage cases с native/P1 codes None/bool/negative/128/129/137/143/255
  и timeout/signal при code 0/1 дают INCONCLUSIVE даже при supplied corr PASS;
  normal_completion/N1 assertions отказывают. Existing suite проверяет partial
  P0, interrupted controls и compiler preflight classification.
- R10: после reseal изменение длины или подмена raw P0 log при неизменном
  command record даёт `command log/environment mismatch: p0`; N2 source_commit
  на 40 zeroes даёт `archived N2 differs from reviewed bytes`. Existing suite
  удаляет image/config/command/N2 artifacts, подменяет environment/config/records
  и проверяет required P1 source archives.
- Python AST с grammar 3.10 для всех G1 `.py` PASS; runner только статически
  прочитан, не импортирован. Documentation diff проверяется без proof run.

SHA256 implementation modules:

```text
correspondence.py 2f98c2778527834b8b595de7d0bafd2cdb53f47475b28aacbbe3d7df30afe969
service.py        dffe1998e525ef0145f5bd7939f6892b3a9575c2cc5e537a5a2a2b526a3e1c23
evidence.py       9418aa023ebed5e225ed33152ba73cc7cd21243cc1f156867e6ee4413bbeab40
run.py            1f7d405c9a6d589fa0362819a1577bc9ab1c48d001263d8d76d5bb49a5964bbd
```

Ограничение R10: сохранённый summary не является authoritative input collector.
В synthetic archive можно заменить summary на PASS/PROVED, reseal и получить
`local_inventory_valid=true`, но recomputed verdict остаётся INCONCLUSIVE,
proof NOT_RUN, acceptance false. Runner сначала пишет pending summary, затем
collect и final summary; поэтому такое различие не новый Phase 1 blocker.
Downstream review обязан использовать recomputed result и отдельно проверять
final transport receipt. `evidence_complete=false` всегда; локальный hash
inventory не удостоверяет подлинность согласованно переписанного архива.

## Closeout

Следующее минимальное действие — исправить локальный R1 qualified-callee
misparse с regression, опубликовать новый exact implementation commit для
проверки. Это не требует verifier rebuild или Cloud. После этого ограниченную
Phase 1 можно рассмотреть к закрытию с **явно оставшимися** R2/R9/linkage OPEN
и watchdog NOT_RUN. Сейчас Phase 1 closure не рекомендовано.

Cloud readiness требует отдельного завершения source contracts/positive gates
и R4–R8 integration review/freeze/authorization/budget; этот документ ничего из
этого не разрешает. Собственный review commit публикуется только в назначенную
review branch, без PR. Cloud 0/0, own active/unresolved runs NONE. **STOP**.
