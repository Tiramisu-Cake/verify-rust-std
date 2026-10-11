# G1 Independent Review

Дата: 2026-10-11, Europe/Moscow. Review target:
`619cd100eed3ef5806f1c37ced79995358bc6ceb`.

**Вердикт: CONDITIONAL.** Пакет пока не готов к отдельной авторизации исполнения.
Нужны перечисленные ниже исправления служебных gates и завершённая, отдельно
проверенная интеграция Cloud. Фундаментальной причины отвергнуть frontend-only
G1 не установлено. Это не разрешение Cloud, не принятие RefinedRust и не G2.

## Scope, изоляция и основания

Собственный sparse worktree: `/root/verify-rust-std-g1-review`; ветка
`review/refinedrust-g1-independent-20261011`, создана от точного target.
Worktree автора не использовался. Изменён только этот review document.
Cloud budget/charge: **0/0**. Компиляция, installation, extraction, proof runs,
Docker/image pull, dispatch, PR и live coordinator mutations не выполнялись.

Прочитаны AGENTS, WORK-POLICY, AGENT-RUNBOOK, Cloud README/PARALLEL-BUILDS,
STATUS/PLAN/COMPLETION-PLAN, индекс, challenge/general rules и G1 phase documents
на target. Принята policy revision
`5bf53668a4afa51c302e599be91a2dbc4b24042d` (редакция 2026-10-10).
`origin` проверен как `Tiramisu-Cake/verify-rust-std`; fetch выполнен; remote
ветка автора указывала на target. Read-only `gh run list --repo
Tiramisu-Cake/verify-rust-std --limit 5` не вернул строк. Это не Cloud API audit.

Исполняемые Cloud interfaces сравнивались через Git objects baseline
`ac6a1c4ebe84ee05302f4cc5829ff1075e99d822`, который назван в proposal;
чужие checkout/clients не изменялись. Будущий resultant infra SHA нужно выбрать
и проверить заново: этот baseline не объявляется текущим production client.

В замечаниях `g1/` означает
`research/challenge-8/refinedrust-feasibility/g1/`. Строки относятся к target;
строки Cloud clients ниже — к явно указанному `ac6a1c4…`.

**Факт** — воспроизведённый service result либо непосредственно проверенное
свойство кода. **Гипотеза** — возможная несовместимость, требующая проверки.
**Evidence отсутствует** — исполнение не наблюдалось; это не доказанный отказ.
BLOCKER блокирует готовность к соответствующей отдельной Cloud authorization;
IMPORTANT требует закрыть указанный gate; MINOR — ограниченное hardening.

## Что уже установлено

- Source manifest trees и все перечисленные source files соответствуют Git
  objects `c7ca8c467aecf10a4b53039372ee97714f854ee3` по SHA256/длине.
  Все десять anchors annotations.json уникальны в закреплённых четырёх файлах.
  Это проверка сохранённых Git bytes, без запуска injector/extractor.
- `annotate.py:53–89,179–185` вставляет только фиксированные attributes,
  проверяет strip equality до и после записи. В штатном пути runner использует
  bundled manifest, включённый в authorization closure. Runtime statements,
  algorithms и generic signatures не переписываются. Исполнение этих проверок
  в Cloud и нейтральность фактического MIR пока NOT_RUN.
- Actual `smallsort.rs:542–577` действительно содержит ранний FnMut, read,
  ManuallyDrop, CopyOnDrop, shift loop, поздний FnMut и implicit guard Drop.
  Actual `manually_drop.rs:161–185,273–278` использует MaybeDangling в поле,
  constructor и Deref; `maybe_dangling.rs:73–91` содержит transparent generic
  wrapper, new и as_ref. MaybeDangling сам не подавляет Drop; подавление payload
  зависит от lang-item ManuallyDrop и compiler glue, а не unit refinement.
- `run.py:234–241` предусматривает native exact-core check до annotations;
  `run.py:134–148` не импортирует stdlib summaries и не меняет trusted RR source.
  `may_unwind_if("True")` — diagnostic permission, не CURRENT-recovery theorem.
  Нет новых Copy/Freeze/purity/no-panic premises или supplied ownership bridge.
