# KANI3300 C1-T2-A — анализ mixed baseline/M1 после CI, worker 15

**Подготовлено координатором 2026-11-12.** Runtime **Codex**, одна аналитическая сессия, **Cloud $0**.
Пакет C1-T2 уже READY: research **10b5800a8e**, local test commit **c2d607d9d5fafdc44a6c5fa3d981f760e522a05a**,
tree **c98ecfb2bd4d68532337fdbe88e49d8a4ea48446**, parent **28e684cbae348130d559b87e030536d8f8a3c1ff**.
Не повторять создание восьми fixtures. Это верификация корректности, не security-работа.

## Активация по новой паре CI: анализ и узкий repair четырёх MU inputs

По координатору baseline Quick **43225818126** (production6134e42dd1 + exact c2d607d9d5): expected **125/9**,
все 8 mixed FAIL и known maybe-uninit-initialized. M1 Quick **43225812282**, composition **d8a39dbc00**, CI **2ae27bd269**:
unit5/0, expected **134/4**. Четыре u8 cases raw/eq stack-left/right — baseline uninit-read `[u8;3]` false FAIL,
M1 PASS, включая actual SpecArrayEq<u8,3> по сообщению координатора. Это действующие differential controls.
Четыре MU cases в обеих lanes остановились раньше raw_eq на единственном layout Unsupported для
**MaybeUninit<[MaybeUninit<u8>;3]>** в maybe_uninit.rs:430 (as_mut_ptr/assume_init). Intended MU read не reached;
их старые failures не подтверждают ни false propagation, ни promotion mask. Exact missing pins/bindings уточнить в INPUTS.

**Выбор (a), разрешён test-only repair сейчас.** Прочитать SCOPE-MU-OF-FLAT.md. В своей ветке от c2d607d9d5
исправить ТОЛЬКО четыре raw-mu source inputs: stack как **[MaybeUninit<u8>;3]** напрямую, без внешнего MU и его
as_mut_ptr/assume_init. Например mutable flat array + `array.as_mut_ptr().cast::<u8>()` и те же реальные writes 7,0,9;
borrow `&array` перед raw_eq. Не заменять на reference к частично initialized [u8;3].
Promoted const operand, значения/holes (P-left offset0/P-right offset2), направления, raw_eq и semantic goldens сохранить.
Четыре u8 cases, old C1-T и original D0 — побайтно unchanged; исходные C1-T2 baseline/M1 results оставить на старых hashes.
Обновить comments: S теперь tracked flat stack, не outer-assume_init temporary. Изменение goldens только для фактически
наблюдённых деталей, не под ранний Unsupported. Если новый setup всё ещё не поддержан, STOP с конкретным source binding,
не расширять layout model или ослаблять payload requirement.

Один новый local test-fix commit; production не менять, Kani не пушить. Source/format/hash checks и bounded Luna High
review valid-reference/input-binding delta. В c1t2a/ записать OLD→NEW hashes/diff rationale/repair SHA и updated CI-REQUEST:
тот же fixed test delta на baseline и M1, плюс unchanged u8/C1-T/D0; rerun только координатора. Новые outcomes NOT_RUN.
Analysis findings по старым inputs сохранить, но не называть repair проверенным до rerun. Causal old-C1-T explanation
по-прежнему требует actual MIR, его не выводить из этих u8 differential outcomes.

## Вход и условие анализа

Прочитать `kani3300/c1t2/{RESULT-KANI3300-C1T2.md,TEST-MANIFEST.json,BINDING-QUESTIONS.md,CI-REQUEST.md}`,
M0 contract и M1 SOURCE-BINDINGS. Baseline production **6134e42dd1c65dc980336e7d9455aba02d423edf**;
M1 **5abdcf982da6aff65662e198af27a9c776830a89** + exact C1-T2 delta, composition SHA/tree задаёт координатор.
Исторические runs **43219870063** и **43222702257** не запускали эти восемь mixed inputs и не заменяют новую пару.

