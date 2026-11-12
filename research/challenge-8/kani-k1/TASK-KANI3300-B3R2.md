# KANI3300 B3R2 — rustc-layout ZST decision и regression/characterization tests, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна стадия, **Cloud $0**, без запусков.
Прочитать **целиком** `kani3300/b3p/AUDIT-EXTERNAL.md` @ t0 **e6fb9eb7ec**, затем это задание:
решения координатора A–C ниже имеют приоритет над предложениями аудитора об issue/rebase/PR.
Это верификация корректности, не security-работа.

## Pins и итоговый commit

Клон **/root/kani-fix-zst-b3**, clean **fix/zst-union-codegen-v2** @
**83a413f9be2d57389c991d9f5d1250b4e4386203**, tree **c9b9bafdeca616fac235574f33dad477c25ad90b**.
Проверить HEAD/branch/dirty state; иначе STOP, без reset/stash. Старую ветку/коммит сохранить.
Создать **fix/zst-union-codegen-v3** от **bf9c58e662fd65c64381ef2ac97a6397ffc0693a** и перенести нужный v2 diff,
затем исправления/тесты. Existing v3 не перезаписывать. Финал — **один fix-plus-tests commit**, sole parent = base;
author/committer **Tiramisu-Cake <igkharin@gmail.com>** через git -c, нейтральное сообщение без [skip ci].
Amend разрешён только новой неопубликованной v3 для review fixes. **Kani не пушить**; workflow/CI-only commits не включать.
По координатору upstream main остался на base, открытых PR на codegen_union нет: rebase/повторный поиск не нужны.

## A — обязательный layout fix и два recursive regression inputs

В `codegen_union` решение о zero-sized payload получать из **rustc layout**, уже вычисленного в `fields_info`:
донести `is_zst = ty_size == 0` либо эквивалентно сравнить padding с union_size в padded ветке.
Не использовать `ty.sizeof_in_bits(&ctx.symbol_table)` для этого решения; не переносить этот запрос в helper/debug_assert/log.
При recursive pointer graph StructTag может ссылаться на IncompleteStruct. В новом conditional не должно быть GOTO sizeof walk.
Логический arm type в unionfield, rustc widths/padding, nonzero payload и zero-padding/all-ZST поведение сохранить.
Не менять глобально struct lowering, ABI/layout, field offsets или private memory models.

Добавить оба auditor cases как **изолированные default-check expected fixtures** (one harness/compiler input каждый),
семантика SUCCESS, не golden «ожидаемый ICE»:

1. Node { next: *const U }, U { big: [u8;16], small: Node }, harness начинает с Node.
2. repr(C) Node2 { next: *const Link }, repr(C) Link { bytes:[u8;8], marker:[Node2;0] }, harness начинает с Node2.

Сохранить recursive type graphs и необходимость положительного padding. Union fields должны быть legal Rust:
добавить Clone/Copy derive Node/Node2, если требуется; не менять arm на другой тип только ради компиляции.
Root не должен заранее codegen U/Link через их value/size_of/вспомогательную сигнатуру и тем скрыть дефект.
Не оставлять полностью мёртвый `_n`: сохранить Node/Node2 через подходящий observable/black_box/noinline consumer,
не добавляя прямой union path в root. При необходимости допустим inferred null pointer cast без отдельного U-typed helper.
Dead-code warning у recursive union fields подавить узко и обоснованно, не читать union только ради -D warnings.
Actual retained type/root order и v2 ICE — **NOT_RUN** до CI; отсутствие воспроизведения не объявлять доказанным отсутствием бага.

## B — обязательные characterization inputs, без ложного PASS

Подготовить исполняемые default-check Rust probes:

- repr(C), Copy Tail { b:u8, z:[();2] } как **ненулевой padded arm** union с byte arm достаточного extent;
- **первый arm без padding** `(u64,[();2])` в union той же ширины.

Сохранить смысл auditor examples; для Tail при полезности отдельный first-arm companion (порядок fields явно record).
Реальные full-extent src byte writes → typed union copy → наблюдаемые initialized data assertions; padding не читать.
Зафиксировать union/arm rustc size, положительный/нулевой padding, retained nested ZST и путь post-copy read.

Первый этап — static **ASSESSMENT-B.md**: текущий A fix не меняет nonzero nested payload и обходит no-padding branch.
Оценить минимальную естественную union-only extension с сохранением logical/physical types и offsets; не считать доказанной
схему рекурсивной перезаписи struct representations. Если нужна general struct/ZST elision/новый representation contract,
это отдельная задача, не расширять текущий fix исподволь.