- P0/N1 — собственные dependency-free fixtures, оба Cargo.lock присутствуют
  в Git. N2 — negative сохранённого source metadata certificate; он проверяет
  только `validate_source_metadata`, не отказ compiler/injector/MIR.
- `service.py:38`, runner и collector сохраняют `verification_accepted=false`,
  `proof_status=NOT_RUN`. Без independently reviewed map автоматический PASS
  не выдаётся. Proposal не применён и сохраняет submit refusal на строке 75.
  Патч не изменяет v2 coordination algorithm или max-two capacity.

Ни один из этих фактов не доказывает actual source admission, DefId/type binding,
resource applicability или safety. Первые три замечания показывают, почему даже
будущая externally reviewed map не заменяет исправление parser gates.

## Замечания и acceptance gates

### R1 — BLOCKER: callee inventory пропускает inline CallS

**Факт.** `g1/correspondence.py:552–569`, особенно строка 552:
`bindings` ищется regex с началом строки `^\s*CallS` в целом definition.
Собственная fixture `test_correspondence.py:65–78` располагает calls после
`<[ "_bbN" :=`. На её `insert_tail_def` inventory извлекает **пустое множество**,
хотя `_radium_blocks` и event auditor видят шесть calls. При пустом supplied
inventory gate `callees:insert_tail` способен получить OBSERVED без разрешения
этих calls. Полный ложный G1 PASS здесь не воспроизводился: штатная fixture
не содержит полной reviewed map, поэтому итог остаётся INCONCLUSIVE.

**Почему существенно:** необходимая callee closure может исчезнуть из проверки;
наличие reviewer hash не делает неправильный parser корректным.

**Минимальное исправление:** использовать один разбор statements для event и
inventory, включая inline first statement. Все emitted calls должны попадать
в inventory; неизвестная форма call — INCONCLUSIVE. Для resolution проверять
конкретную связь location parameter с DefId/type substitution/target definition,
а не только присутствие произвольного Definition в файле.

**Gate:** текущая fixture должна дать четыре distinct bindings и шесть call
sites. Удаление любого binding из map, подмена его unrelated definition или
неизвестная форма CallS не дают OBSERVED/PASS. После отдельного Cloud запуска
сверить множество и число calls с полным реальным generated definition вручную.
Не требовать proof of callees в G1: явно инвентаризировать границу и не выдавать
непроверенный shim за actual-source theorem.

### R2 — BLOCKER: Radium gate не различает normal/unwind continuations

**Факт.** `g1/correspondence.py:463–473`. Проверяется наличие любого `Goto` на
блок из receipt внутри call block; позиция normal/unwind argument не разбирается.
В synthetic fixture перестановка
`(Goto "_bb1") (Goto "_bb10")` → `(Goto "_bb10") (Goto "_bb1")`
в первом FnMut оставляет `fnmut_unwind_policy` и `radium_unwind_paths` OBSERVED.
Normal order проверяется только в MIR (`:451–454`). Для позднего Radium cleanup
достаточно достижимости DropGlue; не проверены все cleanup exits после него.
Отсутствие `UnwindFreeAnnot` само по себе не доказывает корректный unwind edge.

**Почему существенно:** проверка может подтвердить сохранение unwind при его
неправильной трансляции. Это defect gate, не утверждение о наличии такого бага RR.

**Минимальное исправление:** разобрать аргументы CallS и их continuation roles
по writer закреплённого RR. Проверять normal order и early/late cleanup graph
отдельно в Radium; требовать resume/terminate semantics и отсутствие payload
Drop по всем соответствующим выходам. Неизвестная syntax/edge — INCONCLUSIVE.

**Gate:** swapped continuations, normal-only link к cleanup, удалённый late
DropGlue, обход DropGlue к resume и payload drop не могут дать OBSERVED/PASS.
Исходная fixture допускается как synthetic control. Реальные MIR/Radium
обязательно сопоставить по DefId, phase dump, locals, branches и unwind roles
после разрешённого Cloud; synthetic green этого соответствия не доказывает.

### R3 — IMPORTANT: signals/timeouts могут засчитываться controls