Координатор передаёт новые exact baseline/M1 composition/run/tool/flags identities и targeted reports/MIR.
Пока их нет: можно проверить source/manifest и сформулировать точный запрос, но status **AWAITING_CI**, не completed
causal analysis. CI не запускать и не ждать в старой сессии; основной анализ — после отдельного handoff.
При доступности части cases разобрать их; отсутствующие пометить UNAVAILABLE/NOT_RUN по фактической стадии, не обобщать.

## Что установить

1. По всем **6 unchanged C1-T + 8 mixed + 2 original D0**: exact selected input/hash/production, emitted harness/checks,
   setup/compiler/solver/golden/property status и extra failures. C1-T2 mu left/right hole offsets — 0/2, S initialized.
2. Почему old promoted-only legal matched baseline: actual Stack/Aggregate/GlobalAlloc::Memory/Static origins,
   retained raw_eq, CheckAs<[u8;size]>/get, reset/setter/seed/copy и relevance/phase activation. SUCCESS не доказывает
   init event, FAILURE не доказывает нужный operand; missing record при incomplete artifact — UNKNOWN.
3. Mixed D0-like S/P и P/S: native raw_eq и std == specialization, оба pointers/ranges/carriers/AllocIds/masks/symbols;
   источник state до чтения. Source static-lifetime/const item не означает автоматически anonymous promotion.
4. Для legal M1 требовать reached justified checks/equality SUCCESS; для hole — intended P read FAILURE и lawful S check
   SUCCESS, без другого раннего validity/layout/frame/Unsupported failure. Hole через std [u8] == не coverage:
   typed-hole input был бы invalid раньше equality. NOT_APPLICABLE boundary сохраняется.
5. Immutable Some/None bridge и M1 seed: captured referent mask до zero-fill, compatible symbol binding, per-model reset
   completion до first user effect; mutable S не получает immutable seed, post-copy false не reinitialized.
   Compile-time AllocId не runtime object ID. При отсутствии runtime/actual mask binding не писать, что она измерена.
6. Diff baseline/M1 показать **по case/property**, а не общей суммой suite: что различает модели, что лишь regression,
   что LOWERING_MISMATCH/UNBOUND. D0 [u8;4] unchanged остаётся обязательной опорой, [u8;3] probes его не заменяют.

Обычный Quick, --emit=mir и existing authorized property reports; без нового runner/adapter. Недостаток данных —
конкретный targeted запрос координатору, не raw/full-log fallback. D0-A прежняя raw-access exception сюда не переносится.
Не выводить семантику из no-match/cap или переразмечать исторические results как локально полные.

## Findings/repair и результат

Model defect вернуть владельцу 14 с exact source/property/control, production не менять. Concrete fixture binding/validity
дефект можно исправить отдельным test-only commit в своей ветке от c2d607d9d5, с bounded Luna High review и повторным CI
координатора; expected verdict не подстраивать под ложный baseline FAIL. При repair старый run остаётся на старом input,
M3 gate ждёт приёмки нового result. Разрешённое выше удаление внешнего MU возвращает inputs в исходный flat scope;
новое nested-layout support/широкая смена test domain/новый framework — STOP.

g0 **kani3300/c1t2a/**: `INPUTS.json`, `OBSERVATIONS.json`, `BINDINGS.md`, `FINDINGS.md`,
`RESULT-KANI3300-C1T2A.md` (≤20 строк). Для критичных conclusions — bounded Luna High review source/binding logic,
без повторного production review/вложенной делегации. Сохранять reported vs observed/independent assurance и UNKNOWN.
Критерий handoff M3 — обе lanes/critical cases bound либо точный blocker/решение координатора; READY сам gate не открывает.
Research commit [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com> через git -c, stage только kani3300/c1t2a/,
push g0 без force; concurrent update → handoff без reset/stash/чужих файлов. Kani не пушить.
Запрещены local cargo/rustc/Kani/CBMC/Miri/builds, CI/Actions/Cloud dispatch/workflow edits, raw archives/full logs/credentials,
PR/issue/комментарии и сторонние PR links. После результата STOP; M3/model work только отдельной activation.
В этой repair-активации последняя строка: `READY <sha локального test-fix Kani-коммита>`;
в результате отдельно research SHA и completed/partial/AWAITING_RERUN binding status. READY не открывает M3 gate.