Base/v2/v3 поведение устанавливает **CI координатора**. Пока неизвестно, держать B probes в research `b3r2/probes/`
с semantic expected SUCCESS и exact hashes, не ставить crash/Unsupported/ignored test в активную suite как будто это PASS.
CI request использует обычный kani file.rs на этих pinned inputs; новый runner/framework не нужен.
Если v3 проходит — после CI решить перенос probes в active tests с наблюдаемыми goldens; если base и v3 падают,
либо узкая обоснованная extension отдельной repair-стадией, либо явно задокументированное ограничение.
**Base PASS → v3 FAIL/ICE — новая регрессия и blocker**, не «известное ограничение». В этой сессии не угадывать CI исход.

## C — желательные дополнительные controls

По возможности добавить до пяти небольших default-check success harnesses: ZST-array arm первым; [[();2];3];
[[u8;0];2]; выровненный ZST-array [Z;2]; ZST struct, содержащая array. Приоритет — field order и nested arrays.
Сохранить старые 7 harness/assertions/expected без ослабления. Новые controls — отдельный fixture/group.
Logical projections/index bounds/length и data assertions после typed copy сохраняются; zero-size assignment не выдавать
за physical write. Для alignment различить Rust align_of и реально используемый address/reference; не обещать второе по первому.
Добавить **kani::cover!** с различимым post-copy/recursive-root observable и ожиданием SATISFIED по existing
`tests/expected/cover/cover-pass` conventions. Cover подтверждает reachability, не заменяет correctness assertion/type binding.
Невакуумность проверять per-harness; не считать одну общую строку SAT достаточной для всех случаев.
Детали IDs/counts/диагностики не выдумывать; compile/golden outcomes новых inputs пока NOT_RUN.

## Review, CI request и результат

Статика: git diff --check, imports/unused/-D warnings source audit, pinned API/layout review, разрешённая rustfmt-обёртка
`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh --config-path rustfmt.toml`.
Bounded независимый Luna High review A delta + recursive/edge inputs + B assessment, без вложенной делегации;
concrete findings устранить, delta вернуть тому же reviewer. Никаких локальных cargo/rustc/Kani/CBMC/сборок/реальных tests.

В **t0** `research/challenge-8/kani-k1/kani3300/b3r2/`: `NOTES.md` (≤35 строк), `ASSESSMENT-B.md`,
`probes/`, `TEST-MANIFEST.json`, `LIMITATIONS.md`, `REVIEW.md`, `CI-REQUEST.md`, `RESULT-KANI3300-B3R2.md` (≤20 строк).
Manifest: active/probe/deferred отдельно, exact inputs/expected/source shapes и NOT_RUN observed. Parent/count/tree/diff
проверить; tree v3 закономерно новый, старому v2 CI его не приписывать.

CI request: одинаковые A/B/new C inputs на **base bf9c58e662 / v2 83a413f9be / v3 exact new SHA**, per-harness
setup/compiler/CBMC/verdict/cover/exit/exception distinction; старые 7 default controls сохранить. Для A подтвердить
retained Node-first graph и источник ICE, если он есть; для B — полный observed result, не только workflow status.
Подготовить exact test-only patch/hash inventory для base/v2 сравнения без изменения их production/старых branches.
После targeted — существующие format/build/clippy/regression/verify-std jobs координатора на точной голове;
платформенные unavailable/cancelled не PASS. Только **default checks**: отдельная uninit-checks panic не исправляется этим треком.

Допустимы **KANI-ISSUE-DRAFT.md / CBMC-ISSUE-DRAFT.md** только как файлы с source/run/version/repro и явным NOT_RUN
для неизмеренных предположений. Не утверждать прямой CBMC minimum без прогона/данных, не закрывать #5085/#4854 по сходству.
**PR-DRAFT.md / PR-UPSTREAM.md не менять и новый PR-текст не писать** — его обновит владелец по LIMITATIONS/results.
Issue/PR/комментарии не публиковать; никаких сторонних PR links.

Research commit [skip ci], тот же author/committer через git -c, stage только kani3300/b3r2/, push t0 без force;
чужие b1r3/PR-UPSTREAM и другие active/staged файлы не включать. Concurrent/non-fast-forward → handoff без reset/stash/force.
Без Actions/Cloud dispatch/workflow edits, raw logs/archives/credentials. После reviewed local candidate STOP до CI;
последующая B repair/characterization — новая сессия по результатам, не ожидание в старой.
Последняя строка: `READY <sha локального единственного v3 Kani-коммита>`.