**Факт.** `g1/service.py:22–33,46–55`; `g1/run.py:220–226`;
`g1/evidence.py:58–65`. `negative_unknown_procedure(-9, intended_log)` и
`negative_unknown_procedure(-15, intended_log)` возвращают True. N1 не проверяет
`timed_out`; P0 тоже учитывает только code/output. `classify` принимает native
`returncode=0,timed_out=true` и при supplied PASS correspondence выдаёт PASS.
Последнее — воспроизведение service API, не состоявшийся frontend run.

В `run.py:113–120` SIGKILL отправляется только если сам parent не завершился
после TERM: если parent вышел, а descendant проигнорировал TERM, принудительного
завершения оставшейся группы этот код не гарантирует. Это свойство алгоритма;
такой compiler process tree здесь не запускался.

**Минимальное исправление:** controls и native/P1 считать успешными только при
нетаймаутном штатном завершении; N1 требует положительный normal failure code
и единственный intended diagnostic. Collector должен пересчитать это из raw
stage records. Обеспечить bounded termination всей process group и сохранение
timeout/signal как INCONCLUSIVE, независимо от частично записанных definitions.

**Gate:** отрицательные returncodes, timed_out с code 0/1, intended error перед
timeout и частичный P0 output никогда не дают credit. Изолированный service
replay проверяет все сочетания; watchdog/process-tree gate выполняется только
в разрешённой среде, без proof toolchain на VPS. Outer timeout оставляет reserve
на failure evidence и не превращается в отрицательный control.

### R4 — BLOCKER: cold closure и image ещё не воспроизводимы

**Evidence отсутствует; nulls подтверждены.**
`g1/cloud/IMAGE-INPUTS.json:19–30`, `COLD-BUILD-RECIPE.json:22–26,50`;
`Dockerfile.candidate:13–16,24–28,57–65`.
Закреплены source/RR/compiler identities, manifest/archive hashes, base digest
и frontend lockfile. Не закреплены OS package snapshot/versions, deb closure,
vendor/context generation+hash, cargo config, registry destination и итоговый
OCI digest/binary receipts. Dockerfile отказывает при пустых build args, но
заданный извне hash ещё не удостоверяет происхождение closure. Hashes архивов
в candidate не были независимо сверены со скачанными official archives.

**Минимальное исправление:** закончить reviewed cold context recipe. Vendor
должен покрывать RR Cargo.lock **и** native core/library Cargo.lock (включая
proc-macro dependencies); фиксировать git dependency closure, checksums, deb
transitives, context inventory/modes и runtime dynamic library closure.
Dockerfile и receipt generator должны входить в pinned cold input certificate.

**Gate до cold authorization:** все input pins и registry permissions назначены,
полный context manifest/hash/generation проверяемы, offline source replacement
не имеет fallback и recipe остаётся no-Rocq. Результат cold пока получить нельзя:
для него нужна отдельная authorization. После неё только terminal reconciled
cold Build с полными logs/receipt и registry manifest digest допускает warm;
partial image/OOM/timeout не допускает warm или повторную попытку автоматически.
Bit-for-bit повторная воспроизводимость итогового OCI image пока не заявляется.

### R5 — BLOCKER: recipe не совместим с source-input/provider transport

**Факт.** `g1/cloud/refinedrust-g1-admission.recipe.candidate.json:6–16,38–51`;
`g1/cloud/dispatcher-registration.proposal.patch:30–35`;
`g1/entrypoint.sh:4–11`. На baseline `ac6a1c4…`,
`cloud-build/source-input.py:210–216` требует entrypoint в infra_paths под
cloud-build, а `:223–226` отвергает baseline `.gitmodules`, `library/Cargo.*`,
`rust-toolchain.toml`. Proposal вызывает отсутствующий `run-refinedrust-g1.sh`;
его нет и в infra_paths. Sparse certificate не материализует полный library
checkout и gitlink backtrace. Existing provider использует `CLOUD_BUILD_ID`,
project/region/OS/arch (`provider.py:14–42`); G1 требует `BUILD_ID` и не вызывает
этот provider. Нужна явная связь обеих identities, а не только environment flag.

**Минимальное исправление:** добавить узкий infra wrapper и перечислить его
в exact recipe; применять existing provider preflight. Обоснованно расширить
baseline allowlist только для G1 либо перенести эти receipts в отдельно
удостоверяемый full-source transport. В Cloud восстановить полный exact source,
проверить gitlink по pinned .gitmodules, tracked bytes/modes и ambient configs
через verify_inputs до native/annotation; никаких замен source/sysroot.

**Gate:** saved/disposable source-input pack/restore даёт ровно reviewed
entrypoint/input closure с исходными blobs/modes; пропущенный wrapper, extra
path, wrong source/gitlink и mismatch BUILD_ID/CLOUD_BUILD_ID отклоняются.
Package/config size/substitution limits проверить до submit. Не расширять
allowlist остальных lanes и не заменять их provider checks глобально.

### R6 — BLOCKER: authorization и фактически запущенный digest не удостоверены

**Evidence отсутствует; граница явно не реализована.**
`g1/run.py:43–49,87–94`; `g1/authorization.template.json:3`;
`g1/cloud/dispatcher-registration.proposal.patch:75`.
`check_identity(ids, ids)` проверяет форму/внутреннее равенство локального JSON.
Registry binding проверяет совпадение claims и форму receipt hash, но не читает
независимый registry receipt и не устанавливает digest executed step.
Template authorized=false корректен. Это documented misuse guard, не ошибка
криптографической проверки: недостающий внешний authority нельзя подразумевать.

**Минимальное исправление:** reviewed dispatcher transport формирует receipt
из отдельно одобренного phase/ledger и published proof/infra closure; передаёт
его по pinned/hash-bound config без credentials в evidence. Build ID связывается
с API/substitution, expires_at — с разрешённым окном. Независимый closeout
сравнивает submitted config и API Build, execute-step image и фактический image
digest из API image-resolution результата, cold Build/registry receipt и in-image
receipt SHA. Различать image ID/config digest и pushed OCI manifest digest;
для manifest index явно установить platform child relation.

**Gate:** неправильные proof/infra SHA, auth bytes/closure, expiry, cold receipt,
registry digest, executing step либо Build ID отклоняются до admission credit.
Копия identity.json из архива не является external expected identities.
Если API не позволяет независимо установить фактический digest, закрыть это
подтверждённой registry/API цепочкой или оставить INCONCLUSIVE; не доверять
одному PROOF_IMAGE/env. До реализации и review сохранять submit refusal.

### R7 — BLOCKER: collector не подключён к package/upload/verification protocol

**Факт.** `g1/entrypoint.sh:7–11`, `g1/cloud/WARM-CANDIDATE.json:32,40,46`;
`g1/run.py:174,179,262–272`. G1 пишет в `/workspace/g1-evidence`;
baseline `ac6a1c4…/cloud-build/package-evidence.py:18,234–291` работает с
`/workspace/evidence`, allprooflogs/cases, stage artifacts и proof-audit.json.
Простое копирование всего G1 root также нарушает запрет `home` path
в packager `:199–201`, поскольку runner создаёт HOME внутри evidence.
Автоматический runner намеренно возвращает 2 без внешней map: это необходимо
интерпретировать как diagnostic INCONCLUSIVE, не как proof acceptance.

**Минимальное исправление:** wrapper/adapter сохраняет raw G1 subtree,
формирует совместимые stage/case records и proof-audit с accepted=false,
держит HOME/caches вне evidence и сохраняет ошибку до первого compiler command.
Внешний packager связывает submitted config/source certificate/inventory/archive
hash/upload receipt; verify-evidence проверяет это независимо. Reviewed map и
replay result — отдельные hash-bound inputs/outputs, исходный archive неизменен.

**Gate:** disposable package→upload-receipt/download verification либо локальный
saved-data эквивалент даёт корректный protocol package для PASS admission,
INCONCLUSIVE, STOP, setup failure и timeout; tampered/missing/extra file,
wrong archive/config/source identity и unordered/truncated text chunks отвергаются.
В каждом случае verification_accepted=false. Если общий final step связывает
SUCCESS исключительно с proof acceptance, G1 diagnostic status должен иметь
отдельное явное значение, не ослабляющее этот invariant других lanes.

### R8 — IMPORTANT: proposal не фиксирует отдельное окно и число попыток

**Факт, latent до снятия guard.**
`g1/cloud/dispatcher-registration.proposal.patch:52–58,66–68,75`.
Regex-family RR-G1 phases и сравнение ledger deadline с ним самим не фиксируют
независимо одобренные start/main/absolute cutoffs. В этом diff нет exact 1200 s
warm timeout и enforcement one attempt; ceiling 1260 не исключает несколько
коротких terminal submissions. Нынешний guard не позволяет воспользоваться этим.

**Минимальное исправление:** зарегистрировать exact owner/phase/ledger/state,
approval identities и три временных границы; clock before start/after main
отказывает новому submit. Warm timeout=1200, reservation=1260; cold 1740/1800
отдельным account. Учитывать attempted/unresolved token, а не только elapsed
charge, если approved session допускает одну попытку.

**Gate:** saved-state coordinator/client controls на disposable state проверяют
expired/future windows, main-cutoff vs completion window, wrong owner/ledger,
repeat attempt, insufficient budget, unknown API reply и one-owner reservation.
Два occupied project slots отказывают третьему; terminal reconciliation удаляет
только matching token, сохраняя peer. Charge ceil(createTime→finishTime), queue
envelope и unresolved conservative charge остаются прежними. Для прочих lanes
сгенерированные config/authorization/refusal cases должны совпасть с baseline.
Live coordinator в review не трогать.

### R9 — IMPORTANT: RR syntax и output contract ещё не независимо квалифицированы

**Evidence отсутствует; гипотеза несовместимости открыта.**
`g1/annotations.json:27,49,71`; `g1/run.py:134–150`;
`g1/correspondence.py:166–193,519–531,589–604`.
Unit refinement ADTs не устанавливает ownership fields/generic layout. Exact
support для `?Sized`, const methods, Deref/lang items/MaybeDangling, naming
generated definitions и resource tokens не подтверждён реальным RR output.
Parser ожидает single-line Program Definition header, Final Obligation,
name tokens и literal forms/comments вроде `unwind post`. Это contract
assumptions, не evidence. Получить pinned upstream parser/writer через GitLab
raw/web в этом review не удалось (timeout/unavailable); поэтому exact syntax
и действие flags не объявляются независимо проверенными.

**Минимальное исправление до warm authorization:** проверить именно RR
`332d945…` parser/writer/config/wrapper source и frozen blobs, записать допустимые
формы attributes/output и реальные значения опций. `run_check=false` должен
предотвращать Rocq checking, `no_verify=false` оставлять выбранную translation,
`admit_proofs=false` не выдавать admitted proof за проверенный; назвать фактически
генерируемые proof skeletons отдельно. Не менять RR semantics ради matching.

**Gate после отдельно разрешённого Cloud:** реальные P0/N1 diagnostics и P1
MIR/NLL/Radium hashes, definition headers, generic substitutions, selected DefIds
и fields сверяются с source. Independent map не может подменить фактическую
связь callee location parameter с body/spec. Проверить все семь selected bodies,
включая реальный compiler glue; ordinary pointer/FnMut binding gap — STOP после
confirmed selected attribution, unrelated frontend failure — INCONCLUSIVE.
Missing/unsupported syntax остаётся INCONCLUSIVE/STOP согласно causal stage;
никаких guessed maps, only_spec, assumed bridge или source restrictions.
До получения этих данных source admission и proof acceptance — NOT_RUN.

### R10 — IMPORTANT: evidence_complete не означает полный G1 protocol evidence

**Факт.** `g1/evidence.py:41–43,58–78,99`.
Required inventory содержит только четыре служебных JSON; collect дополнительно
читает inputs.json, но не требует image receipt/cargo config, command.json/config/
environment всех attempted stages. N2 пересчитывается по fixture из текущего
collector package, не по архивному `n2-source-certificate.json`. Возвращаемое
`evidence_complete=true` потому шире фактически проверенного inventory contract.

**Минимальное исправление:** stage-dependent required artifact schema, cross-check
execution records с command.json/config/raw logs; archived controls сверять
с published bytes и классифицировать именно их. Разделить local_inventory_valid,
diagnostic_complete и external protocol evidence_complete. Последнее возможно
только после R7 archive/config/source/upload verification.

**Gate:** удалить image receipt, effective RR config, command record или archived
N2, сохранив остальные JSON и resealed inventory: результат не может утверждать
полноту. Не выполненный stage помечается NOT_RUN с causal reason. N2 остаётся
metadata negative и не засчитывается как compiler/injector rejection.

### R11 — MINOR: standalone injector разрешает произвольный manifest

**Факт, ограниченный non-default interface.** `g1/annotate.py:117–129,197–203`.
`--manifest` проверяет schema/HEAD и declared file hashes, но не ограничивает
file/anchor set bundled G1 manifest. Штатный runner этот override не использует
и pins bundled bytes через authorization; обхода штатной closure здесь нет.

**Минимальное исправление:** удалить override из operational entrypoint либо
требовать explicitly approved manifest hash и exact file/symbol/anchor/attr set.

**Gate:** альтернативные file/anchor/attributes с тем же source HEAD не принимаются
operational interface; изменённый approved manifest требует нового published
harness identity. Static interface/manifest audit достаточен для review;
injector на VPS не запускать.

## Проведённая проверка и её пределы

Прочитаны entrypoints/imports service suites. Разрешённые малые изолированные
tests не импортируют runner/injector и не запускают toolchains:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s research/challenge-8/refinedrust-feasibility/g1 -p 'test_*.py' -v
```

**15/15 PASS**, synthetic only. Дополнительные ephemeral service probes дали:

| Probe | Результат target |
| --- | --- |
| N1 intended log, exit -9 / -15 | True / True |
| Whole-definition CallS inventory на собственной fixture | 0 bindings |
| Block parser на той же fixture | 6 call blocks |
| Native code 0 + timed_out=true + supplied corr PASS | verdict PASS, proof NOT_RUN |
| Переставлены normal/unwind Goto первого Radium FnMut | два unwind gates OBSERVED |

Probes не создавали full valid reviewed map и не показывают фактический RR bug
или состоявшийся ложный Cloud PASS. Они показывают конкретные defects gates.
AST/JSON parsing всех g1 Python/JSON, `bash -n entrypoint.sh`, source Git
hash/anchor checks и `git diff --check` прошли. Никаких новых proof claims.

## Минимальный порядок исправлений и решение

1. Исправить R1–R3 и R10: один структурный parser calls/continuations,
   signal/timeout rejection, точные completeness labels. Пройти названные
   mutation gates и review pinned RR syntax/config по R9. G2/proofs не добавлять.
2. Завершить cold input closure R4, получить review recipe/permissions и
   подготовить отдельную cold authorization request. До её исполнения image
   остаётся UNCONFIRMED. Использовать существующий exact image можно лишь при
   независимо подтверждённом полном closure match.
3. Завершить узкий wrapper/recipe/provider и evidence adapter R5/R7; сохранить
   проверки других lanes. Проверить transport/package/disposable coordinator
   gates без изменения production coordinator, затем опубликовать resultant
   infra SHA и frozen proof/harness SHA.
4. Закрыть R6/R8: authority/config/API/OCI chain, exact session/ledger/deadlines,
   one attempt и v2 accounting. Снять dispatch guard только после review
   конкретного operational diff и отдельного решения владельца. Для warm нужна
   terminal cold receipt или эквивалентный независимо проверенный existing image.
5. Только после отдельной warm authorization выполнить один frontend diagnostic;
   реальные output/DefId/cleanup gates R9 и исправленного parser определяют
   admission. Внешний reviewed-map replay сохраняет исходный результат. Даже
   admission PASS оставляет verification_accepted=false, CURRENT recovery и
   Rocq proof NOT_RUN; никаких G2, retry или расширения trust profile автоматически.

**CONDITIONAL:** обязательны R1/R2/R4–R7 и закрытие соответствующих R3/R8–R10
gates; R11 — ограниченное hardening штатного interface. Эта review-сессия
завершена. Активных Build этой review нет; budget 0, unresolved submissions не
создавались. Следующее допустимое действие — решение владельца по исправленному
пакету и отдельная Cloud authorization. После публикации review работа остановлена.
